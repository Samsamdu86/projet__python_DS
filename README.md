# projet__python_DS
# Le prix de l'immobilier dépend-il de l'accès aux commerces alimentaires ?

*Projet de Python pour la data science (ENSAE, 2026) — [Antoine CHARKI], [Samuel BARRE]*

**Pour découvrir le projet, commencer par la synthèse : [`synthese.ipynb`](synthese.ipynb).**
Elle présente la démarche, les difficultés rencontrées, les résultats et leur interprétation.
Le détail du traitement et de l'analyse se trouve dans les notebooks du dossier `notebooks/`.

## Le projet en bref

Tous les commerces alimentaires ne rendent pas le même service : on ne fait pas ses courses de la
semaine chez le boulanger, et on ne va pas à l'hypermarché à pied. Nous étudions si, **à type de
territoire égal**, l'accès aux différents types de commerces alimentaires (hypermarchés, supermarchés,
commerces de proximité, commerces spécialisés) est associé au prix au m² des logements vendus en
France métropolitaine en 2025.

## Données

Toutes les données sont publiques (Licence Ouverte) et téléchargées automatiquement depuis leur source.

| Source | Contenu | Producteur |
|---|---|---|
| [Base permanente des équipements 2025](https://www.insee.fr/fr/statistiques/8217525) | Commerces alimentaires géolocalisés | INSEE |
| [Demandes de valeurs foncières géolocalisées 2025](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees) | Ventes immobilières géolocalisées | DGFiP, mis en forme par Etalab |
| [Grille communale de densité 2025](https://www.insee.fr/fr/information/8571524) | Niveau de densité de chaque commune (7 niveaux) | INSEE |

Périmètre : France métropolitaine, hors Alsace-Moselle (non couverte par les DVF).

## Organisation du dépôt

```
├── synthese.ipynb       ← la synthèse : à lire en premier
├── notebooks/           ← traitement et analyse, à exécuter dans l'ordre
├── src/                 ← fonctions utilisées par les notebooks
├── outputs/tables/      ← tableaux de résultats (lus par la synthèse)
├── outputs/figures/     ← figures
├── data/                ← données téléchargées et intermédiaires (créé à l'exécution, hors Git)
└── requirements.txt     ← dépendances
```

### Notebooks

| Notebook | Rôle | Produit |
|---|---|---|
| [`01_nettoyage_bpe`](notebooks/01_nettoyage_bpe.ipynb) | Sélection des commerces alimentaires (hypermarchés, supermarchés, proximité, spécialisés), retrait des commerces sans coordonnées, restriction à la métropole hors Alsace-Moselle | `data/processed/bpe_alim_2025.parquet` (135 587 commerces) |
| [`02_nettoyage_dvf`](notebooks/02_nettoyage_dvf.ipynb) | Ventes d'un seul logement, retrait des coordonnées aberrantes et des mutations hors vente, filtres de prix (plancher, plafond, écart à la médiane communale), ajout de la densité | `data/processed/dvf_ventes_2025.parquet` (810 517 ventes) |
| [`03_croisement`](notebooks/03_croisement.ipynb) | Distance au commerce le plus proche, nombre de commerces accessibles et indice d'accessibilité par catégorie, avec un rayon adapté au type de territoire | `data/processed/dvf_enrichi_2025.parquet`, tableaux dans `outputs/tables/` |
| [`04_regressions`](notebooks/04_regressions.ipynb) | Régressions du log du prix au m² sur l'accès aux commerces, avec contrôles (surface, type de logement, département, densité) | [`outputs/tables/comparaison_modeles.csv` et `coefficients_M1.csv` à `coefficients_M6.csv`] |

### Fonctions (`src/`)

| Fichier | Contenu |
|---|---|
| `config.py` | Adresses des sources, chemins des dossiers |
| `telechargement.py` | Téléchargement des sources, avec vérification que les fichiers sont complets |
| `densite.py` | Chargement de la grille de densité et ajout du niveau de densité aux ventes |
| `resultats.py` | Construction et écriture des tableaux de résultats |

## Reproduire les résultats

Projet développé sur le [SSP Cloud](https://datalab.sspcloud.fr/) (service Jupyter-python, Python 3.13).

```bash
git clone https://github.com/Samsamdu86/projet__python_DS.git
cd projet__python_DS
pip install -r requirements.txt
```

Exécuter ensuite les notebooks **dans l'ordre**, depuis le dossier `notebooks/` :

| Notebook 
|---|---|
| `01_nettoyage_bpe` | 
| `02_nettoyage_dvf` |
| `03_croisement` |
| `04_regressions` |

Chaque notebook lit les fichiers produits par le précédent dans `data/processed/`. Les sources ne
sont téléchargées qu'une fois, dans `data/raw/`.

La synthèse ne lit que les tableaux de `outputs/tables/`, présents dans le dépôt : elle s'exécute en
quelques secondes, sans relancer le traitement.

## Principaux choix méthodologiques

- seules les **ventes d'un seul logement** sont conservées : le prix d'une vente groupée ne peut pas
  être réparti entre les logements ;
- les prix aberrants sont écartés par un plancher (100 €/m²), un plafond (10 fois la médiane du marché
  le plus cher) et un **écart d'un facteur 10 à la médiane de la commune** ;
- l'accès aux commerces est mesuré par catégorie, dans un rayon adapté au niveau de densité du territoire (99e percentile de la distance au commerce le plus proche). Deux méthodes sont comparées : la frontière nette, qui compte les commerces situés dans ce rayon, et la frontière dégressive, qui pondère ces commerces en fonction de leur distance au logement ;
- les comparaisons se font **à densité égale** (grille communale de densité de l'INSEE) ;
- les résultats décrivent des **associations**, et non des effets causaux.
- les régressions contrôlent les caractéristiques des logements, le département et, à partir du deuxième modèle, la densité urbaine.

## Usage de l'IA

Un assistant d'IA générative (Claude, Anthropic et ChatGPT) a été utilisé pour une partie de l'écriture du code, pour le débogage et pour améliorer la mise en page de nos parties textes. La problématique, les choix méthodologiques et l'interprétation des résultats
sont entièrement les nôtres.
