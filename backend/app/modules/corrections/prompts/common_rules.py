"""
app/modules/corrections/prompts/common_rules.py

Règles communes à tous les prompts de correction Schreiben :
- notation uniquement sur le texte original du candidat
- liste de corrections exhaustive, rédigée en premier, limitée aux fautes de langue
  (les problèmes de contenu vont dans main_weaknesses / feedbacks, jamais dans corrections)
- corrected_text = correction minimale (aucun ajout, aucune réécriture, même hors sujet)
- model_text = Mustertext séparé (version améliorée attendue)
- note de correction calibrée sur la densité d'erreurs
- pas de fausses corrections (en cas de doute, on ne corrige pas)
- définition commune de "Thema verfehlt", qui déclenche la règle propre à chaque examen
"""

CORRECTION_RULES = """═══════════════════════════════════════════════════════
REGELN FÜR KORREKTUR UND BEWERTUNG (verbindlich für alle Teile)
═══════════════════════════════════════════════════════
1. BEWERTUNG NUR AM ORIGINALTEXT: Alle Punkte und Feedbacks beziehen sich ausschließlich auf den Text des Kandidaten, niemals auf corrected_text oder model_text. Zitiere in Feedbacks nur Wörter, die wirklich im Originaltext stehen.

2. "corrections" ZUERST UND VOLLSTÄNDIG, NUR SPRACHE: Gehe den Originaltext Satz für Satz durch und liste JEDEN sprachlichen Fehler auf (Grammatik, Wortstellung, Kasus, Rechtschreibung, Zeichensetzung, falsches Wort, Register). "error" ist die exakte Stelle aus dem Originaltext, wörtlich kopiert. "correction" ist die minimal korrigierte Form. VERBOTEN in "corrections": inhaltliche Probleme (fehlende Leitpunkte, irrelevante oder themenfremde Sätze, verfehltes Thema). Ein sprachlich korrekter Satz ist KEIN Fehler, auch wenn er nicht zur Aufgabe passt. Inhaltliche Probleme gehören nur in main_weaknesses und in die Feedbacks der Inhaltskriterien.

3. "corrected_text" = MINIMALE KORREKTUR: Den Originaltext Wort für Wort übernehmen und NUR die in "corrections" gelisteten Fehler korrigieren. Verboten: neue Sätze, neue Ideen, zusätzliche Konnektoren, Grußformeln oder Abschlusssätze, stilistische Änderungen an korrekten Sätzen, Ergänzung fehlender Leitpunkte, Löschen oder Umschreiben themenfremder Sätze. Jede Änderung im corrected_text MUSS in "corrections" stehen, und jede Korrektur aus "corrections" MUSS im corrected_text umgesetzt sein. Bei verfehltem Thema bleibt corrected_text inhaltlich identisch mit dem Original (nur Sprachfehler korrigiert). Die richtige Antwort auf die Aufgabe steht ausschließlich im model_text.

4. "model_text" = MUSTERTEXT: Eine verbesserte Version, die zeigt, was die Aufgabe erwartet: alle Leitpunkte, richtige Textsorte und Struktur, passende Konnektoren, Zielniveau, empfohlene Wortzahl. Passende Ideen des Kandidaten übernehmen. Nur hier sind neue Sätze und Formulierungen erlaubt. Bei verfehltem Thema: komplett neu nach der Aufgabenstellung.

5. KORREKTHEIT NACH FEHLERDICHTE: Zähle die Fehler aus "corrections" pro 100 Wörter Originaltext.
   0-2 = sehr gut | 3-5 = gut | 6-9 = ausreichend | 10 oder mehr = schwach.
   Die Korrektheitsnote MUSS zu dieser Stufe passen (Umrechnung siehe unten).

6. KEINE FALSCHEN KORREKTUREN: Korrigiere nur eindeutige Fehler. Eine korrekte Formulierung, die man auch anders sagen könnte, ist KEIN Fehler und gehört NICHT in "corrections" (Beispiele: "den ganzen Tag" ist korrekt ohne "lang"; "ein paar" = einige wird kleingeschrieben und ist korrekt; nach einer Anrede mit Komma wie "Lieber Jonas," beginnt der Brieftext mit Kleinbuchstaben, "danke für..." ist dort korrekt). Ein Satzzeichen, das im Originaltext bereits steht, ist kein Fehler: "error" muss immer den tatsächlichen Fehler enthalten, nie einen korrekten Satz ohne sein vorhandenes Satzzeichen. Im Zweifel NICHT korrigieren. Stilistische Verbesserungen gehören ausschließlich in model_text oder suggestions.

7. THEMA VERFEHLT: Prüfe den Grundzweck der Aufgabe (z. B. aus dem Urlaub berichten, sich für eine Einladung bedanken und zusagen, sich beschweren). Erfüllt der Text diesen Grundzweck in der richtigen Textsorte, ist das Thema NICHT verfehlt, auch wenn viele Leitpunkte fehlen oder viel Irrelevantes dabei ist: dann thema_verfehlt = false und nur die Inhaltsnote senken. Beispiel: Eine E-Mail, die für die Einladung dankt und zusagt, aber nur eine der geforderten Fragen stellt, hat das Thema NICHT verfehlt. Das Thema ist nur verfehlt, wenn der Grundzweck gar nicht erfüllt wird (z. B. eine Postkarte über den Arbeitsalltag statt über den Urlaub). Einzelne Wörter, die zufällig einen Leitpunkt berühren, ändern daran nichts. Wenn du "Thema verfehlt" feststellst oder im Feedback schreibst, MUSST du die Thema-verfehlt-Regel des Prüfungsformats oben anwenden (z. B. ECL: kommunikative_wirksamkeit = 0). Die Sprachkriterien werden trotzdem normal nach der Fehlerdichte bewertet. Wenn das JSON-Format ein Feld "thema_verfehlt" pro Aufgabe vorsieht, setze es auf true oder false.
"""