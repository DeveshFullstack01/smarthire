from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def generate_offer_letter(offer):
    """
    Generates a professional Offer Letter PDF
    and returns a BytesIO object.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    elements = []

    title_style = ParagraphStyle(
        name="Title",
        fontSize=22,
        alignment=TA_CENTER,
        textColor=HexColor("#0d6efd"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        name="Heading",
        fontSize=13,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=11,
        leading=22,
    )

    elements.append(
        Paragraph(
            "<b>SMARTHIRE ATS</b>",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            "<b>JOB OFFER LETTER</b>",
            heading_style,
        )
    )

    elements.append(Spacer(1, 20))

    candidate = offer.application.candidate
    job = offer.application.job
    company = job.company

    elements.append(
        Paragraph(
            f"<b>Candidate:</b> {candidate.get_full_name()}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Company:</b> {company.name}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Designation:</b> {offer.designation}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Annual Salary:</b> ₹ {offer.offered_salary}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Joining Date:</b> {offer.joining_date}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Offer Valid Until:</b> {offer.expiry_date}",
            normal_style,
        )
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            offer.recruiter_note,
            normal_style,
        )
    )

    elements.append(Spacer(1, 40))

    elements.append(
        Paragraph(
            "<b>Congratulations! We look forward to working with you.</b>",
            normal_style,
        )
    )

    elements.append(Spacer(1, 50))

    elements.append(
        Paragraph(
            "Authorized Signatory",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            company.name,
            normal_style,
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer