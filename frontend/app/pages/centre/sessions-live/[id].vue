<!-- pages/centre/sessions-live/[id].vue -->
<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <div v-if="loadingSession" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <template v-else-if="session">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Session Sprechen — examinateur</h1>
        <p class="text-sm text-gray-500">
          Statut connexion : <span class="font-medium">{{ statusLabel }}</span>
        </p>
      </div>

      <!-- En attente / connexion -->
      <div
        v-if="connectionStatus === 'connecting'"
        class="bg-white rounded-xl border border-gray-200 p-6 text-center"
      >
        <i class="pi pi-spin pi-spinner text-2xl text-gray-400 mb-2 block" />
        <p class="text-sm text-gray-500">
          En attente que le candidat rejoigne et termine sa préparation…
        </p>
      </div>

      <!-- Préparation en cours (le candidat prépare, on attend) -->
      <div
        v-else-if="connectionStatus === 'preparing'"
        class="bg-white rounded-xl border border-gray-200 p-6 text-center"
      >
        <i class="pi pi-clock text-2xl text-amber-500 mb-2 block" />
        <p class="text-sm text-gray-600">
          Le candidat est en préparation ({{ live.preparationInfo.value?.duration_minutes }} min).
        </p>
      </div>

      <!-- Live -->
      <div
        v-else-if="connectionStatus === 'live'"
        class="bg-white rounded-xl border border-green-200 p-6 text-center space-y-4"
      >
        <div class="flex items-center justify-center gap-2 text-green-700 font-semibold">
          <span class="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
          En direct
        </div>

        <div class="flex items-center justify-center gap-8 pt-2">
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
            <div
              :class="[
                'w-14 h-14 rounded-full flex items-center justify-center transition-all duration-150',
                live.peerSpeaking.value
                  ? 'bg-amber-500 scale-110 shadow-lg shadow-amber-200'
                  : 'bg-gray-200',
              ]"
            >
              <i
                :class="[
                  'pi pi-volume-up text-lg',
                  live.peerSpeaking.value ? 'text-white' : 'text-gray-400',
                ]"
              />
            </div>
            <span class="text-xs font-medium text-gray-500">Candidat</span>
          </div>
        </div>

        <Button label="Terminer la session" severity="danger" text @click="handleEnd" />
      </div>

      <!-- Terminée -->
      <div
        v-else-if="connectionStatus === 'ended'"
        class="bg-linear-to-br from-gray-50 to-white rounded-xl border border-gray-200 p-8 text-center"
      >
        <div
          class="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4"
        >
          <i class="pi pi-check text-gray-500 text-2xl" />
        </div>
        <p class="font-semibold text-gray-900 text-lg">Session terminée</p>
        <p class="text-sm text-gray-500 mt-1">
          Vous pouvez encore compléter vos notes ci-dessous.
        </p>
      </div>

      <div v-else-if="connectionStatus === 'error'" class="bg-red-50 rounded-xl border border-red-200 p-6 text-center">
        <p class="text-sm text-red-600">{{ live.errorMessage.value }}</p>
      </div>

      <!-- Contenu du sujet — référence pour l'examinateur -->
      <div v-if="subjectContent" class="space-y-3">
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

      <!-- Notes de correction — accessible pendant et après la session -->
      <div class="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
        <p class="text-sm font-semibold text-gray-700">Vos notes de correction</p>
        <p class="text-xs text-gray-400">
          Rédigez librement vos observations — pas de grille imposée. L'étudiant
          les verra dans son espace dès la fin de la session.
        </p>
        <Textarea v-model="notes" rows="6" class="w-full" placeholder="Vos observations sur la prestation du candidat…" />
        <div class="flex items-center gap-3">
          <Button label="Enregistrer les notes" :loading="savingNotes" @click="handleSaveNotes" />
          <span v-if="notesSaved" class="text-sm text-green-600">Enregistré ✓</span>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-16 text-gray-400">
      Session introuvable.
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import { useLiveSession } from "~/composables/useLiveSession";
// createBrowserAudioIO() est typé pour SprechenAudioIO côté source, mais
// LiveSessionAudioIO a exactement la même forme (mêmes 4 méthodes/signatures)
// — accepté par typage structurel TS, pas de cast nécessaire.
import { createBrowserAudioIO } from "~/composables/audioIO";
import type { LiveSessionResponse } from "#shared/api";

const route = useRoute();
const liveSessionId = route.params.id as string;

const liveSessionStore = useLiveSessionStore();
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const loadingSession = ref(true);
const session = ref<LiveSessionResponse | null>(null);
const subjectContent = ref<any>(null);

const notes = ref("");
const savingNotes = ref(false);
const notesSaved = ref(false);

// wsBaseUrl dérivé de apiBaseUrl (http(s) -> ws(s)) — ASSUMPTION, à
// confirmer contre la vraie convention utilisée par la page Sprechen IA
// existante si elle diffère.
const wsBaseUrl = computed(() => {
  const base = config.public.apiBaseUrl || "http://localhost:8001";
  return base.replace(/^http/, "ws") + "/api/v1/live-session";
});

const live = useLiveSession({
  liveSessionId,
  role: "examiner",
  wsBaseUrl: wsBaseUrl.value,
  accessToken: tokenCookie.value ?? "",
  audioIO: createBrowserAudioIO({ captureSampleRate: 16000, playbackSampleRate: 16000 }),
});

const connectionStatus = computed(() => live.status.value);

const statusLabel = computed(() => {
  return (
    {
      idle: "Non connecté",
      connecting: "Connexion…",
      preparing: "Préparation du candidat",
      live: "En direct",
      ended: "Terminée",
      error: "Erreur",
    } as Record<string, string>
  )[connectionStatus.value];
});

async function handleEnd() {
  live.endSession();
}

async function handleSaveNotes() {
  savingNotes.value = true;
  notesSaved.value = false;
  const result = await liveSessionStore.submitNotes(liveSessionId, { notes: notes.value });
  savingNotes.value = false;
  if (result.success) notesSaved.value = true;
}

onMounted(async () => {
  const result = await liveSessionStore.getSession(liveSessionId);
  if (result.success && result.session) {
    session.value = result.session;
    notes.value = result.session.examiner_notes || "";
  }

  const contentResult = await liveSessionStore.getSubjectContent(liveSessionId);
  if (contentResult.success) subjectContent.value = contentResult.content;

  loadingSession.value = false;

  live.connect();
});

onBeforeUnmount(() => {
  live.disconnect();
});
</script>