"""
=============================================================================
exporter.py – Écriture des résultats dans un fichier CSV
=============================================================================
"""
 
import csv
from config import CSV_FIELDS
 
 
def write_csv(results: list, output_path: str):
    """
    Écrit la liste de résultats dans un fichier CSV.
    Chaque élément de results est un dict avec les clés définies dans CSV_FIELDS.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(results)
 
    print(f"[OK] Fichier CSV généré : {output_path}")