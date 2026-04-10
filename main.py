

import argparse

from loader import read_file, clean_text, split_by_questions
from analyse import load_tools, analyse_question, count_spelling_errors
from exporter import write_csv


def main():
    parser = argparse.ArgumentParser(
        description="Analyse linguistique d'une copie transcrite en français."
    )
    parser.add_argument(
        "input",
        help="Chemin vers le fichier de transcription (.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        default="resultats_analyse.csv",
        help="Chemin du fichier CSV de sortie (défaut : resultats_analyse.csv)"
    )
    args = parser.parse_args()

    # Chargement des outils NLP
    nlp, spell = load_tools()

    # Lecture du fichier
    print(f"[INFO] Lecture du fichier : {args.input}")
    texte_complet = read_file(args.input)

    # Découpage par questions
    questions = split_by_questions(texte_complet)
    print(f"[INFO] {len(questions)} section(s) détectée(s) : {list(questions.keys())}")

    # Fautes d'orthographe sur la copie entière
    print("[INFO] Calcul des fautes d'orthographe (copie entière)...")
    nb_fautes_globales = count_spelling_errors(clean_text(texte_complet), spell)
    print(f"       → {nb_fautes_globales} faute(s) détectée(s)")

    # Analyse par question
    rows = []
    for label, text in questions.items():
        print(f"[INFO] Analyse de : {label}...")
        metrics = analyse_question(text, nlp, spell)
        row = {
            "question":                    label,
            "nb_fautes_orthographe_copie": nb_fautes_globales,
            **metrics
        }
        rows.append(row)
        print(f"       → {metrics['nb_phrases']} phrase(s), "
              f"{metrics['nb_lemmes_differents']} lemme(s), "
              f"{metrics['nb_phrases_syntaxiquement_correctes']} correcte(s)")

    # Écriture du CSV
    write_csv(rows, args.output)


if __name__ == "__main__":
    main()