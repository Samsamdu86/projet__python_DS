"""Paramètres du projet : sources de données, codes et seuils de nettoyage."""

from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_TABLES = RACINE / "outputs" / "tables"
DOSSIER_FIGURES = RACINE / "outputs" / "figures"
DOSSIER_DONNEES = RACINE / "data" / "processed"
DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)

# Grille communale de densité 2025 (INSEE) — lien vérifié
URL_GRILLE = "https://www.insee.fr/fr/statistiques/fichier/8571524/fichier_diffusion_2025.xlsx"

# DVF géolocalisées 2025 (data.gouv.fr) — à confirmer, voir ci-dessous
URL_DVF = "https://www.data.gouv.fr/api/1/datasets/r/b3a0c6d2-2a5a-45a3-81a8-9e860caf5e14"

# BPE 2025, équipements géolocalisés (INSEE) — à confirmer, voir ci-dessous
URL_BPE = "https://www.insee.fr/fr/statistiques/fichier/8217525/BPE25.parquet"

# Périmètre 
DROM = ["971", "972", "973", "974", "976"]
ABSENTS_DVF = ["57", "67", "68"]          # Alsace-Moselle, absentes du DVF

# Commerces alimentaires 
TYPES_COMMERCES = {
    "hyper": ["B104"],
    "super": ["B105"],
    "proximite": ["B201", "B202"],
    "specialise": ["B204", "B205", "B206", "B207", "B208", "B209", "B210"],
}

#  Nettoyage du DVF 
SURFACE_MIN = 9                # m², surface minimale d'un logement décent
PRIX_M2_PLANCHER = 100         # €/m², en dessous : vente symbolique
FACTEUR_COMMUNE = 10           # écart maximal à la médiane de la commune (et base du plafond)
MIN_VENTES_REFERENCE = 100     # nombre de ventes pour qu'une médiane communale soit fiable

#  Indice d'accessibilité 
QUANTILE_RAYON = 0.99


# Contours des départements (pour la carte du rapport)
URL_DEPARTEMENTS = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/"
    "departements-version-simplifiee.geojson"
)

LIBELLES_DENS7 = {
    "1": "Grands centres urbains",
    "2": "Centres urbains intermédiaires",
    "3": "Ceintures urbaines",
    "4": "Petites villes",
    "5": "Bourgs ruraux",
    "6": "Rural à habitat dispersé",
    "7": "Rural à habitat très dispersé",
}