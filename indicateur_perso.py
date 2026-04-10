"""

indicateurs_perso.py . Indicateurs personnalisés (inspirés du cours)

"""

from collections import Counter
from indicateurs_base import is_stop


# Connecteurs logiques à détecter dans le texte
CONNECTEURS = {
    # Addition
    "de plus", "en outre", "par ailleurs", "également", "aussi",
    "de même", "ainsi que",
    # Opposition
    "cependant", "néanmoins", "toutefois", "pourtant", "or",
    "en revanche", "au contraire", "malgré",
    # Cause
    "car", "parce que", "puisque", "étant donné", "vu que",
    # Conséquence
    "donc", "ainsi", "par conséquent", "c'est pourquoi", "dès lors",
    "de ce fait", "alors",
    # Illustration
    "par exemple", "notamment", "c'est-à-dire", "soit",
    # Conclusion
    "enfin", "en conclusion", "en résumé", "bref", "finalement",
}


def count_syllables(word: str) -> int:
    """
    Estime le nombre de syllabes d'un mot français en comptant
    les groupes de voyelles consécutives.
    """
    word = word.lower()
    voyelles = "aeiouyàâäéèêëîïôùûüœæ"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in voyelles
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    return max(1, count)


def ratio_type_token(doc) -> float:
    """
    Ratio Type/Token = nb de mots uniques / nb total de mots (hors mots vides).
    Mesure la richesse globale du vocabulaire.
    Plus le ratio est proche de 1, plus le vocabulaire est varié.
    """
    tokens = [t.lower_ for t in doc if not is_stop(t) and t.is_alpha]
    if not tokens:
        return 0.0
    return round(len(set(tokens)) / len(tokens), 3)


def longueur_moyenne_phrases(doc) -> float:
    """
    Longueur moyenne des phrases en nombre de mots (hors ponctuation).
    Des phrases longues indiquent une structuration plus élaborée.
    """
    lengths = [
        sum(1 for t in sent if not t.is_punct and not t.is_space)
        for sent in doc.sents
    ]
    if not lengths:
        return 0.0
    return round(sum(lengths) / len(lengths), 2)


def nb_phrases_nominales(doc) -> int:
    """
    Nombre de phrases sans verbe conjugué (phrases nominales).
    Un style trop nominal peut indiquer des phrases incomplètes.
    """
    count = 0
    for sent in doc.sents:
        has_verb = any(
            t.pos_ == "VERB"
            and t.morph.get("VerbForm") not in [["Inf"], ["Part"]]
            for t in sent
        )
        if not has_verb:
            count += 1
    return count


def nb_moyen_syllabes_par_mot(doc) -> float:
    """
    Nombre moyen de syllabes par mot (hors mots vides).
    Un score élevé indique un vocabulaire plus soutenu.
    Inspiré de l'indicateur 'Nombre différent de syllabes' du cours.
    """
    mots = [t.text for t in doc if not is_stop(t) and t.is_alpha]
    if not mots:
        return 0.0
    return round(sum(count_syllables(m) for m in mots) / len(mots), 2)


def top5_mots_frequents(doc) -> str:
    """
    Les 5 mots les plus fréquents (hors mots vides).
    Permet de repérer les répétitions et le champ lexical dominant.
    Inspiré de l'indicateur 'Fréquence / Distribution' du cours.
    """
    mots = [t.lemma_.lower() for t in doc if not is_stop(t) and t.is_alpha]
    if not mots:
        return ""
    return " | ".join(f"{mot}({n})" for mot, n in Counter(mots).most_common(5))


def nb_connecteurs_logiques(doc) -> int:
    """
    Nombre de connecteurs logiques présents dans le texte.
    Leur présence indique une meilleure organisation du discours.
    """
    text_lower = doc.text.lower()
    return sum(1 for c in CONNECTEURS if c in text_lower)