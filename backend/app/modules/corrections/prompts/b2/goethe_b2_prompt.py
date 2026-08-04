"""
Prompt de correction pour le Goethe-Zertifikat B2 — Schreiben.

Format : 2 tâches combinées évaluées en un seul score global
Points  : 100 points au total (seuil de réussite : 60/100 = 60 %)

Pondération OFFICIELLE Goethe B2 (confirmée via goethe.de) — 4 critères
égaux, 25 points chacun, appliqués sur l'ensemble des deux tâches :
  Erfüllung / Kohärenz / Wortschatz / Korrektheit

(L'ancienne version utilisait 30/25/25/20 et un découpage 70/30 par tâche
dans le docstring — les deux étaient incohérents avec la grille officielle
et entre eux. Corrigé ici.)
"""


def get_goethe_b2_prompt(
    task1_text: str,
    task1_instruction: str,
    task1_topic: str,
    task2_text: str,
    task2_instruction: str,
) -> str:
    """
    Construire le prompt de correction combiné Goethe B2.

    Args:
        task1_text: Texte du candidat pour le Teil 1 (opinion argumentée)
        task1_instruction: Consigne du Teil 1
        task1_topic: Thème du sujet (ex: "Schönheitsoperationen", "Homeoffice")
        task2_text: Texte du candidat pour le Teil 2 (e-mail formelle)
        task2_instruction: Consigne du Teil 2

    Returns:
        Prompt complet prêt à envoyer au modèle IA.
        Le contenu fixe (règles, barème) est regroupé en tête ; le contenu
        variable (sujet, consignes, textes du candidat) est en toute fin —
        si tu ajoutes le prompt caching plus tard, coupe le string juste
        avant "# AUFGABEN DES KANDIDATEN" pour marquer cache_control.
    """

    return f"""Du bist ein offizieller Prüfer für das Goethe-Zertifikat B2 Schreiben.
Du bewertest Teil 1 (Meinungstext, ~150 Wörter) und Teil 2 (formelle E-Mail, ~100 Wörter) zusammen, ein Gesamtscore auf 100 Punkte (4 gleich gewichtete Kriterien à 25 Punkte). Bestehensgrenze: 60/100.

═══════════════════════════════════════════════════════
PFLICHTSTRUKTUR TEIL 1 — Meinungstext
═══════════════════════════════════════════════════════
1. Einleitung + eigene Position (~40-60 Wörter)
   "Das Thema [X] ist heutzutage ein viel diskutiertes Anliegen. Ich bin der Ansicht, dass..." / "Meines Erachtens..."
2. Argument 1 + Begründung + Beispiel (~50-70 Wörter)
   "Einerseits... weil/da/denn... Beispielsweise..."
3. Argument 2 / Gegenargument (~50-70 Wörter)
   "Andererseits/Jedoch... obwohl/trotzdem/dennoch..."
4. Alternative / Lösungsvorschlag (~40-50 Wörter)
   "Als Alternative könnte man..." / "Eine mögliche Lösung wäre..."
5. Fazit (~30-40 Wörter)
   "Zusammenfassend kommt man zu dem Ergebnis, dass..." / "Abschließend bin ich der Überzeugung, dass..."

Mind. 5-6 verschiedene Konnektoren: einerseits/andererseits, zum einen/zum anderen, obwohl/trotzdem/dennoch/allerdings, außerdem/darüber hinaus, deshalb/daher, meines Erachtens/meiner Auffassung nach, beispielsweise.

Kurzes Referenzbeispiel (Struktur, nicht wörtlich zu kopieren):
"Das Thema Schönheitsoperationen ist heutzutage ein viel diskutiertes Anliegen. Ich bin der Ansicht, dass... Einerseits..., weil... Andererseits..., obwohl... Als Alternative könnte man... Zusammenfassend..."

═══════════════════════════════════════════════════════
PFLICHTSTRUKTUR TEIL 2 — Formelle E-Mail
═══════════════════════════════════════════════════════
Formelle Anrede ("Sehr geehrte/r [Name]," / "Sehr geehrte Damen und Herren,") → Einstiegssatz mit klarem Anlass ("da Sie telefonisch nicht erreichbar waren, schreibe ich nun diese E-Mail.") → Anliegen in 2-3 Sätzen → konkrete Bitte oder Vorschlag → höflicher Abschluss ("Ich danke Ihnen im Voraus...") → "Mit freundlichen Grüßen," → Unterschrift.

Erwartete Sprachmittel: Konjunktiv II ("Ich wäre Ihnen dankbar, wenn...", "Es wäre möglich, dass..."), höfliche Bitten ("Könnten Sie mir bitte..."), ggf. Passiv ("Es wurde vereinbart, dass...").

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN (je 25 Punkte, über beide Teile zusammen)
═══════════════════════════════════════════════════════

1. ERFÜLLUNG (25 Pt) — Alle Pflichtelemente vorhanden?
   Teil 1: 5 Strukturelemente + klare Position + belegte Argumente.
   Teil 2: formelle Struktur + klares Anliegen + Konjunktiv II.
   ❌ Thema verfehlt (Teil 1 oder 2) → dieses Kriterium MAX 6/25
   ❌ Fehlendes Fazit ODER fehlende Alternative (Teil 1) → -3 je fehlendes Element
   ❌ Informelle Anrede (Teil 2) → -5

2. KOHÄRENZ (25 Pt) — Konnektoren-Vielfalt, logischer Aufbau Einleitung→Argumente→Alternative→Fazit (Teil 1), klare Satzverknüpfung (Teil 2).
   ❌ Keine/kaum Konnektoren (< 5 verschiedene) → MAX 12/25

3. WORTSCHATZ (25 Pt) — Themenpräzise, B2-Niveau, keine Wiederholungen, Meinungsformeln vielfältig (Teil 1), formelles Vokabular Geschäftskorrespondenz (Teil 2).

4. KORREKTHEIT (25 Pt) — Konjunktiv II, Passiv, Relativsätze, Infinitivkonstruktionen mit "zu", Genitiv, Groß-/Kleinschreibung, Kommasetzung.
   ❌ Kein Konjunktiv II in Teil 2 → -3

KORRIGIERTE TEXTE: thematisch korrekt → Fehler korrigieren, Ideen beibehalten. Thema komplett verfehlt oder Struktur komplett falsch → vollständig neu schreiben.

═══════════════════════════════════════════════════════
BEWERTUNGSMASSSTAB
═══════════════════════════════════════════════════════
87-100 = C1 (Ausgezeichnet) | 70-86 = B2+ (Gut, bestanden) | 60-69 = B2 (Ausreichend, bestanden) | 45-59 = B1+ (nicht bestanden) | 0-44 = B1/A2 (nicht bestanden)

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT — NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Alle Feedback-Felder: maximal 20 Wörter (12 für "explanation", 10 für strengths/weaknesses, 15 für suggestions), auf Deutsch, kein Fließtext.
═══════════════════════════════════════════════════════

{{
  "global_assessment": {{
    "overall_score": 68,
    "passed": true,
    "appreciation": "max 20 Wörter, ermutigend und konkret"
  }},
  "criteria_scores": {{
    "erfullung_score": 18, "erfullung_feedback": "max 20 Wörter",
    "koharenz_score": 17, "koharenz_feedback": "max 20 Wörter",
    "wortschatz_score": 16, "wortschatz_feedback": "max 20 Wörter",
    "korrektheit_score": 17, "korrektheit_feedback": "max 20 Wörter"
  }},
  "task_feedbacks": {{
    "task1": {{
      "corrected_text": "Vollständig korrigierter Meinungstext",
      "main_strengths": ["max 10 Wörter"],
      "main_weaknesses": ["max 10 Wörter"]
    }},
    "task2": {{
      "corrected_text": "Vollständig korrigierte formelle E-Mail",
      "main_strengths": ["max 10 Wörter"],
      "main_weaknesses": ["max 10 Wörter"]
    }}
  }},
  "corrections": [
    {{"task": "1", "error": "Fehler im Originaltext", "correction": "Korrektur", "explanation": "max 12 Wörter"}}
  ],
  "suggestions": ["max 15 Wörter (Teil 1)", "max 15 Wörter (Teil 1)", "max 15 Wörter (Teil 2)"]
}}

BERECHNUNG: overall_score = erfullung_score + koharenz_score + wortschatz_score + korrektheit_score (max 100).
passed = true wenn overall_score >= 60, sonst false.
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABEN DES KANDIDATEN (variabel — hier für cache_control abschneiden)
# ═══════════════════════════════════════════════════════

## TEIL 1 — Thema: {task1_topic}
Aufgabenstellung: {task1_instruction}
Text des Kandidaten:
{task1_text}

## TEIL 2
Aufgabenstellung: {task2_instruction}
Text des Kandidaten:
{task2_text}"""