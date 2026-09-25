from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


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