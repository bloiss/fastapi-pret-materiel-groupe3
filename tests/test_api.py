import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import services
from app.main import app
from app.storage import get_session

# --- Base de test dediee, en memoire, reconstruite a chaque test -----------
engine_test = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


def get_session_test():
    with Session(engine_test) as session:
        yield session


app.dependency_overrides[get_session] = get_session_test


@pytest.fixture(autouse=True)
def base_fraiche():
    SQLModel.metadata.create_all(engine_test)
    yield
    SQLModel.metadata.drop_all(engine_test)


client = TestClient(app)


def token_pour(username, password):
    r = client.post("/token", data={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def creer_materiel_direct(reference="PC-001", nom="Laptop Dell", categorie="ordinateur"):
    with Session(engine_test) as session:
        return services.creer_materiel(session, reference, nom, categorie)


# 1) Reference de materiel en double : refus (409), etat inchange
def test_reference_en_double_refusee():
    tok = token_pour("gestionnaire", "gestionpass")
    r1 = client.post("/equipment", json={"reference": "PC-001", "nom": "Laptop", "categorie": "ordinateur"}, headers=auth(tok))
    assert r1.status_code == 201
    r2 = client.post("/equipment", json={"reference": "PC-001", "nom": "Autre", "categorie": "ordinateur"}, headers=auth(tok))
    assert r2.status_code == 409
    r3 = client.get("/equipment", headers=auth(tok))
    assert len(r3.json()) == 1


# 2) Premier emprunt : succes ; second emprunt du meme materiel : refus (409)
def test_double_emprunt_refuse():
    materiel = creer_materiel_direct()
    tok_alice = token_pour("alice", "alicepass")
    r1 = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_alice))
    assert r1.status_code == 201
    tok_bob = token_pour("bob", "bobpass")
    r2 = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_bob))
    assert r2.status_code == 409


# 3) Retour par un autre etudiant : refus (403), pret inchange
def test_retour_par_autre_etudiant_refuse():
    materiel = creer_materiel_direct()
    tok_alice = token_pour("alice", "alicepass")
    pret = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_alice)).json()
    tok_bob = token_pour("bob", "bobpass")
    r = client.patch(f"/loans/{pret['id']}/return", headers=auth(tok_bob))
    assert r.status_code == 403
    prets = client.get("/loans", headers=auth(tok_alice)).json()
    assert prets[0]["date_retour"] is None


# 4) Retour autorise : succes, materiel a nouveau disponible
def test_retour_autorise_puis_disponible():
    materiel = creer_materiel_direct()
    tok_alice = token_pour("alice", "alicepass")
    pret = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_alice)).json()
    r = client.patch(f"/loans/{pret['id']}/return", headers=auth(tok_alice))
    assert r.status_code == 200
    assert r.json()["date_retour"] is not None
    tok_bob = token_pour("bob", "bobpass")
    r2 = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_bob))
    assert r2.status_code == 201


# 5) Rejeu d'un ancien retour apres un nouveau pret : le nouveau pret reste inchange
def test_rejeu_ancien_retour_ne_touche_pas_le_nouveau_pret():
    materiel = creer_materiel_direct()
    tok_alice = token_pour("alice", "alicepass")
    pret1 = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_alice)).json()
    client.patch(f"/loans/{pret1['id']}/return", headers=auth(tok_alice))

    tok_bob = token_pour("bob", "bobpass")
    pret2 = client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_bob)).json()

    r = client.patch(f"/loans/{pret1['id']}/return", headers=auth(tok_alice))
    assert r.status_code == 409

    prets = client.get("/loans", headers=auth(tok_bob)).json()
    assert prets[0]["id"] == pret2["id"]
    assert prets[0]["date_retour"] is None


# 6) Historique complet reserve au gestionnaire
def test_historique_reserve_gestionnaire():
    materiel = creer_materiel_direct()
    tok_alice = token_pour("alice", "alicepass")
    client.post("/loans", json={"materiel_id": materiel.id}, headers=auth(tok_alice))

    r_refuse = client.get(f"/equipment/{materiel.id}/history", headers=auth(tok_alice))
    assert r_refuse.status_code == 403

    tok_gestion = token_pour("gestionnaire", "gestionpass")
    r_ok = client.get(f"/equipment/{materiel.id}/history", headers=auth(tok_gestion))
    assert r_ok.status_code == 200
    assert len(r_ok.json()) == 1


# 7) Cas choisi par le binome : connexion absente -> 401
def test_sans_jeton_refuse():
    r = client.get("/equipment")
    assert r.status_code == 401


# 8) Cas choisi par le binome : ressource inconnue -> 404
def test_materiel_inconnu_404():
    tok = token_pour("gestionnaire", "gestionpass")
    r = client.get("/equipment/9999/history", headers=auth(tok))
    assert r.status_code == 404


# 9) Bonus : mauvais mot de passe -> 401
def test_mauvais_mot_de_passe_401():
    r = client.post("/token", data={"username": "alice", "password": "mauvais"})
    assert r.status_code == 401


# 10) Bonus : donnee invalide -> 422
def test_donnee_invalide_422():
    tok = token_pour("gestionnaire", "gestionpass")
    r = client.post("/equipment", json={"reference": "PC-002"}, headers=auth(tok))
    assert r.status_code == 422
