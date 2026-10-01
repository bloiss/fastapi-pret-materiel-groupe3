from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import equipment, loans, token
from .storage import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Prets de materiel du laboratoire", lifespan=lifespan)

app.include_router(token.router)
app.include_router(equipment.router)
app.include_router(loans.router)
