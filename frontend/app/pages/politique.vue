<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <div
          class="inline-flex items-center gap-2 bg-teal-50 text-teal-800 px-4 py-2 rounded-full text-sm font-semibold mb-4"
        >
          <i class="pi pi-shield"></i>
          <span>Vos données sont protégées</span>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
          Politique de confidentialité
        </h1>
        <p class="text-lg text-gray-600">
          Dernière mise à jour : 15 avril 2026
        </p>
      </div>

      <!-- Content -->
      <div class="bg-white rounded-2xl shadow-lg p-8 sm:p-12 space-y-12">
        <!-- Introduction -->
        <div>
          <p class="text-gray-700 leading-relaxed text-lg">
            Chez <strong>DeutschTest</strong>, nous prenons la protection de vos
            données personnelles très au sérieux. Cette politique de
            confidentialité explique quelles informations nous collectons,
            comment nous les utilisons, et quels sont vos droits concernant vos
            données.
          </p>
        </div>

        <Divider />

        <!-- Section 1 -->
        <div>
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <i class="pi pi-database text-white"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">
              1. Données collectées
            </h2>
          </div>

          <div class="space-y-4 text-gray-700 ml-13">
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">
                Données d'identification
              </h3>
              <ul class="list-disc list-inside space-y-1 ml-4">
                <li>Nom et prénom</li>
                <li>Adresse email</li>
                <li>Numéro de téléphone (optionnel)</li>
                <li>Pays de résidence</li>
              </ul>
            </div>

            <div>
              <h3 class="font-semibold text-gray-900 mb-2">
                Données de navigation
              </h3>
              <ul class="list-disc list-inside space-y-1 ml-4">
                <li>Adresse IP</li>
                <li>Type de navigateur et appareil</li>
                <li>Pages visitées et durée de visite</li>
              </ul>
            </div>

            <div>
              <h3 class="font-semibold text-gray-900 mb-2">Données d'examen</h3>
              <ul class="list-disc list-inside space-y-1 ml-4">
                <li>Réponses aux questions d'examen</li>
                <li>Enregistrements audio (expression orale)</li>
                <li>Productions écrites</li>
                <li>Scores et résultats détaillés</li>
              </ul>
            </div>
          </div>
        </div>

        <Divider />

        <!-- Section 2 -->
        <div>
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <i class="pi pi-cog text-white"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">
              2. Utilisation des données
            </h2>
          </div>

          <div class="space-y-3 text-gray-700 ml-13">
            <p>Nous utilisons vos données pour :</p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>
                <strong>Fournir nos services</strong> : créer votre compte,
                gérer vos examens, générer vos corrections IA
              </li>
              <li>
                <strong>Améliorer notre plateforme</strong> : analyser les
                performances, identifier les bugs
              </li>
              <li>
                <strong>Communiquer avec vous</strong> : emails de confirmation,
                notifications de résultats
              </li>
              <li>
                <strong>Sécurité</strong> : prévenir la fraude, protéger contre
                les abus
              </li>
            </ul>
          </div>
        </div>

        <Divider />

        <!-- Section 3 -->
        <div>
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <i class="pi pi-share-alt text-white"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">
              3. Partage des données
            </h2>
          </div>

          <div class="space-y-3 text-gray-700 ml-13">
            <p class="font-semibold text-lg">
              <strong>Nous ne vendons jamais vos données personnelles.</strong>
            </p>
            <p>Nous partageons vos données uniquement avec :</p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>
                <strong>Prestataires de services</strong> : hébergement,
                paiement, email, IA
              </li>
              <li><strong>Autorités légales</strong> : si requis par la loi</li>
            </ul>
          </div>
        </div>

        <Divider />

        <!-- Section 4 -->
        <div>
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <i class="pi pi-user text-white"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">4. Vos droits</h2>
          </div>

          <div class="space-y-4 text-gray-700 ml-13">
            <p>Vous disposez des droits suivants :</p>
            <div class="grid sm:grid-cols-2 gap-4">
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 mb-2">
                  ✓ Droit d'accès
                </h4>
                <p class="text-sm">Consulter vos données personnelles</p>
              </div>
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 mb-2">
                  ✓ Droit de rectification
                </h4>
                <p class="text-sm">Corriger vos informations</p>
              </div>
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 mb-2">
                  ✓ Droit d'effacement
                </h4>
                <p class="text-sm">Supprimer votre compte</p>
              </div>
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 mb-2">
                  ✓ Droit à la portabilité
                </h4>
                <p class="text-sm">Récupérer vos données</p>
              </div>
            </div>
            <div class="bg-teal-50 border-l-4 border-teal-600 p-4 rounded">
              <p class="font-semibold">Pour exercer vos droits</p>
              <p class="text-sm mt-1">
                Contactez-nous à
                <a
                  href="mailto:lfogouang39@gmail.com"
                  class="text-teal-700 font-semibold"
                  >lfogouang39@gmail.com</a
                >. Nous répondons sous 30 jours maximum.
              </p>
            </div>
          </div>
        </div>

        <Divider />

        <!-- Section 5 -->
        <div>
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <i class="pi pi-lock text-white"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">5. Sécurité</h2>
          </div>

          <div class="space-y-3 text-gray-700 ml-13">
            <p>Nous mettons en œuvre des mesures de sécurité strictes :</p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>
                <strong>Chiffrement SSL/TLS</strong> pour toutes les
                communications
              </li>
              <li>
                <strong>Mots de passe hashés</strong> avec algorithmes sécurisés
              </li>
              <li>
                <strong>Authentification à deux facteurs</strong> (2FA)
                disponible
              </li>
              <li><strong>Sauvegardes cryptées</strong> quotidiennes</li>
            </ul>
          </div>
        </div>

        <Divider />

        <!-- Contact -->
        <div
          class="bg-gradient-to-br from-teal-50 to-teal-100 p-8 rounded-xl border-2 border-teal-200"
        >
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <i class="pi pi-envelope text-white"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">Nous contacter</h2>
          </div>

          <div class="space-y-3 text-gray-700 ml-13">
            <p>
              Pour toute question concernant cette politique de confidentialité
              :
            </p>
            <div class="bg-white p-4 rounded-lg border border-teal-200">
              <p>
                <strong>Email</strong> :
                <a
                  href="mailto:lfogouang39@gmail.com"
                  class="text-teal-700 font-semibold"
                  >lfogouang39@gmail.com</a
                >
              </p>
              <p>
                <strong>Téléphone</strong> : +237 691 85 09 13 / +237 670 88 62
                88
              </p>
              <p><strong>Adresse</strong> : Yaoundé, Cameroun</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: "Politique de confidentialité - DeutschTest",
  meta: [
    {
      name: "description",
      content:
        "Politique de confidentialité de DeutschTest : protection des données, utilisation, conservation et vos droits.",
    },
  ],
});
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(
    135deg,
    hsl(145 63% 32%) 0%,
    hsl(145 50% 22%) 100%
  );
}
</style>
