from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def now_utc():                                
    return datetime.now(timezone.utc)


class Materiel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str = Field(unique=True)
    nom: str
    categorie: str

class Pret(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    materiel_id: int = Field(foreign_key="materiel.id")
    emprunteur: str
    date_debut: datetime = Field(default_factory=now_utc)
    date_retour: Optional[datetime] = None

# Schemas d'entree separes des tables : un client ne doit jamais pouvoir
# fournir lui-meme un id, ni se faire passer pour un autre emprunteur.
class MaterielCreate(SQLModel):
    reference: str
    nom: str
    categorie: str


class PretCreate(SQLModel):
    materiel_id: int
