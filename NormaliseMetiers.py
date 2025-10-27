import csv
import sys


def charger_metiers_reference(fichier_reference):
    metiers = {}
    with open(fichier_reference, newline="", encoding="utf-8") as ref_file:
        reader = csv.reader(ref_file)
        for row in reader:
            if len(row) >= 2:
                metiers[row[0].strip().lower()] = row[1].strip()
    return metiers


def convertir_csv(fichier_entree, fichier_sortie, fichier_reference):
    metiers_ref = charger_metiers_reference(fichier_reference)

    # Compteurs pour les statistiques
    lignes_lues = 0
    metiers_normalises = 0
    metiers_non_traites = 0

    with (
        open(fichier_entree, newline="", encoding="utf-8") as csv_in,
        open(fichier_sortie, "w", newline="", encoding="utf-8") as csv_out,
    ):
        reader = csv.DictReader(csv_in)

        # Détection automatique des colonnes d'entrée
        input_fieldnames = reader.fieldnames
        if not input_fieldnames:
            print("Erreur: Impossible de lire les colonnes du fichier d'entrée")
            return

        print(f"Colonnes détectées dans le fichier d'entrée: {input_fieldnames}")

        # Création des colonnes de sortie : toutes les colonnes d'entrée + Metier_normalise
        output_fieldnames = []
        for field in input_fieldnames:
            if field != "Metier":  # On garde toutes les colonnes sauf Metier
                output_fieldnames.append(field)
        output_fieldnames.append("Metier_normalise")  # On ajoute la colonne normalisée

        writer = csv.DictWriter(csv_out, fieldnames=output_fieldnames)
        writer.writeheader()

        for row in reader:
            lignes_lues += 1
            metier = row.get("Metier", "").strip().lower()

            if metier in metiers_ref:
                metier_normalise = metiers_ref[metier]
                metiers_normalises += 1
            else:
                metier_normalise = f"INCONNU({metier})"
                metiers_non_traites += 1

            # Création de la ligne de sortie avec toutes les colonnes conservées
            output_row = {}
            for field in output_fieldnames:
                if field == "Metier_normalise":
                    output_row[field] = metier_normalise
                elif field in input_fieldnames:
                    output_row[field] = row.get(field, "")

            writer.writerow(output_row)

    # Affichage des statistiques
    print(f"\n=== Statistiques de traitement ===")
    print(f"   Lignes lues: {lignes_lues}")
    print(f"   Métiers normalisés: {metiers_normalises}")
    print(f"   Métiers non traités (INCONNU): {metiers_non_traites}")

    if lignes_lues > 0:
        pourcentage_normalise = (metiers_normalises / lignes_lues) * 100
        print(f"   Taux de normalisation: {pourcentage_normalise:.1f}%")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python NormaliseMetiers.py <input.csv> <output.csv> <reference.csv>")
        print("\nCe script normalise les métiers dans un fichier CSV en conservant toutes les colonnes.")
        print("Le fichier d'entrée peut contenir n'importe quelles colonnes, toutes seront conservées.")
        print("Seule la colonne 'Metier' sera remplacée par 'Metier_normalise'.")
        sys.exit(1)
    convertir_csv(sys.argv[1], sys.argv[2], sys.argv[3])

    # Exemples de fichiers CSV pour test

    # Exemple de reference.csv (inchangé)
    # Format: Metier,Metier_normalise
    # boulanger,Boulanger
    # plombier,Plombier
    # medecin,Médecin
    # enseignant,Enseignant
    # avocat,Avocat
    # ingenieur,Ingénieur
    # architecte,Architecte
    # infirmier,Infirmier
    # comptable,Comptable
    # chauffeur,Chauffeur

    # Exemple de input.csv (format étendu avec nouvelles colonnes)
    # Format: Nom,Adresse,Ville,Metier,Heures_ouverture,Nombre_avis,Note,Jours_fermeture
    # Jean Dupont,12 rue A,Paris,boulanger,"lundi: 07:00-19:00; mardi: 07:00-19:00",142,4.3,1
    # Marie Martin,34 rue B,Lyon,plombier,"lundi: 08:00-18:00; mardi: 08:00-18:00",89,4.1,1
    # Paul Durand,56 rue C,Marseille,medecin,"lundi: 09:00-17:00; mardi: 09:00-17:00",234,4.7,0
    # Sophie Bernard,78 rue D,Toulouse,enseignant,Non disponible,45,4.2,2
    # Luc Petit,90 rue E,Nantes,avocat,"lundi: 09:00-18:00; mardi: 09:00-18:00",67,4.0,2

    # Exemple de output.csv (après conversion avec toutes les colonnes conservées)
    # Format: Nom,Adresse,Ville,Heures_ouverture,Nombre_avis,Note,Jours_fermeture,Metier_normalise
    # Jean Dupont,12 rue A,Paris,"lundi: 07:00-19:00; mardi: 07:00-19:00",142,4.3,1,Boulanger
    # Marie Martin,34 rue B,Lyon,"lundi: 08:00-18:00; mardi: 08:00-18:00",89,4.1,1,Plombier
    # Paul Durand,56 rue C,Marseille,"lundi: 09:00-17:00; mardi: 09:00-17:00",234,4.7,0,Médecin
    # Sophie Bernard,78 rue D,Toulouse,Non disponible,45,4.2,2,Enseignant
    # Luc Petit,90 rue E,Nantes,"lundi: 09:00-18:00; mardi: 09:00-18:00",67,4.0,2,Avocat
