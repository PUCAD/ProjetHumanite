"""
=============================================================================
Projet Humanité Numérique – Partie 2
Analyse linguistique d'une copie transcrite en français
=============================================================================
Auteurs      : [Prénom Nom 1], [Prénom Nom 2]
Date         : 2025
Dépendances  : spacy, language_tool_python, fr_core_news_sm

Installation :
    pip install spacy language_tool_python
    python -m spacy download fr_core_news_sm
=============================================================================
"""

import re
import csv
import sys
import argparse
from pathlib import Path
from collections import Counter

import spacy
import language_tool_python


# =============================================================================
# CONFIGURATION
# =============================================================================

# Modèle spaCy pour le français
NLP_MODEL = "fr_core_news_sm"

# Regex pour détecter les séparateurs de questions dans la copie
# Exemples reconnus : "Question 1", "Q1", "Q 2", "QUESTION 3"
QUESTION_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:Question|QUESTION|Q\.?\s*)(\d+)[^\n]*",
    re.IGNORECASE
)

# ─────────────────────────────────────────────────────────────────────────────
# MOTS VIDES (stop words) personnalisés
# ─────────────────────────────────────────────────────────────────────────────
# Justification :
#   Les mots vides sont des mots grammaticaux très fréquents qui n'apportent
#   pas de sens lexical à l'analyse (articles, prépositions, conjonctions,
#   pronoms courants). Nous combinons la liste de spaCy avec des ajouts
#   spécifiques au français académique afin d'éviter qu'ils ne biaisent
#   les métriques de richesse lexicale et de variété du vocabulaire.
CUSTOM_STOP_WORDS = {
    # Articles et déterminants
    "le", "la", "les", "un", "une", "des", "du", "au", "aux",
    "ce", "cet", "cette", "ces", "mon", "ton", "son", "ma", "ta",
    "sa", "nos", "vos", "leurs", "leur",
    # Prépositions courantes
    "à", "de", "en", "par", "pour", "sur", "sous", "dans", "avec",
    "sans", "entre", "vers", "chez", "contre", "depuis", "jusqu",
    # Conjonctions
    "et", "ou", "mais", "donc", "or", "ni", "car", "que", "qui",
    "quoi", "dont", "où", "si", "bien", "comme", "lorsque", "quand",
    # Pronoms personnels
    "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "me", "te", "se", "lui", "y", "en", "on",
    # Verbes auxiliaires très courants
    "être", "avoir", "est", "sont", "était", "ont", "a", "avait",
    # Adverbes génériques
    "très", "plus", "moins", "peu", "beaucoup", "tout", "bien",
    "aussi", "encore", "même", "alors", "ainsi",
    # Ponctuation et chiffres (au cas où ils passent le tokenizer)
    "-", "–", "—", "«", "»", "...",
}


# =============================================================================
# CHARGEMENT DES OUTILS NLP
# =============================================================================

def load_tools():
    """Charge le modèle spaCy et l'outil LanguageTool (fr)."""
    print("[INFO] Chargement du modèle spaCy français...")
    try:
        nlp = spacy.load(NLP_MODEL)
    except OSError:
        print(f"[ERREUR] Modèle '{NLP_MODEL}' introuvable.")
        print("         Lancez : python -m spacy download fr_core_news_sm")
        sys.exit(1)

    # Enrichir les stop words de spaCy avec notre liste personnalisée
    for word in CUSTOM_STOP_WORDS:
        nlp.vocab[word].is_stop = True

    print("[INFO] Chargement de LanguageTool (français)...")
    tool = language_tool_python.LanguageTool("fr")

    return nlp, tool


# =============================================================================
# LECTURE ET DÉCOUPAGE DU FICHIER
# =============================================================================

def read_file(filepath: str) -> str:
    """Lit le fichier de transcription et retourne le texte brut."""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERREUR] Fichier introuvable : {filepath}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def split_by_questions(text: str) -> dict[str, str]:
    """
    Découpe le texte par question.
    Retourne un dict { "Question 1": "...", "Question 2": "...", ... }
    Si aucun séparateur n'est trouvé, traite l'ensemble comme une seule section.
    """
    matches = list(QUESTION_PATTERN.finditer(text))

    if not matches:
        print("[AVERTISSEMENT] Aucun marqueur de question détecté. "
              "Le texte entier est analysé comme une seule section.")
        return {"Texte complet": text.strip()}

    questions = {}
    for i, match in enumerate(matches):
        key = f"Question {match.group(1)}"
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        questions[key] = text[start:end].strip()

    return questions


# =============================================================================
# ANALYSE LINGUISTIQUE PAR QUESTION
# =============================================================================

def is_stop(token) -> bool:
    """Retourne True si le token est un mot vide ou de la ponctuation."""
    return (
        token.is_stop
        or token.is_punct
        or token.is_space
        or token.lower_ in CUSTOM_STOP_WORDS
        or token.lemma_.lower() in CUSTOM_STOP_WORDS
    )


def count_lemmes(doc) -> int:
    """Nombre de lemmes différents (hors mots vides)."""
    lemmes = {token.lemma_.lower() for token in doc if not is_stop(token) and token.is_alpha}
    return len(lemmes)


def count_sentences(doc) -> int:
    """Nombre total de phrases détectées par spaCy."""
    return sum(1 for _ in doc.sents)


def count_syntactically_correct_sentences(doc, tool) -> int:
    """
    Nombre de phrases sans erreur grammaticale selon LanguageTool.
    Une phrase est jugée correcte si LanguageTool ne retourne aucune erreur
    (hors erreurs de style ou typographiques mineures).
    """
    correct = 0
    for sent in doc.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue
        matches = tool.check(sent_text)
        # On ignore les règles purement stylistiques
        grammar_errors = [
            m for m in matches
            if m.ruleId not in {"WHITESPACE_RULE", "FRENCH_WHITESPACE"}
        ]
        if not grammar_errors:
            correct += 1
    return correct


def count_spelling_errors(text: str, tool) -> int:
    """
    Nombre total de fautes d'orthographe dans le texte complet.
    On filtre uniquement les correspondances de type 'SPELL' (orthographe).
    """
    matches = tool.check(text)
    spelling = [m for m in matches if "spell" in m.ruleId.lower() or "MORFOLOGIK" in m.ruleId]
    return len(spelling)


def count_pos(doc, pos_tag: str) -> int:
    """
    Nombre de tokens différents (lemmes) d'une catégorie grammaticale donnée.
    pos_tag : 'NOUN' pour noms communs, 'ADJ' pour adjectifs, 'VERB' pour verbes, etc.
    """
    lemmes = {
        token.lemma_.lower()
        for token in doc
        if token.pos_ == pos_tag and not is_stop(token) and token.is_alpha
    }
    return len(lemmes)


def classify_sentences(doc) -> tuple[int, int]:
    """
    Classifie les phrases en simples ou complexes.

    Phrase simple  : une seule proposition (un seul verbe conjugué principal,
                     pas de subordination).
    Phrase complexe: plusieurs propositions (présence de propositions
                     subordonnées ou coordonnées avec verbes conjugués).

    Retourne (nb_simples, nb_complexes).
    """
    simples = 0
    complexes = 0

    for sent in doc.sents:
        # Compter les verbes à un mode personnel (pas infinitif ni participe)
        verbes_conjugues = [
            token for token in sent
            if token.pos_ == "VERB"
            and token.morph.get("VerbForm") not in [["Inf"], ["Part"]]
        ]
        # Détecter les marqueurs de subordination / coordination complexe
        has_subordination = any(
            token.dep_ in {"mark", "relcl", "advcl", "csubj", "ccomp", "xcomp"}
            for token in sent
        )

        if len(verbes_conjugues) <= 1 and not has_subordination:
            simples += 1
        else:
            complexes += 1

    return simples, complexes


def analyse_question(text: str, nlp, tool) -> dict:
    """
    Analyse complète d'un bloc de texte correspondant à une question.
    Retourne un dictionnaire de métriques.
    """
    if not text.strip():
        return {
            "nb_lemmes_differents": 0,
            "nb_phrases": 0,
            "nb_phrases_correctes": 0,
            "nb_noms_communs_differents": 0,
            "nb_adjectifs_differents": 0,
            "nb_verbes_differents": 0,
            "nb_phrases_simples": 0,
            "nb_phrases_complexes": 0,
        }

    doc = nlp(text)

    nb_simples, nb_complexes = classify_sentences(doc)

    return {
        "nb_lemmes_differents":       count_lemmes(doc),
        "nb_phrases":                 count_sentences(doc),
        "nb_phrases_correctes":       count_syntactically_correct_sentences(doc, tool),
        "nb_noms_communs_differents": count_pos(doc, "NOUN"),
        "nb_adjectifs_differents":    count_pos(doc, "ADJ"),
        "nb_verbes_differents":       count_pos(doc, "VERB"),
        "nb_phrases_simples":         nb_simples,
        "nb_phrases_complexes":       nb_complexes,
    }


# =============================================================================
# GÉNÉRATION DU CSV
# =============================================================================

CSV_FIELDS = [
    "question",
    "nb_lemmes_differents",
    "nb_phrases",
    "nb_phrases_correctes",
    "nb_fautes_orthographe_copie",   # même valeur sur toutes les lignes
    "nb_noms_communs_differents",
    "nb_adjectifs_differents",
    "nb_verbes_differents",
    "nb_phrases_simples",
    "nb_phrases_complexes",
]


def write_csv(results: list[dict], output_path: str):
    """Écrit les résultats dans un fichier CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(results)
    print(f"[OK] Fichier CSV généré : {output_path}")


# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

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

    # Chargement des outils
    nlp, tool = load_tools()

    # Lecture et découpage du texte
    print(f"[INFO] Lecture du fichier : {args.input}")
    texte_complet = read_file(args.input)
    questions = split_by_questions(texte_complet)
    print(f"[INFO] {len(questions)} section(s) détectée(s) : {list(questions.keys())}")

    # Fautes d'orthographe globales (sur la copie entière)
    print("[INFO] Calcul des fautes d'orthographe (copie entière)...")
    nb_fautes_globales = count_spelling_errors(texte_complet, tool)
    print(f"       → {nb_fautes_globales} faute(s) détectée(s)")

    # Analyse par question
    rows = []
    for question_label, question_text in questions.items():
        print(f"[INFO] Analyse de : {question_label}...")
        metrics = analyse_question(question_text, nlp, tool)
        row = {"question": question_label,
               "nb_fautes_orthographe_copie": nb_fautes_globales,
               **metrics}
        rows.append(row)
        print(f"       → {metrics['nb_phrases']} phrase(s), "
              f"{metrics['nb_lemmes_differents']} lemme(s) différent(s)")

    # Écriture CSV
    write_csv(rows, args.output)


if __name__ == "__main__":
    main()