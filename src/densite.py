"""Ajout de la grille communale de densité de l'INSEE."""

import pandas as pd

# Les arrondissements de Paris, Lyon et Marseille sont regroupés dans la grille
ARRONDISSEMENTS = [("75101", "75120", "75056"),
                   ("69381", "69389", "69123"),
                   ("13201", "13216", "13055")]


def charger_grille(url):
    """Charge la grille de densité (niveau en 7 postes) à l'échelle communale."""
    grille = pd.read_excel(url, sheet_name="Maille communale", header=4, dtype={"CODGEO": str})
    grille = grille[["CODGEO", "DENS7", "LIBDENS7"]].copy()
    grille["DENS7"] = grille["DENS7"].astype(int).astype(str)
    return grille


def ajouter_densite(ventes, grille):
    """Ajoute à chaque vente le niveau de densité (DENS7) de sa commune."""
    ventes = ventes.copy()
    code = ventes["code_commune"].copy()
    for debut, fin, commune in ARRONDISSEMENTS:
        code[code.between(debut, fin)] = commune

    densite = grille.set_index("CODGEO")
    ventes["DENS7"] = code.map(densite["DENS7"])
    ventes["LIBDENS7"] = code.map(densite["LIBDENS7"])

    print("Ventes sans densité :", ventes["DENS7"].isna().sum())
    ventes["DENS"] = ventes["DENS7"].map({"1": "1", "2": "2", "3": "2", "4": "2",
                                         "5": "3", "6": "3", "7": "3"})
    return ventes