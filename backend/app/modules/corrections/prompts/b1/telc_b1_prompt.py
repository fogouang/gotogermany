"""
Prompt de correction pour le Telc Deutsch B1 : Schreiben.

Format OFFICIEL (Übungstest telc Deutsch B1 / Zertifikat Deutsch) :
  - 1 seule tâche (pas de choix A/B), 30 minutes
  - réponse à un e-mail : e-mail INFORMELLE ou HALBFORMELLE selon la situation
  - 4 Leitpunkte, tous à traiter
  - pas de nombre de mots officiel (120-150 mots = repère de la plateforme)

Barème OFFICIEL :
  3 critères, chacun noté A / B / C / D = 5 / 3 / 1 / 0,
  somme des 3 notes x 3 = max 45. Chaque critère vaut donc
  15 / 9 / 3 / 0 points, rien entre les deux.
    I.   Aufgabenbewältigung       (Leitpunkte : A = 4, B = 3, C = 2, D = 1 ou 0)
    II.  Kommunikative Gestaltung  (fonctions langagières, logique, connecteurs, registre)
    III. Formale Richtigkeit       (grammaire, orthographe, ponctuation)
  Thema verfehlt : D partout, soit 0/45.

Les clés JSON (leitpunkte_score, gestaltung_score, richtigkeit_score...)
restent inchangées : le parsing côté backend n'est pas touché.

Sortie : corrected_text = correction minimale du texte du candidat ;
model_text = Mustertext séparé (voir common_rules.CORRECTION_RULES).
"""

from app.modules.corrections.prompts.common_rules import CORRECTION_RULES


def get_telc_b1_prompt(
    text: str,
    task_instruction: str,
    bullet_points: list[str],
) -> str:
    """
    Construire le prompt de correction Telc B1.

    Args:
        text: Texte du candidat
        task_instruction: Consigne complète de la tâche
        bullet_points: Liste des 4 Leitpunkte

    Returns:
        Prompt complet prêt à envoyer au modèle IA.
        Contenu fixe en tête, contenu variable en fin de string : coupe
        juste avant "# AUFGABE DES KANDIDATEN" si tu ajoutes le prompt
        caching plus tard.
    """

    bullet_points_str = "\n".join(f"- {point}" for point in bullet_points)

    return f"""Du bist ein offizieller Prüfer für telc Deutsch B1 (Zertifikat Deutsch), Schriftlicher Ausdruck.
Du bewertest nach den 3 offiziellen telc-Kriterien mit den Stufen A/B/C/D.

═══════════════════════════════════════════════════════
AUFGABENFORMAT (offiziell)
═══════════════════════════════════════════════════════
Eine einzige Aufgabe: Antwort auf eine E-Mail, INFORMELL oder HALBFORMELL je nach Situation
(Freundin/Freund: "Liebe/r ...", du-Form; Bekannte, Kollegin, Vermieter usw.: "Liebe Frau ... / Sehr geehrter Herr ...", Sie-Form).
Das richtige Register ergibt sich aus der Aufgabenstellung: prüfe, ob der Kandidat es trifft und durchhält.
Erwartete Textmerkmale: passende Anrede, Einleitung, Hauptteil mit ALLEN 4 Leitpunkten, Schluss, passende Grußformel, Name.
Länge: keine offizielle Wortzahl; 120-150 Wörter sind ein Richtwert. Zu kurze Texte verlieren Punkte nur, wenn Leitpunkte dadurch nicht angemessen behandelt sind.

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN (offizielles telc-Raster)
═══════════════════════════════════════════════════════
Jedes Kriterium bekommt GENAU EINE Stufe: A = 15, B = 9, C = 3, D = 0 Punkte.
Keine Zwischenwerte (also nie 12, 11, 7 ...).

I. AUFGABENBEWÄLTIGUNG (leitpunkte_score)
   Wie viele der 4 Leitpunkte sind inhaltlich angemessen behandelt?
   A (15) = alle 4 | B (9) = 3 | C (3) = 2 | D (0) = 1 oder keiner.
   Ein nur erwähnter, nicht ausgeführter Leitpunkt zählt nicht als angemessen behandelt.

II. KOMMUNIKATIVE GESTALTUNG (gestaltung_score)
   Bandbreite der Sprachfunktionen und des Wortschatzes, Textlogik, Konnektoren, Register.
   A (15) = breites Spektrum an Sprachfunktionen und Verknüpfungen, Register durchgehend passend: oberes B1.
   B (9)  = B1-Niveau, ausreichende Bandbreite; Fehler eher bei komplexeren Inhalten.
   C (3)  = eine Stufe unter B1: elementare Sprachfunktionen, nur einfache Konnektoren (und, aber, weil).
   D (0)  = zwei oder mehr Stufen unter B1: nur sehr elementare Ausdrücke.
   Falsches oder wechselndes Register (du/Sie gemischt, formell statt informell oder umgekehrt) oder fehlende Anrede/Grußformel: höchstens B.

III. FORMALE RICHTIGKEIT (richtigkeit_score)
   Grammatik, Rechtschreibung, Zeichensetzung. Die Verständlichkeit hat Vorrang.
   A (15) = insgesamt gute Beherrschung, nur gelegentliche systematische Fehler.
   B (9)  = ausreichende Beherrschung; systematische Fehler, die das Verständnis selten beeinträchtigen.
   C (3)  = nur einige einfache Strukturen korrekt, systematische elementare Fehler, oft lautgetreue Schreibung.
   D (0)  = sehr begrenzte Beherrschung, Text kaum verständlich.

SONDERREGEL: Thema verfehlt (Text hat kaum Bezug zur Aufgabe) → alle drei Kriterien D, overall_score = 0, thema_verfehlt = true.

{CORRECTION_RULES}

═══════════════════════════════════════════════════════
BESTEHEN (telc-Regel, NICHT deine Aufgabe)
═══════════════════════════════════════════════════════
Beim telc-Test gibt es für den Schreiben-Teil allein kein "bestanden" oder "nicht bestanden".
Bestanden wird der schriftliche Teil insgesamt (Lesen, Sprachbausteine, Hören, Schreiben: mindestens 135 von 225 Punkten).
Du vergibst nur die Punkte. Schreibe in appreciation und suggestions NIE "bestanden" oder "nicht bestanden".

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT: NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Alle Feedback-Felder: maximal 20 Wörter (12 für "explanation", 15 für suggestions), auf Deutsch, kein Fließtext.
Reihenfolge der Felder einhalten: zuerst "corrections", dann die Bewertung, dann corrected_text und model_text.
═══════════════════════════════════════════════════════

{{
  "corrections": [
    {{"error": "exakte Stelle aus dem Originaltext", "correction": "Korrektur", "explanation": "max 12 Wörter"}}
  ],
  "leitpunkte_score": 9, "leitpunkte_feedback": "max 20 Wörter",
  "gestaltung_score": 9, "gestaltung_feedback": "max 20 Wörter",
  "richtigkeit_score": 15, "richtigkeit_feedback": "max 20 Wörter",
  "overall_score": 33,
  "appreciation": "max 20 Wörter, ermutigend und konkret",
  "thema_verfehlt": false,
  "corrected_text": "Originaltext, nur die gelisteten Fehler korrigiert",
  "model_text": "Mustertext: E-Mail im von der Aufgabe verlangten Register, alle 4 Leitpunkte, 120-150 Wörter",
  "suggestions": ["max 15 Wörter (Leitpunkte)", "max 15 Wörter (Gestaltung)", "max 15 Wörter (Richtigkeit)"]
}}

BERECHNUNG: jeder Score ist 15, 9, 3 oder 0. overall_score = leitpunkte_score + gestaltung_score + richtigkeit_score (max 45).
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN (variabel, hier für cache_control abschneiden)
# ═══════════════════════════════════════════════════════

Aufgabenstellung: {task_instruction}
Zu behandelnde Leitpunkte (alle 4):
{bullet_points_str}
Text des Kandidaten:
{text}"""