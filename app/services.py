from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from .models import Materiel, Pret


def creer_materiel(session: Session, reference: str, nom: str, categorie: str) -> Materiel:
    existe_deja = session.exec(select(Materiel).where(Materiel.reference == reference)).first()
    if existe_deja is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cette reference existe deja")
    materiel = Materiel(reference=reference, nom=nom, categorie=categorie)
    session.add(materiel)
    session.commit()
    session.refresh(materiel)
    return materiel


def lister_materiels(session: Session) -> list[Materiel]:
    return list(session.exec(select(Materiel)).all())


def _pret_actif_pour(session: Session, materiel_id: int) -> Optional[Pret]:
    return session.exec(
        select(Pret).where(Pret.materiel_id == materiel_id, Pret.date_retour == None)
    ).first()


def emprunter(session: Session, materiel_id: int, emprunteur: str) -> Pret:
    materiel = session.get(Materiel, materiel_id)
    if materiel is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Materiel inconnu")
    if _pret_actif_pour(session, materiel_id) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ce materiel a deja un pret actif")
    pret = Pret(materiel_id=materiel_id, emprunteur=emprunteur)
    session.add(pret)
    session.commit()
    session.refresh(pret)
    return pret


def lister_prets_visibles(session: Session, utilisateur: dict) -> list[Pret]:
    if utilisateur["role"] == "gestionnaire":
        return list(session.exec(select(Pret)).all())
    return list(session.exec(select(Pret).where(Pret.emprunteur == utilisateur["username"])).all())


def enregistrer_retour(session: Session, pret_id: int, utilisateur: dict) -> Pret:
    pret = session.get(Pret, pret_id)
    if pret is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Pret inconnu")
    if utilisateur["role"] != "gestionnaire" and pret.emprunteur != utilisateur["username"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez rendre que votre propre pret")
    if pret.date_retour is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ce pret a deja ete rendu")
    from .models import now_utc
    pret.date_retour = now_utc()
    session.add(pret)
    session.commit()
    session.refresh(pret)
    return pret


def historique_materiel(session: Session, materiel_id: int) -> list[Pret]:
    materiel = session.get(Materiel, materiel_id)
    if materiel is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Materiel inconnu")
    prets = session.exec(
        select(Pret).where(Pret.materiel_id == materiel_id).order_by(Pret.date_debut.desc())
    ).all()
    return list(prets)


def disponibilite(session: Session, materiel_id: int) -> bool:
    return _pret_actif_pour(session, materiel_id) is None
