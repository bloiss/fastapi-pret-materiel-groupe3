# Utilisation de l'IA sur ce projet

## Outils utilises

Claude (Anthropic), utilise par Lois en binome avec Kais, pour : comprendre les
concepts (SQL, SQLModel, JWT, architecture FastAPI), proposer du code,
ecrire les tests automatises, et aider au debogage.

## Taches confiees a l'IA

- Explication pedagogique des concepts (SQLModel, JWT, controle de droits,
  codes d'erreur HTTP) avant ecriture du code.
- Proposition de code pour l'authentification, les routes, la couche
  services, la CLI et les tests.
- Verification systematique par execution reelle (pas seulement relecture) :
  chaque suggestion a ete testee avant d'etre conservee.

## Deux exemples precis de suggestions verifiees et corrigees

### Exemple 1 : hachage des mots de passe (passlib vs bcrypt)

L'IA a d'abord propose `passlib.context.CryptContext(schemes=["bcrypt"])` pour
hacher les mots de passe. A l'execution reelle, ce code a leve une erreur :

```
AttributeError: module 'bcrypt' has no attribute '__about__'
```

Cause identifiee : `passlib` (non maintenu depuis 2020) est incompatible avec
les versions recentes du paquet `bcrypt` (>= 4.1). Verification faite en
executant le code tel quel dans l'environnement reel du projet, avec les
versions de paquets effectivement installees.

Correction : remplacement par l'utilisation directe de la librairie `bcrypt`
(`bcrypt.hashpw` / `bcrypt.checkpw`), testee avec succes (hash puis
verification d'un mot de passe correct ET d'un mot de passe incorrect).

### Exemple 2 : date par defaut d'un pret (`datetime.utcnow`)

L'IA a d'abord propose `Field(default_factory=datetime.utcnow)` pour la date
de debut d'un pret. A l'execution reelle contre la base SQLite du projet,
cela a leve :

```
ValueError: Datetime values must have timezone information.
```

Cause identifiee : les versions recentes de SQLAlchemy (utilisee par
SQLModel) exigent une date avec fuseau horaire explicite ; `datetime.utcnow()`
renvoie une date "naive" (sans fuseau).

Correction : remplacement par une fonction `now_utc()` utilisant
`datetime.now(timezone.utc)`, verifiee en executant une insertion reelle en
base et en confirmant que deux prets consecutifs obtiennent bien des horaires
differents (et non une heure figee au demarrage).

## Comment chaque suggestion a ete verifiee

Pour chaque morceau de code propose par l'IA, un test reel a ete execute
(et non une simple relecture) : appels HTTP reels via `TestClient`, insertions
reelles en base SQLite, execution de `pytest` et de `ruff`. Les deux exemples
ci-dessus sont des cas ou cette verification a reellement revele un bug avant
qu'il n'arrive dans le code final.

## Limites de cette documentation

Cette section couvre l'usage de l'IA par Lois. [Kais : ajoute ici tes propres
exemples si tu as egalement utilise une IA sur ta partie, ou indique que tu
n'en as pas utilise.]
