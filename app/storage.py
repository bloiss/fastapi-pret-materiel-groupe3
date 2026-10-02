import os

from sqlmodel import Session, SQLModel, create_engine

from .models import (  # noqa: F401 -- necessaire pour que SQLModel connaisse ces tables avant create_all
    Materiel,
    Pret,
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///laboratoire.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
