from fastapi import APIRouter, Depends
from sqlmodel import Session

from .. import services
from ..auth import exiger_role, get_current_user
from ..models import MaterielCreate
from ..storage import get_session

router = APIRouter()


@router.get(
    "/equipment",
    tags=["Materiel"],
    summary="Lister le materiel",
    description="Renvoie tout le materiel du catalogue. Accessible a tout utilisateur connecte.",
)
def lister_equipement(
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.lister_materiels(session)


@router.post(
    "/equipment",
    status_code=201,
    tags=["Materiel"],
    summary="Ajouter du materiel",
    description="Ajoute un nouveau materiel au catalogue. Reserve au role **gestionnaire**.",
)
def ajouter_equipement(
    materiel: MaterielCreate,
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(exiger_role("gestionnaire")),
):
    return services.creer_materiel(session, materiel.reference, materiel.nom, materiel.categorie)


@router.get(
    "/equipment/{materiel_id}/history",
    tags=["Materiel"],
    summary="Historique d'un materiel",
    description="Liste tous les prets (passes et actifs) d'un materiel. Reserve au role **gestionnaire**.",
)
def historique(
    materiel_id: int,
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(exiger_role("gestionnaire")),
):
    return services.historique_materiel(session, materiel_id)
