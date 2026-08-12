"""
app/modules/start_deutsch/prompts/a2_prompt.py

Prompt de correction pour Start Deutsch A2 — Schreiben Teil 1 (SMS, 20-30
mots) ou Teil 2 (email, 30-40 mots), 3 points de contenu imposés chacun.

Barème OFFICIEL A2 confirmé (Bewertungskriterien Schreiben, Goethe-Zertifikat
A2) — grille A-E sur 2 axes, contrairement au A1 qui est purement numérique :

  Axe "Aufgabenerfüllung" (Sprachfunktion + Register) :
    A : alle 3 Sprachfunktionen inhaltlich und umfänglich angemessen ;
        situations- und partneradäquates Register
    B : 2 Sprachfunktionen angemessen ODER 1 angemessen + 2 teilweise ;
        weitgehend situations-/partneradäquat
    C : 1 Sprachfunktion angemessen UND 1 teilweise ODER alle teilweise ;
        ansatzweise situations-/partneradäquat
    D : 1 Sprachfunktion angemessen oder teilweise ; nicht mehr situations-/
        partneradäquat
    E : Textumfang < 50% der geforderten Wortzahl ODER Thema verfehlt
        → bei E ist die GESAMTE Aufgabe automatisch 0 Punkte

  Axe "Sprache" (Spektrum/Kohärenz/Wortschatz/Strukturen) :
    A : angemessen und differenziert ; vereinzelte Fehlgriffe, Verständnis
        nicht beeinträchtigt
    B : überwiegend angemessen ; mehrere Fehlgriffe, Verständnis nicht
        beeinträchtigt
    C : teilweise angemessen ; mehrere Fehlgriffe, Verständnis teilweise
        beeinträchtigt
    D : kaum angemessen ; mehrere Fehlgriffe, Verständnis erheblich
        beeinträchtigt
    E : Text durchgängig unangemessen

⚠️ Comme pour le A1, le service recalcule le score final à partir des
grades A-E renvoyés ici (conversion grade→points côté service, en fonction
de teil.max_score réellement stocké en DB) plutôt que de faire confiance à
un score libre inventé par l'IA.
"""


def get_start_deutsch_a2_prompt(
    text: str,
    task_instruction: str,
    content_points: list[str],
    task_type: str,  # "sms" ou "email"
) -> str:
    """
    Construire le prompt de correction Start Deutsch A2 — Schreiben.

    Args:
        text: Texte du candidat
        task_instruction: Consigne complète de la tâche
        content_points: Points de contenu imposés (3, typiquement)
        task_type: "sms" (Teil 1, 20-30 mots) ou "email" (Teil 2, 30-40 mots)
    """

    points_str = "\n".join(f"{i}. {p}" for i, p in enumerate(content_points, start=1))
    word_range = "20-30 Wörter" if task_type == "sms" else "30-40 Wörter"
    text_form = "eine kurze SMS/Nachricht" if task_type == "sms" else "eine E-Mail"

    return f"""Du bist ein offizieller Prüfer für das Goethe-Zertifikat A2, Schreiben.
Der Kandidat schreibt {text_form} ({word_range} erwartet). Bewerte nach dem offiziellen A2-Raster, zwei Kriterien, je als Note A/B/C/D/E.

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN (offizielles Goethe-Zertifikat-A2-Raster)
═══════════════════════════════════════════════════════

Zu behandelnde Inhaltspunkte (= die "3 Sprachfunktionen" für Kriterium 1):
{points_str}

KRITERIUM 1 — AUFGABENERFÜLLUNG (Sprachfunktion + Register)
   A : alle 3 Punkte inhaltlich und umfänglich angemessen behandelt; Register (Anrede/Ton) passend zur Situation und zum Empfänger
   B : 2 Punkte angemessen ODER 1 angemessen + 2 teilweise; weitgehend passendes Register
   C : 1 Punkt angemessen UND 1 teilweise ODER alle nur teilweise; Register ansatzweise passend
   D : höchstens 1 Punkt angemessen oder teilweise behandelt; Register nicht mehr passend
   E : Text hat weniger als {"10-15" if task_type == "sms" else "15-20"} Wörter (unter 50% der geforderten Wortzahl) ODER verfehlt komplett das Thema — WENN E: gesamte Aufgabe = 0 Punkte

KRITERIUM 2 — SPRACHE (Wortschatz, Strukturen, Kohärenz)
   A : angemessen und differenziert; vereinzelte Fehler beeinträchtigen das Verständnis nicht
   B : überwiegend angemessen; mehrere Fehler, Verständnis nicht beeinträchtigt
   C : teilweise angemessen; mehrere Fehler, Verständnis teilweise beeinträchtigt
   D : kaum angemessen; mehrere Fehler, Verständnis erheblich beeinträchtigt
   E : Text durchgängig sprachlich unangemessen

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT — NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Feedback-Felder: maximal 15 Wörter, auf Deutsch, einfache Sprache (A2-Niveau).
═══════════════════════════════════════════════════════

{{
  "corrected_text": "Die vollständig korrigierte Version des Textes (A2-Niveau beibehalten)",
  "aufgabenerfuellung_grade": "B",
  "aufgabenerfuellung_feedback": "max 15 Wörter",
  "sprache_grade": "A",
  "sprache_feedback": "max 15 Wörter",
  "appreciation": "max 15 Wörter, ermutigend, einfache Sprache",
  "corrections": [
    {{"error": "identifizierter Fehler", "correction": "Korrektur", "explanation": "max 10 Wörter"}}
  ],
  "suggestions": ["max 12 Wörter, konkret und einfach"]
}}

WICHTIG: "aufgabenerfuellung_grade" und "sprache_grade" müssen genau einer der Werte "A", "B", "C", "D", "E" sein (Großbuchstabe, kein anderer Text).
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN
# ═══════════════════════════════════════════════════════

Aufgabenstellung: {task_instruction}
Text des Kandidaten:
{text}"""