from fastapi import APIRouter, Depends
from sqlmodel import Session

from .. import services
from ..auth import get_current_user
from ..models import PretCreate
from ..storage import get_session

router = APIRouter()


@router.post("/loans", status_code=201)
def emprunter(
    pret: PretCreate,
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.emprunter(session, pret.materiel_id, utilisateur["username"])


@router.get("/loans")
def lister_prets(
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.lister_prets_visibles(session, utilisateur)


@router.patch("/loans/{pret_id}/return")
def rendre(
    pret_id: int,
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.enregistrer_retour(session, pret_id, utilisateur)
