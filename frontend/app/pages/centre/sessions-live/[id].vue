<!-- pages/centre/sessions-live/[id].vue -->
<template>
  <div class="max-w-6xl mx-auto">
    <div v-if="loadingSession" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <template v-else-if="session">
      <div class="mb-6">
        <h1 class="text-xl font-bold text-gray-900">Session Sprechen — examinateur</h1>
        <p class="text-sm text-gray-500">
          Statut connexion : <span class="font-medium">{{ statusLabel }}</span>
        </p>
      </div>

      <div class="lg:grid lg:grid-cols-[1fr_360px] lg:gap-6 lg:items-start">
        <!-- Colonne gauche : statut/vidéo — reste visible en scrollant -->
        <div class="lg:sticky lg:top-4">
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
            class="rounded-2xl overflow-hidden bg-gray-900 text-white shadow-lg"
          >
            <div class="px-4 py-3 text-center border-b border-gray-800">
              <p class="text-sm font-semibold flex items-center justify-center gap-2">
                <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                En direct
              </p>
            </div>

            <div class="grid grid-cols-2 gap-px bg-gray-800">
              <div class="relative bg-gray-950 aspect-video min-h-55">
                <video
                  ref="localVideoEl"
                  autoplay
                  muted
                  playsinline
                  class="w-full h-full object-cover"
                  :class="live.localSpeaking.value ? 'ring-2 ring-inset ring-teal-400' : ''"
                />
                <span class="absolute bottom-2 left-2 text-xs font-medium bg-black/60 px-2 py-1 rounded">
                  Vous
                </span>
              </div>
              <div class="relative bg-gray-950 aspect-video min-h-55">
                <video
                  ref="remoteVideoEl"
                  autoplay
                  playsinline
                  class="w-full h-full object-cover"
                  :class="live.peerSpeaking.value ? 'ring-2 ring-inset ring-amber-400' : ''"
                />
                <span class="absolute bottom-2 left-2 text-xs font-medium bg-black/60 px-2 py-1 rounded">
                  Candidat
                </span>
              </div>
            </div>

            <div class="flex items-center justify-center gap-4 py-4">
              <button
                class="w-11 h-11 rounded-full flex items-center justify-center transition-colors"
                :class="cameraEnabled ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'"
                @click="toggleCamera"
              >
                <i class="pi pi-video text-white text-sm" />
              </button>
              <button
                class="w-11 h-11 rounded-full flex items-center justify-center transition-colors"
                :class="micEnabled ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'"
                @click="toggleMic"
              >
                <i class="pi pi-microphone text-white text-sm" />
              </button>
              <button
                class="w-11 h-11 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors"
                @click="handleEnd"
              >
                <i class="pi pi-phone text-white text-sm" style="transform: rotate(135deg)" />
              </button>
            </div>
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
              Vous pouvez encore compléter vos notes ci-contre.
            </p>
          </div>

          <div v-else-if="connectionStatus === 'error'" class="bg-red-50 rounded-xl border border-red-200 p-6 text-center">
            <p class="text-sm text-red-600">{{ live.errorMessage.value }}</p>
          </div>
        </div>

        <!-- Colonne droite : notes toujours visibles + sujet en accordéon -->
        <div class="mt-6 lg:mt-0 space-y-4">
          <!-- Notes de correction — en premier, toujours accessible sans scroller loin de la vidéo -->
          <div class="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
            <p class="text-sm font-semibold text-gray-700">Vos notes de correction</p>
            <p class="text-xs text-gray-400">
              Rédigez librement vos observations — pas de grille imposée. L'étudiant
              les verra dans son espace dès la fin de la session.
            </p>
            <Textarea v-model="notes" rows="8" class="w-full" placeholder="Vos observations sur la prestation du candidat…" />
            <div class="flex items-center gap-3">
              <Button label="Enregistrer les notes" :loading="savingNotes" @click="handleSaveNotes" />
              <span v-if="notesSaved" class="text-sm text-green-600">Enregistré ✓</span>
            </div>
          </div>

          <!-- Sujet — replié par défaut pour ne pas encombrer, dépliable au besoin -->
          <div v-if="subjectContent" class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <button
              class="w-full flex items-center justify-between px-5 py-4 text-left"
              @click="subjectsExpanded = !subjectsExpanded"
            >
              <span class="text-sm font-semibold text-gray-700">Sujet de l'examen</span>
              <i :class="subjectsExpanded ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" class="text-gray-400 text-xs" />
            </button>
            <div v-if="subjectsExpanded" class="px-5 pb-5 space-y-3 border-t border-gray-100 pt-3">
              <div
                v-for="teil in subjectContent.teile"
                :key="teil.teil_number"
                class="bg-gray-50 rounded-lg p-4"
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
                    class="bg-white rounded-lg px-3 py-2"
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
          </div>
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
import { createLiveVideoCapture, createLiveVideoPlayback } from "~/composables/useLiveVideo";
import type { LiveSessionResponse } from "#shared/api";

const route = useRoute();
const liveSessionId = route.params.id as string;

const liveSessionStore = useLiveSessionStore();
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const loadingSession = ref(true);
const session = ref<LiveSessionResponse | null>(null);
const subjectContent = ref<any>(null);
const subjectsExpanded = ref(false);

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

const videoCapture = createLiveVideoCapture();
const videoPlayback = createLiveVideoPlayback();
const audioIO = createBrowserAudioIO({ captureSampleRate: 16000, playbackSampleRate: 16000 });
const localVideoEl = ref<HTMLVideoElement | null>(null);
const remoteVideoEl = ref<HTMLVideoElement | null>(null);
const cameraEnabled = ref(true);
const micEnabled = ref(true);

function toggleCamera() {
  cameraEnabled.value = !cameraEnabled.value;
  videoCapture.getLocalStream()?.getVideoTracks().forEach((track) => {
    track.enabled = cameraEnabled.value;
  });
}

function toggleMic() {
  micEnabled.value = !micEnabled.value;
  audioIO.getLocalStream()?.getAudioTracks().forEach((track) => {
    track.enabled = micEnabled.value;
  });
}

const live = useLiveSession({
  liveSessionId,
  role: "examiner",
  wsBaseUrl: wsBaseUrl.value,
  accessToken: tokenCookie.value ?? "",
  audioIO,
  videoCapture,
  videoPlayback,
});

// Le flux local n'est disponible qu'une fois startCapture() terminé côté
// composable (getUserMedia est async, déclenché en interne par
// useLiveSession dès le passage en "live") — on sonde jusqu'à ce qu'il
// soit prêt plutôt que de deviner un délai fixe.
let localStreamPoll: ReturnType<typeof setInterval> | null = null;
watch(
  () => live.status.value,
  (status) => {
    if (status === "live") {
      localStreamPoll = setInterval(() => {
        const stream = videoCapture.getLocalStream();
        if (stream && localVideoEl.value) {
          localVideoEl.value.srcObject = stream;
          if (localStreamPoll) clearInterval(localStreamPoll);
          localStreamPoll = null;
        }
      }, 200);
      nextTick(() => {
        if (remoteVideoEl.value) videoPlayback.attach(remoteVideoEl.value);
      });
    } else if (localStreamPoll) {
      clearInterval(localStreamPoll);
      localStreamPoll = null;
    }
  },
);

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
  if (localStreamPoll) clearInterval(localStreamPoll);
  live.disconnect();
});
</script>