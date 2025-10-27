# Scripts de Recherche et Normalisation d'Entreprises

Ce projet contient un ensemble de scripts Python conçus pour être utilisés de manière séquentielle et indépendante dans le processus de collecte, normalisation et filtrage d'informations d'entreprises.

## Workflow des scripts

Les scripts sont pensés pour être appelés à la suite les uns des autres, de manière indépendante :

1. **recherche_entreprises.py** - Collecte initiale (occasionnelle)
2. **NormaliseMetiers.py** - Standardisation des métiers
3. **supprime_doublons.py** - Suppression des doublons
4. **maj_historique.py** - Gestion de l'historique
5. **Filters.py** - Filtrage selon critères évolutifs

## 1. recherche_entreprises.py - Recherche d'entreprises via Google Places

**Premier script à exécuter**, une fois de temps en temps pour récupérer les informations de Google Places.

### Prérequis

1. **Clé API Google Places** :
   - Aller sur <https://console.cloud.google.com/>
   - Activer l'API "Places API"
   - Créer une clé API

2. **Dépendances Python** :

```bash
pip install requests
```

### Usage de base

```bash
python recherche_entreprises.py metiers.csv villes.csv output.csv --api-key YOUR_API_KEY
```

### Options avancées

```bash
python recherche_entreprises.py metiers.csv villes.csv output.csv \
  --api-key YOUR_API_KEY \
  --max-per-search 10 \
  --delay 0.2
```

### Format des fichiers d'entrée

**metiers.csv** :

```csv
metier
boulanger
plombier
restaurant
```

**villes.csv** :

```csv
ville
Paris
Lyon
Marseille
```

### Fichier de sortie

Le script génère un CSV avec les colonnes : `Nom,adresse,ville,metier`

### Exemples d'utilisation

1. **Recherche simple** :

```bash
python recherche_entreprises.py exemples_metiers.csv exemples_villes.csv resultats.csv --api-key YOUR_API_KEY
```

1. **Recherche avec paramètres personnalisés** :

```bash
python recherche_entreprises.py exemples_metiers.csv exemples_villes.csv resultats.csv \
  --api-key YOUR_API_KEY \
  --max-per-search 15 \
  --delay 0.5
```

### Limites et coûts

- L'API Google Places est payante après un certain quota gratuit
- Respectez les limites de taux de l'API (delay recommandé : 0.1-0.5 secondes)
- Vérifiez votre usage sur Google Cloud Console

## 2. NormaliseMetiers.py - Normalisation de métiers

**Deuxième étape** : standardise et regroupe les métiers selon une table de référence.

```bash
python NormaliseMetiers.py input.csv output.csv data/referencesMetiers.csv
```

## 3. supprime_doublons.py - Suppression des doublons

**Troisième étape** : supprime les doublons d'entreprises (ex: un coiffeur et un barbier avec le même nom et la même adresse).

```bash
python supprime_doublons.py input.csv output.csv
```

## 4. maj_historique.py - Gestion de l'historique

**Quatrième étape** : permet de garder une version des informations dans le temps et de maintenir un historique des données.

```bash
python maj_historique.py
```

## 5. Filters.py - Filtrage des données

**Dernière étape** : filtre le fichier d'historique selon des critères qui peuvent évoluer dans le temps.

```bash
python Filters.py
```

## Utilisation complète du workflow

Voici comment utiliser l'ensemble des scripts de manière séquentielle :

```bash
# 1. Collecte initiale (occasionnelle)
python recherche_entreprises.py metiers.csv villes.csv entreprises_brutes.csv --api-key YOUR_API_KEY

# 2. Normaliser les métiers
python NormaliseMetiers.py entreprises_brutes.csv entreprises_normalisees.csv data/referencesMetiers.csv

# 3. Supprimer les doublons
python supprime_doublons.py entreprises_normalisees.csv entreprises_sans_doublons.csv

# 4. Mettre à jour l'historique
python maj_historique.py

# 5. Appliquer les filtres
python Filters.py
```

## Tests

Le projet inclut une suite complète de tests pour chaque script. Chaque test valide trois scénarios :

- **Cas nominal** : Fonctionnement normal avec des données valides
- **Données inconnues** : Traitement de données nouvelles ou non reconnues
- **Données manquantes** : Gestion des données incomplètes ou vides

### Structure des tests

```text
tests/
├── tests_recherche_entreprises/     # Tests pour recherche_entreprises.py
├── tests_normalisation_metiers/     # Tests pour NormaliseMetiers.py
├── tests_supprime_doublons/         # Tests pour supprime_doublons.py
├── tests_maj_historique/           # Tests pour maj_historique.py
├── tests_filters/                  # Tests pour Filters.py
└── run_all_tests.py               # Script pour exécuter tous les tests
```

### Exécution des tests

**Exécuter tous les tests :**

```bash
python tests/run_all_tests.py
```

**Exécuter les tests d'un script spécifique :**

```bash
# Tests pour la normalisation des métiers
python -m unittest tests.tests_normalisation_metiers.test_normalise_metiers

# Tests pour la suppression des doublons
python -m unittest tests.tests_supprime_doublons.test_supprime_doublons

# Tests pour la mise à jour de l'historique
python -m unittest tests.tests_maj_historique.test_maj_historique

# Tests pour le filtrage
python -m unittest tests.tests_filters.test_filters

# Tests pour la recherche d'entreprises
python -m unittest tests.tests_recherche_entreprises.test_recherche_entreprises
```

### Données de test

Chaque dossier de test contient :

- **Fichiers d'entrée** avec différents scénarios (nominal, données inconnues, données manquantes)
- **Fichiers de référence** avec les résultats attendus
- **Script de test** qui compare les résultats générés aux références
