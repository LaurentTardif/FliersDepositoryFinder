#!/usr/bin/env python3
"""
Script pour trier un fichier CSV par ordre alphabétique (par nom d'entreprise)
Optionnellement supprime les doublons pendant le tri
"""

import csv
import sys
import argparse
from typing import List, Dict
import hashlib

def normalize_text(text: str) -> str:
    """Normalise le texte pour la comparaison"""
    return text.strip().lower().replace('  ', ' ')

def create_record_hash(record: Dict[str, str]) -> str:
    """Crée un hash unique pour détecter les doublons"""
    nom = normalize_text(record.get('Nom', ''))
    adresse = normalize_text(record.get('Adresse', ''))
    ville = normalize_text(record.get('Ville', ''))
    metier = normalize_text(record.get('Metier_normalise', record.get('Metier', '')))

    composite_key = f"{nom}|{adresse}|{ville}|{metier}"
    return hashlib.md5(composite_key.encode('utf-8')).hexdigest()

def sort_csv(input_file: str, output_file: str, remove_duplicates: bool = False,
             sort_column: str = 'Nom', verbose: bool = False):
    """
    Trie un fichier CSV par ordre alphabétique

    Args:
        input_file: Fichier CSV d'entrée
        output_file: Fichier CSV de sortie
        remove_duplicates: Supprimer les doublons pendant le tri
        sort_column: Colonne sur laquelle trier
        verbose: Affichage détaillé
    """
    try:
        # Lecture du fichier
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)

        if not data:
            print("Fichier vide, rien à trier.")
            return

        if verbose:
            print(f"📁 Lecture de {len(data)} enregistrements depuis {input_file}")

        # Suppression des doublons si demandée
        if remove_duplicates:
            seen_hashes = set()
            unique_data = []
            duplicates_count = 0

            for record in data:
                record_hash = create_record_hash(record)
                if record_hash not in seen_hashes:
                    seen_hashes.add(record_hash)
                    unique_data.append(record)
                else:
                    duplicates_count += 1
                    if verbose:
                        print(f"🗑️  Doublon supprimé: {record.get('Nom', '')[:40]}")

            data = unique_data
            if verbose:
                print(f"🧹 {duplicates_count} doublons supprimés, {len(data)} enregistrements uniques restants")

        # Tri des données
        if sort_column not in data[0]:
            print(f"Erreur: Colonne '{sort_column}' non trouvée dans le fichier")
            print(f"Colonnes disponibles: {', '.join(data[0].keys())}")
            sys.exit(1)

        data_sorted = sorted(data, key=lambda x: x[sort_column].lower())

        if verbose:
            print(f"📊 Tri effectué sur la colonne '{sort_column}'")

        # Écriture du fichier trié
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = data_sorted[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_sorted)

        print(f"✅ Fichier trié créé: {output_file} ({len(data_sorted)} lignes)")

        if verbose:
            print(f"🔤 Premier: {data_sorted[0][sort_column]}")
            print(f"🔤 Dernier: {data_sorted[-1][sort_column]}")

    except FileNotFoundError:
        print(f"Erreur: Fichier '{input_file}' non trouvé")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Trie un fichier CSV par ordre alphabétique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python trier_csv.py input.csv output.csv
  python trier_csv.py input.csv output.csv --remove-duplicates --verbose
  python trier_csv.py input.csv output.csv --sort-column Ville
        """
    )

    parser.add_argument('input_file', help='Fichier CSV d\'entrée')
    parser.add_argument('output_file', help='Fichier CSV de sortie trié')
    parser.add_argument('--remove-duplicates', '-d', action='store_true',
                       help='Supprimer les doublons pendant le tri')
    parser.add_argument('--sort-column', '-s', default='Nom',
                       help='Colonne sur laquelle trier (défaut: Nom)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Affichage détaillé')

    args = parser.parse_args()

    sort_csv(args.input_file, args.output_file, args.remove_duplicates,
             args.sort_column, args.verbose)

if __name__ == "__main__":
    main()