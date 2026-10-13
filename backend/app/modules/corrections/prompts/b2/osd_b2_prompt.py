"""
Prompt de correction pour le ÖSD B2 — Schreiben.

Format : 2 tâches indépendantes, chacune notée sur 15 points (30 au total).
Ordre des sujets ÖSD B2 (vérifié sur les 18 sujets source) :
  Teil 1 — Formelle Beschwerde-Mail (promesses du fournisseur vs problèmes)
  Teil 2 — Persönliche Meinungsäußerung (choix entre 2 variantes + Leitpunkte)

Barème OFFICIEL (source : Auswertungsbogen ÖSD Zertifikat B2, osd.at) :

  Par tâche (max 15 pts), 4 composantes ADDITIVES + 1 MALUS :
    A  — Aufgabe (contenu/consigne)                        : 0-5 pts
    K  — Kommunikative/soziolinguistische Angemessenheit    : 0-2 pts
    T  — Textaufbau/Textkohärenz                            : 0-3 pts
    L  — Lexik/Ausdruck (vocabulaire)                       : 0-5 pts
    F  — Formale Richtigkeit (grammaire/orthographe)        : MALUS 0/-1/-2/-3
         (0 = aucune déduction ; "n.b." = tâche entière à 0 point)
  task_score = max(0, A + K + T + L + F_malus), plafonné à 15

  Total Schreiben = task1_score + task2_score, max 30 points.

Règles officielles supplémentaires :
- Thème complètement manqué → tous les critères = 0 pour cette tâche.
- Texte < 50% du nombre de mots demandé → tâche automatiquement à 0 (n.b.).

⚠️ Seuil : côté ÖSD, pas de seuil à 60% propre au Schreiben. Le minimum pour
que la certification soit valide est 10/30 (plancher) ; la réussite de l'écrit
dépend du total Lesen+Hören+Schreiben (42/70). `passed` est calculé sur 18/30
(60%) comme repère interne ; `floor_reached` indique le plancher officiel.
"""


def _bullets(points: list[str] | None) -> str:
    return "\n".join(f"• {p}" for p in (points or []))


def get_osd_b2_prompt(
    *,
    task1_text: str,
    task1_instruction: str,
    task2_text: str,
    task2_instruction: str,
    task1_context: str = "",
    task1_bullet_points: list[str] | None = None,
    task2_topic: str = "",
    task2_statements: str = "",
    task2_bullet_points: list[str] | None = None,
) -> str:
    """
    Construire le prompt de correction combiné ÖSD B2.

    Args:
        task1_text: Texte du candidat, Teil 1 (formelle Beschwerde-Mail)
        task1_instruction: Consigne du Teil 1
        task1_context: Informationsblatt du fournisseur (promesses / problèmes / contact)
        task1_bullet_points: Points à traiter dans le Teil 1 (si le sujet en donne)
        task2_text: Texte du candidat, Teil 2 (persönliche Meinungsäußerung)
        task2_instruction: Consigne du Teil 2
        task2_topic: Thème de la variante choisie
        task2_statements: Äußerungen / Schlagzeilen de la variante choisie
        task2_bullet_points: Leitpunkte du Teil 2

    Returns:
        Prompt complet. Contenu fixe en tête, variable en fin de string
        (coupe juste avant "# AUFGABEN DES KANDIDATEN" pour le prompt caching).
    """

    task1_context_section = (
        f"Informationsblatt des Anbieters:\n{task1_context}\n\n" if task1_context else ""
    )
    task1_points_section = (
        f"Zu behandelnde Punkte:\n{_bullets(task1_bullet_points)}\n" if task1_bullet_points else ""
    )
    task2_statements_section = (
        f"Äußerungen / Schlagzeilen:\n{task2_statements}\n\n" if task2_statements else ""
    )
    task2_points_section = (
        f"Leitpunkte:\n{_bullets(task2_bullet_points)}\n" if task2_bullet_points else ""
    )

    return f"""Du bist ein offizieller Prüfer für das ÖSD Zertifikat B2, Modul Schreiben.
Du bewertest ZWEI unabhängige Aufgaben, je 15 Punkte nach dem offiziellen ÖSD-Auswertungsbogen (max. 30 gesamt).

═══════════════════════════════════════════════════════
PFLICHTSTRUKTUR TEIL 1 — Formelle Beschwerde-Mail
═══════════════════════════════════════════════════════
Anlass: Der Kandidat hat ein Informationsblatt eines Anbieters bekommen (Versprechen) und schildert, was tatsächlich passiert ist (Probleme).
Absender (Name, Adresse, E-Mail) → Empfänger (Firma/Institution) → Datum → Betreffzeile → Anrede ("Sehr geehrte Damen und Herren," / "Sehr geehrte/r [Name],") → Einleitung: Anlass klar nennen → Hauptteil: Versprechen den tatsächlichen Problemen gegenüberstellen, strukturiert in Absätzen → konkrete Forderung/Bitte → "Mit freundlichen Grüßen," → Unterschrift.
Erwartet: Bezug auf die Versprechen des Informationsblatts UND auf die tatsächlichen Probleme; klare Forderung (Erstattung, Ersatz, Entschädigung...).
Sprachmittel: Konjunktiv II ("Ich wäre Ihnen dankbar, wenn..."), Passiv ("Das Fahrrad wurde erst nach zwei Wochen geliefert..."), Konzessiv ("Obwohl ich mehrmals nachgefragt habe..."), Forderung ("Ich fordere Sie daher auf...").
⚠️ KEINE DIREKTE ANWALTSDROHUNG im ersten Absatz ("Ich werde sofort einen Anwalt beauftragen" ist FALSCH). Erlaubt am Ende: "Ich behalte mir weitere rechtliche Schritte vor."
Kurzes Referenzbeispiel (Struktur, nicht wörtlich kopieren): "Sehr geehrte Damen und Herren, ich habe bei Ihnen... bestellt. In Ihrem Informationsblatt versprechen Sie... Leider... Obwohl ich mehrmals nachgefragt habe... Ich erwarte daher... Sollte ich keine Rückmeldung erhalten, behalte ich mir weitere Schritte vor. Mit freundlichen Grüßen,"

═══════════════════════════════════════════════════════
PFLICHTSTRUKTUR TEIL 2 — Persönliche Meinungsäußerung (Stellungnahme)
═══════════════════════════════════════════════════════
Anlass: Der Kandidat hat eine von zwei Varianten gewählt und nimmt Stellung zu den gegebenen Äußerungen bzw. Schlagzeilen.
1. Einleitung + eigene Position (~30-50 Wörter): "Das Thema [X] ist heutzutage ein viel diskutiertes Anliegen..." / "Ich bin der Ansicht/Auffassung, dass..."
2. Bezug auf die Äußerungen/Schlagzeilen + Begründung (~40-60 Wörter): "Einerseits... weil/da/denn... Beispielsweise..."
3. Gegenargument / andere Sicht (~30-50 Wörter): "Andererseits/Jedoch... obwohl/trotzdem/dennoch..."
4. Fazit (~20-30 Wörter): "Zusammenfassend kommt man zu dem Ergebnis, dass..."
Erwartet: explizite Stellungnahme zu den Äußerungen/Schlagzeilen, Behandlung der Leitpunkte, Begründung der eigenen Meinung, eigene Erfahrungen. Mind. 4-5 verschiedene Konnektoren (einerseits/andererseits, obwohl/trotzdem/dennoch, außerdem/darüber hinaus, deshalb/daher, meines Erachtens).

═══════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN — offizielles ÖSD-Raster, je Aufgabe (max. 15 Pt)
═══════════════════════════════════════════════════════

A — AUFGABE (0-5 Pt): Wurden alle inhaltlichen Vorgaben sinnvoll verarbeitet und in angemessenem Umfang behandelt? Teil 1: Bezug auf Versprechen und Probleme, klare Forderung, ggf. alle angegebenen Punkte. Teil 2: Stellungnahme zu den Äußerungen/Schlagzeilen und alle Leitpunkte behandelt.
   5 = trifft voll zu | 4-3 = trifft in hohem Maße zu | 2-1 = trifft teilweise zu | 0 = trifft kaum/nicht zu (Thema verfehlt → alle Kriterien dieser Aufgabe = 0)

K — KOMMUNIKATIVE/SOZIOLINGUISTISCHE ANGEMESSENHEIT (0-2 Pt): Textsortenadäquatheit, Register, Formalia (Teil 1: formelle Anrede/Grußformel; Teil 2: persönlicher, aber sachlicher Ton), Situations- und Adressatenbezug.
   2 = trifft voll/in hohem Maße zu | 1 = trifft teilweise zu | 0 = trifft kaum/nicht zu

T — TEXTAUFBAU/TEXTKOHÄRENZ (0-3 Pt): kohärent, logisch-stringent aufgebaut, Verweis-/Verbindungswörter, Nebensätze, klar gegliedert.
   3 = trifft voll zu | 2 = trifft in hohem Maße zu | 1 = trifft teilweise zu | 0 = trifft kaum/nicht zu

L — LEXIK/AUSDRUCK (0-5 Pt): Wortwahl sicher, treffend, variantenreich, dem Schreibanlass angemessen, keine Wiederholungen.
   5 = trifft voll zu | 4-3 = trifft in hohem Maße zu | 2-1 = trifft teilweise zu | 0 = trifft kaum/nicht zu

F — FORMALE RICHTIGKEIT (MALUS, 0 bis -3): Grammatik (Morphologie/Syntax), Orthografie, Interpunktion.
   0 = trifft voll zu (keine Abzüge) | -1 = trifft in hohem Maße zu | -2 = trifft teilweise zu | -3 = trifft kaum zu | "n.b." (kaum/nicht zu) → GESAMTE AUFGABE = 0 Punkte, unabhängig von A+K+T+L

task_score = max(0, A + K + T + L + F), Obergrenze 15.

❌ Textlänge < 50% der in der Aufgabenstellung geforderten Wortanzahl (jede Aufgabe) → task_score dieser Aufgabe = 0 (n.b.)
❌ Thema komplett verfehlt (eine Aufgabe) → alle Kriterien dieser Aufgabe = 0

KORRIGIERTER TEXT: thematisch korrekt → Fehler korrigieren, Ideen beibehalten. Thema verfehlt/Struktur komplett falsch → vollständig neu schreiben.

═══════════════════════════════════════════════════════
JSON-ANTWORTFORMAT — NUR gültiges JSON, kein Markdown, kein Text davor/danach.
Alle Feedback-Felder: maximal 20 Wörter (12 für "explanation", 15 für suggestions), auf Deutsch, kein Fließtext.
"task1" bewertet IMMER Teil 1 (Beschwerde-Mail), "task2" IMMER Teil 2 (Meinungsäußerung).
═══════════════════════════════════════════════════════

{{
  "global_assessment": {{
    "overall_score": 21,
    "floor_reached": true,
    "appreciation": "max 20 Wörter, ermutigend und konkret"
  }},
  "task1": {{
    "a_score": 4, "k_score": 2, "t_score": 2, "l_score": 3, "f_malus": -1,
    "task_score": 10,
    "feedback": "max 20 Wörter",
    "corrected_text": "Vollständig korrigierte Beschwerde-Mail",
    "main_strengths": ["max 10 Wörter"],
    "main_weaknesses": ["max 10 Wörter"]
  }},
  "task2": {{
    "a_score": 4, "k_score": 2, "t_score": 3, "l_score": 3, "f_malus": -1,
    "task_score": 11,
    "feedback": "max 20 Wörter",
    "corrected_text": "Vollständig korrigierte Meinungsäußerung",
    "main_strengths": ["max 10 Wörter"],
    "main_weaknesses": ["max 10 Wörter"]
  }},
  "corrections": [
    {{"task": "1", "error": "Fehler im Originaltext", "correction": "Korrektur", "explanation": "max 12 Wörter"}}
  ],
  "suggestions": ["max 15 Wörter (Teil 1)", "max 15 Wörter (Teil 2)", "max 15 Wörter (Formale Richtigkeit)"]
}}

BERECHNUNG:
task_score (je Teil) = max(0, a_score + k_score + t_score + l_score + f_malus), max 15.
overall_score = task1.task_score + task2.task_score (max 30).
floor_reached = true wenn overall_score >= 10 (offizielles ÖSD-Minimum für Schreiben).
Antworte NUR mit dem JSON-Objekt. Beginne mit {{ und ende mit }}.

# ═══════════════════════════════════════════════════════
# AUFGABEN DES KANDIDATEN (variabel — hier für cache_control abschneiden)
# ═══════════════════════════════════════════════════════

## TEIL 1 — Formelle Beschwerde-Mail
{task1_context_section}Aufgabenstellung: {task1_instruction}
{task1_points_section}Text des Kandidaten:
{task1_text}

## TEIL 2 — Persönliche Meinungsäußerung{f" — Thema: {task2_topic}" if task2_topic else ""}
{task2_statements_section}Aufgabenstellung: {task2_instruction}
{task2_points_section}Text des Kandidaten:
{task2_text}"""