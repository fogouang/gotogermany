<!-- pages/dashboard/sessions-live/[id].vue -->
<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <div v-if="loadingSession" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <template v-else-if="session">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Session Sprechen en direct</h1>
        <p class="text-sm text-gray-500">Avec un examinateur de votre centre.</p>
      </div>

      <!-- Connexion -->
      <div
        v-if="connectionStatus === 'connecting'"
        class="bg-white rounded-xl border border-gray-200 p-6 text-center"
      >
        <i class="pi pi-spin pi-spinner text-2xl text-gray-400 mb-2 block" />
        <p class="text-sm text-gray-500">Connexion à l'examinateur…</p>
      </div>

      <!-- Préparation -->
      <div
        v-else-if="connectionStatus === 'preparing'"
        class="bg-white rounded-xl border border-amber-200 p-6 text-center space-y-4"
      >
        <p class="text-sm text-gray-700">
          Vous avez <strong>{{ live.preparationInfo.value?.duration_minutes }} minutes</strong>
          pour préparer les 3 Teile. Prenez vos notes sur papier, comme à l'examen réel.
        </p>
        <p class="text-3xl font-bold text-amber-700 tabular-nums">
          {{ formattedTimeLeft }}
        </p>
        <Button label="Je suis prêt(e)" @click="live.sendReadyToStart" />
      </div>

      <!-- Live -->
      <div
        v-else-if="connectionStatus === 'live'"
        class="bg-white rounded-xl border border-green-200 p-6 text-center space-y-4"
      >
        <div class="flex items-center justify-center gap-2 text-green-700 font-semibold">
          <span class="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
          En direct avec l'examinateur
        </div>

        <div class="flex items-center justify-center gap-10 pt-2">
          <div class="flex flex-col items-center gap-2">
            <div
              :class="[
                'w-14 h-14 rounded-full flex items-center justify-center transition-all duration-150',
                live.localSpeaking.value
                  ? 'bg-teal-500 scale-110 shadow-lg shadow-teal-200'
                  : 'bg-gray-200',
              ]"
            >
              <i
                :class="[
                  'pi pi-microphone text-lg',
                  live.localSpeaking.value ? 'text-white' : 'text-gray-400',
                ]"
              />
            </div>
            <span class="text-xs font-medium text-gray-500">Vous</span>
          </div>

          <div class="flex flex-col items-center gap-2">
            <AvatarExaminer :talking="live.peerSpeaking.value" class="w-16 h-16" />
            <span class="text-xs font-medium text-gray-500">Examinateur</span>
          </div>
        </div>
      </div>

      <!-- Terminée -->
      <div v-else-if="connectionStatus === 'ended'" class="space-y-5">
        <div
          class="bg-linear-to-br from-teal-50 to-white rounded-xl border border-teal-100 p-8 text-center"
        >
          <div
            class="w-14 h-14 rounded-full bg-teal-100 flex items-center justify-center mx-auto mb-4"
          >
            <i class="pi pi-check text-teal-600 text-2xl" />
          </div>
          <p class="font-semibold text-gray-900 text-lg">Session terminée</p>
          <p class="text-sm text-gray-500 mt-1">
            Votre examen oral avec l'examinateur est terminé.
          </p>
        </div>

        <div
          v-if="session.examiner_notes"
          class="bg-white rounded-xl border border-gray-200 overflow-hidden"
        >
          <div class="flex items-center gap-3 px-5 py-4 border-b border-gray-100 bg-gray-50">
            <div
              class="w-9 h-9 rounded-full bg-amber-500 flex items-center justify-center text-white text-sm shrink-0"
            >
              <i class="pi pi-user" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900">Retour de l'examinateur</p>
              <p v-if="session.notes_sent_at" class="text-xs text-gray-400">
                {{ formatDate(session.notes_sent_at) }}
              </p>
            </div>
          </div>
          <p class="px-5 py-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {{ session.examiner_notes }}
          </p>
        </div>
        <div
          v-else
          class="bg-white rounded-xl border border-dashed border-gray-200 p-6 text-center"
        >
          <i class="pi pi-clock text-2xl text-gray-300 mb-2 block" />
          <p class="text-sm text-gray-400">
            L'examinateur n'a pas encore publié de notes.
          </p>
        </div>

        <div class="flex justify-center">
          <NuxtLink
            to="/dashboard/sessions-live"
            class="text-sm text-teal-600 font-medium hover:text-teal-700 flex items-center gap-1.5"
          >
            <i class="pi pi-arrow-left text-xs" />
            Retour à mes sessions
          </NuxtLink>
        </div>
      </div>

      <div v-else-if="connectionStatus === 'error'" class="bg-red-50 rounded-xl border border-red-200 p-6 text-center">
        <p class="text-sm text-red-600">{{ live.errorMessage.value }}</p>
      </div>

      <!-- Contenu du sujet — bloc totalement INDÉPENDANT de la chaîne
           connecting/preparing/live/ended/error ci-dessus (jamais imbriqué
           au milieu : ça casse le v-else-if suivant, déjà vécu une fois) -->
      <div
        v-if="['preparing', 'live'].includes(connectionStatus) && subjectContent"
        class="space-y-3 mt-6"
      >
        <div
          v-for="teil in subjectContent.teile"
          :key="teil.teil_number"
          class="bg-white rounded-xl border border-gray-200 p-5"
        >
          <p class="text-sm font-semibold text-gray-900 mb-1">
            Teil {{ teil.teil_number }}<span v-if="teil.name"> — {{ teil.name }}</span>
          </p>
          <p v-if="teil.instructions" class="text-sm text-gray-600 mb-2">
            {{ teil.instructions }}
          </p>

          <!-- Thèmes au choix (ex: telc B2 Teil 1) -->
          <div v-if="teil.themes" class="space-y-2 mt-2">
            <div
              v-for="(theme, key) in teil.themes"
              :key="key"
              class="bg-gray-50 rounded-lg px-3 py-2"
            >
              <p class="text-sm font-medium text-gray-800">
                {{ theme.titel || theme.title }}
              </p>
              <ul
                v-if="theme.leitpunkte?.length || theme.punkte?.length"
                class="list-disc list-inside text-sm text-gray-600 mt-1"
              >
                <li v-for="(p, i) in (theme.leitpunkte || theme.punkte)" :key="i">{{ p }}</li>
              </ul>
            </div>
          </div>

          <!-- Discussion (ex: telc B2 Teil 2) -->
          <div v-if="teil.diskussion_titel" class="mt-2">
            <p class="text-sm font-medium text-gray-800">{{ teil.diskussion_titel }}</p>
            <p v-if="teil.diskussion_thema" class="text-sm text-gray-600 mt-1">
              {{ teil.diskussion_thema }}
            </p>
          </div>

          <!-- Scénario (ex: Teil "problème à résoudre") -->
          <p v-if="teil.scenario" class="text-sm text-gray-600 mt-2">
            {{ teil.scenario }}
          </p>

          <ul
            v-if="teil.content_points?.length"
            class="list-disc list-inside text-sm text-gray-600 space-y-0.5 mt-2"
          >
            <li v-for="(point, i) in teil.content_points" :key="i">{{ point }}</li>
          </ul>

          <ul
            v-if="teil.tasks?.length"
            class="list-disc list-inside text-sm text-gray-600 space-y-0.5 mt-2"
          >
            <li v-for="(task, i) in teil.tasks" :key="i">{{ task }}</li>
          </ul>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-16 text-gray-400">
      Session introuvable.
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

import { useLiveSession } from "~/composables/useLiveSession";
// createBrowserAudioIO() est typé pour SprechenAudioIO côté source, mais
// LiveSessionAudioIO a exactement la même forme (mêmes 4 méthodes/signatures)
// — accepté par typage structurel TS, pas de cast nécessaire.
import { createBrowserAudioIO } from "~/composables/audioIO";
// ASSUMPTION — AvatarExaminer.vue vit dans components/sprechen/, donc selon
// ta config Nuxt (components.pathPrefix), l'auto-import peut exiger
// <SprechenAvatarExaminer /> dans le template plutôt que <AvatarExaminer />.
// Si le composant ne s'affiche pas, essaie ce nom préfixé, ou ajoute un
// import explicite ici : import AvatarExaminer from "~/components/sprechen/AvatarExaminer.vue";
import type { LiveSessionResponse } from "#shared/api";

const route = useRoute();
const liveSessionId = route.params.id as string;

const liveSessionStore = useLiveSessionStore();
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const loadingSession = ref(true);
const session = ref<LiveSessionResponse | null>(null);
const subjectContent = ref<any>(null);

const wsBaseUrl = computed(() => {
  const base = config.public.apiBaseUrl || "http://localhost:8001";
  return base.replace(/^http/, "ws") + "/api/v1/live-session";
});

const live = useLiveSession({
  liveSessionId,
  role: "student",
  wsBaseUrl: wsBaseUrl.value,
  accessToken: tokenCookie.value ?? "",
  audioIO: createBrowserAudioIO(),
});

const connectionStatus = computed(() => live.status.value);

// Minuteur local de compte à rebours, purement informatif côté candidat —
// n'affecte aucune logique serveur ; le vrai "no minimum" reste géré par
// sendReadyToStart() cliquable à tout moment, comme convenu.
const secondsLeft = ref(0);
let timerHandle: ReturnType<typeof setInterval> | null = null;

watch(
  () => live.preparationInfo.value,
  (info) => {
    if (!info) return;
    secondsLeft.value = info.duration_minutes * 60;
    if (timerHandle) clearInterval(timerHandle);
    timerHandle = setInterval(() => {
      if (secondsLeft.value > 0) secondsLeft.value--;
    }, 1000);
  },
);

const formattedTimeLeft = computed(() => {
  const m = Math.floor(secondsLeft.value / 60)
    .toString()
    .padStart(2, "0");
  const s = (secondsLeft.value % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
});

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Une fois "ended", re-fetch la session pour récupérer les notes de
// l'examinateur si elles ont été envoyées après la fin (submit_notes
// peut arriver après mark_ended côté backend).
watch(connectionStatus, async (status) => {
  if (status !== "ended") return;
  const result = await liveSessionStore.getSession(liveSessionId);
  if (result.success && result.session) session.value = result.session;
});

onMounted(async () => {
  const result = await liveSessionStore.getSession(liveSessionId);
  if (result.success && result.session) session.value = result.session;

  const contentResult = await liveSessionStore.getSubjectContent(liveSessionId);
  if (contentResult.success) subjectContent.value = contentResult.content;

  loadingSession.value = false;

  live.connect();
});

onBeforeUnmount(() => {
  if (timerHandle) clearInterval(timerHandle);
  live.disconnect();
});
</script>