export type Langue = "fr" | "en" | "de";

export interface SectionConditions {
  id: string;
  titre: string;
  paragraphes?: string[];
  liste?: string[];
  lien?: { label: string; to: string };
}

export interface ConditionsContenu {
  seoTitre: string;
  seoDescription: string;
  eyebrow: string;
  titre: string;
  intro: string;
  maj: string;
  sommaire: string;
  sections: SectionConditions[];
  contact: {
    titre: string;
    texte: string;
    email: string;
    whatsapp: string;
    telephone: string;
  };
}

export const CONTACT_CONDITIONS = {
  email: "lfogouang39@gmail.com",
  whatsapp: "237691850913",
  telephones: ["+237 691 85 09 13", "+237 670 88 62 88"],
  ville: "Yaoundé, Cameroun",
};

export const CONDITIONS: Record<Langue, ConditionsContenu> = {
  fr: {
    seoTitre: "Conditions d'utilisation | GoToGermany",
    seoDescription:
      "Les règles d'utilisation de GoToGermany : compte, abonnements, outils IA, contenus et responsabilités.",
    eyebrow: "Informations légales",
    titre: "Conditions d'utilisation",
    intro:
      "Ces conditions encadrent l'utilisation de GoToGermany. En créant un compte ou en utilisant la plateforme, vous les acceptez.",
    maj: "Dernière mise à jour : 10 octobre 2026",
    sommaire: "Sommaire",
    sections: [
      {
        id: "service",
        titre: "1. Le service",
        paragraphes: [
          "GoToGermany est une plateforme de préparation aux examens d'allemand Goethe, telc, ÖSD, TestDaF et ECL.",
          "Les sujets proposés reprennent le format officiel des examens, mais ce ne sont pas des examens officiels. GoToGermany n'est affilié à aucun de ces organismes et ne délivre aucun certificat. Les noms et logos des organismes appartiennent à leurs propriétaires respectifs.",
        ],
      },
      {
        id: "compte",
        titre: "2. Votre compte",
        liste: [
          "Les informations fournies à l'inscription doivent être exactes.",
          "Vous êtes responsable de la confidentialité de votre mot de passe et de toute activité sur votre compte.",
          "Chaque compte est personnel. Le nombre d'appareils connectés par compte est limité, et le partage d'un compte est interdit.",
          "Un compte peut être créé ou activé par un centre partenaire. Dans ce cas, le centre a accès à vos résultats.",
        ],
      },
      {
        id: "abonnements",
        titre: "3. Abonnements et paiement",
        liste: [
          "Les formules payantes, leurs prix et leur durée sont indiqués sur la page Tarifs.",
          "L'accès est activé dès la confirmation du paiement, pour la durée de la formule choisie.",
          "Les paiements Mobile Money sont traités par notre prestataire pawaPay.",
        ],
      },
      {
        id: "ia",
        titre: "4. Outils d'intelligence artificielle",
        paragraphes: [
          "La correction des productions écrites (Schreiben) et le simulateur d'expression orale (Sprechen) utilisent l'intelligence artificielle et fonctionnent avec des crédits IA.",
          "Les notes et commentaires produits par ces outils sont indicatifs. Ils vous aident à progresser, mais ne remplacent pas l'évaluation d'un examinateur officiel.",
        ],
      },
      {
        id: "contenus",
        titre: "5. Contenus et propriété",
        paragraphes: [
          "Les sujets, audios, corrigés et autres contenus de la plateforme sont réservés à votre usage personnel de préparation.",
        ],
        liste: [
          "Il est interdit de les copier, télécharger en masse, revendre ou diffuser, en tout ou en partie.",
          "Il est interdit d'utiliser des outils automatisés pour extraire les contenus.",
        ],
      },
      {
        id: "usage",
        titre: "6. Utilisation acceptable",
        liste: [
          "Ne pas contourner la limite d'appareils ni les mesures de sécurité.",
          "Ne pas perturber le fonctionnement de la plateforme.",
          "Ne pas utiliser le service à des fins illégales.",
        ],
        paragraphes: [
          "En cas de non-respect de ces conditions, notamment de partage de compte, l'accès au compte peut être suspendu.",
        ],
      },
      {
        id: "responsabilite",
        titre: "7. Responsabilité",
        paragraphes: [
          "GoToGermany vous aide à vous préparer, mais la réussite à un examen dépend de votre travail et de la décision des examinateurs. Aucun résultat n'est garanti.",
          "Nous faisons notre possible pour que la plateforme reste disponible, sans pouvoir exclure des interruptions, par exemple pour maintenance.",
        ],
      },
      {
        id: "donnees",
        titre: "8. Données personnelles",
        paragraphes: [
          "La façon dont nous collectons et utilisons vos données est décrite dans notre politique de confidentialité.",
        ],
        lien: { label: "Lire la politique de confidentialité", to: "/politique" },
      },
      {
        id: "modifications",
        titre: "9. Modification des conditions",
        paragraphes: [
          "Ces conditions peuvent évoluer. La date de dernière mise à jour figure en haut de cette page.",
        ],
      },
    ],
    contact: {
      titre: "Une question sur ces conditions ?",
      texte: "Notre équipe vous répond par e-mail, WhatsApp ou téléphone.",
      email: "Écrire un e-mail",
      whatsapp: "WhatsApp",
      telephone: "Téléphone",
    },
  },

  en: {
    seoTitre: "Terms of use | GoToGermany",
    seoDescription:
      "The rules for using GoToGermany: account, plans, AI tools, content and responsibilities.",
    eyebrow: "Legal information",
    titre: "Terms of use",
    intro:
      "These terms govern the use of GoToGermany. By creating an account or using the platform, you accept them.",
    maj: "Last updated: October 10, 2026",
    sommaire: "Contents",
    sections: [
      {
        id: "service",
        titre: "1. The service",
        paragraphes: [
          "GoToGermany is a preparation platform for the Goethe, telc, ÖSD, TestDaF and ECL German exams.",
          "Our papers follow the official exam format, but they are not official exams. GoToGermany is not affiliated with any of these bodies and does not issue certificates. The names and logos of these bodies belong to their respective owners.",
        ],
      },
      {
        id: "compte",
        titre: "2. Your account",
        liste: [
          "The information you provide when signing up must be accurate.",
          "You are responsible for keeping your password confidential and for all activity on your account.",
          "Each account is personal. The number of devices per account is limited, and sharing an account is not allowed.",
          "An account may be created or activated by a partner centre. In that case, the centre can see your results.",
        ],
      },
      {
        id: "abonnements",
        titre: "3. Plans and payment",
        liste: [
          "Paid plans, their prices and their duration are shown on the Pricing page.",
          "Access is activated as soon as payment is confirmed, for the duration of the chosen plan.",
          "Mobile Money payments are processed by our provider pawaPay.",
        ],
      },
      {
        id: "ia",
        titre: "4. Artificial intelligence tools",
        paragraphes: [
          "Writing correction (Schreiben) and the speaking simulator (Sprechen) use artificial intelligence and run on AI credits.",
          "Scores and feedback from these tools are indicative. They help you improve, but they do not replace the assessment of an official examiner.",
        ],
      },
      {
        id: "contenus",
        titre: "5. Content and ownership",
        paragraphes: [
          "Papers, audio, answer keys and other platform content are for your personal exam preparation only.",
        ],
        liste: [
          "You may not copy, bulk download, resell or distribute them, in whole or in part.",
          "You may not use automated tools to extract content.",
        ],
      },
      {
        id: "usage",
        titre: "6. Acceptable use",
        liste: [
          "Do not bypass the device limit or security measures.",
          "Do not disrupt the operation of the platform.",
          "Do not use the service for illegal purposes.",
        ],
        paragraphes: [
          "If these terms are not respected, in particular in case of account sharing, access to the account may be suspended.",
        ],
      },
      {
        id: "responsabilite",
        titre: "7. Liability",
        paragraphes: [
          "GoToGermany helps you prepare, but passing an exam depends on your work and on the examiners' decision. No result is guaranteed.",
          "We do our best to keep the platform available, but interruptions may occur, for example for maintenance.",
        ],
      },
      {
        id: "donnees",
        titre: "8. Personal data",
        paragraphes: [
          "How we collect and use your data is described in our privacy policy.",
        ],
        lien: { label: "Read the privacy policy", to: "/politique" },
      },
      {
        id: "modifications",
        titre: "9. Changes to these terms",
        paragraphes: [
          "These terms may change. The date of the last update is shown at the top of this page.",
        ],
      },
    ],
    contact: {
      titre: "A question about these terms?",
      texte: "Our team answers by email, WhatsApp or phone.",
      email: "Send an email",
      whatsapp: "WhatsApp",
      telephone: "Phone",
    },
  },

  de: {
    seoTitre: "Nutzungsbedingungen | GoToGermany",
    seoDescription:
      "Die Regeln für die Nutzung von GoToGermany: Konto, Tarife, KI-Werkzeuge, Inhalte und Verantwortung.",
    eyebrow: "Rechtliche Informationen",
    titre: "Nutzungsbedingungen",
    intro:
      "Diese Bedingungen regeln die Nutzung von GoToGermany. Mit der Erstellung eines Kontos oder der Nutzung der Plattform akzeptieren Sie sie.",
    maj: "Zuletzt aktualisiert: 10. Oktober 2026",
    sommaire: "Inhalt",
    sections: [
      {
        id: "service",
        titre: "1. Der Dienst",
        paragraphes: [
          "GoToGermany ist eine Plattform zur Vorbereitung auf die Deutschprüfungen von Goethe, telc, ÖSD, TestDaF und ECL.",
          "Unsere Modelltests folgen dem offiziellen Prüfungsformat, sind aber keine offiziellen Prüfungen. GoToGermany ist mit keiner dieser Institutionen verbunden und stellt keine Zertifikate aus. Namen und Logos der Institutionen gehören ihren jeweiligen Inhabern.",
        ],
      },
      {
        id: "compte",
        titre: "2. Ihr Konto",
        liste: [
          "Die Angaben bei der Registrierung müssen korrekt sein.",
          "Sie sind für die Geheimhaltung Ihres Passworts und für alle Aktivitäten in Ihrem Konto verantwortlich.",
          "Jedes Konto ist persönlich. Die Anzahl der Geräte pro Konto ist begrenzt, und die Weitergabe eines Kontos ist untersagt.",
          "Ein Konto kann von einem Partnerzentrum erstellt oder aktiviert werden. In diesem Fall sieht das Zentrum Ihre Ergebnisse.",
        ],
      },
      {
        id: "abonnements",
        titre: "3. Tarife und Zahlung",
        liste: [
          "Die kostenpflichtigen Tarife, ihre Preise und ihre Laufzeit stehen auf der Seite Preise.",
          "Der Zugang wird sofort nach Zahlungsbestätigung für die Laufzeit des gewählten Tarifs freigeschaltet.",
          "Mobile-Money-Zahlungen werden von unserem Dienstleister pawaPay abgewickelt.",
        ],
      },
      {
        id: "ia",
        titre: "4. Werkzeuge mit künstlicher Intelligenz",
        paragraphes: [
          "Die Korrektur schriftlicher Texte (Schreiben) und der Sprechsimulator (Sprechen) nutzen künstliche Intelligenz und funktionieren mit KI-Guthaben.",
          "Die Bewertungen und Rückmeldungen dieser Werkzeuge sind Richtwerte. Sie helfen Ihnen beim Lernen, ersetzen aber nicht die Bewertung durch offizielle Prüfer.",
        ],
      },
      {
        id: "contenus",
        titre: "5. Inhalte und Eigentum",
        paragraphes: [
          "Modelltests, Audios, Lösungen und andere Inhalte der Plattform sind ausschließlich für Ihre persönliche Prüfungsvorbereitung bestimmt.",
        ],
        liste: [
          "Es ist untersagt, sie ganz oder teilweise zu kopieren, massenhaft herunterzuladen, weiterzuverkaufen oder zu verbreiten.",
          "Es ist untersagt, automatisierte Werkzeuge zum Auslesen der Inhalte zu verwenden.",
        ],
      },
      {
        id: "usage",
        titre: "6. Zulässige Nutzung",
        liste: [
          "Die Gerätebegrenzung und Sicherheitsmaßnahmen nicht umgehen.",
          "Den Betrieb der Plattform nicht stören.",
          "Den Dienst nicht für rechtswidrige Zwecke nutzen.",
        ],
        paragraphes: [
          "Bei Verstößen gegen diese Bedingungen, insbesondere bei Weitergabe des Kontos, kann der Zugang zum Konto gesperrt werden.",
        ],
      },
      {
        id: "responsabilite",
        titre: "7. Haftung",
        paragraphes: [
          "GoToGermany unterstützt Ihre Vorbereitung, aber das Bestehen einer Prüfung hängt von Ihrer Arbeit und der Entscheidung der Prüfer ab. Ein Ergebnis wird nicht garantiert.",
          "Wir bemühen uns, die Plattform verfügbar zu halten, Unterbrechungen, zum Beispiel für Wartungsarbeiten, sind jedoch möglich.",
        ],
      },
      {
        id: "donnees",
        titre: "8. Personenbezogene Daten",
        paragraphes: [
          "Wie wir Ihre Daten erheben und verwenden, ist in unserer Datenschutzerklärung beschrieben.",
        ],
        lien: { label: "Datenschutzerklärung lesen", to: "/politique" },
      },
      {
        id: "modifications",
        titre: "9. Änderungen der Bedingungen",
        paragraphes: [
          "Diese Bedingungen können sich ändern. Das Datum der letzten Aktualisierung steht oben auf dieser Seite.",
        ],
      },
    ],
    contact: {
      titre: "Fragen zu diesen Bedingungen?",
      texte: "Unser Team antwortet per E-Mail, WhatsApp oder Telefon.",
      email: "E-Mail schreiben",
      whatsapp: "WhatsApp",
      telephone: "Telefon",
    },
  },
};