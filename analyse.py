"""

analyse.py .Fonctions d'analyse linguistique

"""

import re
import sys

import spacy
from spellchecker import SpellChecker

from config import NLP_MODEL, CUSTOM_STOP_WORDS
from loader import clean_text



# CHARGEMENT DES OUTILS


def load_tools():
    """Charge le modèle spaCy français et le correcteur orthographique."""
    print("[INFO] Chargement du modèle spaCy français...")
    try:
        nlp = spacy.load(NLP_MODEL)
    except OSError:
        print(f"[ERREUR] Modèle '{NLP_MODEL}' introuvable.")
        print("         Lancez : pip install fr-core-news-sm")
        sys.exit(1)

    # Enrichir les stop words de spaCy avec notre liste personnalisée
    for word in CUSTOM_STOP_WORDS:
        nlp.vocab[word].is_stop = True

    print("[INFO] Chargement du correcteur orthographique (français)...")
    spell = SpellChecker(language="fr", distance=1)

    return nlp, spell



# FONCTIONS UTILITAIRES


def is_stop(token) -> bool:
    """Retourne True si le token est un mot vide ou de la ponctuation."""
    return (
        token.is_stop or token.is_punct or token.is_space
        or token.lower_ in CUSTOM_STOP_WORDS
        or token.lemma_.lower() in CUSTOM_STOP_WORDS
    )



# MÉTRIQUES


def count_lemmes(doc) -> int:
    """Nombre de lemmes différents (hors mots vides)."""
    return len({t.lemma_.lower() for t in doc if not is_stop(t) and t.is_alpha})


def count_sentences(doc) -> int:
    """Nombre total de phrases détectées par spaCy."""
    return sum(1 for _ in doc.sents)


def count_syntactically_correct_sentences(doc) -> int:
    """
    Nombre de phrases syntaxiquement correctes.
    Heuristique : une phrase est correcte si elle contient
    au moins un sujet (nsubj) ET un verbe conjugué.
    """
    correct = 0
    for sent in doc.sents:
        has_subject = any(t.dep_ in {"nsubj", "nsubj:pass"} for t in sent)
        has_verb    = any(
            t.pos_ == "VERB"
            and t.morph.get("VerbForm") not in [["Inf"], ["Part"]]
            for t in sent
        )
        if has_subject and has_verb:
            correct += 1
    return correct


def count_spelling_errors(text: str, spell: SpellChecker) -> int:
    """
    Nombre de fautes d'orthographe via pyspellchecker.
    On ignore les mots < 3 caractères et les mots commençant
    par une majuscule (noms propres probables).
    """
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]{3,}\b", text)
    lower_words = [w.lower() for w in words if not w[0].isupper()]
    return len(spell.unknown(lower_words))


def count_pos(doc, pos_tag: str) -> int:
    """
    Nombre de lemmes différents pour une catégorie grammaticale.
    pos_tag : 'NOUN' (noms communs), 'ADJ' (adjectifs), 'VERB' (verbes)
    """
    return len({
        t.lemma_.lower() for t in doc
        if t.pos_ == pos_tag and not is_stop(t) and t.is_alpha
    })


def classify_sentences(doc) -> tuple:
    """
    Classifie les phrases en simples ou complexes.
    Phrase simple  : <= 1 verbe conjugué et pas de subordonnée.
    Phrase complexe: > 1 verbe conjugué OU présence de subordination.
    Retourne (nb_simples, nb_complexes).
    """
    simples = complexes = 0
    for sent in doc.sents:
        verbes = [
            t for t in sent
            if t.pos_ == "VERB"
            and t.morph.get("VerbForm") not in [["Inf"], ["Part"]]
        ]
        sub = any(
            t.dep_ in {"mark", "relcl", "advcl", "csubj", "ccomp", "xcomp"}
            for t in sent
        )
        if len(verbes) <= 1 and not sub:
            simples += 1
        else:
            complexes += 1
    return simples, complexes



# ANALYSE COMPLÈTE D'UNE QUESTION


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
        ]}

    doc = nlp(text)
    nb_simples, nb_complexes = classify_sentences(doc)

    return {
        "nb_lemmes_differents":                count_lemmes(doc),
        "nb_phrases":                          count_sentences(doc),
        "nb_phrases_syntaxiquement_correctes": count_syntactically_correct_sentences(doc),
        "nb_noms_communs_differents":          count_pos(doc, "NOUN"),
        "nb_adjectifs_differents":             count_pos(doc, "ADJ"),
        "nb_verbes_differents":                count_pos(doc, "VERB"),
        "nb_phrases_simples":                  nb_simples,
        "nb_phrases_complexes":                nb_complexes,
    }