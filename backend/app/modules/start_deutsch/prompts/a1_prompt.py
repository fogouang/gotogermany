"""
app/modules/start_deutsch/prompts/a1_prompt.py

Prompt de correction pour Start Deutsch A1 — Schreiben Teil 2 (email/SMS
courte, ~30 mots, 3 points de contenu imposés). Teil 1 (formulaire à trous)
n'est jamais envoyé ici — il est corrigé automatiquement côté service
(format_type = form_fill), pas par l'IA.

Barème OFFICIEL A1 confirmé (Bewertungskriterien Schreiben, Goethe/telc
Start Deutsch 1) :
  Par point de contenu (généralement 3 points de contenu par tâche) :
    3 points   : accompli et compréhensible
    1,5 point  : partiellement accompli (lacunes linguistiques/de contenu)
    0 point    : non accompli et/ou incompréhensible
  + 1 point bonus "Kommunikative Gestaltung" (forme adaptée au type de texte,
    ex. une vraie formule de salutation) :
    1 point    : adapté au type de texte
    0,5 point  : formules atypiques ou manquantes
    0 point    : aucune formule adaptée au type de texte

Pour 3 points de contenu : max = 3×3 + 1 = 10 points (confirmé par les
Leistungsbeispiele officiels : "Beispiel 1 — 10 Punkte").

⚠️ Contrairement à telc B1, on ne fait PAS confiance à un overall_score
librement calculé par l'IA : le score final est recalculé côté service à
partir des points par critère renvoyés ici, pour garantir la cohérence avec
teil.max_score stocké en DB (le nombre de points de contenu peut varier
d'une tâche à l'autre).
"""


def get_start_deutsch_a1_prompt(
    text: str,
    task_instruction: str,
    content_points: list[str],
) -> str:
    """
    Construire le prompt de correction Start Deutsch A1 — Schreiben.

    Args:
        text: Texte du candidat
        task_instruction: Consigne complète de la tâche
        content_points: Points de contenu imposés (ex. ["Warum schreiben Sie?",
            "Sagen Sie: später kommen.", "Fragen Sie: helfen?"])

    Returns:
        Prompt complet prêt à envoyer au modèle IA.
    """

    points_str = "\n".join(f"{i}. {p}" for i, p in enumerate(content_points, start=1))
    n_points = len(content_points)
    max_content_score = n_points * 3
    max_score = max_content_score + 1

    return f"""Du bist ein offizieller Prüfer für das Goethe-Zertifikat A1 / telc Deutsch A1 (Start Deutsch 1), Schreiben.
Der Kandidat befindet sich auf dem elementarsten Sprachniveau (A1) — bewerte entsprechend nachsichtig bei Grammatik/Rechtschreibung, solange die Nachricht verständlich bleibt.

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN (offizielles Raster — {n_points} Inhaltspunkte)
═══════════════════════════════════════════════════════

Für JEDEN der {n_points} Inhaltspunkte einzeln bewerten:
   3 Punkte    : Punkt vollständig behandelt und verständlich
   1,5 Punkte  : Punkt nur teilweise behandelt (sprachliche oder inhaltliche Mängel)
   0 Punkte    : Punkt nicht behandelt und/oder unverständlich

Zusätzlich EIN Bonus-Kriterium "Kommunikative Gestaltung" (Textsorte-adäquate Form, z. B. Anrede/Gruß bei einer E-Mail):
   1 Punkt     : der Textsorte angemessen
   0,5 Punkte  : untypische oder fehlende Wendungen (z. B. keine Anrede)
   0 Punkte    : keine textsortenspezifischen Wendungen

Zu behandelnde Inhaltspunkte:
{points_str}

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT — NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Feedback-Felder: maximal 15 Wörter, auf Deutsch, einfache Sprache (A1-Niveau).
═══════════════════════════════════════════════════════

{{
  "corrected_text": "Die vollständig korrigierte Version des Textes (kurz, A1-Niveau beibehalten)",
  "content_point_scores": [{", ".join(["3" for _ in range(n_points)]) if n_points else ""}],
  "content_point_feedback": [{", ".join(['"max 15 Wörter"' for _ in range(n_points)]) if n_points else ""}],
  "communicative_score": 1,
  "communicative_feedback": "max 15 Wörter",
  "appreciation": "max 15 Wörter, ermutigend, einfache Sprache",
  "corrections": [
    {{"error": "identifizierter Fehler", "correction": "Korrektur", "explanation": "max 10 Wörter"}}
  ],
  "suggestions": ["max 12 Wörter, konkret und einfach"]
}}

WICHTIG: "content_point_scores" muss genau {n_points} Werte enthalten (einer pro Inhaltspunkt, je 0, 1.5 oder 3), in derselben Reihenfolge wie oben aufgelistet. "communicative_score" ist 0, 0.5 oder 1.
Maximal mögliche Punktzahl dieser Aufgabe: {max_score} ({max_content_score} Inhalt + 1 Kommunikation).
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN
# ═══════════════════════════════════════════════════════

Aufgabenstellung: {task_instruction}
Text des Kandidaten:
{text}"""