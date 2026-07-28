import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.complaint import Complaint


def build_complaint_pdf(complaint: Complaint) -> bytes:
    """
    Generate a professional pharmaceutical QMS complaint report PDF using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Pharma QMS Palette
    primary_color = colors.HexColor("#1A56DB")
    dark_gray = colors.HexColor("#1F2937")
    light_bg = colors.HexColor("#F9FAFB")
    accent_border = colors.HexColor("#E5E7EB")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#6B7280"),
    )

    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_gray,
    )

    story: list[Any] = []

    # 1. Header Title Banner
    story.append(Paragraph("AICCMS Pharma QMS — Quality Complaint Report", title_style))
    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | Confidentially Documented",
            subtitle_style,
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=primary_color,
            spaceBefore=2,
            spaceAfter=12,
        )
    )

    # 2. General Complaint Metadata Table
    story.append(Paragraph("1. Complaint Record Details", heading2_style))
    meta_data = [
        [
            Paragraph("<b>Complaint ID:</b>", body_style),
            Paragraph(complaint.complaint_id, body_style),
            Paragraph("<b>Status:</b>", body_style),
            Paragraph(complaint.status, body_style),
        ],
        [
            Paragraph("<b>Date Received:</b>", body_style),
            Paragraph(str(complaint.date_received), body_style),
            Paragraph("<b>Priority:</b>", body_style),
            Paragraph(complaint.priority or "—", body_style),
        ],
        [
            Paragraph("<b>Product Name:</b>", body_style),
            Paragraph(complaint.product_name or "—", body_style),
            Paragraph("<b>Risk Level:</b>", body_style),
            Paragraph(complaint.risk_level or "—", body_style),
        ],
        [
            Paragraph("<b>Batch Number:</b>", body_style),
            Paragraph(complaint.batch_number or "—", body_style),
            Paragraph("<b>Category:</b>", body_style),
            Paragraph(complaint.category or "—", body_style),
        ],
        [
            Paragraph("<b>Customer:</b>", body_style),
            Paragraph(complaint.customer_name or "—", body_style),
            Paragraph("<b>Submitted By:</b>", body_style),
            Paragraph(complaint.submitted_by or "—", body_style),
        ],
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), light_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, accent_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, accent_border),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Complaint Description
    if complaint.complaint_text:
        story.append(Paragraph("2. Reported Complaint Description", heading2_style))
        story.append(
            Paragraph(
                complaint.complaint_text.replace("\n", "<br/>"),
                body_style,
            )
        )
        story.append(Spacer(1, 10))

    # 4. AI Advisory Copilot Section
    if complaint.ai_analysis:
        ai = complaint.ai_analysis
        raw = ai.raw_llm_response or {}
        story.append(Paragraph("3. AI Advisory Copilot Evaluation", heading2_style))

        summary_text = (
            raw.get("summary", {}).get("detailed_summary")
            or ai.complaint_summary
            or "AI analysis completed."
        )
        story.append(Paragraph(f"<b>Summary:</b> {summary_text}", body_style))
        story.append(Spacer(1, 4))

        if ai.root_cause_recommendation:
            story.append(
                Paragraph(
                    f"<b>Root Cause Hypothesis:</b><br/>{ai.root_cause_recommendation.replace('\n', '<br/>')}",
                    body_style,
                )
            )
            story.append(Spacer(1, 4))

        if ai.capa_recommendation:
            story.append(
                Paragraph(
                    f"<b>CAPA Recommendations:</b><br/>{ai.capa_recommendation.replace('\n', '<br/>')}",
                    body_style,
                )
            )
            story.append(Spacer(1, 4))

        risk_exp = raw.get("risk_explanation", {}).get("explanation")
        if risk_exp:
            story.append(
                Paragraph(
                    f"<b>Risk Explanation ({ai.risk_level}):</b> {risk_exp}",
                    body_style,
                )
            )

        story.append(Spacer(1, 10))

    # 5. Reviewer Notes
    notes = [n for n in getattr(complaint, "notes", []) if not getattr(n, "is_deleted", False)]
    if notes:
        story.append(Paragraph("4. Quality Reviewer Notes", heading2_style))
        note_rows = [
            [
                Paragraph("<b>Author</b>", body_style),
                Paragraph("<b>Date</b>", body_style),
                Paragraph("<b>Note Content</b>", body_style),
            ]
        ]
        for note in notes:
            note_rows.append([
                Paragraph(note.author, body_style),
                Paragraph(note.created_at.strftime("%Y-%m-%d %H:%M"), body_style),
                Paragraph(note.content, body_style),
            ])

        note_table = Table(note_rows, colWidths=[100, 110, 330])
        note_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, accent_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, accent_border),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(note_table)
        story.append(Spacer(1, 10))

    # Build PDF document
    doc.build(story)
    return buffer.getvalue()
