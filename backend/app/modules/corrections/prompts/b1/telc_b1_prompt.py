"""
Prompt de correction pour le Telc Deutsch B1 — Schreiben.

Format : 1 tâche unique — e-mail informelle à un(e) ami(e)
Points  : 45 points au total (seuil de réussite : 27/45 = 60 %)
Mots    : 120-150 mots recommandés
"""


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
        bullet_points: Liste des points à traiter (ex. ["Ihre Hobbys", "Urlaubspläne", ...])

    Returns:
        Prompt complet prêt à envoyer au modèle IA
    """

    bullet_points_str = "\n".join(f"- {point}" for point in bullet_points)

    return f"""Du bist ein offizieller Prüfer für das Telc Deutsch B1-Zertifikat.

═══════════════════════════════════════════════════════
# AUFGABE DES KANDIDATEN
═══════════════════════════════════════════════════════

Aufgabenstellung:
{task_instruction}

Zu behandelnde Punkte:
{bullet_points_str}

Text des Kandidaten:
{text}

═══════════════════════════════════════════════════════
# BEWERTUNGSRASTER — TELC DEUTSCH B1 (45 Punkte)
═══════════════════════════════════════════════════════

## 1. AUFGABENERFÜLLUNG (15 Punkte)
Wurden alle verlangten Punkte behandelt?
- Alle 4 Punkte vollständig und klar behandelt → 13-15 Punkte
- 3 Punkte behandelt oder 4 Punkte oberflächlich → 9-12 Punkte
- 2 Punkte behandelt → 5-8 Punkte
- 1 Punkt oder weniger → 0-4 Punkte

PFLICHTSTRUKTUR für eine informelle E-Mail:
✅ Anrede: "Liebe [Name]" / "Lieber [Name]"
✅ Einleitungssatz: "Wie geht es dir?", "Ich freue mich über deinen Brief..."
✅ Hauptteil: alle Aufgabenpunkte abdecken
✅ Abschlusssatz: "Ich freue mich auf deine Antwort", "Schreib mir bald!"
✅ Grußformel: "Liebe Grüße" / "Herzliche Grüße"
✅ Unterschrift (Vorname)

ERWARTETE KONNEKTOREN (mind. 3-4 verwenden):
- "Tatsächlich..." / "Zusätzlich..." / "Außerdem..."
- "Entweder...oder..." / "Zwar...aber..."
- "Bezüglich [Thema]..." / "Was [Thema] betrifft,..."
- "Ich würde gerne wissen, ob..."
- "Ich freue mich sehr, dass..." / "Es freut mich, dass..."

## 2. TEXTKOHÄSION UND KOHÄRENZ (10 Punkte)
- Logische Verknüpfung zwischen Sätzen und Absätzen
- Sinnvolle Verwendung von Konnektoren
- Klarer Textfluss und roter Faden

## 3. WORTSCHATZ (10 Punkte)
- Vielfalt und Angemessenheit des Vokabulars
- Kein übermäßiger Gebrauch von Grundwörtern
- Registerkontrolle: informeller, freundschaftlicher Ton

## 4. GRAMMATIK UND RECHTSCHREIBUNG (10 Punkte)
- Korrekte Zeitformen (Präsens, Perfekt, Futur mit "werden/wollen")
- Satzstellung (Verb an 2. Stelle, Nebensätze mit "weil", "dass", "ob")
- Kasus (Akkusativ / Dativ nach Präpositionen)
- Rechtschreibung und Zeichensetzung

═══════════════════════════════════════════════════════
# BEWERTUNGSMASSSTAB
═══════════════════════════════════════════════════════

| Punkte  | Niveau  | Bewertung                       |
|---------|---------|---------------------------------|
| 40-45   | B2      | Ausgezeichnet                   |
| 32-39   | B1+     | Gut – Prüfung bestanden         |
| 27-31   | B1      | Ausreichend – Prüfung bestanden |
| 18-26   | A2+     | Nicht bestanden                 |
| 0-17    | A2/A1   | Nicht bestanden                 |

Bestandsgrenze: 27/45 Punkte (60 %)

═══════════════════════════════════════════════════════
# MUSTERBEISPIEL (Orientierung für Korrektoren)
═══════════════════════════════════════════════════════

Aufgabe: Schreibe an deinen Freund Viktor über deine Hobbys, das Buch über Malta,
         deine Urlaubspläne und einen Vorschlag zum Treffen.

Mustertext (B1-Niveau, ~130 Wörter):

```
Lieber Viktor,

wie geht es dir? Gestern habe ich deinen Brief gelesen und mich darüber sehr gefreut.
Vielen Dank für das Buch über Malta — ich habe bereits reingeschaut und es gefällt mir sehr!

Es freut mich sehr, dass du nach meinen Hobbys gefragt hast. Ich lese entweder Bücher
oder gehe wandern. Beim Wandern fotografiere ich häufig die Natur — ähnlich wie du!

Für meinen nächsten Urlaub werde ich eine Wanderung mit meinen Freunden in den Bergen
unternehmen, um ein bisschen die Natur zu genießen.

Ein Treffen mit dir wäre großartig. Gib Bescheid, wann es dir passt, und wir finden eine
gute Gelegenheit. Ich freue mich auf unser Treffen!

Liebe Grüße,
Anna
```

═══════════════════════════════════════════════════════
# ⚠️ KRITISCHE REGELN VOR DER KORREKTUR
═══════════════════════════════════════════════════════

## SCHRITT 1 — AUFGABENERFÜLLUNG PRÜFEN

Vor der Bewertung MUSS geprüft werden:
✅ Wurde eine informelle E-Mail geschrieben (nicht ein Aufsatz oder Bericht)?
✅ Wird der Empfänger mit "du" angesprochen?
✅ Sind mind. 3 der verlangten Punkte behandelt?
✅ Gibt es Anrede, Hauptteil, Grußformel und Unterschrift?

❌ THEMA VERFEHLT → aufgabe_score MAX = 4/15, overall_score MAX = 20/45
❌ Förmliche statt informelle E-Mail → struktur_score -3
❌ Weniger als 2 Punkte behandelt → aufgabe_score MAX = 8/15

## SCHRITT 2 — KORRIGIERTEN TEXT ERSTELLEN

### FALL A: Kandidat ist THEMATISCH KORREKT
Nur korrigieren:
- Rechtschreib- und Grammatikfehler
- Unnatürliche Formulierungen
- Fehlende Konnektoren ergänzen
→ Die Ideen des Kandidaten BEIBEHALTEN

### FALL B: Kandidat hat THEMA VERFEHLT
Den Text VOLLSTÄNDIG neu schreiben:
- Korrekte informelle E-Mail-Struktur verwenden
- Alle verlangten Punkte aus der Aufgabenstellung behandeln
- Niveau und Stil des Kandidaten annähernd beibehalten
- 120-150 Wörter

═══════════════════════════════════════════════════════
# AUTOMATISCHE ABZÜGE
═══════════════════════════════════════════════════════

1. Thema verfehlt (kein Brief / falscher Empfänger) → MAX 20/45
2. Förmliche statt informelle Anrede → struktur_score -3
3. Keine Grußformel → struktur_score -2
4. Keine Konnektoren verwendet → kohaesion_score MAX 5/10
5. Weniger als 80 Wörter → aufgabe_score -3
6. Mehr als 200 Wörter (Themenverfehlung durch Ausdehnung) → aufgabe_score -1

═══════════════════════════════════════════════════════
# JSON-ANTWORTFORMAT
═══════════════════════════════════════════════════════

Antworte NUR mit einem gültigen JSON-Objekt (kein Markdown, kein Text davor oder danach):

{{
  "corrected_text": "Die vollständig korrigierte oder neu geschriebene informelle E-Mail",

  "aufgabe_score": 12,
  "aufgabe_feedback": "Detaillierte Analyse: Welche Punkte wurden behandelt? Was fehlt?",

  "kohaesion_score": 8,
  "kohaesion_feedback": "Analyse der Konnektoren und des Textflusses",

  "wortschatz_score": 7,
  "wortschatz_feedback": "Bewertung des Vokabulars: Vielfalt, Register, Wiederholungen",

  "grammatik_score": 7,
  "grammatik_feedback": "Grammatik- und Rechtschreibanalyse: Zeitformen, Kasus, Satzstellung",

  "overall_score": 34,
  "passed": true,
  "appreciation": "Ermutigende und konstruktive Gesamtbewertung auf Deutsch",

  "corrections": [
    {{"error": "identifizierter Fehler", "correction": "Korrektur", "explanation": "Pädagogische Erklärung auf Deutsch"}},
    {{"error": "weiterer Fehler", "correction": "Korrektur", "explanation": "Erklärung"}}
  ],

  "suggestions": [
    "Tipp 1 zur Verbesserung der Struktur",
    "Tipp 2 zur Bereicherung des Wortschatzes",
    "Tipp 3 zur Grammatikverbesserung"
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