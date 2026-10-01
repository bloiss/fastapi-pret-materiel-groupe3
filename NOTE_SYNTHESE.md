# Note de synthese - Prets de materiel du laboratoire

Projet realise en binome par Lois Bureau et Kais, dans le cadre du module
B2 Cybersecurite (Python/FastAPI), groupe 3.

## 1. Repartition du travail

**Lois** : modelisation des donnees (`app/models.py`), authentification JWT
et gestion des roles (`app/auth.py`), couche services / regles metier
(`app/services.py`), routes HTTP (`app/routes/`), CLI (`cli.py`), suite de
tests automatises (`tests/test_api.py`), configuration (`pyproject.toml`,
`.gitignore`, `.env.example`, `requirements.txt`) et documentation
(`README.md`, `USAGE_IA.md`).

**Kais** : [Kais, remplace ce paragraphe par ce que tu as reellement fait sur
le projet : revue de code, tests manuels via `/docs`, partie de la
documentation, preparation de l'oral, autre contribution. L'objectif de
cette note est de refleter le travail reel de chacun, pas une repartition
inventee.]

## 2. Schema des principaux elements du programme

```
Client (navigateur / curl / CLI)
        |
        v
+-------------------+        +----------------------+
|  routes/           |  -->   |  auth.py             |
|  token.py          |        |  (JWT, roles,        |
|  equipment.py      |        |   verification token)|
|  loans.py          |        +----------------------+
+-------------------+
        |
        v
+-------------------+
|  services.py       |   <-- regles metier : pas de double emprunt,
|  (logique metier)  |       controle de propriete sur le retour,
+-------------------+       historique reserve au gestionnaire
        |
        v
+-------------------+
|  storage.py         |  -->  base SQLite (laboratoire.db)
|  models.py           |      (via SQLModel / SQLAlchemy)
+-------------------+
```

La CLI (`cli.py`) n'appelle jamais les routes HTTP : elle importe directement
`services.py`, pour ne jamais dupliquer les regles metier a deux endroits
differents.

## 3. Deux decisions techniques expliquees

### a) Comptes utilisateurs fixes, sans table ni inscription publique

Le socle commun impose des comptes deja definis (au moins un gestionnaire et
deux etudiants) et interdit l'inscription libre. Plutot que de creer une
table `Utilisateur` en base - ce qui aurait ajoute de la complexite
(hachage a gerer en base, migration, etc.) sans repondre a un besoin reel du
sujet - les comptes sont stockes dans un dictionnaire Python en memoire
(`UTILISATEURS` dans `app/auth.py`), avec mot de passe hache via `bcrypt`.
C'est suffisant pour la demonstration demandee et plus simple a expliquer et
a defendre a l'oral.

### b) L'emprunteur est toujours pris dans le jeton JWT, jamais dans le corps de la requete

Lors d'un emprunt (`POST /loans`), le champ `emprunteur` n'est jamais lu dans
le JSON envoye par le client : il vient uniquement de l'utilisateur identifie
par son jeton (`utilisateur["username"]`, recupere via `get_current_user`).
Si on l'acceptait depuis la requete, n'importe quel etudiant connecte
pourrait creer un pret au nom de quelqu'un d'autre simplement en changeant
une valeur dans le JSON. C'est le meme principe qui protege le retour d'un
pret : on compare toujours l'identite du jeton au proprietaire reel du pret
(sauf pour le role gestionnaire, qui peut agir sur tous les prets).

## 4. Limites connues

- Les comptes utilisateurs sont fixes en memoire et redemarrent "a zero" avec
  l'application ; ce n'est pas adapte a une vraie mise en production, mais
  conforme a ce que demande le sujet pour ce projet d'apprentissage.
- La base SQLite est un fichier local unique : elle ne gere pas des ecritures
  concurrentes a grande echelle, ce qui est acceptable pour une demonstration
  mais pas pour un usage en production avec beaucoup d'utilisateurs
  simultanes.
- Le projet est stocke dans un dossier synchronise par OneDrive. Dans ce
  contexte, un fichier SQLite peut occasionnellement rencontrer des erreurs
  de verrouillage ("disk I/O error") si une synchronisation a lieu pendant
  une ecriture. Voir la section "Limite connue" du `README.md` pour le
  contournement (fermer l'app, ou deplacer le projet hors d'un dossier
  synchronise pour un usage intensif).
- Le jeton JWT expire au bout de 30 minutes sans mecanisme de rafraichissement
  automatique : apres expiration, l'utilisateur doit simplement se
  reconnecter via `/token`.
