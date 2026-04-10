"""

indicateurs_base.py  Indicateurs obligatoires du sujet

"""

import re
from spellchecker import SpellChecker
from config import CUSTOM_STOP_WORDS


def is_stop(token) -> bool:
    """Retourne True si le token est un mot vide ou de la ponctuation."""
    return (
        token.is_stop or token.is_punct or token.is_space
        or token.lower_ in CUSTOM_STOP_WORDS
        or token.lemma_.lower() in CUSTOM_STOP_WORDS
    )


def count_lemmes(doc) -> int:
    """Nombre de lemmes différents (hors mots vides)."""
    return len({t.lemma_.lower() for t in doc if not is_stop(t) and t.is_alpha})


def count_sentences(doc) -> int:
    """Nombre total de phrases détectées par spaCy."""
    return sum(1 for _ in doc.sents)


def count_syntactically_correct_sentences(doc) -> int:
    """
    Nombre de phrases syntaxiquement correctes.
    Heuristique : phrase correcte = sujet (nsubj) + verbe conjugué.
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
    On ignore les mots < 3 caractères et ceux commençant par une majuscule.
    """
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]{3,}\b", text)
    lower_words = [w.lower() for w in words if not w[0].isupper()]
    return len(spell.unknown(lower_words))


def count_pos(doc, pos_tag: str) -> int:
    """Nombre de lemmes différents pour une catégorie grammaticale (NOUN, ADJ, VERB)."""
    return len({
        t.lemma_.lower() for t in doc
        if t.pos_ == pos_tag and not is_stop(t) and t.is_alpha
    })


def classify_sentences(doc) -> tuple:
    """
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