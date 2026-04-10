"""
=============================================================================
loader.py – Lecture du fichier et découpage par questions
=============================================================================
"""

import re
import sys
from pathlib import Path

from config import QUESTION_PATTERN


def read_file(filepath: str) -> str:
    """Lit le fichier de transcription et retourne le texte brut."""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERREUR] Fichier introuvable : {filepath}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def clean_text(text: str) -> str:
    """
    Nettoie les artefacts courants de transcription (OCR, manuscrit numérisé) :
    - normalise les points répétés (... → .)
    - supprime les puces isolées
    - fusionne les sauts de ligne en espaces
    - supprime les guillemets
    """
    text = re.sub(r'["«»]', '', text)
    text = re.sub(r'\.\s*\.+', '.', text)
    text = re.sub(r'•\s*', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def split_by_questions(text: str) -> dict:
    """
    Découpe le texte par question (Question 1, Q2, QUESTION 3...).
    Le texte situé avant la première question est conservé sous 'Introduction'.
    Si aucun marqueur n'est trouvé, retourne le texte entier comme une seule section.
    """
    matches = list(QUESTION_PATTERN.finditer(text))

    if not matches:
        print("[AVERTISSEMENT] Aucun marqueur de question détecté. "
              "Le texte entier est analysé comme une seule section.")
        return {"Texte complet": text.strip()}

    questions = {}

    # Texte avant la première question → Introduction
    intro = text[:matches[0].start()].strip()
    if intro:
        questions["Introduction"] = intro

    for i, match in enumerate(matches):
        key = f"Question {match.group(1)}"
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        questions[key] = text[start:end].strip()

    return questions