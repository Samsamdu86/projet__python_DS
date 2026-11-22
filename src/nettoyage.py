"""Chargement et nettoyage de la BPE et du DVF géolocalisé."""

import geopandas as gpd
import pandas as pd

from src.config import (
    ABSENTS_DVF, DROM, FACTEUR_COMMUNE, MIN_VENTES_REFERENCE,
    PRIX_M2_PLANCHER, SURFACE_MIN,
)

COLONNES_BPE = [
    "DOM", "SDOM", "TYPEQU", "SIRET", "NOMRS", "APET",
    "DEPCOM", "DEP", "REG", "LIBCOM",
    "LONGITUDE", "LATITUDE", "QUALITE_XY", "DENS7",
]

COLONNES_DVF = [
    "id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere",
    "code_commune", "nom_commune", "code_departement",
    "type_local", "surface_reelle_bati", "surface_terrain",
    "longitude", "latitude",
]


def _bilan(etape, avant, apres):
    """Affiche le nombre de lignes retirées par une étape de nettoyage."""
    print(f"{etape} : {avant - apres} lignes retirées ({1 - apres / avant:.2%}), {apres} restantes")


def en_geodataframe(df, col_lon, col_lat):
    """Transforme un tableau avec longitude/latitude en GeoDataFrame en Lambert 93."""
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[col_lon], df[col_lat]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2154")


def filtrer_metropole(df, col_lon, col_lat):
    """Retire les points situés hors d'un rectangle englobant la métropole et la Corse."""
    dans_metropole = df[col_lon].between(-5.5, 10) & df[col_lat].between(41, 51.5)
    return df[dans_metropole].copy()


#  BPE

def nettoyer_bpe(bpe_brut):
    """Commerces alimentaires de métropole (hors Alsace-Moselle), géolocalisés."""
    n0 = len(bpe_brut)
    bpe = bpe_brut.loc[bpe_brut["SDOM"].isin(["B1", "B2"]), COLONNES_BPE].copy()
    bpe = bpe[bpe["TYPEQU"] != "B103"]                    # grandes surfaces de bricolage
    _bilan("Sélection des commerces alimentaires", n0, len(bpe))

    for col in ["TYPEQU", "SIRET", "DEPCOM", "DEP", "REG", "DENS7"]:
        bpe[col] = bpe[col].astype("string")
    for col in ["LONGITUDE", "LATITUDE"]:
        bpe[col] = pd.to_numeric(bpe[col], errors="coerce")

    n = len(bpe)
    bpe = bpe.drop_duplicates()
    _bilan("Doublons exacts", n, len(bpe))

    n = len(bpe)
    bpe = bpe[~bpe["DEP"].isin(DROM + ABSENTS_DVF)]
    _bilan("Périmètre (DROM, Alsace-Moselle)", n, len(bpe))

    n = len(bpe)
    bpe = bpe.dropna(subset=["LONGITUDE", "LATITUDE"])
    bpe = filtrer_metropole(bpe, "LONGITUDE", "LATITUDE")
    _bilan("Coordonnées manquantes ou aberrantes", n, len(bpe))

    return en_geodataframe(bpe, "LONGITUDE", "LATITUDE")


#  DVF

def charger_dvf(url):
    """Charge le DVF géolocalisé en ne gardant que les colonnes utiles (tout en texte)."""
    return pd.read_csv(url, dtype=str, usecols=COLONNES_DVF)


def selectionner_ventes_logement(dvf_brut):
    """Ventes d'un seul logement (maison ou appartement), sans local professionnel."""
    dvf = dvf_brut.copy()
    for col in ["valeur_fonciere", "surface_reelle_bati", "surface_terrain", "longitude", "latitude"]:
        dvf[col] = pd.to_numeric(dvf[col], errors="coerce")

    n = len(dvf)
    dvf = dvf[(dvf["nature_mutation"] == "Vente") & ~dvf["code_departement"].isin(DROM)]
    _bilan("Ventes de métropole", n, len(dvf))

    # Ventes contenant un local commercial ou industriel : à exclure
    ids_pro = dvf.loc[dvf["type_local"].str.startswith("Local", na=False), "id_mutation"].unique()

    # Un logement répété sur plusieurs parcelles ne compte qu'une fois
    logements = dvf[dvf["type_local"].isin(["Maison", "Appartement"])].drop_duplicates(
        subset=["id_mutation", "type_local", "surface_reelle_bati"]
    )
    nb_logements = logements.groupby("id_mutation")["type_local"].transform("size")

    n = logements["id_mutation"].nunique()
    ventes = logements[(nb_logements == 1) & ~logements["id_mutation"].isin(ids_pro)]
    _bilan("Ventes d'un seul logement, sans local professionnel", n, len(ventes))

    n = len(ventes)
    ventes = ventes.dropna(subset=["valeur_fonciere", "surface_reelle_bati",
                                   "code_commune", "longitude", "latitude"])
    ventes = filtrer_metropole(ventes, "longitude", "latitude")
    _bilan("Informations manquantes ou coordonnées aberrantes", n, len(ventes))

    return ventes.copy()


def filtrer_prix(ventes):
    """Calcule le prix au m² et retire les ventes hors marché ou aberrantes."""
    n = len(ventes)
    dvf = ventes[(ventes["valeur_fonciere"] > 0) & (ventes["surface_reelle_bati"] >= SURFACE_MIN)].copy()
    dvf["prix_m2"] = dvf["valeur_fonciere"] / dvf["surface_reelle_bati"]
    _bilan(f"Prix nul ou surface < {SURFACE_MIN} m²", n, len(dvf))

    # 1. Plancher : prix symboliques (à retirer AVANT de calculer les médianes)
    n = len(dvf)
    dvf = dvf[dvf["prix_m2"] >= PRIX_M2_PLANCHER]
    _bilan(f"Prix < {PRIX_M2_PLANCHER} €/m²", n, len(dvf))

    # 2. Plafond : FACTEUR fois la médiane du marché le plus cher (communes fiables)
    stats = dvf.groupby("code_commune")["prix_m2"].agg(["median", "size"])
    plafond = FACTEUR_COMMUNE * stats.loc[stats["size"] >= MIN_VENTES_REFERENCE, "median"].max()
    n = len(dvf)
    dvf = dvf[dvf["prix_m2"] <= plafond]
    _bilan(f"Prix > {plafond:.0f} €/m²", n, len(dvf))

    # 3. Écart à la médiane de la commune
    mediane = dvf.groupby("code_commune")["prix_m2"].transform("median")
    ratio = dvf["prix_m2"] / mediane
    n = len(dvf)
    dvf = dvf[ratio.between(1 / FACTEUR_COMMUNE, FACTEUR_COMMUNE)]
    _bilan(f"Écart à la commune > facteur {FACTEUR_COMMUNE}", n, len(dvf))

    return dvf.copy()


def nettoyer_dvf(dvf_brut):
    """Chaîne complète de nettoyage du DVF, renvoyée en GeoDataFrame (Lambert 93)."""
    ventes = selectionner_ventes_logement(dvf_brut)
    ventes = filtrer_prix(ventes)
    return en_geodataframe(ventes, "longitude", "latitude")