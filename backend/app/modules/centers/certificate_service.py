"""
app/modules/centers/certificate_service.py
"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, HRFlowable
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.centers.models import CenterLicense
from app.modules.centers.repository import CenterLicenseRepository, CenterRepository
from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository
from app.shared.exceptions.http import BadRequestException

logger = logging.getLogger(__name__)

GREEN = colors.HexColor("#0d6e4f")
GOLD = colors.HexColor("#b08d57")
DARK = colors.HexColor("#0f172a")
GREY = colors.HexColor("#64748b")

PAYMENT_METHOD_LABELS = {
    "mobile_money": "Mobile Money",
    "bank_transfer": "Virement bancaire",
}


class CenterLicenseCertificateService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.license_repo = CenterLicenseRepository(db)
        self.center_repo = CenterRepository(db)
        self.user_repo = UserRepository(db)
        self.certificates_dir = Path("storage/certificates")
        self.certificates_dir.mkdir(parents=True, exist_ok=True)

    async def generate_for_license(self, license_id: UUID) -> str:
        """
        Récupère toutes les données réelles liées à la licence et génère le PDF.
        Retourne l'URL relative du fichier généré.
        """
        license_ = await self.license_repo.get_by_id_or_404(license_id)

        if license_.status.value != "active":
            raise BadRequestException(
                detail="Une attestation ne peut être générée que pour une licence active."
            )

        center = await self.center_repo.get_by_id_or_404(license_.center_id)
        formula = license_.formula  # chargé via relation si eager, sinon requête séparée ci-dessous
        if formula is None:
            from app.modules.centers.repository import LicenseFormulaRepository
            formula = await LicenseFormulaRepository(self.db).get_by_id_or_404(license_.formula_id)

        director = await self._get_director(center.id)
        director_name = director.full_name if director else "Direction du centre"

        certificate_ref = f"GTG-LIC-{license_.start_date.year}-{str(license_.id)[:6].upper()}"
        payment_method_label = PAYMENT_METHOD_LABELS.get(
            license_.payment_method.value if license_.payment_method else "", "—"
        )

        pdf_filename = f"{certificate_ref}.pdf"
        pdf_path = self.certificates_dir / pdf_filename

        self._build_pdf(
            pdf_path=str(pdf_path),
            center_name=center.name,
            director_name=director_name,
            formula_label=formula.label,
            start_date=license_.start_date,
            end_date=license_.end_date,
            max_students=license_.max_students,
            payment_method=payment_method_label,
            payment_reference=license_.payment_reference or "—",
            certificate_ref=certificate_ref,
            issued_at=datetime.now(timezone.utc),
        )

        return f"/certificates/{pdf_filename}"

    async def _get_director(self, center_id: UUID) -> User | None:
        from sqlalchemy import select
        result = await self.db.execute(
            select(User).where(
                User.center_id == center_id,
                User.role == UserRole.center_director,
            )
        )
        return result.scalars().first()

    # ── Génération PDF ────────────────────────────────────

    def _draw_border(self, canvas_obj, doc):
        canvas_obj.saveState()
        width, height = A4
        margin = 1.1 * cm
        canvas_obj.setStrokeColor(GOLD)
        canvas_obj.setLineWidth(1.2)
        canvas_obj.rect(margin, margin, width - 2 * margin, height - 2 * margin)
        inner = margin + 0.15 * cm
        canvas_obj.setStrokeColor(GREEN)
        canvas_obj.setLineWidth(0.6)
        canvas_obj.rect(inner, inner, width - 2 * inner, height - 2 * inner)
        canvas_obj.restoreState()

    def _build_pdf(
        self,
        pdf_path: str,
        center_name: str,
        director_name: str,
        formula_label: str,
        start_date: datetime,
        end_date: datetime,
        max_students: int,
        payment_method: str,
        payment_reference: str,
        certificate_ref: str,
        issued_at: datetime,
    ):
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2.4 * cm,
            leftMargin=2.4 * cm,
            topMargin=1.8 * cm,
            bottomMargin=1.8 * cm,
        )
        styles = getSampleStyleSheet()

        kicker_style = ParagraphStyle(
            "Kicker", parent=styles["Normal"], fontSize=9, textColor=GOLD,
            alignment=TA_CENTER, spaceAfter=2,
        )
        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"], fontSize=24, textColor=DARK,
            alignment=TA_CENTER, spaceAfter=2, fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "Subtitle", parent=styles["Normal"], fontSize=10.5, textColor=GREY,
            alignment=TA_CENTER, spaceAfter=0,
        )
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"], fontSize=10.5, textColor=DARK,
            alignment=TA_JUSTIFY, leading=15, spaceAfter=6,
        )
        center_name_style = ParagraphStyle(
            "CenterName", parent=styles["Heading1"], fontSize=19, textColor=GREEN,
            alignment=TA_CENTER, spaceBefore=6, spaceAfter=6, fontName="Helvetica-Bold",
        )
        label_style = ParagraphStyle(
            "Label", parent=styles["Normal"], fontSize=9, textColor=GREY,
            fontName="Helvetica-Bold",
        )
        value_style = ParagraphStyle(
            "Value", parent=styles["Normal"], fontSize=11, textColor=DARK,
        )
        footer_style = ParagraphStyle(
            "Footer", parent=styles["Normal"], fontSize=8, textColor=GREY,
            alignment=TA_CENTER,
        )
        ref_style = ParagraphStyle(
            "Ref", parent=styles["Normal"], fontSize=8.5, textColor=GREY,
            alignment=TA_CENTER,
        )
        doc_title_style = ParagraphStyle(
            "DocTitle", parent=styles["Normal"], fontSize=14, textColor=DARK,
            alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=3,
        )

        story = []

        # ── En-tête ──────────────────────────────────────
        story.append(Paragraph("I T I A&nbsp;&nbsp;S A R L", kicker_style))
        story.append(Paragraph("GOTOGERMANY", title_style))
        story.append(Paragraph("Plateforme de préparation aux examens d'allemand", subtitle_style))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="60%", thickness=0.8, color=GOLD, hAlign="CENTER"))
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph("ATTESTATION DE LICENCE DE CENTRE", doc_title_style))
        story.append(Paragraph(f"Réf. {certificate_ref}", ref_style))
        story.append(Spacer(1, 0.5 * cm))

        # ── Corps ─────────────────────────────────────────
        story.append(Paragraph(
            "ITIA SARL, éditeur de la plateforme GoToGermany, atteste par la présente que le "
            "centre de formation ci-dessous bénéficie d'une licence d'accès active, permettant "
            "à ses étudiants inscrits d'utiliser la plateforme de préparation aux examens "
            "d'allemand (TELC, Goethe, ÖSD) dans les conditions décrites ci-après.",
            body_style,
        ))

        story.append(Paragraph(center_name.upper(), center_name_style))
        story.append(Paragraph(f"Représenté par {director_name}", subtitle_style))
        story.append(Spacer(1, 0.5 * cm))

        # ── Tableau des conditions ────────────────────────
        rows = [
            [Paragraph("FORMULE SOUSCRITE", label_style), Paragraph(formula_label, value_style)],
            [Paragraph("PLACES ALLOUÉES", label_style), Paragraph(f"{max_students} étudiants", value_style)],
            [Paragraph("DATE DE DÉBUT", label_style), Paragraph(start_date.strftime("%d/%m/%Y"), value_style)],
            [Paragraph("DATE D'ÉCHÉANCE", label_style), Paragraph(end_date.strftime("%d/%m/%Y"), value_style)],
            [Paragraph("MODE DE PAIEMENT", label_style), Paragraph(payment_method, value_style)],
            [Paragraph("RÉFÉRENCE PAIEMENT", label_style), Paragraph(payment_reference, value_style)],
        ]
        table = Table(rows, colWidths=[5.5 * cm, 10.5 * cm])
        table.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.6 * cm))

        story.append(Paragraph(
            "Cette attestation certifie la souscription et l'activation de la licence décrite "
            "ci-dessus à la date d'émission. Elle est établie à titre justificatif et n'a pas de "
            "valeur comptable, le reçu de paiement correspondant fait foi pour toute question "
            "fiscale ou comptable.",
            ParagraphStyle("Note", parent=body_style, fontSize=9, textColor=GREY,
                            fontName="Helvetica-Oblique", spaceAfter=0, leading=13),
        ))
        story.append(Spacer(1, 0.9 * cm))

        # ── Signature ─────────────────────────────────────
        sign_data = [
            [
                Paragraph(f"Fait à Dschang, le {issued_at.strftime('%d/%m/%Y')}", value_style),
                Paragraph("Pour ITIA SARL", label_style),
            ],
            [
                Paragraph("", value_style),
                Paragraph("<br/><br/>_____________________", value_style),
            ],
        ]
        sign_table = Table(sign_data, colWidths=[8 * cm, 8 * cm])
        sign_table.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ]))
        story.append(sign_table)

        story.append(Spacer(1, 0.7 * cm))
        story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            "ITIA SARL - Dschang, Cameroun - www.prep-telc-osd.com<br/>"
            "Document généré automatiquement, vérifiable auprès d'ITIA SARL sur présentation de la référence ci-dessus.",
            footer_style,
        ))

        doc.build(story, onFirstPage=self._draw_border, onLaterPages=self._draw_border)