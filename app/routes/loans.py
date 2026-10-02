from fastapi import APIRouter, Depends
from sqlmodel import Session

from .. import services
from ..auth import get_current_user
from ..models import PretCreate
from ..storage import get_session

router = APIRouter()


@router.post(
    "/loans",
    status_code=201,
    tags=["Prets"],
    summary="Emprunter du materiel",
    description="Cree un nouveau pret pour l'utilisateur connecte. Refuse (409) si le materiel a deja un pret actif.",
)
def emprunter(
    pret: PretCreate,
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.emprunter(session, pret.materiel_id, utilisateur["username"])


@router.get(
    "/loans",
    tags=["Prets"],
    summary="Lister les prets",
    description="Un etudiant ne voit que ses propres prets ; un gestionnaire voit tous les prets.",
)
def lister_prets(
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.lister_prets_visibles(session, utilisateur)


@router.patch(
    "/loans/{pret_id}/return",
    tags=["Prets"],
    summary="Rendre du materiel",
    description="Marque un pret comme rendu. Refuse (403) si ce n'est ni le proprietaire du pret ni un gestionnaire.",
)
def rendre(
    pret_id: int,
    session: Session = Depends(get_session),
    utilisateur: dict = Depends(get_current_user),
):
    return services.enregistrer_retour(session, pret_id, utilisateur)