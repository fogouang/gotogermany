<template>
  <div class="overflow-hidden">

    <!-- ── Hero ─────────────────────────────────────────── -->
    <section class="relative min-h-[70vh] flex items-center justify-center text-white overflow-hidden "
      style="background: linear-gradient(135deg, #0d6e4f 0%, #064e3b 60%, #0d6e4f 100%);">

      <!-- Grille de fond -->
      <div class="absolute inset-0 opacity-10"
        style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;" />

      <!-- Cercles décoratifs animés -->
      <div class="absolute top-20 right-20 w-64 h-64 rounded-full blur-3xl animate-pulse-slow"
        style="background: radial-gradient(circle, rgba(245,158,11,0.3), transparent);" />
      <div class="absolute bottom-10 left-10 w-48 h-48 rounded-full blur-3xl animate-pulse-slow-delay"
        style="background: radial-gradient(circle, rgba(245,158,11,0.2), transparent);" />

      <div class="relative max-w-4xl mx-auto px-6 text-center">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-8 animate-fade-down"
          style="background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.4); color: #F59E0B;">
          <i class="pi pi-star-fill text-xs"></i>
          <span>Plateforme officielle de préparation</span>
        </div>

        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold mb-6 leading-tight animate-fade-up">
          Réussissez votre<br/>
          <span style="color: #F59E0B;">examen d'allemand</span>
        </h1>

        <p class="text-xl text-white/75 max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-up-delay">
          GoToGermany vous propose des simulations conformes aux examens officiels Goethe, ÖSD et TELC.
          Préparez-vous aux niveaux B1 et B2 avec des tests réalistes et des corrections intelligentes.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center animate-fade-up-delay-2 mb-16">
          <NuxtLink to="/tarifs"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition-all duration-300 hover:scale-105 hover:shadow-xl"
            style="background: #F59E0B; color: #064e3b;">
            Commencer maintenant <i class="pi pi-arrow-right"></i>
          </NuxtLink>
          <NuxtLink to="/dashboard/examens"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition-all duration-300 hover:scale-105"
            style="background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.3); color: white; backdrop-filter: blur(4px);">
            Voir les examens <i class="pi pi-eye"></i>
          </NuxtLink>
        </div>
      </div>

      <!-- Wave -->
      <div class="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 80" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full">
          <path d="M0 0L60 8C120 16 240 32 360 37.3C480 43 600 37 720 32C840 27 960 21 1080 21.3C1200 21 1320 27 1380 29.3L1440 32V80H0V0Z" fill="white"/>
        </svg>
      </div>
    </section>

    <!-- ── Stats ─────────────────────────────────────────── -->
    <section class="py-16 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-8">
          <div v-for="stat in stats" :key="stat.label"
            class="text-center group hover:scale-105 transition-transform duration-300">
            <div class="text-4xl sm:text-5xl font-extrabold mb-2"
              style="background: linear-gradient(135deg, #0d6e4f, #F59E0B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
              {{ stat.value }}
            </div>
            <p class="text-gray-500 text-sm font-medium">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Ce qu'on propose ──────────────────────────────── -->
    <section class="py-20 bg-gray-50">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16">
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-4"
            style="background: #e6f4ef; color: #0d6e4f;">
            <i class="pi pi-book"></i> Notre offre
          </div>
          <h2 class="text-4xl font-bold text-gray-900 mb-4">Une préparation sérieuse, simple et efficace</h2>
          <p class="text-lg text-gray-500 max-w-2xl mx-auto">
            Accédez à des examens blancs conçus selon les mêmes critères que les tests officiels.
            Payez une fois, préparez-vous autant que vous voulez pendant la durée choisie.
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="feature in features" :key="feature.title"
            class="bg-white rounded-2xl p-7 border-2 border-gray-100 hover:border-transparent hover:shadow-2xl transition-all duration-400 group relative overflow-hidden">
            <div class="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-400 rounded-2xl"
              :style="`background: ${feature.color};`" />
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3"
              :style="`background: linear-gradient(135deg, ${feature.color}, ${feature.colorDark});`">
              <i :class="['pi text-2xl text-white', feature.icon]"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">{{ feature.title }}</h3>
            <p class="text-gray-500 leading-relaxed text-sm">{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Niveaux B1 + B2 ──────────────────────────────── -->
    <section class="py-20 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">Niveaux disponibles</h2>
          <p class="text-gray-500 text-lg">Deux niveaux, des milliers de questions, une seule plateforme</p>
        </div>

        <div class="grid md:grid-cols-2 gap-8">
          <!-- B1 -->
          <div class="level-card relative rounded-3xl p-8 overflow-hidden group hover:-translate-y-2 transition-all duration-400 cursor-pointer border-2"
            style="border-color: #F59E0B; background: white;"
            @click="navigateTo('/dashboard/examens')">
            <div class="absolute top-0 right-0 text-white text-xs font-bold px-4 py-2 rounded-bl-xl"
              style="background: linear-gradient(135deg, #F59E0B, #d97706);">POPULAIRE</div>
            <div class="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-400"
              style="background: #F59E0B;" />
            <div class="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-400"
              style="background: linear-gradient(135deg, #F59E0B, #d97706);">
              <span class="text-3xl font-extrabold text-white">B1</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-3">Intermédiaire</h3>
            <p class="text-gray-500 mb-5 leading-relaxed">
              Comprenez l'essentiel dans des situations courantes — travail, école, voyages.
              Idéal pour la demande de visa ou de résidence en Allemagne.
            </p>
            <div class="flex flex-wrap gap-2">
              <span v-for="org in ['Goethe', 'ÖSD', 'TELC']" :key="org"
                class="text-xs font-semibold px-3 py-1 rounded-full"
                style="background: rgba(245,158,11,0.12); color: #92400e;">{{ org }}</span>
            </div>
          </div>

          <!-- B2 -->
          <div class="level-card relative rounded-3xl p-8 overflow-hidden group hover:-translate-y-2 transition-all duration-400 cursor-pointer border-2"
            style="border-color: #0d6e4f; background: white;"
            @click="navigateTo('/dashboard/examens')">
            <div class="absolute top-0 right-0 text-white text-xs font-bold px-4 py-2 rounded-bl-xl"
              style="background: linear-gradient(135deg, #0d6e4f, #064e3b);">NOUVEAU</div>
            <div class="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-400"
              style="background: #0d6e4f;" />
            <div class="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-400"
              style="background: linear-gradient(135deg, #0d6e4f, #064e3b);">
              <span class="text-3xl font-extrabold text-white">B2</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-3">Avancé</h3>
            <p class="text-gray-500 mb-5 leading-relaxed">
              Maîtrisez des sujets complexes avec fluidité. Requis pour les études universitaires
              ou les emplois qualifiés en Allemagne ou en Autriche.
            </p>
            <div class="flex flex-wrap gap-2">
              <span v-for="org in ['Goethe', 'ÖSD', 'TELC']" :key="org"
                class="text-xs font-semibold px-3 py-1 rounded-full"
                style="background: rgba(13,110,79,0.1); color: #064e3b;">{{ org }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Partenaires & Certifications ─────────────────── -->
    <section class="py-20 text-white relative overflow-hidden"
      style="background: linear-gradient(135deg, #0d6e4f 0%, #064e3b 100%);">
      <div class="absolute top-0 right-0 w-80 h-80 rounded-full blur-3xl opacity-20"
        style="background: radial-gradient(circle, #F59E0B, transparent); transform: translate(30%,-30%);" />
      <div class="absolute bottom-0 left-0 w-60 h-60 rounded-full blur-3xl opacity-15"
        style="background: radial-gradient(circle, #F59E0B, transparent); transform: translate(-30%,30%);" />

      <div class="relative max-w-5xl mx-auto px-6 text-center">
        <h2 class="text-4xl font-bold mb-4">Certifications & Partenaires</h2>
        <p class="text-white/70 text-lg mb-14 max-w-2xl mx-auto">
          Nos tests sont conçus selon les critères officiels de ces institutions reconnues. Nous collaborons
          avec des centres de formation certifiés pour garantir la qualité.
        </p>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-14">
          <div v-for="cert in certifications" :key="cert.name"
            class="rounded-2xl p-6 text-center group hover:scale-105 hover:bg-white/20 transition-all duration-300 cursor-default"
            style="background: rgba(255,255,255,0.1); backdrop-filter: blur(4px);">
            <div class="w-14 h-14 mx-auto bg-white rounded-full flex items-center justify-center mb-4
              group-hover:shadow-lg group-hover:shadow-yellow-400/20 transition-all duration-300">
              <i :class="['pi text-2xl', cert.icon]" style="color: #0d6e4f;"></i>
            </div>
            <h4 class="font-bold text-lg mb-1">{{ cert.name }}</h4>
            <p class="text-sm" style="color: rgba(255,255,255,0.6);">{{ cert.desc }}</p>
          </div>
        </div>

        <!-- CTA -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink to="/tarifs"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold transition-all duration-300 hover:scale-105 hover:shadow-xl"
            style="background: #F59E0B; color: #064e3b;">
            Voir les tarifs <i class="pi pi-tag"></i>
          </NuxtLink>
          <NuxtLink to="/dashboard/examens"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold transition-all duration-300 hover:scale-105"
            style="background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.3); color: white;">
            Essayer un examen <i class="pi pi-play"></i>
          </NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'À propos — GoToGermany',
  meta: [{ name: 'description', content: 'Préparez-vous aux examens d\'allemand B1 et B2 avec GoToGermany. Simulations conformes Goethe, ÖSD, TELC.' }],
})

const stats = [
  { value: '3 000+', label: 'Candidats préparés' },
  { value: '92%', label: 'Taux de réussite' },
  { value: 'B1 & B2', label: 'Niveaux disponibles' },
  { value: '24/7', label: 'Accès illimité' },
]

const features = [
  {
    icon: 'pi-file-edit',
    title: 'Examens blancs réalistes',
    desc: 'Chaque test reproduit fidèlement la structure, la durée et les types de questions des examens officiels Goethe, ÖSD et TELC.',
    color: '#0d6e4f',
    colorDark: '#064e3b',
  },
  {
    icon: 'pi-volume-up',
    title: 'Hörverstehen avec audio',
    desc: 'La compréhension orale est intégrée avec de vrais fichiers audio, exactement comme le jour de l\'examen.',
    color: '#F59E0B',
    colorDark: '#d97706',
  },
  {
    icon: 'pi-lock',
    title: 'Accès simple & flexible',
    desc: 'Choisissez votre durée d\'accès (7 jours, 1 mois, 3 mois…) et payez via MTN ou Orange Money. Accès immédiat.',
    color: '#0d6e4f',
    colorDark: '#064e3b',
  },
  {
    icon: 'pi-chart-bar',
    title: 'Suivi de progression',
    desc: 'Consultez vos scores par module, identifiez vos points faibles et mesurez votre progression au fil du temps.',
    color: '#F59E0B',
    colorDark: '#d97706',
  },
  {
    icon: 'pi-users',
    title: 'Centres partenaires',
    desc: 'Nous collaborons avec des centres de formation certifiés qui recommandent GoToGermany à leurs apprenants.',
    color: '#0d6e4f',
    colorDark: '#064e3b',
  },
  {
    icon: 'pi-mobile',
    title: 'Paiement mobile money',
    desc: 'Payez facilement avec MTN MoMo ou Orange Money. Aucune carte bancaire nécessaire.',
    color: '#F59E0B',
    colorDark: '#d97706',
  },
]

const certifications = [
  { name: 'Goethe-Institut', icon: 'pi-building', desc: 'Certification internationale' },
  { name: 'ÖSD', icon: 'pi-shield', desc: 'Diplôme autrichien' },
  { name: 'TELC', icon: 'pi-verified', desc: 'Certifications européennes' },
  { name: 'Centres partenaires', icon: 'pi-home', desc: 'Réseau de formation certifié' },
]
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.1); }
}
@keyframes pulse-slow-delay {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.15); }
}
@keyframes fade-down {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-up {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-pulse-slow { animation: pulse-slow 4s ease-in-out infinite; }
.animate-pulse-slow-delay { animation: pulse-slow-delay 5s ease-in-out infinite 1s; }
.animate-fade-down { animation: fade-down 0.6s ease-out forwards; }
.animate-fade-up { animation: fade-up 0.7s ease-out 0.2s both; }
.animate-fade-up-delay { animation: fade-up 0.7s ease-out 0.4s both; }
.animate-fade-up-delay-2 { animation: fade-up 0.7s ease-out 0.6s both; }

.level-card { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.level-card:hover { box-shadow: 0 20px 60px rgba(0,0,0,0.12); }
</style>