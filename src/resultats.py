"""Tableaux de résultats (petits, destinés à être enregistrés en CSV dans le dépôt)."""

import pandas as pd

BORNES_TRANCHES = [0, 0.2, 0.4, 0.6, 0.8, 1]


def prix_par_densite(dvf):
    """Prix médian au m² par niveau de densité et type de logement."""
    return (dvf.groupby(["DENS7", "type_local"])["prix_m2"]
            .agg(prix_m2_median="median", nb_ventes="size")
            .round(0).reset_index())


def distances_par_densite(dvf, categories):
    """Distance médiane au commerce le plus proche de chaque catégorie, par niveau de densité."""
    colonnes = [f"dist_{cat}" for cat in categories]
    return dvf.groupby("DENS7")[colonnes].median().round(0).reset_index()


def resume_departements(dvf):
    """Prix médian et distance médiane au supermarché par département (pour la carte)."""
    return (dvf.groupby("code_departement")
            .agg(prix_m2_median=("prix_m2", "median"),
                 dist_super_median=("dist_super", "median"),
                 nb_ventes=("prix_m2", "size"))
            .round(0).reset_index())


def prix_par_tranche(dvf, categories, exclure_paris=False):
    """Prix médian au m² par catégorie, niveau de densité et quintile d'accès (1 = moins bien desservi)."""
    donnees = dvf[dvf["code_departement"] != "75"] if exclure_paris else dvf
    tableaux = []
    for cat in categories:
        tranche = pd.cut(donnees[f"rang_{cat}"], bins=BORNES_TRANCHES,
                         labels=[1, 2, 3, 4, 5], include_lowest=True).rename("tranche_acces")
        tableau = (donnees.groupby(["DENS7", tranche], observed=True)["prix_m2"]
                   .agg(prix_m2_median="median", nb_ventes="size")
                   .reset_index())
        tableau.insert(0, "categorie", cat)
        tableaux.append(tableau)
    return pd.concat(tableaux, ignore_index=True).round(0)


def ecrire(tableaux, dossier):
    """Écrit chaque tableau du dictionnaire {nom: DataFrame} en CSV dans le dossier."""
    dossier.mkdir(parents=True, exist_ok=True)
    for nom, tableau in tableaux.items():
        tableau.to_csv(dossier / f"{nom}.csv", index=False)
        print(f"{nom}.csv : {len(tableau)} lignes")