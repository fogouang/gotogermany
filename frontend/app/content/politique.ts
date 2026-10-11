// app/content/politique.ts
// Politique de confidentialité, une version par langue.
// Les textes peuvent contenir du HTML simple (<strong>, <a>).

export interface PolitiqueSection {
  id: string;
  icone: string;
  titre: string;
  intro?: string;
  important?: string;
  groupes?: { titre?: string; items: string[] }[];
  droits?: { titre: string; texte: string }[];
  encadre?: { titre: string; texte: string };
}

export interface PolitiqueContenu {
  metaTitre: string;
  metaDescription: string;
  badge: string;
  titre: string;
  majLabel: string;
  maj: string;
  sommaire: string;
  introduction: string;
  sections: PolitiqueSection[];
  contact: {
    titre: string;
    intro: string;
    email: string;
    telephone: string;
    adresse: string;
    adresseValeur: string;
  };
}

const EMAIL = "lfogouang39@gmail.com";
const lienEmail = `<a href="mailto:${EMAIL}">${EMAIL}</a>`;

export const POLITIQUE: Record<"fr" | "en" | "de", PolitiqueContenu> = {
  // ───────────────────────── FRANÇAIS ─────────────────────────
  fr: {
    metaTitre: "Politique de confidentialité · GoToGermany",
    metaDescription:
      "Politique de confidentialité de GoToGermany : données collectées, utilisation, partage, sécurité et vos droits.",
    badge: "Vos données sont protégées",
    titre: "Politique de confidentialité",
    majLabel: "Dernière mise à jour",
    maj: "10 octobre 2026",
    sommaire: "Sommaire",
    introduction:
      "Chez <strong>GoToGermany</strong>, nous prenons la protection de vos données personnelles très au sérieux. Cette politique explique quelles informations nous collectons, comment nous les utilisons, avec qui nous les partageons, et quels sont vos droits.",
    sections: [
      {
        id: "donnees",
        icone: "pi pi-database",
        titre: "Données collectées",
        groupes: [
          {
            titre: "Données d'identification",
            items: ["Nom et prénom", "Adresse email", "Numéro de téléphone"],
          },
          {
            titre: "Données de connexion et de navigation",
            items: [
              "Adresse IP",
              "Type de navigateur et d'appareil, ainsi qu'un identifiant d'appareil utilisé pour appliquer la limite d'appareils par compte",
              "Pages visitées et durée de visite",
            ],
          },
          {
            titre: "Données d'examen",
            items: [
              "Réponses aux questions d'examen",
              "Productions écrites (Schreiben)",
              "Enregistrements audio des exercices d'expression orale (Sprechen) et des sessions live",
              "Scores et résultats détaillés",
            ],
          },
          {
            titre: "Données de paiement",
            items: [
              "Historique de vos paiements (montant, date, moyen de paiement)",
              "Vos données de carte ou de compte Mobile Money sont traitées par notre prestataire de paiement : <strong>GoToGermany ne les conserve pas</strong>",
            ],
          },
        ],
      },
      {
        id: "utilisation",
        icone: "pi pi-cog",
        titre: "Utilisation des données",
        intro: "Nous utilisons vos données pour :",
        groupes: [
          {
            items: [
              "<strong>Fournir nos services</strong> : créer votre compte, gérer vos examens, générer vos corrections",
              "<strong>Améliorer la plateforme</strong> : analyser les performances, corriger les bugs",
              "<strong>Communiquer avec vous</strong> : emails de confirmation, notifications de résultats",
              "<strong>Sécurité</strong> : prévenir la fraude et le partage de comptes",
            ],
          },
        ],
      },
      {
        id: "partage",
        icone: "pi pi-share-alt",
        titre: "Partage des données",
        important: "Nous ne vendons jamais vos données personnelles.",
        intro: "Vos données sont partagées uniquement avec :",
        groupes: [
          {
            items: [
              "<strong>Votre centre de formation</strong>, si votre compte a été créé ou activé par lui : il voit votre progression et vos résultats pour assurer votre suivi",
              "<strong>Nos prestataires techniques</strong> : hébergement des serveurs, paiement (pawaPay), envoi d'emails",
              "<strong>Nos fournisseurs d'intelligence artificielle</strong> (Anthropic et Google), uniquement pour la correction de vos productions écrites et le simulateur d'oral",
              "<strong>Les autorités</strong>, uniquement si la loi l'exige",
            ],
          },
        ],
      },
      {
        id: "droits",
        icone: "pi pi-user",
        titre: "Vos droits",
        intro: "Vous disposez des droits suivants sur vos données :",
        droits: [
          { titre: "Droit d'accès", texte: "Consulter vos données personnelles" },
          { titre: "Droit de rectification", texte: "Corriger vos informations" },
          { titre: "Droit d'effacement", texte: "Supprimer votre compte et vos données" },
          { titre: "Droit à la portabilité", texte: "Récupérer vos données" },
        ],
        encadre: {
          titre: "Pour exercer vos droits",
          texte: `Écrivez-nous à ${lienEmail}. Nous répondons sous 30 jours maximum.`,
        },
      },
      {
        id: "securite",
        icone: "pi pi-lock",
        titre: "Sécurité",
        intro: "Nous mettons en œuvre les mesures suivantes pour protéger vos données :",
        groupes: [
          {
            items: [
              "<strong>Chiffrement HTTPS</strong> de toutes les communications",
              "<strong>Mots de passe chiffrés</strong> : ils ne sont jamais stockés en clair",
              "<strong>Accès selon le rôle</strong> : chaque utilisateur ne voit que ses propres données, et un centre uniquement celles de ses étudiants",
              "<strong>Limite d'appareils par compte</strong>, pour empêcher le partage d'identifiants",
              "<strong>Sauvegardes régulières</strong> de la base de données",
            ],
          },
        ],
      },
    ],
    contact: {
      titre: "Nous contacter",
      intro: "Pour toute question concernant cette politique de confidentialité :",
      email: "Email",
      telephone: "Téléphone",
      adresse: "Adresse",
      adresseValeur: "Yaoundé, Cameroun",
    },
  },

  // ───────────────────────── ENGLISH ─────────────────────────
  en: {
    metaTitre: "Privacy policy · GoToGermany",
    metaDescription:
      "GoToGermany privacy policy: data collected, use, sharing, security and your rights.",
    badge: "Your data is protected",
    titre: "Privacy policy",
    majLabel: "Last updated",
    maj: "October 10, 2026",
    sommaire: "Contents",
    introduction:
      "At <strong>GoToGermany</strong>, we take the protection of your personal data very seriously. This policy explains what information we collect, how we use it, who we share it with, and what your rights are.",
    sections: [
      {
        id: "donnees",
        icone: "pi pi-database",
        titre: "Data we collect",
        groupes: [
          {
            titre: "Identification data",
            items: ["First and last name", "Email address", "Phone number"],
          },
          {
            titre: "Login and browsing data",
            items: [
              "IP address",
              "Browser and device type, plus a device identifier used to enforce the device limit per account",
              "Pages visited and time spent",
            ],
          },
          {
            titre: "Exam data",
            items: [
              "Answers to exam questions",
              "Written work (Schreiben)",
              "Audio recordings of speaking exercises (Sprechen) and live sessions",
              "Scores and detailed results",
            ],
          },
          {
            titre: "Payment data",
            items: [
              "Your payment history (amount, date, payment method)",
              "Your card or Mobile Money account details are processed by our payment provider: <strong>GoToGermany does not store them</strong>",
            ],
          },
        ],
      },
      {
        id: "utilisation",
        icone: "pi pi-cog",
        titre: "How we use your data",
        intro: "We use your data to:",
        groupes: [
          {
            items: [
              "<strong>Provide our services</strong>: create your account, manage your exams, generate your corrections",
              "<strong>Improve the platform</strong>: analyse performance, fix bugs",
              "<strong>Communicate with you</strong>: confirmation emails, result notifications",
              "<strong>Security</strong>: prevent fraud and account sharing",
            ],
          },
        ],
      },
      {
        id: "partage",
        icone: "pi pi-share-alt",
        titre: "Data sharing",
        important: "We never sell your personal data.",
        intro: "Your data is shared only with:",
        groupes: [
          {
            items: [
              "<strong>Your training centre</strong>, if your account was created or activated by it: it can see your progress and results in order to follow you",
              "<strong>Our technical providers</strong>: server hosting, payment (pawaPay), email delivery",
              "<strong>Our artificial intelligence providers</strong> (Anthropic and Google), only to correct your written work and run the speaking simulator",
              "<strong>Authorities</strong>, only when required by law",
            ],
          },
        ],
      },
      {
        id: "droits",
        icone: "pi pi-user",
        titre: "Your rights",
        intro: "You have the following rights over your data:",
        droits: [
          { titre: "Right of access", texte: "View your personal data" },
          { titre: "Right to rectification", texte: "Correct your information" },
          { titre: "Right to erasure", texte: "Delete your account and your data" },
          { titre: "Right to portability", texte: "Get a copy of your data" },
        ],
        encadre: {
          titre: "To exercise your rights",
          texte: `Write to us at ${lienEmail}. We reply within 30 days at most.`,
        },
      },
      {
        id: "securite",
        icone: "pi pi-lock",
        titre: "Security",
        intro: "We use the following measures to protect your data:",
        groupes: [
          {
            items: [
              "<strong>HTTPS encryption</strong> for all communications",
              "<strong>Encrypted passwords</strong>: they are never stored in plain text",
              "<strong>Role-based access</strong>: each user only sees their own data, and a centre only sees its own students",
              "<strong>Device limit per account</strong>, to prevent credential sharing",
              "<strong>Regular backups</strong> of the database",
            ],
          },
        ],
      },
    ],
    contact: {
      titre: "Contact us",
      intro: "For any question about this privacy policy:",
      email: "Email",
      telephone: "Phone",
      adresse: "Address",
      adresseValeur: "Yaoundé, Cameroon",
    },
  },

  // ───────────────────────── DEUTSCH ─────────────────────────
  de: {
    metaTitre: "Datenschutzerklärung · GoToGermany",
    metaDescription:
      "Datenschutzerklärung von GoToGermany: erhobene Daten, Nutzung, Weitergabe, Sicherheit und Ihre Rechte.",
    badge: "Ihre Daten sind geschützt",
    titre: "Datenschutzerklärung",
    majLabel: "Zuletzt aktualisiert",
    maj: "10. Oktober 2026",
    sommaire: "Inhalt",
    introduction:
      "Bei <strong>GoToGermany</strong> nehmen wir den Schutz Ihrer personenbezogenen Daten sehr ernst. Diese Erklärung beschreibt, welche Informationen wir erheben, wie wir sie nutzen, an wen wir sie weitergeben und welche Rechte Sie haben.",
    sections: [
      {
        id: "donnees",
        icone: "pi pi-database",
        titre: "Erhobene Daten",
        groupes: [
          {
            titre: "Identifikationsdaten",
            items: ["Vor- und Nachname", "E-Mail-Adresse", "Telefonnummer"],
          },
          {
            titre: "Anmelde- und Nutzungsdaten",
            items: [
              "IP-Adresse",
              "Browser- und Gerätetyp sowie eine Gerätekennung, mit der die Begrenzung der Geräte pro Konto umgesetzt wird",
              "Besuchte Seiten und Verweildauer",
            ],
          },
          {
            titre: "Prüfungsdaten",
            items: [
              "Antworten auf Prüfungsfragen",
              "Schriftliche Arbeiten (Schreiben)",
              "Audioaufnahmen der Sprechübungen (Sprechen) und der Live-Sitzungen",
              "Punktzahlen und detaillierte Ergebnisse",
            ],
          },
          {
            titre: "Zahlungsdaten",
            items: [
              "Ihr Zahlungsverlauf (Betrag, Datum, Zahlungsmethode)",
              "Ihre Karten- oder Mobile-Money-Daten werden von unserem Zahlungsdienstleister verarbeitet: <strong>GoToGermany speichert sie nicht</strong>",
            ],
          },
        ],
      },
      {
        id: "utilisation",
        icone: "pi pi-cog",
        titre: "Nutzung der Daten",
        intro: "Wir nutzen Ihre Daten, um:",
        groupes: [
          {
            items: [
              "<strong>Unsere Dienste bereitzustellen</strong>: Ihr Konto zu erstellen, Ihre Prüfungen zu verwalten, Ihre Korrekturen zu erstellen",
              "<strong>Die Plattform zu verbessern</strong>: Leistung zu analysieren, Fehler zu beheben",
              "<strong>Mit Ihnen zu kommunizieren</strong>: Bestätigungs-E-Mails, Benachrichtigungen über Ergebnisse",
              "<strong>Sicherheit zu gewährleisten</strong>: Betrug und die Weitergabe von Konten zu verhindern",
            ],
          },
        ],
      },
      {
        id: "partage",
        icone: "pi pi-share-alt",
        titre: "Weitergabe der Daten",
        important: "Wir verkaufen Ihre personenbezogenen Daten niemals.",
        intro: "Ihre Daten werden ausschließlich weitergegeben an:",
        groupes: [
          {
            items: [
              "<strong>Ihr Sprachzentrum</strong>, wenn es Ihr Konto erstellt oder aktiviert hat: Es sieht Ihren Fortschritt und Ihre Ergebnisse, um Sie zu begleiten",
              "<strong>Unsere technischen Dienstleister</strong>: Server-Hosting, Zahlung (pawaPay), E-Mail-Versand",
              "<strong>Unsere KI-Anbieter</strong> (Anthropic und Google), ausschließlich für die Korrektur Ihrer schriftlichen Arbeiten und den Sprechsimulator",
              "<strong>Behörden</strong>, nur wenn das Gesetz es verlangt",
            ],
          },
        ],
      },
      {
        id: "droits",
        icone: "pi pi-user",
        titre: "Ihre Rechte",
        intro: "Sie haben folgende Rechte an Ihren Daten:",
        droits: [
          { titre: "Auskunftsrecht", texte: "Ihre personenbezogenen Daten einsehen" },
          { titre: "Recht auf Berichtigung", texte: "Ihre Angaben korrigieren" },
          { titre: "Recht auf Löschung", texte: "Ihr Konto und Ihre Daten löschen" },
          { titre: "Recht auf Datenübertragbarkeit", texte: "Eine Kopie Ihrer Daten erhalten" },
        ],
        encadre: {
          titre: "So üben Sie Ihre Rechte aus",
          texte: `Schreiben Sie uns an ${lienEmail}. Wir antworten innerhalb von höchstens 30 Tagen.`,
        },
      },
      {
        id: "securite",
        icone: "pi pi-lock",
        titre: "Sicherheit",
        intro: "Wir setzen folgende Maßnahmen zum Schutz Ihrer Daten ein:",
        groupes: [
          {
            items: [
              "<strong>HTTPS-Verschlüsselung</strong> aller Verbindungen",
              "<strong>Verschlüsselte Passwörter</strong>: Sie werden niemals im Klartext gespeichert",
              "<strong>Rollenbasierter Zugriff</strong>: Jede Person sieht nur ihre eigenen Daten, ein Zentrum nur die seiner Lernenden",
              "<strong>Gerätebegrenzung pro Konto</strong>, um die Weitergabe von Zugangsdaten zu verhindern",
              "<strong>Regelmäßige Sicherungen</strong> der Datenbank",
            ],
          },
        ],
      },
    ],
    contact: {
      titre: "Kontakt",
      intro: "Bei Fragen zu dieser Datenschutzerklärung:",
      email: "E-Mail",
      telephone: "Telefon",
      adresse: "Adresse",
      adresseValeur: "Yaoundé, Kamerun",
    },
  },
};

export const CONTACT_POLITIQUE = {
  email: EMAIL,
  telephones: ["+237 691 85 09 13", "+237 670 88 62 88"],
};