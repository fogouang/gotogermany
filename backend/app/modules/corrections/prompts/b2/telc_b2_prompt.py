"""
Prompt de correction pour le Telc Deutsch B2 : Schreiben.

Format OFFICIEL (Übungstest telc Deutsch B2) :
  - 2 tâches au choix, l'élève n'en traite qu'une :
      Aufgabe A : Bitte um Informationen (demande d'informations)
      Aufgabe B : Beschwerde (réclamation)
  - e-mail HALBFORMELLE, au moins 150 mots, 30 minutes
  - Leitpunkte : 3 des 4, OU 2 + un aspect personnel lié à la situation
  - adresse, expéditeur et date NON exigés (Betreff, Anrede, Schluss oui)

Barème OFFICIEL :
  3 critères, chacun noté A / B / C / D = 5 / 3 / 1 / 0,
  somme des 3 notes x 3 = max 45. Chaque critère vaut donc
  15 / 9 / 3 / 0 points, rien entre les deux.
    I.   Aufgabenbewältigung      (A = 3 Leitpunkte ou 2 + 1 aspect, B = 2 ou 1 + 1, C = 1, D = 0)
    II.  Kommunikative Gestaltung (bandbreite, logique, connecteurs, registre, VOCABULAIRE)
    III. Formale Richtigkeit      (grammaire, orthographe, ponctuation)
  Thema verfehlt : D partout. Situation verfehlt : seulement I = D.

Corrigé par rapport à la version précédente : réclamation imposée alors
qu'il y a 2 types de tâche, bloc adresse/date exigé, règle "Anwaltsdrohung"
inventée, barème continu, vocabulaire placé en III, JSON d'exemple invalide
(clé "appreciation" en double, virgule manquante).

Les clés JSON (aufgabenbewaeltigung_score, gestaltung_score...) restent
inchangées : le parsing côté backend n'est pas touché.

Sortie : corrected_text = correction minimale du texte du candidat ;
model_text = Mustertext séparé (voir common_rules.CORRECTION_RULES).
"""

from app.modules.corrections.prompts.common_rules import CORRECTION_RULES


def get_telc_b2_prompt(
    text: str,
    task_instruction: str,
    bullet_points: list[str],
    context_ad: str = "",
) -> str:
    """
    Construire le prompt de correction Telc B2.

    Args:
        text: Texte du candidat
        task_instruction: Consigne complète de la tâche choisie (A ou B)
        bullet_points: Les 4 Leitpunkte de la tâche choisie
        context_ad: Texte de l'annonce/publicité fournie dans le sujet (optionnel)

    Returns:
        Prompt complet prêt à envoyer au modèle IA.
        Contenu fixe en tête, contenu variable en fin de string : coupe
        juste avant "# AUFGABE DES KANDIDATEN" si tu ajoutes le prompt
        caching plus tard.
    """

    bullet_points_str = "\n".join(f"• {point}" for point in bullet_points)
    context_section = f"""Anzeige / Kontext:
{context_ad}

""" if context_ad else ""

    return f"""Du bist ein offizieller Prüfer für telc Deutsch B2, Schriftlicher Ausdruck.
Du bewertest nach den 3 offiziellen telc-Kriterien mit den Stufen A/B/C/D.

═══════════════════════════════════════════════════════
AUFGABENFORMAT (offiziell)
═══════════════════════════════════════════════════════
Der Kandidat hat EINE von zwei Aufgaben gewählt:
  Aufgabe A: Bitte um Informationen (Anfrage zu einer Anzeige)
  Aufgabe B: Beschwerde (Erwartungen laut Anzeige vs. tatsächliche Erfahrung, Forderung)
Erkenne an der Aufgabenstellung unten, welche es ist, und bewerte danach.
Textsorte: halbformelle E-Mail, durchgehend Sie-Form, mindestens 150 Wörter.
Erwartete Textmerkmale: Betreff, Anrede, Einleitung (Anlass), Hauptteil mit den gewählten Leitpunkten in Absätzen, Schluss, Grußformel.
Absender, Empfängeradresse und Datum werden NICHT erwartet und NICHT bewertet.
Leitpunkte: 3 der 4 Leitpunkte ODER 2 Leitpunkte + 1 eigener, zur Situation passender Aspekt.

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN (offizielles telc-Raster)
═══════════════════════════════════════════════════════
Jedes Kriterium bekommt GENAU EINE Stufe: A = 15, B = 9, C = 3, D = 0 Punkte.
Keine Zwischenwerte (also nie 12, 11, 7 ...).

I. AUFGABENBEWÄLTIGUNG (aufgabenbewaeltigung_score)
   Deckt der Text Aufgabe und Situation ab? Zähle die auf B2-Niveau angemessen behandelten Leitpunkte.
   A (15) = 3 Leitpunkte ODER 2 + 1 situationsbezogener eigener Aspekt.
   B (9)  = 2 Leitpunkte ODER 1 + 1 eigener Aspekt.
   C (3)  = 1 Leitpunkt ODER nur 1 eigener Aspekt.
   D (0)  = kein Leitpunkt angemessen behandelt.
   Mehr als 3 behandelte Leitpunkte bringen keinen Zusatzpunkt.

II. KOMMUNIKATIVE GESTALTUNG (gestaltung_score)
   Ausdrucksfähigkeit, Aufbau und Textlogik, Verknüpfungen, Register UND Wortschatz.
   A (15) = klar und überzeugend, breites Spektrum, vielfältige Verknüpfungen, Wortschatz voll angemessen;
            die Textmerkmale (Betreff, Anrede, Schluss/Grußformel) sind vorhanden.
   B (9)  = klar, ausreichende Bandbreite, einzelne Wortschatzlücken, eingeschränkte Verknüpfung.
   C (3)  = für die Alltagskommunikation ausreichend, nur einfache Verknüpfungen; Textlogik, Wortschatz oder Register überwiegend unpassend.
   D (0)  = nur elementare Sprachfunktionen; Textlogik, Verknüpfung, Wortschatz und Register völlig unpassend.
   KEIN B (also höchstens C), wenn: Register falsch oder uneinheitlich (z. B. du statt Sie, du/Sie gemischt),
   Wortschatz unter B2, oder Leitpunkte nur aufgezählt ohne logische Verbindung.

III. FORMALE RICHTIGKEIT (richtigkeit_score)
   Grammatik, Rechtschreibung, Zeichensetzung.
   A (15) = gute Beherrschung der Grammatik, keine systematischen Fehler, nur gelegentliche Versehen; Orthografie und Zeichensetzung weitgehend korrekt.
   B (9)  = recht gute Beherrschung, wenige systematische Fehler, die das Verständnis nicht gefährden.
   C (3)  = ausreichende Beherrschung trotz deutlichem Einfluss der Muttersprache; mehrere systematische Fehler, Sinn meist klar.
   D (0)  = nur einige einfache Strukturen korrekt, viele systematische elementare Fehler, oft lautgetreue Schreibung.
   Ist III = D, können I und II trotzdem A, B oder C erhalten.

SONDERREGELN:
- Thema verfehlt (Text hat kaum Bezug zur Aufgabe) → alle drei Kriterien D, overall_score = 0.
- Situation verfehlt (Thema passt, Situation nicht, z. B. Bewerbung statt Anfrage) → nur I = D, II und III normal bewerten.

{CORRECTION_RULES}
Falsches Register (du statt Sie) ist ein Fehler: in "corrections" listen und im corrected_text korrigieren.

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
  "aufgabenbewaeltigung_score": 15, "aufgabenbewaeltigung_feedback": "max 20 Wörter",
  "gestaltung_score": 9, "gestaltung_feedback": "max 20 Wörter",
  "richtigkeit_score": 9, "richtigkeit_feedback": "max 20 Wörter",
  "overall_score": 33,
  "appreciation": "max 20 Wörter, ermutigend und konkret",
  "corrected_text": "Originaltext, nur die gelisteten Fehler korrigiert",
  "model_text": "Mustertext: halbformelle E-Mail zur gewählten Aufgabe (Anfrage oder Beschwerde), mit Betreff, mindestens 150 Wörter",
  "suggestions": ["max 15 Wörter (Leitpunkte)", "max 15 Wörter (Gestaltung)", "max 15 Wörter (Richtigkeit)"]
}}

BERECHNUNG: jeder Score ist 15, 9, 3 oder 0. overall_score = aufgabenbewaeltigung_score + gestaltung_score + richtigkeit_score (max 45).
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN (variabel, hier für cache_control abschneiden)
# ═══════════════════════════════════════════════════════

{context_section}Aufgabenstellung: {task_instruction}
Leitpunkte der gewählten Aufgabe (3 davon oder 2 + eigener Aspekt):
{bullet_points_str}
Text des Kandidaten:
{text}"""