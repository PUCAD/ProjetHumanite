"""

analyse.py . Chargement des outils et analyse complète d'une question

"""

import sys

import spacy
from spellchecker import SpellChecker

from config import NLP_MODEL, CUSTOM_STOP_WORDS
from loader import clean_text
from indicateurs_base import (
    count_lemmes, count_sentences, count_syntactically_correct_sentences,
    count_spelling_errors, count_pos, classify_sentences,
)
from indicateurs_perso import (
    ratio_type_token, longueur_moyenne_phrases, nb_phrases_nominales,
    nb_moyen_syllabes_par_mot, top5_mots_frequents, nb_connecteurs_logiques,
)


def load_tools():
    """Charge le modèle spaCy français et le correcteur orthographique."""
    print("[INFO] Chargement du modèle spaCy français...")
    try:
        nlp = spacy.load(NLP_MODEL)
    except OSError:
        print(f"[ERREUR] Modèle '{NLP_MODEL}' introuvable.")
        print("         Lancez : pip install fr-core-news-sm")
        sys.exit(1)

    for word in CUSTOM_STOP_WORDS:
        nlp.vocab[word].is_stop = True

    print("[INFO] Chargement du correcteur orthographique (français)...")
    spell = SpellChecker(language="fr", distance=1)

    return nlp, spell


def analyse_question(text: str, nlp, spell) -> dict:
    """
    Analyse complète d'un bloc de texte (une question).
    Retourne un dictionnaire de toutes les métriques.
    """
    text = clean_text(text)

    if not text:
        return {k: 0 for k in [
            "nb_lemmes_differents", "nb_phrases",
            "nb_phrases_syntaxiquement_correctes",
            "nb_noms_communs_differents", "nb_adjectifs_differents",
            "nb_verbes_differents", "nb_phrases_simples", "nb_phrases_complexes",
            "ratio_type_token", "longueur_moyenne_phrases",
            "nb_phrases_nominales", "nb_moyen_syllabes_par_mot",
            "top5_mots_frequents", "nb_connecteurs_logiques",
        ]}

    doc = nlp(text)
    nb_simples, nb_complexes = classify_sentences(doc)

    return {
        #  Indicateurs obligatoires 
        "nb_lemmes_differents":                count_lemmes(doc),
        "nb_phrases":                          count_sentences(doc),
        "nb_phrases_syntaxiquement_correctes": count_syntactically_correct_sentences(doc),
        "nb_noms_communs_differents":          count_pos(doc, "NOUN"),
        "nb_adjectifs_differents":             count_pos(doc, "ADJ"),
        "nb_verbes_differents":                count_pos(doc, "VERB"),
        "nb_phrases_simples":                  nb_simples,
        "nb_phrases_complexes":                nb_complexes,
        #  Indicateurs personnalisés 
        "ratio_type_token":                    ratio_type_token(doc),
        "longueur_moyenne_phrases":            longueur_moyenne_phrases(doc),
        "nb_phrases_nominales":                nb_phrases_nominales(doc),
        "nb_moyen_syllabes_par_mot":           nb_moyen_syllabes_par_mot(doc),
        "top5_mots_frequents":                 top5_mots_frequents(doc),
        "nb_connecteurs_logiques":             nb_connecteurs_logiques(doc),
    }