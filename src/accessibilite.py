"""Mesures d'accès aux commerces alimentaires : distances, rayons et indices."""

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def distances_plus_proche(ventes, commerces, types_commerces):
    """Distance de chaque vente au commerce le plus proche de chaque catégorie."""
    resultats = pd.DataFrame(index=ventes.index)
    for cat, codes in types_commerces.items():
        selection = commerces.loc[commerces["TYPEQU"].isin(codes), ["geometry"]]
        plus_proche = gpd.sjoin_nearest(
            ventes[["geometry"]], selection, how="left", distance_col=f"dist_{cat}"
        )
        plus_proche = plus_proche[~plus_proche.index.duplicated()]   # égalités de distance
        resultats[f"dist_{cat}"] = plus_proche[f"dist_{cat}"]

    colonnes = [f"dist_{cat}" for cat in types_commerces]
    resultats["dist_plus_proche"] = resultats[colonnes].min(axis=1)
    resultats["type_plus_proche"] = resultats[colonnes].idxmin(axis=1).str.replace("dist_", "")
    return resultats


def calculer_rayons(ventes, categories, q):
    """Rayon par niveau de densité et par catégorie : quantile q de la distance au plus proche."""
    return pd.DataFrame({
        cat: ventes.groupby("DENS7")[f"dist_{cat}"].quantile(q) for cat in categories
    })


def indice_lineaire(xy_ventes, rayon_vente, arbre, rayons_commerces, taille_bloc=5_000):
    """Somme sur les commerces de max(0, 1 - d/R), avec R = min(rayon du logement, rayon du commerce)."""
    resultat = np.zeros(len(xy_ventes))
    for debut in range(0, len(xy_ventes), taille_bloc):
        bloc = xy_ventes[debut:debut + taille_bloc]
        paires = cKDTree(bloc).sparse_distance_matrix(
            arbre, max_distance=rayon_vente, output_type="ndarray"
        )
        rayon_paire = np.minimum(rayon_vente, rayons_commerces[paires["j"]])
        contributions = np.clip(1 - paires["v"] / rayon_paire, 0, None)
        resultat[debut:debut + len(bloc)] = np.bincount(
            paires["i"], weights=contributions, minlength=len(bloc)
        )
    return resultat


def calculer_indices(ventes, commerces, types_commerces, rayons, suffixe=""):
    """Indice d'accessibilité de chaque catégorie de commerce, pour chaque vente."""
    resultats = pd.DataFrame(index=ventes.index)
    for cat, codes in types_commerces.items():
        selection = commerces[commerces["TYPEQU"].isin(codes)]
        arbre = cKDTree(np.column_stack([selection.geometry.x, selection.geometry.y]))
        rayons_commerces = selection["DENS7"].map(rayons[cat]).to_numpy(dtype=float)

        colonne = f"acces_{cat}{suffixe}"
        resultats[colonne] = np.nan
        for niveau, rayon in rayons[cat].items():
            masque = (ventes["DENS7"] == niveau).to_numpy()
            if masque.sum() == 0:
                continue
            xy = np.column_stack([ventes.geometry.x[masque], ventes.geometry.y[masque]])
            resultats.loc[masque, colonne] = indice_lineaire(xy, rayon, arbre, rayons_commerces)
    return resultats


def ajouter_rangs(ventes, categories):
    """Rang (entre 0 et 1) de chaque indice à l'intérieur de son niveau de densité."""
    ventes = ventes.copy()
    for cat in categories:
        ventes[f"rang_{cat}"] = ventes.groupby("DENS7")[f"acces_{cat}"].rank(pct=True)
    return ventes