"""
app/modules/centers/router.py
"""
from uuid import UUID
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentDirector, CurrentCenterStaff
from app.modules.centers.schemas import (
    CenterCreateRequest,
    CenterResponse,
    CenterDetailResponse,
    BranchCreateRequest,
    BranchResponse,
    LicenseFormulaCreateRequest,
    LicenseFormulaResponse,
    CenterLicenseActivateRequest,
    CenterLicenseExtendRequest,
    CenterLicenseResponse,
    LicenseUsageResponse,
    CenterCreditPoolRechargeRequest,
    CenterDefaultCreditsUpdateRequest,
    CenterCreditTransactionResponse,
    CenterPoolResponse,
)
from app.modules.centers.service import CenterService
from app.shared.database.session import get_db
from app.modules.centers.repository import CenterLicenseRepository
from app.shared.exceptions.http import BadRequestException
from app.modules.centers.certificate_service import CenterLicenseCertificateService

router = APIRouter()


# ── Directeur (routes /me/... — toujours déclarées avant /{center_id}/...) ──

@router.get("/me/branches", response_model=list[BranchResponse])
async def list_my_branches(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Liste les succursales du centre du directeur connecté."""
    return await CenterService(db).list_my_branches(current_director.center_id)


@router.post("/me/branches", response_model=BranchResponse, status_code=201)
async def create_my_branch(
    data: BranchCreateRequest,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Le directeur crée une succursale supplémentaire pour son propre centre."""
    return await CenterService(db).create_branch(current_director.center_id, data)


@router.get("/me/usage", response_model=LicenseUsageResponse)
async def get_my_center_usage(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Vue consolidée pour le panel directeur : quota, jours restants, répartition par succursale."""
    return await CenterService(db).get_usage_for_center(current_director.center_id)


@router.get("/me/license/certificate")
async def get_my_license_certificate(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Le directeur génère/télécharge l'attestation de la licence active de son propre centre."""
    license_ = await CenterLicenseRepository(db).get_active_for_center(current_director.center_id)
    if not license_:
        raise BadRequestException(detail="Aucune licence active pour votre centre.")
    url = await CenterLicenseCertificateService(db).generate_for_license(license_.id)
    return {"certificate_url": url}


@router.get("/me/pool", response_model=CenterPoolResponse)
async def get_my_center_pool(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Le directeur consulte le solde du pool et le défaut par étudiant de son centre."""
    center = await CenterService(db).center_repo.get_by_id_or_404(current_director.center_id)
    return center


@router.patch("/me/default-credits", response_model=CenterPoolResponse)
async def update_default_credits(
    data: CenterDefaultCreditsUpdateRequest,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Le directeur fixe le nombre de crédits attribués par défaut à chaque
    nouvel étudiant créé dans son centre."""
    return await CenterService(db).update_default_credits(
        current_director.center_id, data.default_credits_per_student, current_director
    )


@router.get("/me/credit-transactions", response_model=list[CenterCreditTransactionResponse])
async def get_my_center_credit_transactions(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Vue d'audit complète pour le directeur — tout l'historique des
    ajustements de crédits de son centre, toutes secrétaires confondues."""
    return await CenterService(db).get_credit_transactions_for_director(
        current_director.center_id
    )


@router.get("/me/credit-transactions/mine", response_model=list[CenterCreditTransactionResponse])
async def get_my_credit_transactions(
    current_user: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    """Historique restreint aux propres actions de l'utilisateur connecté
    (secrétaire : ses ajustements uniquement). Un directeur qui appelle cette
    route ne voit également que ses propres actions — pour la vue complète
    du centre, utiliser /me/credit-transactions."""
    return await CenterService(db).get_credit_transactions_for_secretary(current_user)


# ── Admin ITIA ────────────────────────────────

@router.post("", response_model=CenterResponse, status_code=201)
async def create_center(
    data: CenterCreateRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Créer un centre — crée aussi sa branch principale automatiquement."""
    return await CenterService(db).create_center(data)


@router.get("", response_model=list[CenterResponse])
async def list_centers(
    skip: int = 0,
    limit: int = 100,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les centres — admin ITIA."""
    return await CenterService(db).list_centers(skip=skip, limit=limit)


@router.get("/formulas", response_model=list[LicenseFormulaResponse])
async def list_formulas(
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Liste les formules de licence actives — admin ITIA."""
    return await CenterService(db).list_active_formulas()


@router.post("/formulas", response_model=LicenseFormulaResponse, status_code=201)
async def create_formula(
    data: LicenseFormulaCreateRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Créer une formule de licence (durée × plafond)."""
    return await CenterService(db).create_formula(data)


@router.post("/{center_id}/branches", response_model=BranchResponse, status_code=201)
async def create_branch(
    center_id: UUID,
    data: BranchCreateRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Créer une succursale supplémentaire — admin ITIA."""
    return await CenterService(db).create_branch(center_id, data)


@router.post("/{center_id}/license/activate", response_model=CenterLicenseResponse, status_code=201)
async def activate_license(
    center_id: UUID,
    data: CenterLicenseActivateRequest,
    current_admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Activer une licence pour un centre — après confirmation du paiement."""
    return await CenterService(db).activate_license(center_id, data, current_admin)


@router.post("/{center_id}/license/extend", response_model=CenterLicenseResponse)
async def extend_license(
    center_id: UUID,
    data: CenterLicenseExtendRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Étendre le quota d'une licence active — prorata jusqu'à la fin existante."""
    return await CenterService(db).extend_license(center_id, data)


@router.get("/{center_id}/license/certificate")
async def get_license_certificate_admin(
    center_id: UUID,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Génère et retourne l'attestation PDF de la licence active du centre — admin ITIA."""
    license_ = await CenterLicenseRepository(db).get_active_for_center(center_id)
    if not license_:
        raise BadRequestException(detail="Aucune licence active pour ce centre.")
    url = await CenterLicenseCertificateService(db).generate_for_license(license_.id)
    return {"certificate_url": url}


@router.post("/{center_id}/credit-pool/recharge", response_model=CenterPoolResponse)
async def recharge_credit_pool(
    center_id: UUID,
    data: CenterCreditPoolRechargeRequest,
    current_admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Rechargement manuel du pool de crédits IA d'un centre — admin ITIA
    uniquement, validé après négociation/paiement hors plateforme."""
    return await CenterService(db).recharge_pool(
        center_id, data.amount, current_admin, data.reason
    )