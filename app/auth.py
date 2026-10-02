import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-ne-jamais-utiliser-en-prod")
ALGORITHM = "HS256"
EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _hash(mot_de_passe: str) -> bytes:
    return bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt())


# Comptes fixes imposes par le socle commun : pas d'inscription publique,
# au moins un compte par role, et au moins DEUX comptes etudiant (pour
# pouvoir tester le controle de propriete entre deux etudiants differents).
UTILISATEURS = {
    "alice": {"password_hash": _hash("alicepass"), "role": "etudiant"},
    "bob": {"password_hash": _hash("bobpass"), "role": "etudiant"},
    "gestionnaire": {"password_hash": _hash("gestionpass"), "role": "gestionnaire"},
}


def authentifier(username: str, password: str):
    utilisateur = UTILISATEURS.get(username)
    if utilisateur is None:
        return None
    if not bcrypt.checkpw(password.encode(), utilisateur["password_hash"]):
        return None
    return {"username": username, "role": utilisateur["role"]}


def creer_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    erreur_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expire",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise erreur_401
    username = payload.get("sub")
    role = payload.get("role")
    if username is None or role is None or username not in UTILISATEURS:
        raise erreur_401
    return {"username": username, "role": role}


def exiger_role(role_attendu: str):
    def dependance(utilisateur: dict = Depends(get_current_user)) -> dict:
        if utilisateur["role"] != role_attendu:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action reservee au role '{role_attendu}'",
            )
        return utilisateur
    return dependance
