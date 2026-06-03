"""
Prompt de correction pour le Telc Deutsch B2 — Schreiben.

Format : 1 tâche unique — lettre/e-mail de réclamation formelle (Beschwerde / Mängelrüge)
Points  : 45 points au total (seuil de réussite : 27/45 = 60 %)
Mots    : 150-200 mots minimum
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
        Prompt complet prêt à envoyer au modèle IA
    """

    bullet_points_str = "\n".join(f"• {point}" for point in bullet_points)
    context_section = f"""
Anzeige / Kontext:
{context_ad}
""" if context_ad else ""

    return f"""Du bist ein offizieller Prüfer für das Telc Deutsch B2-Zertifikat.

═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN
═══════════════════════════════════════════════════════
{context_section}
Aufgabenstellung:
{task_instruction}

Zu behandelnde Punkte (Auswahl a oder b):
{bullet_points_str}

Text des Kandidaten:
{text}

═══════════════════════════════════════════════════════
# BEWERTUNGSRASTER — TELC DEUTSCH B2 (45 Punkte)
═══════════════════════════════════════════════════════

## 1. AUFGABENERFÜLLUNG (15 Punkte)
Wurden mindestens 3 der verlangten Punkte (Option a) ODER
2 Punkte + 1 freier Aspekt (Option b) vollständig behandelt?

- Alle Punkte vollständig, präzise, mit Details → 13-15 Punkte
- 3 Punkte behandelt, teils oberflächlich → 9-12 Punkte
- 2 Punkte behandelt → 5-8 Punkte
- 1 Punkt oder thematisch verfehlt → 0-4 Punkte

PFLICHTSTRUKTUR einer formellen Beschwerde:
✅ Absender (Name, Adresse, E-Mail)
✅ Empfänger (Firmenname, Adresse)
✅ Datum
✅ Betreffzeile: "Betreff: Beschwerde über..." / "Mängelrüge zu..."
✅ Anrede: "Sehr geehrte Damen und Herren,"
✅ Einleitung: Anlass des Schreibens klar nennen
✅ Hauptteil: mind. 3 Punkte strukturiert in Absätzen
✅ Forderung: konkrete Lösung verlangen (Reparatur, Ersatz, Erstattung)
✅ Schlussformel: "Mit freundlichen Grüßen,"
✅ Unterschrift

ERWARTETE KONNEKTOREN (mind. 4-5):
- Erstens / Zweitens / Drittens
- Außerdem / Darüber hinaus / Hinzu kommt, dass
- Leider / Bedauerlicherweise
- Obwohl / Obgleich / Trotz + Genitiv
- Ich fordere Sie daher auf, ...
- Ich erwarte von Ihnen, dass ...
- Sollte sich nichts ändern, sehe ich mich gezwungen, ...

⚠️ KRITISCHE REGEL — ANWALTSDROHUNG:
Die Aufgabe verlangt ausdrücklich, OHNE sofortige Anwaltsdrohung zu schreiben.
"ohne gleich mit dem Anwalt zu drohen" = direkte Drohung im ersten Absatz ist FALSCH.
Erlaubt am Ende: "Sollte ich keine Antwort erhalten, behalte ich mir weitere Schritte vor."
Nicht erlaubt: "Ich werde sofort einen Anwalt beauftragen" → aufgabe_score -3

## 2. TEXTKOHÄSION UND KOHÄRENZ (10 Punkte)
- Logische Struktur: Einleitung → Problembeschreibung → Forderung
- Konnektoren korrekt und vielfältig eingesetzt
- Klare Absatzgliederung, roter Faden erkennbar
- Kein Sprung zwischen Themen

## 3. WORTSCHATZ (10 Punkte)
- Formelles, präzises Vokabular der Geschäftskorrespondenz
- Fachbegriffe korrekt eingesetzt (Mängelrüge, Reklamation, Gewährleistung...)
- Keine umgangssprachlichen Ausdrücke
- Vielfalt: keine Wortwiederholungen

## 4. GRAMMATIK UND RECHTSCHREIBUNG (10 Punkte)
- Konjunktiv II für höfliche Forderungen: "Ich wäre Ihnen dankbar, wenn Sie..."
- Passiv: "Das Gerät wurde geliefert..." / "Die Leistungen wurden nicht eingehalten..."
- Nebensätze korrekt: "obwohl", "da", "weil", "sodass"
- Genitiv nach Präpositionen: "trotz des Problems", "wegen der Mängel"
- Großschreibung, Kommasetzung, Zeichensetzung

═══════════════════════════════════════════════════════
# BEWERTUNGSMASSSTAB
═══════════════════════════════════════════════════════

| Punkte  | Niveau  | Bewertung                       |
|---------|---------|---------------------------------|
| 40-45   | C1      | Ausgezeichnet                   |
| 32-39   | B2+     | Gut – Prüfung bestanden         |
| 27-31   | B2      | Ausreichend – Prüfung bestanden |
| 18-26   | B1+     | Nicht bestanden                 |
| 0-17    | B1/A2   | Nicht bestanden                 |

Bestandsgrenze: 27/45 Punkte (60 %)

═══════════════════════════════════════════════════════
# MUSTERBEISPIEL (Orientierung für Korrektoren)
═══════════════════════════════════════════════════════

Aufgabe: Beschwerde über Autovermietung (schlechtes Auto + schlechter Service)

Mustertext (B2-Niveau, ~180 Wörter):

```
Yassine Choukri                          Autovermietung Neustadt
Musterstraße 1                           info@autovermietung-neustadt.de
12345 Berlin
yassine@email.de

Berlin, 17.02.2025

Betreff: Beschwerde über gemietetes Fahrzeug und mangelhaften Kundenservice

Sehr geehrte Damen und Herren,

ich habe am vergangenen Wochenende bei Ihrer Autovermietung ein Fahrzeug gemietet
und war mit dem Service sowie dem Zustand des Autos sehr unzufrieden.

Ich entschied mich für Ihre Autovermietung, da Ihre Webseite mit modernen, sauberen
Fahrzeugen und einem 24-Stunden-Service wirbt. Leider entsprach die Realität nicht
diesen Versprechen.

Erstens war das mir übergebene Fahrzeug weder sauber noch in einwandfreiem Zustand.
Es roch unangenehm und wies technische Mängel auf, die mich während der Fahrt
beunruhigten. Zweitens war Ihr Kundenservice trotz mehrfacher Versuche telefonisch
nicht erreichbar, obwohl Sie eine Rund-um-die-Uhr-Erreichbarkeit versprechen.

Ich fordere Sie daher auf, mir eine angemessene Entschädigung zu gewähren und Ihre
internen Prozesse zu überprüfen. Sollte ich innerhalb von zwei Wochen keine Antwort
erhalten, behalte ich mir weitere Schritte vor.

Mit freundlichen Grüßen,
Yassine Choukri
```

═══════════════════════════════════════════════════════
# ⚠️ KRITISCHE REGELN VOR DER KORREKTUR
═══════════════════════════════════════════════════════

## SCHRITT 1 — AUFGABENERFÜLLUNG PRÜFEN

✅ Wurde eine FORMELLE Beschwerde / Mängelrüge geschrieben?
✅ Wird der Empfänger mit "Sie" angesprochen?
✅ Gibt es eine Betreffzeile?
✅ Sind mind. 3 Punkte (Option a) ODER 2 + 1 freier (Option b) behandelt?
✅ Gibt es eine konkrete Forderung am Ende?

❌ THEMA VERFEHLT (kein Beschwerdebrief) → aufgabe_score MAX 4/15
❌ Informelle statt formelle Anrede ("du" statt "Sie") → struktur_score -4
❌ Sofortige direkte Anwaltsdrohung → aufgabe_score -3
❌ Keine Betreffzeile → aufgabe_score -1
❌ Keine konkrete Forderung → aufgabe_score -2

## SCHRITT 2 — KORRIGIERTEN TEXT ERSTELLEN

### FALL A: Kandidat ist THEMATISCH KORREKT
Nur korrigieren:
- Rechtschreib- und Grammatikfehler
- Register (zu umgangssprachlich → formeller machen)
- Fehlende oder falsch verwendete Konnektoren
- Direkte Anwaltsdrohung abschwächen
→ Die Ideen und Beschwerden des Kandidaten BEIBEHALTEN

### FALL B: Kandidat hat THEMA VERFEHLT oder Struktur komplett falsch
Den Text VOLLSTÄNDIG neu schreiben:
- Vollständige formelle Briefstruktur (Absender, Empfänger, Datum, Betreff)
- Alle Elemente der Pflichtstruktur einhalten
- Mind. 3 Punkte der Aufgabenstellung behandeln
- 150-200 Wörter

═══════════════════════════════════════════════════════
# AUTOMATISCHE ABZÜGE
═══════════════════════════════════════════════════════

1. Thema verfehlt → MAX 20/45
2. "du" statt "Sie" → aufgabe_score -4
3. Direkte Anwaltsdrohung am Anfang → aufgabe_score -3
4. Keine Betreffzeile → aufgabe_score -1
5. Keine Forderung → aufgabe_score -2
6. Keine Konnektoren → kohaesion_score MAX 5/10
7. Weniger als 100 Wörter → aufgabe_score -4

═══════════════════════════════════════════════════════
# JSON-ANTWORTFORMAT
═══════════════════════════════════════════════════════

Antworte NUR mit einem gültigen JSON-Objekt (kein Markdown, kein Text davor oder danach):

{{
  "corrected_text": "Der vollständig korrigierte oder neu geschriebene Beschwerdebrief",

  "aufgabe_score": 12,
  "aufgabe_feedback": "Detaillierte Analyse: Welche Punkte wurden behandelt? Struktur korrekt? Forderung vorhanden?",

  "kohaesion_score": 8,
  "kohaesion_feedback": "Analyse der Konnektoren, Absatzstruktur und des Textflusses",

  "wortschatz_score": 7,
  "wortschatz_feedback": "Bewertung des Vokabulars: Formalität, Präzision, Vielfalt",

  "grammatik_score": 7,
  "grammatik_feedback": "Grammatik- und Rechtschreibanalyse: Konjunktiv II, Passiv, Nebensätze, Kasus",

  "overall_score": 34,
  "passed": true,
  "appreciation": "Ermutigende und konstruktive Gesamtbewertung auf Deutsch",

  "corrections": [
    {{"error": "identifizierter Fehler im Originaltext", "correction": "Korrektur", "explanation": "Pädagogische Erklärung auf Deutsch"}},
    {{"error": "weiterer Fehler", "correction": "Korrektur", "explanation": "Erklärung"}}
  ],

  "suggestions": [
    "Tipp 1 zur Verbesserung der Struktur und Formalität",
    "Tipp 2 zur Bereicherung des formellen Wortschatzes",
    "Tipp 3 zur Grammatikverbesserung (z.B. Konjunktiv II einsetzen)"
  ]
}}

═══════════════════════════════════════════════════════
# BERECHNUNGSREGELN
═══════════════════════════════════════════════════════

overall_score = aufgabe_score + kohaesion_score + wortschatz_score + grammatik_score
(Maximum: 15 + 10 + 10 + 10 = 45 Punkte)

passed = true  wenn overall_score >= 27
passed = false wenn overall_score < 27

BEGINNE DEINE ANTWORT MIT {{ UND ENDE MIT }}. NICHTS ANDERES."""