from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import authentifier, creer_token

router = APIRouter()


@router.post(
    "/token",
    tags=["Authentification"],
    summary="Se connecter",
    description="Verifie l'identifiant et le mot de passe, puis renvoie un jeton JWT valable 30 minutes.",
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    utilisateur = authentifier(form_data.username, form_data.password)
    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = creer_token(utilisateur["username"], utilisateur["role"])
    return {"access_token": token, "token_type": "bearer"}
