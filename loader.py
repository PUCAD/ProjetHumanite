"""
=============================================================================
config.py – Constantes et mots vides
=============================================================================
"""

import re

# Modèle spaCy pour le français
NLP_MODEL = "fr_core_news_sm"

# Regex pour détecter les séparateurs de questions dans la copie
# Exemples reconnus : "Question 1", "Q1", "Q 2", "QUESTION 3", "Q.3"
QUESTION_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:Question|QUESTION|Q\.?\s*)(\d+)[^\n]*",
    re.IGNORECASE
)

# Colonnes du fichier CSV de sortie
CSV_FIELDS = [
    "question",
    "nb_lemmes_differents",
    "nb_phrases",
    "nb_phrases_syntaxiquement_correctes",
    "nb_fautes_orthographe_copie",
    "nb_noms_communs_differents",
    "nb_adjectifs_differents",
    "nb_verbes_differents",
    "nb_phrases_simples",
    "nb_phrases_complexes",
]

# ─────────────────────────────────────────────────────────────────────────────
# MOTS VIDES (stop words) personnalisés
# ─────────────────────────────────────────────────────────────────────────────
# Justification :
#   Les mots vides sont des mots grammaticaux très fréquents qui n'apportent
#   pas de sens lexical à l'analyse (articles, prépositions, conjonctions,
#   pronoms courants). Nous combinons la liste native de spaCy avec des ajouts
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
    # Contractions OCR fréquentes
    "l", "d", "j", "n", "s", "m", "c", "qu",
    # Ponctuation résiduelle
    "-", "–", "—", "«", "»", "...",
}