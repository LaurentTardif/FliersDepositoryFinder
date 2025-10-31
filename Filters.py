#!/usr/bin/env python3
"""
Script de filtrage des entreprises selon des règles métier
Applique des règles pour marquer les entreprises à filtrer dans le champ 'Filtré'
"""

import argparse
import csv
import os
import sys
from typing import Dict, List


def apply_filter_rules(record: Dict[str, str]) -> tuple[str, str]:
    """
    Applique les règles métier pour déterminer si une entreprise doit être filtrée

    Règles:
    1. Si nombre_avis < 20 alors Filtré = "OUI"
    2. Si jours_fermeture > 3 alors Filtré = "OUI"
    3. Si metier_normalise = "Restaurant" et note < 4.5 alors Filtré = "OUI"
    4. Si metier_normalise = "Coiffeur_Barbier" et note < 4 alors Filtré = "OUI"

    Args:
        record: Dictionnaire contenant les données d'une entreprise

    Returns:
        Tuple (filtré, raison) - ("OUI"/"NON", raison du filtrage ou "")
    """
    try:
        # Récupération des valeurs avec gestion des champs vides
        nombre_avis = record.get("Nombre_avis", "").strip()
        jours_fermeture = record.get("Jours_fermeture", "").strip()
        note = record.get("Note", "").strip()
        metier_normalise = record.get("Metier_normalise", "").strip()

        # Règle 1: Nombre d'avis < 20
        if nombre_avis:
            try:
                nb_avis = int(nombre_avis)
                if nb_avis < 20:
                    return ("OUI", "Nombre d'avis insuffisant (< 20)")
            except ValueError:
                # Si conversion impossible, ignorer cette règle
                pass

        # Règle 2: Jours de fermeture > 3
        if jours_fermeture:
            try:
                jours_fermes = int(jours_fermeture)
                if jours_fermes > 3:
                    return ("OUI", "Trop de jours de fermeture (> 3)")
            except ValueError:
                # Si conversion impossible, ignorer cette règle
                pass

        # Règle 3: Restaurant avec note < 4.5
        if metier_normalise.lower() == "restaurant":
            if note:
                try:
                    note_float = float(note)
                    if note_float < 4.5:
                        return ("OUI", "Restaurant - Note insuffisante (< 4.5)")
                except ValueError:
                    # Si conversion impossible, ignorer cette règle
                    pass

        # Règle 4: Coiffeur_Barbier avec note < 4
        if metier_normalise.lower() == "coiffeur_barbier":
            if note:
                try:
                    note_float = float(note)
                    if note_float < 4.0:
                        return ("OUI", "Coiffeur/Barbier - Note insuffisante (< 4.0)")
                except ValueError:
                    # Si conversion impossible, ignorer cette règle
                    pass

        # Si aucune règle ne s'applique, ne pas filtrer
        return ("NON", "Pas de filtre")

    except Exception as e:
        print(f"⚠️  Erreur lors de l'application des règles pour {record.get('Nom', 'Inconnu')}: {e}")
        return ("NON", "Pas de filtre")


def process_filter_file(input_file: str, output_file: str, verbose: bool = False):
    """
    Traite le fichier d'entrée et applique les règles de filtrage

    Args:
        input_file: Chemin vers le fichier d'entrée
        output_file: Chemin vers le fichier de sortie
        verbose: Afficher les détails du traitement
    """

    if not os.path.exists(input_file):
        print(f"❌ Erreur: Fichier d'entrée '{input_file}' non trouvé")
        return

    print(f"🔍 Application des règles de filtrage...")
    print(f"   Entrée: {input_file}")
    print(f"   Sortie: {output_file}")
    print()

    try:
        # Lecture du fichier d'entrée
        with open(input_file, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames

            if not fieldnames:
                print("❌ Erreur: Impossible de lire les colonnes du fichier")
                return

            # Vérifier que les colonnes requises sont présentes (elles doivent être créées par maj_historique)
            required_columns = ["Filtré", "Raison_Filtrage"]
            missing_columns = [col for col in required_columns if col not in fieldnames]

            if missing_columns:
                print(f"❌ Erreur: Colonnes requises manquantes: {', '.join(missing_columns)}")
                print(f"   Le fichier d'entrée doit être généré par maj_historique.py")
                print(f"   Colonnes disponibles: {', '.join(fieldnames)}")
                return

            print(f"📋 Colonnes détectées: {', '.join(fieldnames)}")

            # Compteurs pour les statistiques
            total_records = 0
            filtered_count = 0
            rule1_count = 0  # Nombre d'avis < 20
            rule2_count = 0  # Jours fermeture > 3
            rule3_count = 0  # Restaurant note < 4.5
            rule4_count = 0  # Coiffeur_Barbier note < 4

            # Lecture de tous les enregistrements
            records = list(reader)
            total_records = len(records)

            print(f"📊 {total_records} entrées trouvées")
            print()

            # Traitement des enregistrements
            for record in records:
                original_filtre = record.get("Filtré", "NON")

                # Application des règles métier
                new_filtre, raison = apply_filter_rules(record)

                # Mise à jour des champs
                record["Filtré"] = new_filtre
                record["Raison_Filtrage"] = raison

                # Comptage pour les statistiques
                if new_filtre == "OUI":
                    filtered_count += 1

                    # Détail des règles appliquées (pour les statistiques)
                    if "Nombre d'avis insuffisant" in raison:
                        rule1_count += 1
                    elif "Trop de jours de fermeture" in raison:
                        rule2_count += 1
                    elif "Restaurant - Note insuffisante" in raison:
                        rule3_count += 1
                    elif "Coiffeur/Barbier - Note insuffisante" in raison:
                        rule4_count += 1

                # Affichage détaillé si demandé
                if verbose and (new_filtre != original_filtre):
                    print(f"🔄 {record.get('Nom', 'Inconnu')}: {original_filtre} → {new_filtre} ({raison})")

        # Écriture du fichier de sortie
        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        # Affichage des statistiques
        print("📈 Statistiques de filtrage:")
        print(f"   Total des entrées: {total_records}")
        print(f"   Entrées filtrées (Filtré=OUI): {filtered_count}")
        print(f"   Entrées non filtrées (Filtré=NON): {total_records - filtered_count}")
        print()
        print("📋 Détail des règles appliquées:")
        print(f"   Règle 1 (Nombre d'avis < 20): {rule1_count} entrées")
        print(f"   Règle 2 (Jours fermeture > 3): {rule2_count} entrées")
        print(f"   Règle 3 (Restaurant note < 4.5): {rule3_count} entrées")
        print(f"   Règle 4 (Coiffeur/Barbier note < 4.0): {rule4_count} entrées")
        print()
        print(f"✅ Fichier filtré sauvegardé: {output_file}")

    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Applique des règles de filtrage métier aux entreprises",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Règles de filtrage appliquées:
  1. Si Nombre_avis < 20 alors Filtré = "OUI"
  2. Si Jours_fermeture > 3 alors Filtré = "OUI"
  3. Si Metier_normalise = "Restaurant" et Note < 4.5 alors Filtré = "OUI"
  4. Si Metier_normalise = "Coiffeur_Barbier" et Note < 4.0 alors Filtré = "OUI"

Exemples d'usage:
  python Filters.py historique.csv historique_filtre.csv
  python Filters.py historique.csv historique_filtre.csv --verbose
        """,
    )

    parser.add_argument("input_file", help="Fichier CSV d'entrée (historique)")
    parser.add_argument("output_file", help="Fichier CSV de sortie (historique filtré)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Afficher les détails du traitement")

    args = parser.parse_args()

    # Validation des arguments
    if not args.input_file.endswith(".csv"):
        print("❌ Erreur: Le fichier d'entrée doit être un fichier CSV")
        sys.exit(1)

    if not args.output_file.endswith(".csv"):
        print("❌ Erreur: Le fichier de sortie doit être un fichier CSV")
        sys.exit(1)

    # Traitement
    process_filter_file(args.input_file, args.output_file, args.verbose)


if __name__ == "__main__":
    main()
