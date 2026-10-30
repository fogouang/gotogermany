"""
app/modules/exams/import_normalize.py

Sujets Start Deutsch 1 / 2 (A1, A2) produits avec un schéma plus simple :
true_false, matching_2options, mc_image, mc_text, form_fill, sprechen_group_*.

Ce module les réécrit dans le schéma habituel de la plateforme AVANT la validation,
pour que la suite de l'import (parsers, correction, affichage) reste la même.
Un JSON déjà au format habituel traverse sans changement.
"""
from __future__ import annotations

import re
from copy import deepcopy

MODULE_NAMES = {
    "lesen": "Lesen",
    "hoeren": "Hören",
    "horen": "Hören",
    "hören": "Hören",
    "schreiben": "Schreiben",
    "sprechen": "Sprechen",
}

# Durées officielles Start Deutsch, utilisées seulement si le JSON n'en donne pas
DEFAULT_MINUTES = {
    "A1": {"lesen": 25, "hoeren": 20, "horen": 20, "schreiben": 20, "sprechen": 15},
    "A2": {"lesen": 30, "hoeren": 30, "horen": 30, "schreiben": 30, "sprechen": 15},
}

STOP = {"der", "die", "das", "den", "dem", "ein", "eine", "einen", "und", "oder", "mit", "von", "im", "in", "am"}


def _keyword(value: str) -> str:
    """Mot-clé tolérant pour la correction automatique d'un champ de formulaire."""
    words = [w for w in re.findall(r"[0-9]+|[A-Za-zÄÖÜäöüß]+", value) if w.lower() not in STOP]
    if not words:
        return re.escape(value.lower())
    parts = []
    for w in words:
        w = w.lower()
        parts.append(w if w.isdigit() or len(w) <= 6 else w[: len(w) - 2])
    return "|".join(dict.fromkeys(parts))


def _options(options) -> tuple[dict, dict, bool]:
    """[{label, text | image_description, url}] -> ({a: texte}, {a: url}, options_en_images)."""
    if isinstance(options, dict):
        return options, {}, False
    texts, sources, images = {}, {}, False
    for opt in options or []:
        label = str(opt.get("label", "")).lower()
        if not label:
            continue
        if opt.get("image_file") or opt.get("image_description"):
            images = True
        texts[label] = opt.get("text") or opt.get("image_description") or ""
        if opt.get("url"):
            sources[label] = opt["url"]
    return texts, sources, images


def _plays(instructions: str) -> int | None:
    text = (instructions or "").lower()
    if "zweimal" in text:
        return 2
    if "einmal" in text:
        return 1
    return None


def _words(instructions: str) -> int | None:
    m = re.search(r"(?:circa|ca\.?)\s*(\d+)\s*Wörter", instructions or "", re.IGNORECASE)
    return int(m.group(1)) if m else None


def _is_horen(slug: str) -> bool:
    return any(p in slug for p in ("hor", "hoer", "hör"))


def _teil(teil: dict, module_slug: str) -> dict:
    fmt = teil.get("format_type", "")
    t = deepcopy(teil)
    horen = _is_horen(module_slug)

    plays = _plays(t.get("instructions", ""))
    if horen and plays and not (t.get("max_plays") or t.get("ecoutes")):
        t["max_plays"] = plays

    if fmt == "true_false":
        t["format_type"] = "richtig_falsch"
        if t.get("text"):
            # Hören : le texte est la transcription (jamais affichée) ; Lesen : le support
            t["transcription" if horen else "stimulus_text"] = t.pop("text")

    elif fmt in ("mc_text", "mc_image", "matching_2options"):
        t["format_type"] = "qcm_abc"
        transcripts = []
        for q in t.get("questions", []):
            texts, sources, images = _options(q.get("options"))
            q["stem"] = q.get("stem") or q.get("question") or q.get("scenario") or ""
            q["options"] = texts
            if sources:
                q["option_sources"] = sources
            if images:
                q["image_options"] = True
            if q.get("transcript"):
                transcripts.append(f"{q['number']}. {q.pop('transcript')}")
        if transcripts and "transcription" not in t:
            t["transcription"] = "\n\n".join(transcripts)

    elif fmt == "form_fill":
        # Formulaire (A1 Schreiben 1) : un champ = une réponse courte
        t["format_type"] = "kurzantwort"
        if t.get("prompt_text"):
            t["stimulus_text"] = t.pop("prompt_text")
        t["questions"] = [
            {
                "number": f["number"],
                "prompt": f.get("label", ""),
                "accepted_answers": [f.get("correct_value", "")],
                "keywords": [_keyword(f.get("correct_value", ""))],
                "required_parts": 2 if re.search(r"\bund\b", f.get("correct_value", "")) else 1,
                "correction": "auto_puis_enseignant",
            }
            for f in t.pop("fields", [])
        ]

    elif fmt == "free_text":
        if t.get("prompt") and not t.get("scenario"):
            t["scenario"] = t.pop("prompt")
        if t.get("content_points") and not t.get("prompts"):
            t["prompts"] = t.pop("content_points")
        if not t.get("word_count_target"):
            t["word_count_target"] = _words(t.get("instructions", "")) or 30
        # Lettre à « Frau / Herr ... » : registre formel (Sie)
        if not t.get("register") and re.search(r"\b(Frau|Herrn?)\s+[A-ZÄÖÜ]", t.get("scenario", "")):
            t["register"] = "formell"

    elif fmt == "sprechen_group_intro":
        t["format_type"] = "oral_kennenlernen"
        t["topics"] = t.pop("prompts", [])

    elif fmt in ("sprechen_group_word_card", "sprechen_group_image_card"):
        # Cartes (mots ou images) : les images arrivent ensuite par l'import d'images
        t["format_type"] = "oral_interaction"
        cards = t.pop("cards", [])
        t["prompts"] = [c if isinstance(c, str) else c.get("description", "") for c in cards]
        t["karten_typ"] = "bild" if fmt.endswith("image_card") else "wort"

    return t


def normalize_exam_json(data: dict) -> dict:
    """Réécrit un sujet au schéma simplifié ; renvoie le JSON tel quel sinon."""
    out = deepcopy(data)
    level = str(out.get("cefr_code") or out.get("level") or "").upper()
    out.setdefault("cefr_code", level or None)
    for m in out.get("modules", []):
        slug = str(m.get("slug", "")).lower()
        m.setdefault("name", MODULE_NAMES.get(slug, slug.capitalize()))
        if "time_limit_minutes" not in m and slug in DEFAULT_MINUTES.get(level, {}):
            m["time_limit_minutes"] = DEFAULT_MINUTES[level][slug]
        m["teile"] = [_teil(t, slug) for t in m.get("teile", [])]
    return out