/**
 * constants/sprachlicheMittel.ts
 *
 * Banque statique d'expressions utiles ("Sprachliche Mittel") pour Schreiben
 * et Sprechen, couvrant Goethe B1/B2, TELC B1/B2 et ÖSD B2/J.
 *
 * Ces contenus sont indépendants du JSON généré par le pipeline d'examen —
 * ils sont valables pour n'importe quel sujet du même format, donc pas besoin
 * de les régénérer ni de les stocker en base.
 *
 * Utilisation : resolveMittelKey(...) pour trouver la bonne clé selon le
 * contexte (provider, cefr, module, format_type, teil_number), puis
 * SPRACHLICHE_MITTEL[key] pour récupérer les catégories/phrases.
 */

export interface MittelCategory {
  label: string;
  phrases: string[];
}

export interface MittelBank {
  title: string;
  categories: MittelCategory[];
}

export const SPRACHLICHE_MITTEL: Record<string, MittelBank> = {
  // ═══════════════════════════════════════════════════════════
  // GOETHE / ÖSD B1 (Arena B1) — SCHREIBEN
  // ═══════════════════════════════════════════════════════════
  goethe_b1_schreiben_email_informell: {
    title: "Persönliche E-Mail",
    categories: [
      {
        label: "Anrede",
        phrases: ["Liebe(r) [Name],", "Liebe Familie [Name],", "Hallo [Name],"],
      },
      {
        label: "Einleitung",
        phrases: [
          "Vielen Dank für deine E-Mail!",
          "Mir geht es gut, ich hoffe dir auch.",
          "Ich schreibe dir, weil …",
          "Der Grund für diese E-Mail ist, dass …",
        ],
      },
      {
        label: "Etwas beschreiben",
        phrases: [
          "Ich möchte dir erzählen, wie …",
          "Es war wirklich schön / lustig / interessant …",
          "Stell dir vor, …",
        ],
      },
      {
        label: "Etwas begründen",
        phrases: [
          "Das liegt daran, dass …",
          "Der Grund dafür ist einfach: …",
          "Das ist passiert, weil …",
        ],
      },
      {
        label: "Einen Vorschlag machen",
        phrases: [
          "Ich schlage vor, dass …",
          "Hättest du Lust, …?",
          "Wir könnten doch …",
        ],
      },
      {
        label: "Schluss",
        phrases: [
          "Schreib mir bald zurück!",
          "Liebe / Herzliche Grüße",
          "Bis bald,",
        ],
      },
    ],
  },

  goethe_b1_schreiben_internet_beitrag: {
    title: "Internet-Beitrag",
    categories: [
      {
        label: "Einleitung",
        phrases: [
          "Das Thema „…“ ist momentan sehr aktuell.",
          "Über … wird zurzeit viel diskutiert.",
          "Ich möchte hier kurz meine Meinung dazu äußern.",
        ],
      },
      {
        label: "Meinung äußern",
        phrases: [
          "Meiner Meinung nach …",
          "Ich bin der Ansicht, dass …",
          "Ich persönlich finde, dass …",
        ],
      },
      {
        label: "Argumentieren",
        phrases: [
          "Ein wichtiger Punkt dabei ist …",
          "Außerdem sollte man bedenken, dass …",
          "Auf der einen Seite …, auf der anderen Seite …",
        ],
      },
      {
        label: "Abschluss",
        phrases: [
          "Zusammenfassend lässt sich sagen, dass …",
          "Das ist meine Meinung - wie seht ihr das?",
        ],
      },
    ],
  },

  goethe_b1_schreiben_email_formell: {
    title: "Formelle E-Mail",
    categories: [
      {
        label: "Anrede",
        phrases: [
          "Sehr geehrte Frau [Name],",
          "Sehr geehrter Herr [Name],",
          "Sehr geehrte Damen und Herren,",
        ],
      },
      {
        label: "Um Entschuldigung bitten",
        phrases: [
          "Es tut mir leid, aber ich kann leider nicht …",
          "Leider ist es mir nicht möglich, … zu …",
          "Ich muss Sie um Verständnis bitten.",
        ],
      },
      {
        label: "Begründung",
        phrases: [
          "Das liegt daran, dass …",
          "Der Grund dafür ist: …",
          "Ich muss nämlich …",
        ],
      },
      {
        label: "Schluss",
        phrases: ["Mit freundlichen Grüßen", "Mit besten Grüßen"],
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // GOETHE / ÖSD B1 (Arena B1) — SPRECHEN
  // ═══════════════════════════════════════════════════════════
  goethe_b1_sprechen_teil1: {
    title: "Gemeinsam etwas planen",
    categories: [
      { label: "Vorschlagen", phrases: ["Ich schlage vor, dass …", "Mein Vorschlag ist: …", "Ich habe eine Idee: …"] },
      { label: "Zustimmen", phrases: ["Einverstanden!", "Der Meinung bin ich auch.", "Das finde ich auch gut."] },
      { label: "Widersprechen", phrases: ["Da bin ich anderer Meinung.", "Das finde ich nicht so gut.", "Ich sehe das anders."] },
      { label: "Meinung äußern", phrases: ["Ich denke/glaube, dass …", "Meiner Meinung nach …"] },
      { label: "Etwas hinzufügen", phrases: ["Da wäre noch Folgendes: …", "Ein weiterer Punkt: …"] },
      { label: "Gespräch abschließen", phrases: ["Also, was denkst du?", "Ich glaube, wir sind fertig.", "Wir haben alles besprochen."] },
    ],
  },

  goethe_b1_sprechen_teil2_folie1: {
    title: "Folie 1 - Einleitung",
    categories: [
      { label: "Einleitung", phrases: ["Ich möchte heute folgendes Thema präsentieren: …", "Zuerst spreche ich über meine persönlichen Erfahrungen, dann über die Situation in meinem Heimatland und meine Meinung."] },
    ],
  },
  goethe_b1_sprechen_teil2_folie2: {
    title: "Folie 2 - Eigene Erfahrung",
    categories: [
      { label: "Erfahrung", phrases: ["Was mich betrifft, ich …", "Ich habe einmal Folgendes erlebt: …"] },
    ],
  },
  goethe_b1_sprechen_teil2_folie3: {
    title: "Folie 3 - Situation im Heimatland",
    categories: [
      { label: "Situation", phrases: ["In meinem Heimatland …", "Bei uns …", "Hier haben wir folgende Situation: …"] },
    ],
  },
  goethe_b1_sprechen_teil2_folie4: {
    title: "Folie 4 - Vor-/Nachteile und Meinung",
    categories: [
      { label: "Vor-/Nachteile", phrases: ["Das hat folgenden Vorteil/Nachteil: …", "Meine persönliche Meinung dazu ist, dass …"] },
    ],
  },
  goethe_b1_sprechen_teil2_folie5: {
    title: "Folie 5 — Abschluss",
    categories: [
      { label: "Abschluss", phrases: ["Damit komme ich zum Schluss meiner Präsentation.", "Ich danke dir für dein Interesse. Wenn du Fragen hast, beantworte ich sie gern."] },
    ],
  },

  goethe_b1_sprechen_teil3: {
    title: "Kommentieren und eine Frage stellen",
    categories: [
      { label: "Kommentar", phrases: ["Deine Präsentation hat mir gut gefallen.", "Ich fand deine Präsentation wirklich interessant."] },
      { label: "Frage stellen", phrases: ["Ich habe nun folgende Frage: …", "Könntest du mir noch sagen, …?"] },
      { label: "Bedanken & antworten", phrases: ["Vielen Dank, das freut mich.", "Soviel ich weiß, …", "Ich bin nicht ganz sicher, aber ich glaube, dass …"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // ÖSD B2/J (Arena ÖSD B2) — SCHREIBEN
  // ═══════════════════════════════════════════════════════════
  oesd_b2_schreiben_beschwerde: {
    title: "Formelle Beschwerde-Mail",
    categories: [
      { label: "Anrede", phrases: ["Sehr geehrter Herr [Name],", "Sehr geehrte Frau [Name],", "Sehr geehrte Damen und Herren,"] },
      { label: "Einleitung", phrases: ["Mit diesem Schreiben möchte ich meine Unzufriedenheit über Ihre Dienste ausdrücken.", "In Ihrem Angebot las ich, dass … / Außerdem versprachen Sie …"] },
      { label: "Kontrast versprochen/real", phrases: ["In Wirklichkeit aber …", "Anders als versprochen …", "Was mich besonders geärgert hat, ist die Tatsache, dass …"] },
      { label: "Forderung", phrases: ["Aus diesem Grund möchte ich Sie um eine begründete Antwort bitten.", "Ich erwarte, dass Sie …"] },
      { label: "Schluss", phrases: ["Mit freundlichen Grüßen"] },
    ],
  },

  oesd_b2_schreiben_meinung: {
    title: "Persönliche Meinungsäußerung",
    categories: [
      { label: "Einleitung", phrases: ["Das Thema „…“ ist sicher interessant und immer aktuell.", "Besonders wichtig finde ich …, weil …"] },
      { label: "Argumentation", phrases: ["Ein weiterer wichtiger Aspekt ist …", "Man muss auch bedenken, dass …", "Natürlich kann man lange darüber diskutieren, ob …"] },
      { label: "Eigene Erfahrung", phrases: ["Aus eigener Erfahrung kann ich sagen, dass …", "Von Freunden habe ich gehört, dass …"] },
      { label: "Situation im eigenen Land", phrases: ["Bei uns in [Land] …", "Abschließend möchte ich kurz etwas über die Situation in meinem Land schreiben."] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // ÖSD B2/J — SPRECHEN
  // ═══════════════════════════════════════════════════════════
  oesd_b2_sprechen_kennenlernen: {
    title: "Jemanden kennenlernen und beraten",
    categories: [
      { label: "Einstieg", phrases: ["Ich heiße … und komme aus …", "Darf ich dich etwas fragen zu …?"] },
      { label: "Eigene Erfahrung teilen", phrases: ["Bei mir ist es so, dass …", "Ich habe die Erfahrung gemacht, dass …"] },
      { label: "Rat geben", phrases: ["An deiner Stelle würde ich …", "Ich würde dir empfehlen, …"] },
    ],
  },

  oesd_b2_sprechen_bild: {
    title: "Ein Bild beschreiben und interpretieren",
    categories: [
      { label: "Bildwahl begründen", phrases: ["Ich habe dieses Bild gewählt, weil … (es lebendig ist / ein aktuelles Thema präsentiert)"] },
      { label: "Beschreiben", phrases: ["Das Bild zeigt …"] },
      { label: "Interpretieren", phrases: ["Ich vermute / Es könnte sein, dass …"] },
      { label: "Titel kommentieren", phrases: ["Den Titel des Bildes finde ich originell / gut passend / nicht so passend, weil …"] },
    ],
  },

  oesd_b2_sprechen_meinungsaustausch: {
    title: "Meinungsaustausch",
    categories: [
      { label: "Position vertreten", phrases: ["Das Wichtigste bei diesem Thema ist …"] },
      { label: "Widersprechen", phrases: ["Ich bin anderer Meinung.", "Da muss ich dir widersprechen."] },
      { label: "Relativieren", phrases: ["Du vergisst, dass …", "Das ist zwar richtig, aber …"] },
      { label: "Zu bedenken geben", phrases: ["Bedenke bitte auch, dass …"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // GOETHE B2 — SCHREIBEN
  // ═══════════════════════════════════════════════════════════
  goethe_b2_schreiben_forumsbeitrag: {
    title: "Forumsbeitrag",
    categories: [
      { label: "Einleitung", phrases: ["Dieses Thema spielt im Alltag vieler Menschen eine große Rolle.", "Die Debatte über … ist aktueller denn je."] },
      { label: "Meinung äußern", phrases: ["Meiner Meinung nach …", "Ich bin der Ansicht, dass …", "Ich persönlich finde …"] },
      { label: "Begründen", phrases: ["Dafür gibt es mehrere Gründe: …", "Das liegt vor allem daran, dass …"] },
      { label: "Gegenposition einräumen", phrases: ["Obwohl vieles dafür spricht, gibt es auch Kritik.", "Nicht alle sind dieser Meinung."] },
      { label: "Schluss", phrases: ["Zusammenfassend lässt sich sagen, dass …", "Abschließend möchte ich betonen, dass …"] },
    ],
  },

  goethe_b2_schreiben_nachricht: {
    title: "Persönliche Nachricht",
    categories: [
      { label: "Anrede/Anlass", phrases: ["Ich schreibe Ihnen, weil …", "Leider muss ich Sie über Folgendes informieren: …"] },
      { label: "Problem schildern", phrases: ["Aufgrund eines Missverständnisses …", "Leider konnte ich nicht …, weil …"] },
      { label: "Bitte formulieren", phrases: ["Könnten Sie mir bitte … zusenden?", "Ich wäre Ihnen sehr dankbar, wenn …"] },
      { label: "Schluss", phrases: ["Vielen Dank im Voraus.", "Mit freundlichen Grüßen"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // GOETHE B2 — SPRECHEN
  // ═══════════════════════════════════════════════════════════
  goethe_b2_sprechen_monolog: {
    title: "Ein Thema präsentieren",
    categories: [
      { label: "Einleitung", phrases: ["In meinem Vortrag geht es um …", "Ich zeige Ihnen zuerst …, dann stelle ich Ihnen … vor."] },
      { label: "Hauptteil", phrases: ["Anschließend spreche ich über die Vor- und Nachteile.", "Ein Beispiel dafür ist …"] },
      { label: "Persönliche Erfahrung", phrases: ["Aus eigener Erfahrung kann ich sagen, dass …"] },
      { label: "Schluss", phrases: ["Zusammenfassend kann man sagen, dass …", "Mein Fazit ist, dass …"] },
    ],
  },

  goethe_b2_sprechen_diskussion: {
    title: "Diskussion führen",
    categories: [
      { label: "Standpunkt einbringen", phrases: ["Meiner Meinung nach …", "Ich bin (fest) davon überzeugt, dass …"] },
      { label: "Zustimmen/Widersprechen", phrases: ["Da stimme ich dir zu.", "Ich sehe das etwas anders."] },
      { label: "Verallgemeinerung vermeiden", phrases: ["Man darf das aber nicht verallgemeinern.", "Man muss verschiedene Aspekte beachten."] },
      { label: "Abschließen", phrases: ["Das ist meine ehrliche Meinung zu diesem Thema.", "Wie denkt ihr darüber?"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // TELC B1 — SCHREIBEN
  // ═══════════════════════════════════════════════════════════
  telc_b1_schreiben_email_informell: {
    title: "Persönliche E-Mail (informell)",
    categories: [
      { label: "Anrede", phrases: ["Liebe(r) [Name],", "Hallo [Name],"] },
      { label: "Einleitung", phrases: ["Vielen Dank für deine E-Mail, ich habe mich sehr gefreut.", "Wie geht es dir? Mir geht es …"] },
      { label: "Sachverhalt beschreiben", phrases: ["Ich wollte dir erzählen, dass …", "Bei mir ist Folgendes passiert: …"] },
      { label: "Begründen", phrases: ["Das liegt daran, dass …"] },
      { label: "Vorschlag machen", phrases: ["Ich schlage vor, dass wir …", "Hättest du Lust, mich zu besuchen?"] },
      { label: "Schluss", phrases: ["Ich freue mich auf deine Antwort.", "Liebe Grüße"] },
    ],
  },

  telc_b1_schreiben_internet_beitrag: {
    title: "Internet-Beitrag (Forum)",
    categories: [
      { label: "Einleitung", phrases: ["Ich habe den Beitrag von [Name] gelesen und möchte dazu Stellung nehmen."] },
      { label: "Eigene Meinung", phrases: ["Meiner Meinung nach …", "Ich finde, dass …"] },
      { label: "Begründung", phrases: ["Das sehe ich so, weil …"] },
      { label: "Schluss", phrases: ["Das ist zumindest meine Erfahrung / Meinung."] },
    ],
  },

  telc_b1_schreiben_email_formell: {
    title: "Formelle E-Mail (kurz)",
    categories: [
      { label: "Anrede", phrases: ["Sehr geehrte Frau [Name],", "Sehr geehrter Herr [Name],"] },
      { label: "Entschuldigung", phrases: ["Leider kann ich heute nicht … teilnehmen.", "Es tut mir leid, aber ich kann nicht …"] },
      { label: "Begründung", phrases: ["Der Grund dafür ist, dass …"] },
      { label: "Schluss", phrases: ["Mit freundlichen Grüßen"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // TELC B1 — SPRECHEN
  // ═══════════════════════════════════════════════════════════
  telc_b1_sprechen_kennenlernen: {
    title: "Einander kennenlernen",
    categories: [
      { label: "Sich vorstellen", phrases: ["Ich heiße … / Mein Name ist …", "Ich komme aus … und lerne seit … Deutsch."] },
      { label: "Über sich erzählen", phrases: ["Ich wohne in … mit …", "Ich habe (keine) Geschwister."] },
    ],
  },

  telc_b1_sprechen_thema: {
    title: "Über ein Thema sprechen",
    categories: [
      { label: "Text einführen", phrases: ["Ich habe einen Artikel über … gelesen.", "In dem Artikel steht, dass …"] },
      { label: "Meinung äußern", phrases: ["Ich finde, dass …", "Meiner Meinung nach …"] },
      { label: "Erfahrung teilen", phrases: ["Ich habe die Erfahrung gemacht, dass …"] },
      { label: "Vorschlag/Frage", phrases: ["Vielleicht könnte man …", "Was denkst du darüber?"] },
    ],
  },

  telc_b1_sprechen_planen: {
    title: "Gemeinsam etwas planen",
    categories: [
      { label: "Vorschlagen", phrases: ["Wie wäre es, wenn wir …?", "Ich schlage vor, dass …"] },
      { label: "Zustimmen", phrases: ["Das ist eine gute Idee.", "Einverstanden."] },
      { label: "Widersprechen", phrases: ["Ich bin nicht sicher, ob das gut ist.", "Ich hätte lieber …"] },
      { label: "Entscheiden", phrases: ["Also machen wir das so:", "Wir sind uns einig, dass …"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // TELC B2 — SCHREIBEN
  // ═══════════════════════════════════════════════════════════
  telc_b2_schreiben_brief: {
    title: "Formelle E-Mail / Brief",
    categories: [
      { label: "Anrede", phrases: ["Sehr geehrte Damen und Herren,", "Sehr geehrte Frau [Name],", "Sehr geehrter Herr [Name],"] },
      { label: "Einleitung (Bezug zur Anzeige)", phrases: ["Ihre Anzeige zu … habe ich mit Interesse gelesen.", "… als ich Ihre Anzeige las, war ich sofort interessiert."] },
      { label: "Nach Informationen fragen", phrases: ["Ich hätte gerne mehr Informationen über …", "Wäre es möglich, …?"] },
      { label: "Klärung einfordern", phrases: ["Mir ist allerdings nicht klar, ob/wie/wann …", "Es ist mir nicht ganz klar geworden, ob …"] },
      { label: "Schluss", phrases: ["Ich freue mich auf Ihre Antwort.", "Mit freundlichen Grüßen"] },
    ],
  },

  // ═══════════════════════════════════════════════════════════
  // TELC B2 — SPRECHEN
  // ═══════════════════════════════════════════════════════════
  telc_b2_sprechen_praesentation: {
    title: "Präsentation",
    categories: [
      { label: "Einleitung", phrases: ["Ich möchte dir von … erzählen.", "Mein Thema ist …"] },
      { label: "Hauptteil", phrases: ["Zuerst / Dann / Danach / Später …", "Ein wichtiger Punkt dabei war …"] },
      { label: "Persönliche Bewertung", phrases: ["Was mich betrifft, …", "Ich fand es besonders …, weil …"] },
    ],
  },

  telc_b2_sprechen_diskussion: {
    title: "Diskussion",
    categories: [
      { label: "Text einführen", phrases: ["Der Titel des Textes lautet „…“.", "Im Text geht es um die Frage, ob …"] },
      { label: "Nachfragen", phrases: ["Was denkst du darüber?", "Siehst du das auch so?", "Stimmst du mir zu?"] },
      { label: "Eigene Position", phrases: ["Ich sehe das anders, weil …", "Das stimmt, aber man muss auch bedenken, dass …"] },
    ],
  },
};

/**
 * Résout la clé de banque à utiliser selon le contexte de l'examen.
 * Retourne null si aucune correspondance connue (le panneau ne s'affiche
 * simplement pas dans ce cas — pas d'erreur bloquante).
 */
export function resolveMittelKey(params: {
  provider?: string; // "Goethe" | "TELC" | "ÖSD" | "OSD"
  cefrCode?: string; // "B1" | "B2"
  moduleSlug?: string; // "schreiben" | "sprechen" | ...
  formatType?: string; // format_type du teil
  teilNumber?: number;
}): string | null {
  const provider = (params.provider || "").toLowerCase();
  const cefr = (params.cefrCode || "").toLowerCase();
  const moduleSlug = (params.moduleSlug || "").toLowerCase();
  const formatType = (params.formatType || "").toLowerCase();
  const teil = params.teilNumber;

  const isGoethe = provider.includes("goethe") && !provider.includes("ösd") && !provider.includes("osd");
  const isOsd = provider.includes("ösd") || provider.includes("osd");
  const isTelc = provider.includes("telc");
  const isGoetheOrOsdB1 = (isGoethe || isOsd) && cefr === "b1";

  const isSchreiben = moduleSlug.includes("schreib") || moduleSlug.includes("schriftlich");
  const isSprechen =
    moduleSlug.includes("sprech") ||
    moduleSlug.includes("muendlich") ||
    moduleSlug.includes("mündlich");

  // ── Goethe / ÖSD B1 (Arena B1) ──────────────────────────
  if (isGoetheOrOsdB1) {
    if (isSchreiben) {
      if (teil === 1) return "goethe_b1_schreiben_email_informell";
      if (teil === 2) return "goethe_b1_schreiben_internet_beitrag";
      if (teil === 3) return "goethe_b1_schreiben_email_formell";
    }
    if (isSprechen) {
      if (teil === 1) return "goethe_b1_sprechen_teil1";
      if (teil === 3) return "goethe_b1_sprechen_teil3";
      // Teil 2 (Folien) est géré séparément par folie active — voir
      // resolveMittelKeyForFolie() ci-dessous.
    }
  }

  // ── ÖSD B2/J ─────────────────────────────────────────────
  if (isOsd && cefr === "b2") {
    if (isSchreiben) {
      if (teil === 1) return "oesd_b2_schreiben_beschwerde";
      if (teil === 2) return "oesd_b2_schreiben_meinung";
    }
    if (isSprechen) {
      if (formatType === "oral_kennenlernen") return "oesd_b2_sprechen_kennenlernen";
      if (formatType === "bildbeschreibung") return "oesd_b2_sprechen_bild";
      if (formatType === "oral_meinungsaustausch") return "oesd_b2_sprechen_meinungsaustausch";
    }
  }

  // ── Goethe B2 ────────────────────────────────────────────
  if (isGoethe && cefr === "b2") {
    if (isSchreiben) {
      if (teil === 1) return "goethe_b2_schreiben_forumsbeitrag";
      if (teil === 2) return "goethe_b2_schreiben_nachricht";
    }
    if (isSprechen) {
      if (formatType === "oral_monologue") return "goethe_b2_sprechen_monolog";
      if (formatType === "oral_discussion") return "goethe_b2_sprechen_diskussion";
    }
  }

  // ── TELC B1 ──────────────────────────────────────────────
  if (isTelc && cefr === "b1") {
    if (isSchreiben) {
      if (teil === 1) return "telc_b1_schreiben_email_informell";
      if (teil === 2) return "telc_b1_schreiben_internet_beitrag";
      if (teil === 3) return "telc_b1_schreiben_email_formell";
    }
    if (isSprechen) {
      if (formatType === "oral_kennenlernen") return "telc_b1_sprechen_kennenlernen";
      if (formatType === "oral_thema") return "telc_b1_sprechen_thema";
      if (formatType === "oral_interaction") return "telc_b1_sprechen_planen";
    }
  }

  // ── TELC B2 ──────────────────────────────────────────────
  if (isTelc && cefr === "b2") {
    if (isSchreiben) return "telc_b2_schreiben_brief";
    if (isSprechen) {
      if (formatType === "oral_monologue") return "telc_b2_sprechen_praesentation";
      if (formatType === "oral_discussion") return "telc_b2_sprechen_diskussion";
    }
  }

  return null;
}

/**
 * Cas particulier : Sprechen Teil 2 Goethe/ÖSD B1 a 5 banques distinctes,
 * une par Folie active (1 à 5).
 */
export function resolveMittelKeyForFolie(folieNumber: number): string | null {
  if (folieNumber >= 1 && folieNumber <= 5) {
    return `goethe_b1_sprechen_teil2_folie${folieNumber}`;
  }
  return null;
}