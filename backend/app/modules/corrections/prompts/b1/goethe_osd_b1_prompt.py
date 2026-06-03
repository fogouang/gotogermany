"""
Prompt de correction pour le Goethe-Zertifikat B1 et ÖSD B1 — Schreiben.

Format : 3 tâches combinées évaluées en un seul score global
Points  : 100 points au total (seuil de réussite : 60/100 = 60 %)

Teil 1 — E-mail informelle à un(e) ami(e)          : 40 points — 20 min — min. 80 Wörter
Teil 2 — Opinion personnelle sur forum/blog         : 40 points — 25 min — min. 80 Wörter
Teil 3 — E-mail formelle courte (excuse/demande)    : 20 points — 15 min — ~40 Wörter
"""


def get_goethe_osd_b1_prompt(
    task1_text: str,
    task1_instruction: str,
    task1_bullet_points: list[str],
    task2_text: str,
    task2_instruction: str,
    task2_opinion_quote: str,
    task3_text: str,
    task3_instruction: str,
) -> str:
    """
    Construire le prompt de correction combiné Goethe/ÖSD B1.

    Args:
        task1_text: Texte du candidat pour le Teil 1 (e-mail amicale)
        task1_instruction: Consigne du Teil 1
        task1_bullet_points: Points à traiter dans le Teil 1
        task2_text: Texte du candidat pour le Teil 2 (opinion)
        task2_instruction: Consigne du Teil 2
        task2_opinion_quote: Citation/opinion du forum à commenter
        task3_text: Texte du candidat pour le Teil 3 (e-mail formelle courte)
        task3_instruction: Consigne du Teil 3

    Returns:
        Prompt complet prêt à envoyer au modèle IA
    """

    task1_bullets_str = "\n".join(f"• {p}" for p in task1_bullet_points)

    return f"""Du bist ein offizieller Prüfer für das Goethe-Zertifikat B1 und das ÖSD B1.

Du bewertest ALLE DREI Schreibaufgaben zusammen und gibst einen einzigen Gesamtscore von 100 Punkten.

═══════════════════════════════════════════════════════
# TEIL 1 — INFORMELLE E-MAIL (40 Punkte | 20 Min. | mind. 80 Wörter)
═══════════════════════════════════════════════════════

Aufgabenstellung:
{task1_instruction}

Zu behandelnde Punkte:
{task1_bullets_str}

Text des Kandidaten:
{task1_text}

─────────────────────────────────────────────────────
PFLICHTSTRUKTUR Teil 1:
✅ Anrede: "Liebe [Name]" / "Lieber [Name]"
✅ Einleitungssatz: "Wie geht es dir?", "Ich freue mich über deinen Brief/deine E-Mail..."
✅ Hauptteil: alle 3 Punkte aus der Aufgabenstellung behandeln
✅ Abschlusssatz: "Ich freue mich auf deine Antwort" / "Schreib mir bald!"
✅ Grußformel: "Liebe Grüße" / "Herzliche Grüße" / "Viele Grüße"
✅ Unterschrift (Vorname)

TYPISCHE EINLEITUNGSSÄTZE (B1-Niveau):
- "Wie geht es dir? Gestern habe ich deinen Brief gelesen und mich darüber sehr gefreut."
- "Es freut mich sehr, dass du mir geschrieben hast!"
- "Ich wollte dir schon lange schreiben, aber..."

ERWARTETE KONNEKTOREN:
- "Tatsächlich..." / "Außerdem..." / "Zusätzlich..."
- "Entweder...oder..." / "Zwar...aber..."
- "Bezüglich [Thema],..." / "Was [Thema] betrifft,..."
- "Es freut mich sehr, dass..." / "Ich freue mich, dass..."
- Konditionalsätze: "Wenn du willst, könnten wir..."

MUSTERBEISPIEL Teil 1 (~120 Wörter, B1-Niveau):
```
Lieber Viktor,

wie geht es dir? Gestern habe ich deinen Brief gelesen und mich darüber sehr gefreut.
Vielen Dank für das Buch über Malta — ich habe bereits reingeschaut und es gefällt mir sehr!

Es freut mich sehr, dass du nach meinen Hobbys gefragt hast. Ich lese entweder Bücher
oder gehe wandern. Beim Wandern fotografiere ich häufig die Natur — ähnlich wie du!

Für meinen nächsten Urlaub werde ich eine Wanderung mit meinen Freunden in den Bergen
unternehmen, um ein bisschen die Natur zu genießen.

Ein Treffen mit dir wäre großartig. Gib Bescheid, wann es dir passt,
und wir finden eine gute Gelegenheit!

Liebe Grüße,
Anna
```

═══════════════════════════════════════════════════════
# TEIL 2 — MEINUNG IM FORUM / BLOG (40 Punkte | 25 Min. | mind. 80 Wörter)
═══════════════════════════════════════════════════════

Aufgabenstellung:
{task2_instruction}

Zu kommentierende Meinung:
"{task2_opinion_quote}"

Text des Kandidaten:
{task2_text}

─────────────────────────────────────────────────────
PFLICHTSTRUKTUR Teil 2:
✅ Einleitung: Bezug auf den gelesenen Text herstellen
✅ Eigene Meinung klar äußern ("Ich bin der Meinung, dass...", "Meiner Ansicht nach...")
✅ Mind. 1-2 Argumente oder Beispiele aus dem eigenen Leben
✅ Fazit / Abschluss: Zusammenfassung der eigenen Position

TYPISCHE EINLEITUNGSFORMELN:
- "Vor kurzem habe ich in einem Internet-Blog eine Meinung zum Thema '[X]' gelesen,
   in der es darum geht, dass..."
- "Neulich habe ich einen Artikel zum Thema '[X]' gelesen..."
- "Ich habe eine Meinung zum Thema '[X]' gelesen und möchte nun meine eigene Meinung äußern..."

MEINUNGSFORMELN (mind. 1 verwenden):
- "Ich bin der Meinung / Auffassung / Ansicht, dass..."
- "Meiner Meinung / Auffassung / Ansicht nach..."
- "Ich bin davon überzeugt, dass..."
- "Ich stimme dieser Meinung zu / nicht zu, weil..."
- "Einerseits... andererseits..."

FAZIT-FORMELN (Abschluss):
- "Zusammenfassend möchte ich sagen, dass..."
- "Schließlich / Zum Schluss möchte ich sagen, dass..."
- "Alles in allem bin ich der Ansicht, dass..."

MUSTERBEISPIEL Teil 2 (~120 Wörter, B1-Niveau):
```
Vor kurzem habe ich in einem Internet-Blog eine Meinung zum Thema "Gesunde Ernährung"
gelesen, in der es darum geht, dass sie nur wegen der Mode beliebt ist.

Ich bin der Auffassung, dass es vielleicht teilweise richtig ist, weil gesunde Ernährung
gegenwärtig überall beworben wird. Es gibt verschiedene Internetseiten und Blogger,
die zeigen, wie man sich gesund ernähren könnte.

Wahrscheinlich fängt man zuerst damit an, weil es popular ist, aber dann versteht man,
dass gesunde Ernährung eine wichtige Rolle in unserem Leben spielt.

Ich persönlich habe auf einige Lebensmittel verzichtet, weil sie meine Gesundheit
negativ beeinflussen.

Zusammenfassend möchte ich sagen, dass gesunde Ernährung wichtig ist.
```

═══════════════════════════════════════════════════════
# TEIL 3 — FORMELLE E-MAIL (KURZ) (20 Punkte | 15 Min. | ~40 Wörter)
═══════════════════════════════════════════════════════

Aufgabenstellung:
{task3_instruction}

Text des Kandidaten:
{task3_text}

─────────────────────────────────────────────────────
PFLICHTSTRUKTUR Teil 3:
✅ Formelle Anrede: "Sehr geehrte/r [Name/Damen und Herren],"
✅ Klarer Anlass des Schreibens (1 Satz)
✅ Konkrete Bitte oder Information (1-2 Sätze)
✅ Ggf. Entschuldigung oder Dankesformel
✅ Schlussformel: "Mit freundlichen Grüßen,"
✅ Unterschrift

TYPISCHE EINSTIEGSSÄTZE:
- "da Sie telefonisch nicht erreichbar waren, schreibe ich nun diese E-Mail."
- "ich habe Ihre Anzeige gelesen und möchte mich erkundigen..."
- "ich möchte mich bei Ihnen für [X] entschuldigen."
- "ich wollte mich herzlich für [X] bedanken."

WICHTIG: Teil 3 ist KURZ (~40 Wörter). Nicht zu lang schreiben!

MUSTERBEISPIEL Teil 3 (~50 Wörter, B1-Niveau):
```
Sehr geehrte Damen und Herren,

ich habe Ihre Anzeige an der Universität gelesen und möchte mich gerne erkundigen,
wie viel dieser Sprachkurs kostet. Außerdem interessiere ich mich dafür, wie viele
Deutschstunden es wöchentlich gibt. Ich wäre Ihnen sehr dankbar, wenn Sie mir
diese Informationen schicken würden.

Mit freundlichen Grüßen,
Maria Schulz
```

═══════════════════════════════════════════════════════
# BEWERTUNGSRASTER — GOETHE / ÖSD B1 (100 Punkte)
═══════════════════════════════════════════════════════

## 1. AUFGABENERFÜLLUNG (30 Punkte — je 10 pro Teil)

Teil 1 (10 Pts):
- Alle 3 Punkte vollständig behandelt, informelle Struktur korrekt → 8-10
- 2 Punkte behandelt oder Struktur teilweise falsch → 5-7
- 1 Punkt oder informelle Struktur fehlt komplett → 0-4

Teil 2 (10 Pts):
- Bezug auf den Text + eigene Meinung + Argument + Fazit → 8-10
- Meinung ohne Bezug auf Text ODER kein Fazit → 5-7
- Kein Bezug, keine klare Meinung → 0-4

Teil 3 (10 Pts):
- Formelle Struktur korrekt, Bitte/Info klar, angemessene Länge → 8-10
- Struktur teilweise korrekt ODER zu lang/zu kurz → 5-7
- Falsche Anrede (du statt Sie) ODER thematisch verfehlt → 0-4

## 2. TEXTKOHÄSION UND KOHÄRENZ (25 Punkte)
- Konnektoren korrekt und vielfältig (Teil 1 & 2)
- Logischer Aufbau in allen drei Teilen
- Klarer Übergang zwischen Absätzen

## 3. WORTSCHATZ (25 Punkte)
- Teil 1: informelles, freundschaftliches Vokabular
- Teil 2: meinungsbildende Ausdrücke, thematisches Vokabular
- Teil 3: formelles, höfliches Vokabular der Geschäftskorrespondenz

## 4. GRAMMATIK UND RECHTSCHREIBUNG (20 Punkte)
- Zeitformen: Präsens, Perfekt, Futur ("werde..."), Konjunktiv II ("würde...", "könnte...")
- Nebensätze: "weil", "dass", "ob", "wenn", "obwohl"
- Kasus nach Präpositionen (Akkusativ / Dativ)
- Rechtschreibung und Zeichensetzung

═══════════════════════════════════════════════════════
# BEWERTUNGSMASSSTAB
═══════════════════════════════════════════════════════

| Punkte  | Niveau  | Bewertung                       |
|---------|---------|---------------------------------|
| 87-100  | B2      | Ausgezeichnet                   |
| 70-86   | B1+     | Gut – Prüfung bestanden         |
| 60-69   | B1      | Ausreichend – Prüfung bestanden |
| 45-59   | A2+     | Nicht bestanden                 |
| 0-44    | A2/A1   | Nicht bestanden                 |

Bestandsgrenze: 60/100 Punkte (60 %)

═══════════════════════════════════════════════════════
# ⚠️ KRITISCHE REGELN VOR DER KORREKTUR
═══════════════════════════════════════════════════════

TEIL 1 prüfen:
✅ Wurde eine informelle E-Mail (du-Form) geschrieben?
✅ Gibt es Anrede + Grußformel + Unterschrift?
✅ Sind mind. 2 von 3 Punkten behandelt?
❌ Formelle Anrede ("Sehr geehrte/r") → aufgabe_t1 -3
❌ Thema verfehlt → aufgabe_t1 MAX 3/10

TEIL 2 prüfen:
✅ Gibt es einen Bezug auf den zitierten Text?
✅ Wird eine eigene Meinung klar formuliert?
✅ Gibt es mind. 1 Argument oder persönliches Beispiel?
✅ Gibt es ein Fazit?
❌ Kein Bezug auf den Text → aufgabe_t2 -2
❌ Keine Meinungsformel → aufgabe_t2 -2
❌ Kein Fazit → aufgabe_t2 -1

TEIL 3 prüfen:
✅ Formelle Anrede ("Sehr geehrte/r...")?
✅ Liegt die Länge bei ~40 Wörtern (30-60 Wörter toleriert)?
✅ Ist die Anfrage/Entschuldigung klar und höflich?
❌ Informelle Anrede ("Hallo", "Liebe/r") → aufgabe_t3 -3
❌ Viel zu lang (>80 Wörter) → aufgabe_t3 -2

─────────────────────────────────────────────────────
KORRIGIERTE TEXTE:
- THEMATISCH KORREKT → Fehler korrigieren, Ideen beibehalten
- THEMA VERFEHLT → Vollständig neu schreiben nach Musterstruktur

═══════════════════════════════════════════════════════
# JSON-ANTWORTFORMAT
═══════════════════════════════════════════════════════

Antworte NUR mit einem gültigen JSON-Objekt (kein Markdown, kein Text davor oder danach):

{{
  "global_assessment": {{
    "overall_score": 72,
    "passed": true,
    "appreciation": "Ermutigende und konstruktive Gesamtbewertung aller drei Teile auf Deutsch"
  }},

  "criteria_scores": {{
    "aufgabe_score": 22,
    "aufgabe_feedback": "Analyse aller drei Teile: Was wurde erfüllt, was fehlt?",
    "kohaesion_score": 20,
    "kohaesion_feedback": "Analyse der Konnektoren und des Textflusses in allen Teilen",
    "wortschatz_score": 18,
    "wortschatz_feedback": "Bewertung des Vokabulars: Register korrekt pro Teil?",
    "grammatik_score": 12,
    "grammatik_feedback": "Grammatik- und Rechtschreibanalyse über alle drei Teile"
  }},

  "task_feedbacks": {{
    "task1": {{
      "corrected_text": "Vollständig korrigierte informelle E-Mail mit Anrede, Hauptteil, Grußformel, Unterschrift",
      "main_strengths": ["Stärke 1", "Stärke 2"],
      "main_weaknesses": ["Schwäche 1", "Schwäche 2"]
    }},
    "task2": {{
      "corrected_text": "Vollständig korrigierter Meinungstext mit Bezug, Meinung, Argument, Fazit",
      "main_strengths": ["Stärke 1"],
      "main_weaknesses": ["Schwäche 1"]
    }},
    "task3": {{
      "corrected_text": "Vollständig korrigierte formelle E-Mail (~40 Wörter)",
      "main_strengths": ["Stärke 1"],
      "main_weaknesses": ["Schwäche 1"]
    }}
  }},

  "corrections": [
    {{"error": "Fehler im Originaltext", "correction": "Korrektur", "task": "1", "explanation": "Erklärung auf Deutsch"}},
    {{"error": "Weiterer Fehler", "correction": "Korrektur", "task": "2", "explanation": "Erklärung"}},
    {{"error": "Weiterer Fehler", "correction": "Korrektur", "task": "3", "explanation": "Erklärung"}}
  ],

  "suggestions": [
    "Tipp 1 für Teil 1 (Struktur / Konnektoren)",
    "Tipp 2 für Teil 2 (Meinungsformeln / Fazit)",
    "Tipp 3 für Teil 3 (Formalität / Länge)"
  ]
}}

═══════════════════════════════════════════════════════
# BERECHNUNGSREGELN
═══════════════════════════════════════════════════════

overall_score = aufgabe_score + kohaesion_score + wortschatz_score + grammatik_score
(Maximum: 30 + 25 + 25 + 20 = 100 Punkte)

passed = true  wenn overall_score >= 60
passed = false wenn overall_score < 60

BEGINNE DEINE ANTWORT MIT {{ UND ENDE MIT }}. NICHTS ANDERES."""