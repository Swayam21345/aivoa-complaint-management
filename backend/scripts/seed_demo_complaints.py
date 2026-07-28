import asyncio
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.complaint import Complaint
from app.models.ai_analysis import AIAnalysis
from app.models.rca import RCARecord
from app.models.capa import CAPARecord
from app.models.audit_event import AuditEvent

DEMO_COMPLAINTS = [
    {
        "id": uuid.UUID("a1111111-1111-1111-1111-111111111111"),
        "complaint_id": "CC-20260728-0001",
        "date_received": date(2026, 7, 20),
        "status": "CAPA_IN_PROGRESS",
        "priority": "High",
        "product_name": "Amoxicillin & Clavulanate 875mg/125mg Tablets",
        "batch_number": "LOT-AMX-2026-402",
        "customer_name": "Mercy General Hospital Pharmacy",
        "category": "Product Quality Defect",
        "risk_level": "High",
        "submitted_by": "Dr. Sarah Jenkins (Chief Pharmacist)",
        "assigned_to": "QA Manager",
        "assigned_by": "System Administrator",
        "complaint_text": "Hospital pharmacy reported that 3 blister packs from Lot AMX-2026-402 contained discolored tablets with dark brown speckling and crumbling edges. Moisture breach suspected in packaging blister line.",
        "ai_summary": "Discoloration and tablet crumbling reported in 3 blister packs of Amoxicillin & Clavulanate 875mg/125mg Tablets (Lot AMX-2026-402) at Mercy General Hospital Pharmacy.",
        "root_cause_rec": "1. Moisture ingress during blister sealing due to temperature fluctuations on Packaging Line #3.\n2. Inadequate seal integrity check during batch clearance.\n3. Micro-channel leak in aluminum foil substrate.",
        "capas_rec": "1. Quarantine remaining inventory of Lot AMX-2026-402.\n2. Perform leak testing and seal integrity validation on Packaging Line #3.\n3. Revise blister sealing temperature calibration SOP.",
        "rca": {
            "id": uuid.UUID("b1111111-1111-1111-1111-111111111111"),
            "rca_number": "RCA-20260728-0001",
            "methodology": "FIVE_WHYS",
            "primary_root_cause": "Faulty heating element in blister sealing station caused localized temperature drop below 165°C, resulting in incomplete foil-to-PVC bonding and micro-moisture ingress.",
            "root_cause_category": "Equipment Failure",
            "status": "APPROVED",
            "created_by": "Lead Investigator",
        },
        "capa": {
            "id": uuid.UUID("c1111111-1111-1111-1111-111111111111"),
            "capa_number": "CAPA-20260728-0001",
            "title": "Blister Sealer Heating Element Replacement & Automated Temperature Monitoring",
            "description": "Replace worn heating element on Packaging Line #3 blister sealer and install continuous digital temperature sensor with automated line-stop interlock.",
            "action_type": "CORRECTIVE",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
            "owner": "QA Manager",
        }
    },
    {
        "id": uuid.UUID("a2222222-2222-2222-2222-222222222222"),
        "complaint_id": "CC-20260728-0002",
        "date_received": date(2026, 7, 22),
        "status": "UNDER_INVESTIGATION",
        "priority": "Medium",
        "product_name": "Metformin Hydrochloride 500mg ER Tablets",
        "batch_number": "LOT-MET-2026-109",
        "customer_name": "CVS Specialty Distribution Center",
        "category": "Packaging & Labeling",
        "risk_level": "Medium",
        "submitted_by": "Robert Vance (Receiving Supervisor)",
        "assigned_to": "Lead Investigator",
        "assigned_by": "QA Manager",
        "complaint_text": "Outer shipper carton secondary labeling was missing 2D DataMatrix barcode and expiration date stamp on 15 shipping cases received at logistics hub.",
        "ai_summary": "Missing 2D DataMatrix barcode and expiration date on 15 secondary shipper cases of Metformin 500mg ER (Lot MET-2026-109).",
        "root_cause_rec": "1. Sensor mis-alignment on inkjet cartoning coder.\n2. Incomplete vision system verification trigger prior to case packing.",
        "capas_rec": "1. Re-label affected 15 cartons with validated barcode labels.\n2. Recalibrate online vision inspection sensor.",
        "rca": {
            "id": uuid.UUID("b2222222-2222-2222-2222-222222222222"),
            "rca_number": "RCA-20260728-0002",
            "methodology": "FISHBONE",
            "primary_root_cause": "Inkjet printer nozzle clogging combined with optical sensor bypass switch left enabled after maintenance.",
            "root_cause_category": "Operational Error",
            "status": "UNDER_REVIEW",
            "created_by": "Lead Investigator",
        },
        "capa": None
    },
    {
        "id": uuid.UUID("a3333333-3333-3333-3333-333333333333"),
        "complaint_id": "CC-20260728-0003",
        "date_received": date(2026, 7, 25),
        "status": "QA_REVIEW",
        "priority": "Critical",
        "product_name": "Sterile Water for Injection 50mL Vials",
        "batch_number": "LOT-SWI-2026-012",
        "customer_name": "Mayo Clinic Quality Assurance",
        "category": "Particulate Contamination",
        "risk_level": "High",
        "submitted_by": "Dr. Michael Chang (Surgical Director)",
        "assigned_to": "QA Manager",
        "assigned_by": "System Administrator",
        "complaint_text": "Operating room surgical nurse observed visible translucent particulate floating in two un-opened 50mL glass vials prior to IV drug reconstitution.",
        "ai_summary": "Visible translucent particulate contamination observed in 2 vials of Sterile Water for Injection 50mL (Lot SWI-2026-012) prior to surgical IV use.",
        "root_cause_rec": "1. Depyrogenation tunnel temperature deviation during vial washing.\n2. Silicone oil droplets from stopper lubrication system.\n3. Glass delamination micro-flakes.",
        "capas_rec": "1. Immediate health hazard evaluation (HHE) and medical risk assessment.\n2. Comprehensive particle isolation via polarized light microscopy and FTIR spectroscopy.\n3. Initiate targeted field recall for Lot SWI-2026-012.",
        "rca": {
            "id": uuid.UUID("b3333333-3333-3333-3333-333333333333"),
            "rca_number": "RCA-20260728-0003",
            "methodology": "HYBRID",
            "primary_root_cause": "FTIR spectroscopy confirmed particles were silicone emulsion droplets resulting from an over-pressurized stopper silicone washing pump on Sterilization Line A.",
            "root_cause_category": "Process Deviation",
            "status": "APPROVED",
            "created_by": "QA Manager",
        },
        "capa": {
            "id": uuid.UUID("c3333333-3333-3333-3333-333333333333"),
            "capa_number": "CAPA-20260728-0003",
            "title": "Stopper Siliconization Pump Flow Meter Upgrade & 100% Automatic Inspection",
            "description": "Install positive displacement metering pump on stopper siliconizer and enable high-definition camera visual particle inspection on aseptic line.",
            "action_type": "PREVENTIVE",
            "priority": "HIGH",
            "status": "COMPLETED",
            "owner": "QA Manager",
        }
    }
]

async def seed():
    async with AsyncSessionLocal() as db:
        print("Seeding demo complaint records into PostgreSQL...")
        for cdata in DEMO_COMPLAINTS:
            # Check existing
            stmt = select(Complaint).where(Complaint.complaint_id == cdata["complaint_id"])
            res = await db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                print(f"Complaint {cdata['complaint_id']} already exists. Skipping.")
                continue

            complaint = Complaint(
                id=cdata["id"],
                complaint_id=cdata["complaint_id"],
                date_received=cdata["date_received"],
                status=cdata["status"],
                priority=cdata["priority"],
                product_name=cdata["product_name"],
                batch_number=cdata["batch_number"],
                customer_name=cdata["customer_name"],
                category=cdata["category"],
                risk_level=cdata["risk_level"],
                submitted_by=cdata["submitted_by"],
                assigned_to=cdata["assigned_to"],
                assigned_by=cdata["assigned_by"],
                complaint_text=cdata["complaint_text"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(complaint)

            # AI Analysis record
            ai_record = AIAnalysis(
                id=uuid.uuid4(),
                complaint_id=cdata["id"],
                extracted_product_name=cdata["product_name"],
                extracted_batch_number=cdata["batch_number"],
                extracted_customer_name=cdata["customer_name"],
                extracted_category=cdata["category"],
                risk_level=cdata["risk_level"],
                complaint_summary=cdata["ai_summary"],
                root_cause_recommendation=cdata["root_cause_rec"],
                capa_recommendation=cdata["capas_rec"],
                model_used="gemma2-9b-it",
                created_at=datetime.now(timezone.utc),
            )
            db.add(ai_record)

            # Audit event
            evt = AuditEvent(
                id=uuid.uuid4(),
                complaint_id=cdata["id"],
                action_type="COMPLAINT_CREATED",
                description=f"Complaint {cdata['complaint_id']} ingested into QMS repository.",
                actor_email="system@aiccms.local",
                created_at=datetime.now(timezone.utc),
            )
            db.add(evt)

            # RCA record if present
            if cdata["rca"]:
                rdata = cdata["rca"]
                rca = RCARecord(
                    id=rdata["id"],
                    complaint_id=cdata["id"],
                    rca_number=rdata["rca_number"],
                    methodology=rdata["methodology"],
                    primary_root_cause=rdata["primary_root_cause"],
                    root_cause_category=rdata["root_cause_category"],
                    status=rdata["status"],
                    created_by=rdata["created_by"],
                    updated_by=rdata["created_by"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(rca)

            # CAPA record if present
            if cdata["capa"]:
                cpdata = cdata["capa"]
                capa = CAPARecord(
                    id=cpdata["id"],
                    complaint_id=cdata["id"],
                    capa_number=cpdata["capa_number"],
                    title=cpdata["title"],
                    description=cpdata["description"],
                    corrective_action=cpdata["description"],
                    priority=cpdata["priority"],
                    status=cpdata["status"],
                    owner=cpdata["owner"],
                    created_by="QA Manager",
                    updated_by="QA Manager",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(capa)

        await db.commit()
        print("Demo complaints successfully seeded into PostgreSQL database!")

if __name__ == "__main__":
    asyncio.run(seed())
