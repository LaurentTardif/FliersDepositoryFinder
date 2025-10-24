# Scripts de Recherche et Normalisation d'Entreprises

Ce projet contient deux outils principaux :

## 1. NormaliseMetiers.py - Normalisation de métiers

Normalise les noms de métiers selon une table de référence.

### Usage

```bash
python NormaliseMetiers.py input.csv output.csv data/referencesMetiers.csv
```

## 2. recherche_entreprises.py - Recherche d'entreprises via Google Places

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

2. **Recherche avec paramètres personnalisés** :

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

### Intégration avec NormaliseMetiers.py

Vous pouvez chaîner les deux scripts :

```bash
# 1. Rechercher les entreprises
python recherche_entreprises.py metiers.csv villes.csv entreprises_brutes.csv --api-key YOUR_API_KEY

# 2. Normaliser les métiers trouvés
python NormaliseMetiers.py entreprises_brutes.csv entreprises_normalisees.csv data/referencesMetiers.csv
```
