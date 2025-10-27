#!/usr/bin/env python3
"""
Script de suppression des doublons dans les fichiers CSV d'entreprises
Supprime les lignes dupliquées basées sur les colonnes: Nom, Adresse, Ville, Metier
"""

import argparse
import csv
import hashlib
import sys
from typing import Dict, List, Set, Tuple


def normalize_text(text: str) -> str:
    """
    Normalise le texte pour la comparaison de doublons

    Args:
        text: Texte à normaliser

    Returns:
        Texte normalisé (minuscules, espaces supprimés)
    """
    return text.strip().lower().replace("  ", " ")


def create_record_hash(record: Dict[str, str]) -> str:
    """
    Crée un hash unique pour un enregistrement basé sur les champs clés

    Args:
        record: Dictionnaire contenant les données d'une ligne

    Returns:
        Hash MD5 de l'enregistrement normalisé
    """
    # Normalisation des champs clés
    nom = normalize_text(record.get("Nom", ""))
    adresse = normalize_text(record.get("Adresse", ""))
    ville = normalize_text(record.get("Ville", ""))
    metier = normalize_text(record.get("Metier_normalise", record.get("Metier", "")))

    # Création d'une clé composite
    composite_key = f"{nom}|{adresse}|{ville}|{metier}"

    # Génération du hash
    return hashlib.md5(composite_key.encode("utf-8")).hexdigest()


def are_similar_records(record1: Dict[str, str], record2: Dict[str, str], similarity_threshold: float = 0.9) -> bool:
    """
    Vérifie si deux enregistrements sont similaires (optionnel pour détection avancée)

    Args:
        record1: Premier enregistrement
        record2: Deuxième enregistrement
        similarity_threshold: Seuil de similarité (non utilisé dans cette version simple)

    Returns:
        True si les enregistrements sont considérés comme des doublons
    """
    # Pour cette version, on utilise une correspondance exacte après normalisation
    return create_record_hash(record1) == create_record_hash(record2)


def remove_duplicates(input_file: str, output_file: str, verbose: bool = False, sort_by: str = None) -> Tuple[int, int]:
    """
    Supprime les doublons d'un fichier CSV

    Args:
        input_file: Chemin du fichier CSV d'entrée
        output_file: Chemin du fichier CSV de sortie
        verbose: Affichage détaillé des opérations
        sort_by: Colonne sur laquelle trier (optionnel)

    Returns:
        Tuple (nombre_total, nombre_uniques)
    """
    seen_hashes: Set[str] = set()
    unique_records: List[Dict[str, str]] = []
    total_records = 0
    duplicate_records = 0

    try:
        # Lecture du fichier d'entrée
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Détection automatique des colonnes d'entrée
            input_fieldnames = reader.fieldnames
            if not input_fieldnames:
                raise ValueError("Impossible de lire les colonnes du fichier d'entrée")

            print(f"Colonnes détectées dans le fichier d'entrée: {input_fieldnames}")

            # Vérification des colonnes requises pour la détection de doublons
            required_base_columns = {"Nom", "Adresse", "Ville"}
            if not required_base_columns.issubset(set(input_fieldnames)):
                missing = required_base_columns - set(input_fieldnames)
                print(f"Colonnes disponibles: {input_fieldnames}")
                print(f"Colonnes minimales requises: {required_base_columns}")
                raise ValueError(f"Colonnes manquantes: {missing}")

            # Vérifier qu'on a au moins une colonne métier
            has_metier = "Metier" in input_fieldnames
            has_metier_normalise = "Metier_normalise" in input_fieldnames
            if not (has_metier or has_metier_normalise):
                raise ValueError("Aucune colonne 'Metier' ou 'Metier_normalise' trouvée")

            for row_num, record in enumerate(reader, 1):
                total_records += 1

                # Création du hash pour ce record
                record_hash = create_record_hash(record)

                if record_hash not in seen_hashes:
                    # Nouvel enregistrement unique
                    seen_hashes.add(record_hash)
                    unique_records.append(record)

                    if verbose:
                        print(f"[{row_num}] Unique: {record.get('Nom', '')[:30]}...")
                else:
                    # Doublon détecté
                    duplicate_records += 1

                    if verbose:
                        print(f"[{row_num}] Doublon supprimé: {record.get('Nom', '')[:30]}...")

        # Tri des données si demandé
        if sort_by:
            if unique_records and sort_by in unique_records[0]:
                if verbose:
                    print(f"📊 Tri des données par '{sort_by}'...")
                unique_records = sorted(unique_records, key=lambda x: x.get(sort_by, "").lower())
                if verbose:
                    print(f"   Premier: {unique_records[0].get(sort_by, '')}")
                    print(f"   Dernier: {unique_records[-1].get(sort_by, '')}")
            else:
                available_columns = list(unique_records[0].keys()) if unique_records else []
                print(f"⚠️  Colonne '{sort_by}' non trouvée. Colonnes disponibles: {', '.join(available_columns)}")
                print("   Tri ignoré, suppression des doublons effectuée.")

        # Écriture du fichier de sortie avec toutes les colonnes détectées
        output_fieldnames = input_fieldnames  # Conserver toutes les colonnes d'entrée

        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=output_fieldnames)
            writer.writeheader()

            for record in unique_records:
                # Créer un enregistrement avec toutes les colonnes présentes
                clean_record = {col: record.get(col, "") for col in output_fieldnames}
                writer.writerow(clean_record)

        return total_records, len(unique_records)

    except FileNotFoundError:
        print(f"Erreur: Fichier d'entrée '{input_file}' non trouvé")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")
        sys.exit(1)


def analyze_duplicates(input_file: str):
    """
    Analyse les doublons sans les supprimer (mode analyse)

    Args:
        input_file: Chemin du fichier CSV à analyser
    """
    hash_count: Dict[str, int] = {}
    hash_examples: Dict[str, Dict[str, str]] = {}
    total_records = 0

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for record in reader:
                total_records += 1
                record_hash = create_record_hash(record)

                if record_hash in hash_count:
                    hash_count[record_hash] += 1
                else:
                    hash_count[record_hash] = 1
                    hash_examples[record_hash] = record

        # Affichage des statistiques
        duplicates = {h: count for h, count in hash_count.items() if count > 1}
        unique_count = len([h for h, count in hash_count.items() if count == 1])

        print(f"\n📊 Analyse des doublons:")
        print(f"   Total d'enregistrements: {total_records}")
        print(f"   Enregistrements uniques: {unique_count}")
        print(f"   Groupes de doublons: {len(duplicates)}")
        print(f"   Total de doublons: {sum(duplicates.values()) - len(duplicates)}")

        if duplicates:
            print(f"\n🔍 Exemples de doublons:")
            for i, (hash_key, count) in enumerate(list(duplicates.items())[:5], 1):
                example = hash_examples[hash_key]
                print(f"   {i}. {example.get('Nom', '')[:40]} ({count} occurrences)")

    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Suppression des doublons dans les fichiers CSV d'entreprises",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python supprime_doublons.py input.csv output.csv
  python supprime_doublons.py input.csv output.csv --verbose --sort Nom
  python supprime_doublons.py input.csv output.csv --sort Note
  python supprime_doublons.py input.csv --analyze

Le script compare les enregistrements sur la base des colonnes:
  - Nom (normalisé)
  - Adresse (normalisée)
  - Ville (normalisée)
  - Metier ou Metier_normalise (normalisé)

Ce script conserve automatiquement toutes les colonnes présentes dans le fichier d'entrée.
Cela inclut les nouvelles colonnes comme Heures_ouverture, Nombre_avis, Note, Jours_fermeture.

Options de tri disponibles: toutes les colonnes détectées dans le fichier
La normalisation supprime les espaces en trop et convertit en minuscules.
        """,
    )

    parser.add_argument("input_file", help="Fichier CSV d'entrée")
    parser.add_argument("output_file", nargs="?", help="Fichier CSV de sortie (requis sauf avec --analyze)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Affichage détaillé des opérations")
    parser.add_argument(
        "--analyze", "-a", action="store_true", help="Mode analyse: affiche les statistiques sans créer de fichier de sortie"
    )
    parser.add_argument("--sort", "-s", metavar="COLUMN", help="Trier les résultats par colonne (ex: Nom, Ville, Metier)")

    args = parser.parse_args()

    # Validation des arguments
    if not args.analyze and not args.output_file:
        print("Erreur: fichier de sortie requis (sauf avec --analyze)")
        parser.print_help()
        sys.exit(1)

    if args.analyze:
        # Mode analyse
        print(f"🔍 Analyse des doublons dans: {args.input_file}")
        analyze_duplicates(args.input_file)
    else:
        # Mode suppression
        print(f"🧹 Suppression des doublons...")
        print(f"   Entrée: {args.input_file}")
        print(f"   Sortie: {args.output_file}")
        if args.sort:
            print(f"   Tri par: {args.sort}")

        total, unique = remove_duplicates(args.input_file, args.output_file, args.verbose, args.sort)
        duplicates_removed = total - unique

        print(f"\n✅ Traitement terminé:")
        print(f"   Enregistrements traités: {total}")
        print(f"   Enregistrements uniques: {unique}")
        print(f"   Doublons supprimés: {duplicates_removed}")

        if total > 0:
            reduction_percent = (duplicates_removed / total) * 100
            print(f"   Réduction: {reduction_percent:.1f}%")


if __name__ == "__main__":
    main()

# Exemples de fichiers CSV compatibles:
#
# Format étendu (avec nouvelles colonnes) - input.csv:
# Nom,Adresse,Ville,Metier,Heures_ouverture,Nombre_avis,Note,Jours_fermeture
# Jean Dupont,12 rue A,Paris,boulanger,"lundi: 07:00-19:00",142,4.3,1
# Marie Martin,34 rue B,Lyon,plombier,"lundi: 08:00-18:00",89,4.1,1
# Jean Dupont,12 rue A,Paris,boulanger,"lundi: 07:00-19:00",142,4.3,1
# Sophie Bernard,78 rue D,Toulouse,enseignant,Non disponible,45,4.2,2
#
# Résultat après suppression des doublons (toutes colonnes conservées):
# Nom,Adresse,Ville,Metier,Heures_ouverture,Nombre_avis,Note,Jours_fermeture
# Jean Dupont,12 rue A,Paris,boulanger,"lundi: 07:00-19:00",142,4.3,1
# Marie Martin,34 rue B,Lyon,plombier,"lundi: 08:00-18:00",89,4.1,1
# Sophie Bernard,78 rue D,Toulouse,enseignant,Non disponible,45,4.2,2
#
# Format classique (ancien format) - input.csv:
# Nom,Adresse,Ville,Metier
# Jean Dupont,12 rue A,Paris,boulanger
# Marie Martin,34 rue B,Lyon,plombier
# Jean Dupont,12 rue A,Paris,boulanger
# Sophie Bernard,78 rue D,Toulouse,enseignant
#
# Résultat après suppression des doublons:
# Nom,Adresse,Ville,Metier
# Jean Dupont,12 rue A,Paris,boulanger
# Marie Martin,34 rue B,Lyon,plombier
# Sophie Bernard,78 rue D,Toulouse,enseignant
