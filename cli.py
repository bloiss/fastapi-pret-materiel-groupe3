import argparse
import json

from sqlmodel import Session

from app import services
from app.storage import engine, init_db


def commande_inventaire(format_sortie: str):
    init_db()
    with Session(engine) as session:
        materiels = services.lister_materiels(session)
        resultat = [
            {
                "reference": m.reference,
                "nom": m.nom,
                "disponible": services.disponibilite(session, m.id),
            }
            for m in materiels
        ]
    if format_sortie == "json":
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
    else:
        for item in resultat:
            etat = "disponible" if item["disponible"] else "emprunte"
            print(f"{item['reference']:10s} {item['nom']:20s} {etat}")


def main():
    parser = argparse.ArgumentParser(description="CLI d'administration du laboratoire")
    sous_commandes = parser.add_subparsers(dest="commande", required=True)

    inventaire_parser = sous_commandes.add_parser("inventaire", help="Liste le materiel et sa disponibilite")
    inventaire_parser.add_argument("--format", choices=["json", "texte"], default="texte")

    args = parser.parse_args()

    if args.commande == "inventaire":
        commande_inventaire(args.format)


if __name__ == "__main__":
    main()
