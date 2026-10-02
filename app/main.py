from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import equipment, loans, token
from .storage import init_db

tags_metadata = [
    {
        "name": "Authentification",
        "description": "Connexion et obtention du jeton JWT. A utiliser en premier avec le bouton **Authorize**.",
    },
    {
        "name": "Materiel",
        "description": "Consultation et gestion du catalogue de materiel du laboratoire.",
    },
    {
        "name": "Prets",
        "description": "Emprunt, consultation et retour de materiel.",
    },
]

DESCRIPTION = """
API de gestion des prets de materiel du laboratoire.

Permet a un **etudiant** d'emprunter et de rendre du materiel, et a un **gestionnaire** d'ajouter du
materiel au catalogue et de consulter l'historique des prets.

Comptes de demonstration : `alice` / `alicepass`, `bob` / `bobpass` (etudiants),
`gestionnaire` / `gestionpass` (gestionnaire).
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Prets de materiel du laboratoire",
    description=DESCRIPTION,
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    swagger_ui_parameters={
        "docExpansion": "list",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "filter": True,
    },
)

app.include_router(token.router)
app.include_router(equipment.router)
app.include_router(loans.router)
