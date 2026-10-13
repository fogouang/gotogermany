// app/config/site.ts
// Infos de marque centralisées (logo, nom, liens).
// Uniquement ce qui existe déjà dans nuxt.config.ts et les layouts.
export const SITE = {
  name: "GoToGermany",
  url: "https://prep-telc-osd.com",
  logo: "/images/logo.png",
  ogImage: "https://prep-telc-osd.com/images/og-image.png",
  twitter: "@GoToGermany",
  // Numéro au format international sans "+" ni espaces (tel: et wa.me)
  phone: "237691850913",
  phoneLabel: "+237 691 85 09 13",
  email: "lfogouang39@gmail.com",
  phone2Label: "+237 670 88 62 88",
  // Communauté WhatsApp : rejointe librement via le lien d'invitation
  whatsappCommunity: "https://chat.whatsapp.com/CxUdtE70ckv66iQjikHqBF",

  // Réseaux sociaux : laisser vide tant que la page n'existe pas (masqué)
  social: {
    facebook: "",
    instagram: "",
    linkedin: "",
    tiktok: "",
  },
} as const;
