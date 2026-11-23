"""Téléchargement des données sources."""

import urllib.request

from src.config import RACINE

DOSSIER_BRUT = RACINE / "data" / "raw"


def telecharger(url, nom_fichier):

    
    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_BRUT / nom_fichier
    if chemin.exists():
        print(f"{nom_fichier} : déjà présent, lecture locale")
    else:
        print(f"{nom_fichier} : téléchargement depuis {url} ...")
        urllib.request.urlretrieve(url, chemin)
        print(f"{nom_fichier} : {chemin.stat().st_size / 1e6:.0f} Mo téléchargés")
    return chemin