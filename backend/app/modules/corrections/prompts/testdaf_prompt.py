"""
app/modules/corrections/prompts/testdaf_prompt.py

ESQUISSE À VALIDER : correction TestDaF (digital) Schreiben.

Format officiel (Der digitale TestDaF, Sprachenzentrum Uni Passau) :
  - 2 tâches, ~60 min
  - Aufgabe 1 : argumentativer Text (isoliert) : offene Frage + ggf. 1-2 Aussagen ;
    Position beziehen, Argumente abwägen, Beispiele/Begründungen, eigene Meinung.
  - Aufgabe 2 : Zusammenfassung (integriert) : Lesetext + Grafik/Tabelle ;
    für eine Fragestellung relevante Informationen aus beiden Quellen zusammenfassen.
  - Rohpunkte 0-20, umgerechnet in TDN 3 / 4 / 5. Pas de "réussi/échoué" global.

HYPOTHÈSE (raster détaillé non publié) : 10 points par tâche
  Aufgabenbewältigung 4 | Textaufbau 3 | Sprachliche Realisierung 3
  TDN estimé : >= 16 TDN 5 | >= 13 TDN 4 | >= 9 TDN 3 | sinon unter TDN 3
TODO : nombres de mots officiels non publiés (à compléter).

Sortie : corrected_text = correction minimale du texte du candidat ;
model_text = Mustertext séparé (voir common_rules.CORRECTION_RULES).
"""

from app.modules.corrections.prompts.common_rules import CORRECTION_RULES


def get_testdaf_prompt(
    task1_text: str,
    task1_instruction: str,
    task2_text: str,
    task2_instruction: str,
    task2_source: str,
) -> str:
    return f"""Du bist ein erfahrener Bewerter für den digitalen TestDaF, Prüfungsteil Schreiben (Niveau B2 bis C1, akademischer Kontext).
Der Kandidat hat 2 Aufgaben bearbeitet. Bewerte jede Aufgabe auf 10 Punkte (Gesamt max. 20).

═══════════════════════════════════════════════════════
AUFGABE 1 : Argumentativer Text
═══════════════════════════════════════════════════════
Erwartet : klare Position zur Frage, Pro- und Contra-Argumente abgewogen, Begründungen
und Beispiele, eigene Meinung im Schluss, akademisch-sachlicher Stil.

═══════════════════════════════════════════════════════
AUFGABE 2 : Zusammenfassung (Lesetext + Grafik)
═══════════════════════════════════════════════════════
Erwartet : nur die für die Fragestellung relevanten Informationen aus BEIDEN Quellen,
in eigenen Worten, korrekt wiedergegeben (Zahlen/Trends der Grafik), Redewiedergabe
(laut, dem Text zufolge, Konjunktiv I), keine eigene Meinung.
❗ Nur eine Quelle verwendet -> Aufgabenbewältigung max. 2.
❗ Lange wörtliche Übernahmen aus dem Lesetext -> Sprachliche Realisierung max. 1.

═══════════════════════════════════════════════════════
KRITERIEN PRO AUFGABE
═══════════════════════════════════════════════════════
- inhalt_score (0-4) : Aufgabenbewältigung, Vollständigkeit, Relevanz.
- aufbau_score (0-3) : Gliederung, Kohärenz, Konnektoren, Leserführung.
- sprache_score (0-3) : Wortschatz (akademisch), Strukturen, Korrektheit.
Thema verfehlt -> Aufgabe 0 Punkte.

GESCHÄTZTES NIVEAU (Gesamtpunkte /20) : >= 16 TDN 5 | >= 13 TDN 4 | >= 9 TDN 3 | sonst unter TDN 3.

{CORRECTION_RULES}
UMRECHNUNG sprache_score (Fehlerdichte je Aufgabe): sehr gut 3 | gut 2 | ausreichend 1 | schwach 0.

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT : NUR gültiges JSON, kein Markdown.
Feedback auf Deutsch, kurz (max 15 Wörter pro Eintrag).
Reihenfolge der Felder einhalten: zuerst "corrections", dann die Bewertung, dann die Texte.
═══════════════════════════════════════════════════════
{{
  "corrections": [
    {{"task": "1", "error": "exakte Stelle aus dem Originaltext", "correction": "Korrektur", "explanation": "max 12 Wörter"}}
  ],
  "global_assessment": {{
    "overall_score": 14,
    "tdn_estimate": "TDN 4",
    "appreciation": "max 20 Wörter"
  }},
  "task1": {{
    "inhalt_score": 3, "aufbau_score": 2, "sprache_score": 2, "task_score": 7,"thema_verfehlt": false,
    "corrected_text": "Originaltext 1, nur Fehler korrigiert",
    "model_text": "Mustertext argumentativer Text",
    "main_strengths": ["max 10 Wörter"], "main_weaknesses": ["max 10 Wörter"]
  }},
  "task2": {{
    "inhalt_score": 3, "aufbau_score": 2, "sprache_score": 2, "task_score": 7,"thema_verfehlt": false,
    "corrected_text": "Originalzusammenfassung, nur Fehler korrigiert",
    "model_text": "Mustertext Zusammenfassung aus beiden Quellen",
    "main_strengths": ["max 10 Wörter"], "main_weaknesses": ["max 10 Wörter"]
  }},
  "suggestions": ["max 15 Wörter", "max 15 Wörter"]
}}

BERECHNUNG : task_score = inhalt + aufbau + sprache (max 10). overall_score = task1 + task2 (max 20).
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABEN DES KANDIDATEN
# ═══════════════════════════════════════════════════════

## AUFGABE 1 : Argumentativer Text
Aufgabenstellung: {task1_instruction}
Text des Kandidaten:
{task1_text}

## AUFGABE 2 : Zusammenfassung
Aufgabenstellung: {task2_instruction}
Quellenmaterial (Lesetext + Grafikbeschreibung):
{task2_source or "(nicht verfügbar)"}
Text des Kandidaten:
{task2_text}"""