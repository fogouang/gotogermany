"""
app/modules/corrections/prompts/ecl_prompt.py

ESQUISSE À VALIDER : correction ECL Schreiben (B1 et B2).

Format officiel (eclexam.eu, "Exam Format") :
  - 2 textes, chacun basé sur 4 Leitpunkte
  - B1 : ~100 + ~100 mots, 40 min | B2 : ~150 + ~150 mots, 60 min
  - Types : Kommentar (Forum/Website), Bericht, E-Mail/Nachricht (B1), Aufsatz (B2)
  - Schreiben : 25 points maximum
Critères officiels (eclexam.eu, "Criteria for Assessing Writing"), 0 à 5 chacun :
  Formale Korrektheit, Schriftliche Korrektheit, Wortschatz, Stil,
  Kommunikative Wirksamkeit. Kommunikative Wirksamkeit = 0 -> tâche = 0.

HYPOTHÈSE (à confirmer) : chaque texte noté sur 25 (5 x 5), note Schreiben =
moyenne des deux textes (max 25). Module réussi à 40 % = 10/25 (règle 2026).
"""

WORD_TARGET = {"b1": 100, "b2": 150}


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {b}" for b in items) if items else "- (keine Leitpunkte angegeben)"


def get_ecl_prompt(
    level: str,
    task1_text: str,
    task1_instruction: str,
    task1_bullets: list[str],
    task2_text: str,
    task2_instruction: str,
    task2_bullets: list[str],
) -> str:
    level = level.lower()
    niveau = level.upper()
    target = WORD_TARGET.get(level, 150)

    return f"""Du bist ein erfahrener Prüfer für die ECL-Prüfung Deutsch, Niveau {niveau}, Teil Schreiben.
Der Kandidat hat 2 Texte geschrieben (je ca. {target} Wörter), jeder zu 4 vorgegebenen Leitpunkten.

═══════════════════════════════════════════════════════
BEWERTUNG PRO TEXT (offizielle ECL-Kriterien, je 0 bis 5 Punkte)
═══════════════════════════════════════════════════════
1. FORMALE KORREKTHEIT : Morphologie und Syntax.
2. SCHRIFTLICHE KORREKTHEIT : Absätze, Zeichensetzung, Rechtschreibung.
3. WORTSCHATZ : Umfang und angemessener Einsatz, Niveau {niveau}.
4. STIL : Register, Textsorte, pragmatische und soziolinguistische Angemessenheit.
5. KOMMUNIKATIVE WIRKSAMKEIT : Aufgabe erfüllt, alle 4 Leitpunkte behandelt, Textsorte eingehalten.

Bänder : 5, 3, 1 und 0 beschrieben ; 4 und 2 sind Zwischenstufen.
❗ Kommunikative Wirksamkeit = 0 (Thema verfehlt) -> der ganze Text erhält 0 Punkte.
❗ Pro fehlendem Leitpunkt Kommunikative Wirksamkeit um mindestens 1 senken.
❗ Deutlich zu kurzer Text (< 70 % von {target} Wörtern) -> Kommunikative Wirksamkeit max. 2.

KORRIGIERTE TEXTE : Fehler korrigieren, Ideen und Aufbau des Kandidaten beibehalten.

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT : NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Feedback auf Deutsch, kurz (max 15 Wörter pro Eintrag).
═══════════════════════════════════════════════════════
{{
  "global_assessment": {{
    "overall_score": 17,
    "passed": true,
    "appreciation": "max 20 Wörter, ermutigend und konkret"
  }},
  "task1": {{
    "formale_korrektheit": 4,
    "schriftliche_korrektheit": 3,
    "wortschatz": 4,
    "stil": 3,
    "kommunikative_wirksamkeit": 4,
    "task_score": 18,
    "leitpunkte_behandelt": 4,
    "corrected_text": "Vollständig korrigierter Text 1",
    "main_strengths": ["max 10 Wörter"],
    "main_weaknesses": ["max 10 Wörter"]
  }},
  "task2": {{
    "formale_korrektheit": 3,
    "schriftliche_korrektheit": 3,
    "wortschatz": 3,
    "stil": 3,
    "kommunikative_wirksamkeit": 4,
    "task_score": 16,
    "leitpunkte_behandelt": 4,
    "corrected_text": "Vollständig korrigierter Text 2",
    "main_strengths": ["max 10 Wörter"],
    "main_weaknesses": ["max 10 Wörter"]
  }},
  "corrections": [
    {{"task": "1", "error": "Fehler", "correction": "Korrektur", "explanation": "max 12 Wörter"}}
  ],
  "suggestions": ["max 15 Wörter", "max 15 Wörter"]
}}

BERECHNUNG : task_score = Summe der 5 Kriterien (max 25), 0 wenn kommunikative_wirksamkeit = 0.
overall_score = (task1.task_score + task2.task_score) / 2, auf ganze Zahl gerundet (max 25).
passed = true wenn overall_score >= 10.
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABEN DES KANDIDATEN
# ═══════════════════════════════════════════════════════

## TEXT 1
Aufgabenstellung: {task1_instruction}
Leitpunkte:
{_bullets(task1_bullets)}
Text des Kandidaten:
{task1_text}

## TEXT 2
Aufgabenstellung: {task2_instruction}
Leitpunkte:
{_bullets(task2_bullets)}
Text des Kandidaten:
{task2_text}"""