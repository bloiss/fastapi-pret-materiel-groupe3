# Prets de materiel du laboratoire

API FastAPI permettant de gerer le pret de materiel (ordinateurs, cles de securite)
dans un laboratoire : qui possede quoi, et interdiction des doubles prets.

Projet realise en binome par Lois et Kais (YNOV B2 Cybersecurite).

## 1. Installation

```
git clone <url-du-depot>
cd fastapi-pret-materiel-groupe3
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

## 2. Configuration

```
copy .env.example .env         # Windows
# cp .env.example .env         # Mac/Linux
```

Ouvrir `.env` et remplacer `JWT_SECRET_KEY` par une valeur quelconque pour le
developpement local (ce fichier n'est jamais commite, voir `.gitignore`).

## 3. Comptes de demonstration (fictifs, crees automatiquement au demarrage)

| Utilisateur     | Mot de passe   | Role         |
|-----------------|----------------|--------------|
| alice           | alicepass      | etudiant     |
| bob             | bobpass        | etudiant     |
| gestionnaire    | gestionpass    | gestionnaire |

## 4. Lancer l'API

```
uvicorn app.main:app --reload
```

La base `laboratoire.db` (SQLite) est creee automatiquement au premier
demarrage. Documentation interactive : http://127.0.0.1:8000/docs

## 5. Remettre la base a zero (donnees fictives uniquement)

```
del laboratoire.db             # Windows
# rm laboratoire.db            # Mac/Linux
```

Le fichier est recree automatiquement au prochain demarrage de l'API ou de la CLI.

## 6. Lancer la CLI

```
python cli.py inventaire --format json
```

Affiche, pour chaque materiel, sa reference, son nom, et sa disponibilite
(calculee a partir des prets actifs en base).

## 7. Lancer les tests

```
python -m pytest tests/test_api.py -v
```

Les tests utilisent une base SQLite en memoire dediee (jamais `laboratoire.db`),
recreee avant chaque test.

## 8. Scenario de demonstration (rejouable)

1. `del laboratoire.db` pour repartir d'une base vide.
2. Se connecter en tant que `gestionnaire`, ajouter un materiel (`POST /equipment`).
3. Se connecter en tant que `alice`, emprunter ce materiel (`POST /loans`) -> succes.
4. Se connecter en tant que `bob`, tenter d'emprunter le meme materiel -> refus (409).
5. `bob` tente de rendre le pret d'`alice` -> refus (403).
6. `alice` rend son pret (`PATCH /loans/{id}/return`) -> succes, materiel redisponible.
7. `bob` emprunte a son tour -> succes.
8. `alice` rejoue son ancien retour -> refus (409), le pret de `bob` reste inchange.
9. `gestionnaire` consulte l'historique (`GET /equipment/{id}/history`).
10. `python cli.py inventaire --format json` et `python -m pytest tests/test_api.py -v`.

## 9. Architecture

```
app/
  main.py      -> assemble l'application FastAPI
  models.py    -> tables SQLModel (Materiel, Pret) + schemas d'entree
  storage.py   -> connexion a la base SQLite
  auth.py      -> authentification JWT, comptes fixes, controle de role
  services.py  -> toute la logique metier (regles, codes d'erreur)
  routes/      -> endpoints HTTP, qui appellent uniquement services.py
cli.py         -> reutilise services.py, ne recopie aucune regle
tests/         -> tests automatises (base dediee en memoire)
```

## 10. Limite connue

Le projet utilise SQLite via un fichier local (`laboratoire.db`). Si ce
dossier est synchronise par un service cloud (OneDrive, Google Drive...), des
verrous de fichier concurrents peuvent occasionnellement provoquer une erreur
d'ecriture. En cas de souci, interrompre la synchronisation du dossier pendant
le developpement/la demonstration, ou travailler dans un dossier non synchronise.

## 11. Verification

Etapes ci-dessus executees avec succes le 2026-10-01 depuis une copie neuve
du depot : installation, 10/10 tests passes, CLI fonctionnelle, API
accessible sur /docs.
