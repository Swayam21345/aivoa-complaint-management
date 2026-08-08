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
    },
    {
        "id": uuid.UUID("a4444444-4444-4444-4444-444444444444"),
        "complaint_id": "CC-20260728-0004",
        "date_received": date(2026, 7, 26),
        "status": "NEW",
        "priority": "High",
        "product_name": "Epinephrine Auto-Injector 0.3mg",
        "batch_number": "LOT-EPI-2026-881",
        "customer_name": "Kaiser Permanente Central Pharmacy",
        "category": "Device Malfunction",
        "risk_level": "High",
        "submitted_by": "Pharmacist Ellen Ripley",
        "assigned_to": None,
        "assigned_by": None,
        "complaint_text": "Patient returned an unused Epinephrine Auto-Injector stating needle safety guard mechanism remained locked during emergency training simulation deployment test.",
        "ai_summary": "Epinephrine Auto-Injector safety guard failing to release during deployment test on Lot EPI-2026-881.",
        "root_cause_rec": "1. Spring tension intolerance in safety sleeve assembly.\n2. Excess molding flash on plastic actuator latch.",
        "capas_rec": "1. Perform automated actuation force testing on retain sample batch.\n2. Quarantine lot EPI-2026-881 pending device history record review.",
        "rca": None,
        "capa": None
    },
    {
        "id": uuid.UUID("a5555555-5555-5555-5555-555555555555"),
        "complaint_id": "CC-20260728-0005",
        "date_received": date(2026, 7, 26),
        "status": "TRIAGED",
        "priority": "Low",
        "product_name": "Ondansetron 4mg ODT (Oral Disintegrating Tablets)",
        "batch_number": "LOT-OND-2026-054",
        "customer_name": "Walgreens Regional Depot #12",
        "category": "Customer Satisfaction",
        "risk_level": "Low",
        "submitted_by": "Quality Lead Mark Davis",
        "assigned_to": "Lead Investigator",
        "assigned_by": "QA Manager",
        "complaint_text": "Two retail store customers reported strawberry flavor masking was noticeably weaker than prior refill batches.",
        "ai_summary": "Taste variation in Ondansetron 4mg ODT Lot OND-2026-054 reported by 2 customers.",
        "root_cause_rec": "1. Flavor excipient lot variation.\n2. Incomplete dry mixing blending time.",
        "capas_rec": "1. Verify assay and organoleptic testing results on Certificate of Analysis.\n2. Review blending homogenization validation records.",
        "rca": None,
        "capa": None
    },
    {
        "id": uuid.UUID("a6666666-6666-6666-6666-666666666666"),
        "complaint_id": "CC-20260728-0006",
        "date_received": date(2026, 7, 27),
        "status": "ASSIGNED",
        "priority": "Medium",
        "product_name": "Enoxaparin Sodium 60mg/0.6mL Syringes",
        "batch_number": "LOT-ENO-2026-310",
        "customer_name": "Cleveland Clinic Supply Chain",
        "category": "Container Integrity",
        "risk_level": "Medium",
        "submitted_by": "Inpatient Pharmacy Supervisor",
        "assigned_to": "Lead Investigator",
        "assigned_by": "QA Manager",
        "complaint_text": "Nurses reported pre-filled syringes exhibited higher than normal plunger glide force during subcutaneous administration.",
        "ai_summary": "Increased plunger glide resistance in Enoxaparin 60mg pre-filled syringes (Lot ENO-2026-310).",
        "root_cause_rec": "1. Barrel silicone coating thickness non-uniformity.\n2. Rubber stopper formulation durometer variation.",
        "capas_rec": "1. Measure break-through and glide force on retain samples.\n2. Review siliconization spray nozzle maintenance logs.",
        "rca": None,
        "capa": None
    },
    {
        "id": uuid.UUID("a7777777-7777-7777-7777-777777777777"),
        "complaint_id": "CC-20260728-0007",
        "date_received": date(2026, 7, 27),
        "status": "ROOT_CAUSE_IDENTIFIED",
        "priority": "High",
        "product_name": "Tobramycin Ophthalmic Solution 0.3%",
        "batch_number": "LOT-TOB-2026-921",
        "customer_name": "Johns Hopkins Outpatient Clinic",
        "category": "Physical Appearance Deviation",
        "risk_level": "High",
        "submitted_by": "Dr. Aris Thorne (Ophthalmology Lead)",
        "assigned_to": "QA Manager",
        "assigned_by": "System Administrator",
        "complaint_text": "Slight opalescence haze observed in 5 bottles stored at 25°C room temperature. Solution should remain clear and colorless.",
        "ai_summary": "Opalescent precipitation in Tobramycin 0.3% ophthalmic solution Lot TOB-2026-921.",
        "root_cause_rec": "1. Temperature-dependent solubility drop of benzalkonium chloride preservative.\n2. pH shift below 5.2 during buffer preparation.",
        "capas_rec": "1. Conduct HPLC active assay and degradation profile analysis.\n2. Re-evaluate buffer pH tolerance limits.",
        "rca": {
            "id": uuid.UUID("b7777777-7777-7777-7777-777777777777"),
            "rca_number": "RCA-20260728-0007",
            "methodology": "FIVE_WHYS",
            "primary_root_cause": "Low ambient storage temperature caused micro-crystallization of preservative benzalkonium chloride due to tight pH buffer specifications.",
            "root_cause_category": "Raw Material Defect",
            "status": "APPROVED",
            "created_by": "Lead Investigator",
        },
        "capa": None
    },
    {
        "id": uuid.UUID("a8888888-8888-8888-8888-888888888888"),
        "complaint_id": "CC-20260728-0008",
        "date_received": date(2026, 7, 28),
        "status": "QA_REVIEW",
        "priority": "High",
        "product_name": "Heparin Sodium 5,000 USP Units/mL",
        "batch_number": "LOT-HEP-2026-605",
        "customer_name": "Mount Sinai Hospital Blood Bank",
        "category": "Potency / Assay Deviation",
        "risk_level": "High",
        "submitted_by": "Blood Bank Operations Director",
        "assigned_to": "QA Manager",
        "assigned_by": "System Administrator",
        "complaint_text": "QC laboratory testing indicated anti-Factor Xa activity assay was 91.2% of label claim (specification range: 95.0% - 105.0%).",
        "ai_summary": "Sub-specification potency assay (91.2%) for Heparin Sodium Lot HEP-2026-605.",
        "root_cause_rec": "1. Thermal degradation during active API storage.\n2. Analytical testing calibration drift.",
        "capas_rec": "1. Issue voluntary market recall for Lot HEP-2026-605.\n2. Implement cold-chain temperature logger monitoring on crude API storage vessels.",
        "rca": {
            "id": uuid.UUID("b8888888-8888-8888-8888-888888888888"),
            "rca_number": "RCA-20260728-0008",
            "methodology": "HYBRID",
            "primary_root_cause": "API storage tank cooling jacket sensor failure exposed active heparin raw material to 38°C for 72 hours prior to formulation.",
            "root_cause_category": "Equipment Failure",
            "status": "APPROVED",
            "created_by": "QA Manager",
        },
        "capa": {
            "id": uuid.UUID("c8888888-8888-8888-8888-888888888888"),
            "capa_number": "CAPA-20260728-0008",
            "title": "API Tank Chiller Dual Redundancy & Real-Time SCADA Alarm Integration",
            "description": "Install redundant secondary chiller unit and integrate real-time temperature alarm triggers with automated SMS/email alerts to plant engineering.",
            "action_type": "CORRECTIVE",
            "priority": "HIGH",
            "status": "COMPLETED",
            "owner": "QA Manager",
        }
    },
    {
        "id": uuid.UUID("a9999999-9999-9999-9999-999999999999"),
        "complaint_id": "CC-20260728-0009",
        "date_received": date(2026, 7, 28),
        "status": "QA_APPROVED",
        "priority": "Medium",
        "product_name": "Insulin Glargine 100 units/mL SoloStar Pen",
        "batch_number": "LOT-INS-2026-114",
        "customer_name": "Endocrine Care Specialists Clinic",
        "category": "Device Mechanical Defect",
        "risk_level": "Medium",
        "submitted_by": "Dr. Hannah Vance (Endocrinologist)",
        "assigned_to": "QA Manager",
        "assigned_by": "System Administrator",
        "complaint_text": "Dose selector dial mechanism did not click loudly at 2-unit increments on 4 pen units from single retail box.",
        "ai_summary": "Audible click feedback failure on Insulin Glargine pen dose selector dial Lot INS-2026-114.",
        "root_cause_rec": "1. Ratchet gear plastic rib wear.\n2. Lubricant over-application on internal dial gear ring.",
        "capas_rec": "1. Audit supplier injection molding tool tolerances.\n2. Update automated assembly line grease dispensing nozzle calibration.",
        "rca": {
            "id": uuid.UUID("b9999999-9999-9999-9999-999999999999"),
            "rca_number": "RCA-20260728-0009",
            "methodology": "FIVE_WHYS",
            "primary_root_cause": "Automatic lubricant dispensing nozzle over-lubricated internal ratchet ring, dampening audible click mechanism.",
            "root_cause_category": "Process Deviation",
            "status": "APPROVED",
            "created_by": "Lead Investigator",
        },
        "capa": {
            "id": uuid.UUID("c9999999-9999-9999-9999-999999999999"),
            "capa_number": "CAPA-20260728-0009",
            "title": "Precision Grease Dispensing Valve Upgrade for Insulin Pen Line",
            "description": "Replace pneumatic grease dispenser with micro-metering peristaltic valve to guarantee exact 0.05mL lubricant volume per pen assembly.",
            "action_type": "PREVENTIVE",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "owner": "QA Manager",
        }
    },
    {
        "id": uuid.UUID("a1010101-1010-1010-1010-101010101010"),
        "complaint_id": "CC-20260728-0010",
        "date_received": date(2026, 7, 28),
        "status": "CLOSED",
        "priority": "Low",
        "product_name": "Lisinopril 10mg Tablets 100-Count Bottle",
        "batch_number": "LOT-LIS-2026-702",
        "customer_name": "AmerisourceBergen Warehouse Depot",
        "category": "Shipping / Transit Damage",
        "risk_level": "Low",
        "submitted_by": "Logistics Quality Inspector",
        "assigned_to": "QA Manager",
        "assigned_by": "System Administrator",
        "complaint_text": "One wooden pallet received at distribution warehouse exhibited corner shipper box crush damage from freight transport strapping.",
        "ai_summary": "Transit box crush damage on 2 outer cartons of Lisinopril 10mg Lot LIS-2026-702.",
        "root_cause_rec": "1. Excessive pallet strapping tension applied by third-party carrier.\n2. Cardboard edge protector missing on pallet corners.",
        "capas_rec": "1. Replace 2 damaged outer shipping cartons.\n2. Issue Carrier Non-Conformance Notice (NCN) to logistics vendor.",
        "rca": {
            "id": uuid.UUID("b1010101-1010-1010-1010-101010101010"),
            "rca_number": "RCA-20260728-0010",
            "methodology": "FIVE_WHYS",
            "primary_root_cause": "Freight carrier applied manual steel banding without corner edge protectors, crushing top outer carton edges.",
            "root_cause_category": "Operational Error",
            "status": "APPROVED",
            "created_by": "QA Manager",
        },
        "capa": {
            "id": uuid.UUID("c1010101-1010-1010-1010-101010101010"),
            "capa_number": "CAPA-20260728-0010",
            "title": "Logistics Carrier SOP Enforcement & Heavy-Duty Corner Board Requirement",
            "description": "Update Palletizing Standard Operating Procedure SOP-LOG-018 requiring mandatory heavy-duty corner protectors on all outbound freight shipments.",
            "action_type": "PREVENTIVE",
            "priority": "LOW",
            "status": "COMPLETED",
            "owner": "QA Manager",
        }
    }
]

async def seed():
    async with AsyncSessionLocal() as db:
        print("Seeding 10 comprehensive demo complaint records...")
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
        print("10 Demo complaints successfully seeded into database!")

if __name__ == "__main__":
    asyncio.run(seed())
