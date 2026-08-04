"""
Prompt de correction pour le Telc Deutsch B2 — Schreiben.

Format : 1 tâche unique — lettre/e-mail de réclamation formelle (Beschwerde / Mängelrüge)
Points  : 45 points au total (seuil de réussite : 27/45 = 60 %)
Mots    : 150-200 mots minimum

Pondération OFFICIELLE telc B2 (même système que B1 — confirmé via telc.net) :
3 critères, chacun noté A(5)/B(3)/C(1)/D(0) par deux correcteurs, somme x3.
  I.   Aufgabenbewältigung      : 15 Punkte (Leitpunkte, Struktur, Forderung)
  II.  Kommunikative Gestaltung : 15 Punkte (Kohärenz, Konnektoren, Register)
  III. Formale Richtigkeit      : 15 Punkte (Grammatik, Orthografie, Wortschatz)

⚠️ Corrigé depuis l'ancienne version à 4 critères (15/10/10/10) qui séparait
Wortschatz de Grammatik — non conforme au barème réel telc (même correction
que pour telc B1).
"""


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
        task_instruction: Consigne complète de la tâche
        bullet_points: Liste des points à traiter (a/b choix)
        context_ad: Texte de l'annonce/publicité fournie dans le sujet (optionnel)

    Returns:
        Prompt complet prêt à envoyer au modèle IA.
        Contenu fixe en tête, contenu variable en fin de string — coupe
        juste avant "# AUFGABE DES KANDIDATEN" si tu ajoutes le prompt
        caching plus tard.
    """

    bullet_points_str = "\n".join(f"• {point}" for point in bullet_points)
    context_section = f"""Anzeige / Kontext:
{context_ad}

""" if context_ad else ""

    return f"""Du bist ein offizieller Prüfer für das Telc Deutsch B2-Zertifikat, Schriftlicher Ausdruck.
Du bewertest nach den 3 offiziellen telc-Kriterien, je 15 Punkte (max. 45). Bestehensgrenze: 27/45 (60%).

═══════════════════════════════════════════════════════
PFLICHTSTRUKTUR — formelle Beschwerde / Mängelrüge
═══════════════════════════════════════════════════════
Absender (Name, Adresse, E-Mail) → Empfänger (Firma, Adresse) → Datum → Betreffzeile ("Betreff: Beschwerde über..." / "Mängelrüge zu...") → Anrede ("Sehr geehrte Damen und Herren,") → Einleitung: Anlass klar nennen → Hauptteil: mind. 3 Punkte strukturiert in Absätzen → konkrete Forderung (Reparatur/Ersatz/Erstattung) → "Mit freundlichen Grüßen," → Unterschrift.
Konnektoren (mind. 4-5): erstens/zweitens/drittens, außerdem/darüber hinaus, leider/bedauerlicherweise, obwohl/obgleich/trotz+Genitiv, "Ich fordere Sie daher auf...", "Ich erwarte von Ihnen, dass...".
150-200 Wörter empfohlen.

⚠️ KRITISCHE REGEL — ANWALTSDROHUNG: die Aufgabe verlangt, OHNE sofortige Anwaltsdrohung zu schreiben. "Ich werde sofort einen Anwalt beauftragen" im ersten Absatz ist FALSCH. Erlaubt am Ende: "Sollte ich keine Antwort erhalten, behalte ich mir weitere Schritte vor." Verstoß → aufgabenbewaeltigung_score -3.

Kurzes Referenzbeispiel (Struktur, nicht wörtlich kopieren): "Sehr geehrte Damen und Herren, ich habe am vergangenen Wochenende... Erstens war... Zweitens war... Ich fordere Sie daher auf... Sollte ich keine Antwort erhalten, behalte ich mir weitere Schritte vor. Mit freundlichen Grüßen,"

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN (je 15 Punkte, offizielles telc-Raster)
═══════════════════════════════════════════════════════

I. AUFGABENBEWÄLTIGUNG (15 Pt) — mind. 3 Punkte (Option a) ODER 2 Punkte + 1 freier Aspekt (Option b) vollständig behandelt?
   Alle Punkte vollständig, präzise, mit Details → 13-15
   3 Punkte behandelt, teils oberflächlich → 9-12
   2 Punkte behandelt → 5-8
   1 Punkt oder thematisch verfehlt → 0-4
   ❌ Thema verfehlt (kein Beschwerdebrief) → MAX 4/15, overall_score MAX 20/45
   ❌ Sofortige Anwaltsdrohung → -3 | Keine Betreffzeile → -1 | Keine konkrete Forderung → -2
   ❌ Weniger als 100 Wörter → -4

II. KOMMUNIKATIVE GESTALTUNG (15 Pt) — logische Struktur (Einleitung→Problembeschreibung→Forderung), Konnektoren vielfältig, klare Absatzgliederung, kein Themensprung, durchgehend formelles Register (Sie-Form).
   ❌ "du" statt "Sie" → -4
   ❌ Keine/kaum Konnektoren → MAX 6/15

III. FORMALE RICHTIGKEIT (15 Pt) — Konjunktiv II für höfliche Forderungen ("Ich wäre Ihnen dankbar, wenn..."), Passiv ("Das Gerät wurde geliefert..."), Nebensätze (obwohl/da/weil/sodass), Genitiv nach Präpositionen, Rechtschreibung/Zeichensetzung, formelles präzises Vokabular (Mängelrüge, Reklamation, Gewährleistung), keine Umgangssprache, keine Wortwiederholungen.

KORRIGIERTER TEXT: thematisch korrekt → Fehler korrigieren, Register formeller machen, Anwaltsdrohung abschwächen, Ideen beibehalten. Thema verfehlt/Struktur komplett falsch → vollständig neu schreiben (vollständige Briefstruktur, mind. 3 Punkte, 150-200 Wörter).

═══════════════════════════════════════════════════════
BEWERTUNGSMASSSTAB
═══════════════════════════════════════════════════════
40-45 = C1 (Ausgezeichnet) | 32-39 = B2+ (Gut, bestanden) | 27-31 = B2 (Ausreichend, bestanden) | 18-26 = B1+ (nicht bestanden) | 0-17 = B1/A2 (nicht bestanden)

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT — NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Alle Feedback-Felder: maximal 20 Wörter (12 für "explanation", 15 für suggestions), auf Deutsch, kein Fließtext.
═══════════════════════════════════════════════════════

{{
  "corrected_text": "Der vollständig korrigierte oder neu geschriebene Beschwerdebrief",
  "aufgabenbewaeltigung_score": 12, "aufgabenbewaeltigung_feedback": "max 20 Wörter",
  "gestaltung_score": 11, "gestaltung_feedback": "max 20 Wörter",
  "richtigkeit_score": 11, "richtigkeit_feedback": "max 20 Wörter",
  "overall_score": 34,
  "passed": true,
  "appreciation": "max 20 Wörter, ermutigend und konkret",
  "corrections": [
    {{"error": "identifizierter Fehler im Originaltext", "correction": "Korrektur", "explanation": "max 12 Wörter"}}
  ],
  "suggestions": ["max 15 Wörter (Struktur/Forderung)", "max 15 Wörter (Gestaltung)", "max 15 Wörter (Richtigkeit)"]
}}

BERECHNUNG: overall_score = aufgabenbewaeltigung_score + gestaltung_score + richtigkeit_score (max 45).
passed = true wenn overall_score >= 27, sonst false.
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN (variabel — hier für cache_control abschneiden)
# ═══════════════════════════════════════════════════════

{context_section}Aufgabenstellung: {task_instruction}
Zu behandelnde Punkte (Auswahl a oder b):
{bullet_points_str}
Text des Kandidaten:
{text}"""