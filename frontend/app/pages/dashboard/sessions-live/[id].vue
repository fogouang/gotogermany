<!-- pages/dashboard/sessions-live/[id].vue -->
<template>
  <div class=" space-y-6">
    <div v-if="loadingSession" class="flex flex-col items-center gap-3 py-20">
      <ProgressSpinner style="width: 42px; height: 42px" stroke-width="3" />
      <p class="text-sm text-gray-400">Session wird geladen…</p>
    </div>

    <template v-else-if="session">
      <!-- En-tête -->
      <div>
        <p class="text-xs font-bold uppercase tracking-widest text-primary-600">Sprechen · Live-Prüfung</p>
        <h1 class="text-xl font-bold text-gray-900 mt-0.5">Session Sprechen en direct</h1>
        <p class="text-sm text-gray-500 mt-0.5">Avec un examinateur de votre centre.</p>
      </div>

      <!-- Connexion -->
      <div
        v-if="connectionStatus === 'connecting'"
        class="bg-white rounded-2xl border border-gray-200 px-6 py-14 text-center"
      >
        <div class="relative w-14 h-14 mx-auto mb-5">
          <span class="absolute inset-0 rounded-full bg-primary-200 animate-ping opacity-60" />
          <span class="relative flex items-center justify-center w-14 h-14 rounded-full bg-primary-100">
            <i class="pi pi-wifi text-primary-600 text-lg" />
          </span>
        </div>
        <p class="text-sm font-medium text-gray-700">Connexion à l'examinateur…</p>
        <p class="text-xs text-gray-400 mt-1">Merci de patienter, ça ne prend que quelques secondes.</p>
      </div>

      <!-- Préparation -->
      <div
        v-else-if="connectionStatus === 'preparing'"
        class="bg-white rounded-2xl border border-primary-200 overflow-hidden"
      >
        <div class="flex items-center gap-2 px-6 py-3 bg-primary-50 border-b border-primary-100">
          <i class="pi pi-pencil text-primary-600 text-xs" />
          <p class="text-xs font-bold uppercase tracking-wide text-amber-700">Vorbereitungszeit</p>
        </div>

        <div class="px-6 py-8 text-center space-y-5">
          <p class="text-sm text-gray-600 max-w-sm mx-auto leading-relaxed">
            Vous avez <strong class="text-gray-900">{{ live.preparationInfo.value?.duration_minutes }} minutes</strong>
            pour préparer les 3 Teile. Prenez vos notes sur papier, comme à l'examen réel.
          </p>

          <div class="relative w-32 h-32 mx-auto flex items-center justify-center">
            <span class="absolute inset-0 rounded-full border-4 border-secondary-100" />
            <span class="absolute inset-0 rounded-full border-4 border-secondary-400 border-t-transparent animate-[spin_6s_linear_infinite]" />
            <span class="text-2xl font-bold text-amber-800 tabular-nums">{{ formattedTimeLeft }}</span>
          </div>

          <Button label="Je suis prêt(e)" icon="pi pi-check" @click="live.sendReadyToStart" class="bg-secondary-400 " />
        </div>
      </div>

      <!-- Live -->
      <section
        v-else-if="connectionStatus === 'live'"
        class="grid gap-6 lg:grid-cols-[1.6fr_1fr]"
      >
        <!-- Scène principale -->
        <div class="space-y-4">
          <div class="relative overflow-hidden rounded-2xl border border-gray-200 bg-[#0b1220] shadow-lg">
            <!-- Bandeau live -->
            <div class="absolute inset-x-0 top-0 z-10 flex flex-wrap items-center justify-between gap-2 bg-linear-to-b from-black/70 to-transparent px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="inline-flex items-center gap-1.5 rounded-full bg-red-600 px-2.5 py-1 text-[11px] font-bold uppercase tracking-widest text-white">
                  <span class="w-2 h-2 rounded-full bg-white animate-pulse" /> En direct
                </span>
                <span class="rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur">
                  Sprechen · Prüfung
                </span>
              </div>
              <span class="rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur tabular-nums">
                {{ elapsedTime }}
              </span>
            </div>

            <!-- Flux principal : examinateur -->
            <div class="relative aspect-video w-full bg-gray-950">
              <video
                ref="remoteVideoEl"
                autoplay
                playsinline
                class="w-full h-full object-cover"
              />
              <div
                v-if="live.peerSpeaking.value"
                class="absolute bottom-4 left-4 flex items-end gap-1"
              >
                <span
                  v-for="i in 5"
                  :key="i"
                  class="w-1.5 rounded-full bg-white/90"
                  :style="{ height: `${8 + (i % 3) * 8}px`, animation: `pulse 0.6s ease-in-out ${i * 90}ms infinite alternate` }"
                />
              </div>
              <span class="absolute bottom-4 right-4 flex items-center gap-1.5 rounded-full bg-black/60 backdrop-blur-sm px-2.5 py-1 text-xs font-medium text-white">
                <i class="pi pi-verified text-[10px]" />
                Examinateur
              </span>

              <!-- Vignette locale -->
              <div class="absolute bottom-4 left-4 h-28 w-44 overflow-hidden rounded-xl border-2 border-white/30 bg-gray-900 shadow-lg sm:h-32 sm:w-52">
                <video
                  ref="localVideoEl"
                  autoplay
                  muted
                  playsinline
                  class="h-full w-full object-cover"
                  :class="live.localSpeaking.value ? 'ring-2 ring-inset ring-primary-400' : ''"
                />
                <span class="absolute bottom-1.5 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] font-semibold text-white">
                  <i :class="micEnabled ? 'pi pi-microphone' : 'pi pi-microphone text-red-400'" class="text-[10px]" />
                  Vous
                </span>
              </div>

              <span
                v-if="handRaised"
                class="absolute left-4 top-16 inline-flex items-center gap-2 rounded-full bg-amber-500 px-3 py-1.5 text-xs font-bold text-white"
              >
                ✋ Main levée
              </span>
            </div>
          </div>

          <!-- Barre de contrôle -->
          <div class="flex flex-wrap items-center justify-center gap-2 rounded-2xl border border-gray-200 bg-white p-3">
            <button
              class="rounded-xl border p-3 transition-all hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-primary-400"
              :class="micEnabled ? 'border-gray-200 bg-gray-50 text-gray-700' : 'border-transparent bg-red-600 text-white'"
              :aria-label="micEnabled ? 'Couper le micro' : 'Activer le micro'"
              :title="micEnabled ? 'Couper le micro' : 'Activer le micro'"
              @click="toggleMic"
            >
              <i class="pi pi-microphone" />
            </button>
            <button
              class="rounded-xl border p-3 transition-all hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-primary-400"
              :class="cameraEnabled ? 'border-gray-200 bg-gray-50 text-gray-700' : 'border-transparent bg-red-600 text-white'"
              :aria-label="cameraEnabled ? 'Couper la caméra' : 'Activer la caméra'"
              :title="cameraEnabled ? 'Couper la caméra' : 'Activer la caméra'"
              @click="toggleCamera"
            >
              <i class="pi pi-video" />
            </button>
            <button
              class="rounded-xl border p-3 transition-all hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-primary-400"
              :class="handRaised ? 'border-transparent bg-amber-500 text-white' : 'border-gray-200 bg-gray-50 text-gray-700'"
              aria-label="Lever la main"
              title="Lever la main"
              @click="handRaised = !handRaised"
            >
              ✋
            </button>
            <button
              class="ml-1 inline-flex items-center gap-2 rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5 focus-visible:outline-2 focus-visible:outline-red-300"
              aria-label="Quitter l'examen"
              @click="live.endSession"
            >
              <i class="pi pi-phone text-sm" style="transform: rotate(135deg)" />
              Quitter
            </button>
          </div>

          <p class="flex items-center gap-2 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-xs font-medium text-amber-800">
            <i class="pi pi-exclamation-triangle shrink-0" />
            Restez visible à l'écran pendant toute l'épreuve orale.
          </p>
        </div>

        <!-- Panneau latéral -->
        <aside class="flex min-h-130 flex-col rounded-2xl border border-gray-200 bg-white">
          <div class="flex gap-1 border-b border-gray-100 p-2">
            <button
              v-for="opt in sideTabs"
              :key="opt.key"
              class="relative flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold transition-colors"
              :class="activeSideTab === opt.key ? 'bg-primary-500 text-white' : 'text-gray-500 hover:bg-gray-50'"
              @click="activeSideTab = opt.key"
            >
              <i :class="['pi', opt.icon]" />
              {{ opt.label }}
              <span
                v-if="opt.key === 'chat' && unreadChatCount > 0 && activeSideTab !== 'chat'"
                class="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white"
              >
                {{ unreadChatCount }}
              </span>
            </button>
          </div>

          <!-- Chat — relayé en temps réel par le backend, rien n'est persisté -->
          <div v-if="activeSideTab === 'chat'" class="flex flex-1 flex-col">
            <div ref="chatScrollEl" class="flex-1 space-y-3 overflow-y-auto p-4">
              <p v-if="live.chatMessages.value.length === 0" class="text-center text-xs text-gray-400 py-6">
                Aucun message pour l'instant.
              </p>
              <div
                v-for="(m, i) in live.chatMessages.value"
                :key="i"
                class="flex"
                :class="m.from === 'student' ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-[85%] rounded-2xl px-3.5 py-2 text-sm"
                  :class="m.from === 'student' ? 'bg-primary-500 text-white' : 'border border-gray-200 bg-gray-50 text-gray-800'"
                >
                  <p v-if="m.from !== 'student'" class="mb-0.5 text-[11px] font-bold text-gray-400">Examinateur</p>
                  {{ m.text }}
                </div>
              </div>
            </div>
            <form class="flex gap-2 border-t border-gray-100 p-3" @submit.prevent="handleSendChat">
              <input
                v-model="chatDraft"
                type="text"
                placeholder="Écrire un message…"
                aria-label="Message"
                class="flex-1 rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 outline-none focus:border-primary-500"
              />
              <button type="submit" aria-label="Envoyer" class="rounded-xl bg-primary-500 px-3.5 text-white">
                <i class="pi pi-send text-sm" />
              </button>
            </form>
          </div>

          <!-- Participants -->
          <ul v-else-if="activeSideTab === 'people'" class="flex-1 space-y-2 overflow-y-auto p-4">
            <li class="flex items-center gap-3 rounded-xl border border-primary-200 bg-primary-50 p-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-sm font-black text-white">
                {{ authStore.userName?.slice(0, 2).toUpperCase() || "??" }}
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-bold text-primary-800">{{ authStore.userName }} · Candidat</p>
              </div>
            </li>
            <li class="flex items-center gap-3 rounded-xl border border-gray-200 p-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-sm font-black text-gray-700">
                <i class="pi pi-verified" />
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold">Examinateur</p>
              </div>
              <span class="ml-auto text-gray-400">
                <i :class="live.peerSpeaking.value ? 'pi pi-volume-up text-green-600' : 'pi pi-volume-off'" />
              </span>
            </li>
          </ul>

          <!-- Statut — signaux RÉELS uniquement -->
          <div v-else-if="activeSideTab === 'status'" class="flex-1 space-y-3 overflow-y-auto p-4">
            <div
              class="flex items-center justify-between rounded-xl border p-3 text-sm"
              :class="micEnabled ? 'border-green-300 bg-green-50 text-green-700' : 'border-red-300 bg-red-50 text-red-700'"
            >
              <span class="font-semibold">Micro</span>
              <span class="text-xs font-bold uppercase tracking-widest">{{ micEnabled ? "Actif" : "Coupé" }}</span>
            </div>
            <div
              class="flex items-center justify-between rounded-xl border p-3 text-sm"
              :class="cameraEnabled ? 'border-green-300 bg-green-50 text-green-700' : 'border-red-300 bg-red-50 text-red-700'"
            >
              <span class="font-semibold">Caméra</span>
              <span class="text-xs font-bold uppercase tracking-widest">{{ cameraEnabled ? "Active" : "Coupée" }}</span>
            </div>
            <div class="rounded-xl border border-gray-200 bg-gray-50 p-3 text-xs text-gray-500">
              Contrôle d'identité et de session non automatisés pour l'instant — l'examinateur supervise directement l'appel.
            </div>
          </div>
        </aside>
      </section>

      <!-- Terminée -->
      <div v-else-if="connectionStatus === 'ended'" class="space-y-5">
        <div class="bg-linear-to-br from-primary-50 to-white rounded-2xl border border-primary-100 px-8 py-10 text-center">
          <div class="w-14 h-14 rounded-full bg-primary-100 flex items-center justify-center mx-auto mb-4">
            <i class="pi pi-check text-primary-600 text-2xl" />
          </div>
          <p class="font-semibold text-gray-900 text-lg">Session terminée</p>
          <p class="text-sm text-gray-500 mt-1">
            Votre examen oral avec l'examinateur est terminé.
          </p>
        </div>

        <div
          v-if="session.examiner_notes"
          class="bg-white rounded-2xl border border-gray-200 overflow-hidden"
        >
          <div class="flex items-center gap-3 px-5 py-4 border-b border-gray-100 bg-gray-50">
            <div class="w-9 h-9 rounded-full bg-amber-500 flex items-center justify-center text-white text-sm shrink-0">
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
        <div v-else class="bg-white rounded-2xl border border-dashed border-gray-200 px-6 py-10 text-center">
          <i class="pi pi-clock text-2xl text-gray-300 mb-2 block" />
          <p class="text-sm text-gray-400">
            L'examinateur n'a pas encore publié de notes.
          </p>
        </div>

        <div class="flex justify-center">
          <NuxtLink
            to="/dashboard/sessions-live"
            class="text-sm text-primary-600 font-medium hover:text-primary-700 flex items-center gap-1.5 focus-visible:outline focus-visible:outline-primary-300 rounded px-1"
          >
            <i class="pi pi-arrow-left text-xs" />
            Retour à mes sessions
          </NuxtLink>
        </div>
      </div>

      <div
        v-else-if="connectionStatus === 'error'"
        class="bg-red-50 rounded-2xl border border-red-200 px-6 py-10 text-center"
      >
        <i class="pi pi-exclamation-triangle text-2xl text-red-400 mb-2 block" />
        <p class="text-sm text-red-600">{{ live.errorMessage.value }}</p>
      </div>

      <!-- Contenu du sujet — visible UNIQUEMENT pendant la prépa côté
           candidat (masqué une fois en direct, l'écran doit se concentrer
           sur l'appel). Bloc totalement INDÉPENDANT de la chaîne
           connecting/preparing/live/ended/error ci-dessus (jamais imbriqué
           au milieu : ça casse le v-else-if suivant, déjà vécu une fois) -->
      <div
        v-if="connectionStatus === 'preparing' && subjectContent"
        class="space-y-3 mt-6"
      >
        <p class="text-xs font-bold uppercase tracking-widest text-gray-400 px-1">Sujet à préparer</p>

        <div
          v-for="teil in subjectContent.teile"
          :key="teil.teil_number"
          class="bg-white rounded-xl border border-gray-200 p-5"
        >
          <div class="flex items-center gap-2 mb-2">
            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-gray-900 text-white text-xs font-bold shrink-0">
              {{ teil.teil_number }}
            </span>
            <p class="text-sm font-semibold text-gray-900">
              Teil {{ teil.teil_number }}<span v-if="teil.name"> — {{ teil.name }}</span>
            </p>
          </div>
          <p v-if="teil.instructions" class="text-sm text-gray-600 mb-2 pl-8">
            {{ teil.instructions }}
          </p>

          <!-- Thèmes au choix (ex: telc B2 Teil 1) -->
          <div v-if="teil.themes" class="space-y-2 mt-2 pl-8">
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
          <div v-if="teil.diskussion_titel" class="mt-2 pl-8">
            <p class="text-sm font-medium text-gray-800">{{ teil.diskussion_titel }}</p>
            <p v-if="teil.diskussion_thema" class="text-sm text-gray-600 mt-1">
              {{ teil.diskussion_thema }}
            </p>
          </div>

          <!-- Scénario (ex: Teil "problème à résoudre") -->
          <p v-if="teil.scenario" class="text-sm text-gray-600 mt-2 pl-8">
            {{ teil.scenario }}
          </p>

          <ul
            v-if="teil.content_points?.length"
            class="list-disc list-inside text-sm text-gray-600 space-y-0.5 mt-2 pl-8"
          >
            <li v-for="(point, i) in teil.content_points" :key="i">{{ point }}</li>
          </ul>

          <ul
            v-if="teil.tasks?.length"
            class="list-disc list-inside text-sm text-gray-600 space-y-0.5 mt-2 pl-8"
          >
            <li v-for="(task, i) in teil.tasks" :key="i">{{ task }}</li>
          </ul>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-20">
      <i class="pi pi-inbox text-3xl text-gray-200 mb-3 block" />
      <p class="text-sm text-gray-400">Session introuvable.</p>
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
import { createLiveVideoCapture, createLiveVideoPlayback } from "~/composables/useLiveVideo";
import type { LiveSessionResponse } from "#shared/api";

const route = useRoute();
const liveSessionId = route.params.id as string;

const liveSessionStore = useLiveSessionStore();
const authStore = useAuthStore();
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const loadingSession = ref(true);
const session = ref<LiveSessionResponse | null>(null);
const subjectContent = ref<any>(null);

const wsBaseUrl = computed(() => {
  const base = config.public.apiBaseUrl || "http://localhost:8001";
  return base.replace(/^http/, "ws") + "/api/v1/live-session";
});

const videoCapture = createLiveVideoCapture();
const videoPlayback = createLiveVideoPlayback();
const localVideoEl = ref<HTMLVideoElement | null>(null);
const remoteVideoEl = ref<HTMLVideoElement | null>(null);
const audioIO = createBrowserAudioIO({ captureSampleRate: 16000, playbackSampleRate: 16000 });
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
  role: "student",
  wsBaseUrl: wsBaseUrl.value,
  accessToken: tokenCookie.value ?? "",
  audioIO,
  videoCapture,
  videoPlayback,
});

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

// Minuteur local de compte à rebours, purement informatif côté candidat —
// n'affecte aucune logique serveur ; le vrai "no minimum" reste géré par
// sendReadyToStart() cliquable à tout moment, comme convenu.
const secondsLeft = ref(0);
let timerHandle: ReturnType<typeof setInterval> | null = null;

watch(
  () => live.preparationInfo.value,
  (info) => {
    if (!info) return;
    secondsLeft.value = info.duration_minutes * 60; // initialise le compte à rebours
    if (timerHandle) clearInterval(timerHandle);
    timerHandle = setInterval(() => {
      if (secondsLeft.value > 0) secondsLeft.value--; // décrémente chaque seconde
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

// ── Timer écoulé pendant le live (affichage seulement) ───────────────
const elapsedSeconds = ref(0);
let elapsedInterval: ReturnType<typeof setInterval> | null = null;

const elapsedTime = computed(() => {
  const m = String(Math.floor(elapsedSeconds.value / 60)).padStart(2, "0");
  const s = String(elapsedSeconds.value % 60).padStart(2, "0");
  return `${m}:${s}`;
});

watch(connectionStatus, (status) => {
  if (status === "live" && !elapsedInterval) {
    elapsedSeconds.value = 0;
    elapsedInterval = setInterval(() => elapsedSeconds.value++, 1000);
  } else if (status !== "live" && elapsedInterval) {
    clearInterval(elapsedInterval);
    elapsedInterval = null;
  }
});

// ── Chat — lu directement depuis `live` (vrai canal WebSocket relayé
// par le backend, sans persistance) ──────────────────────────────────
const chatDraft = ref("");
const chatScrollEl = ref<HTMLElement | null>(null);
const lastSeenChatCount = ref(0);

// ── Main levée (cosmétique — pas de signal envoyé à l'examinateur) ──
const handRaised = ref(false);

// ── Onglets du panneau latéral (déclarés AVANT les watch qui les
// utilisent — sinon TDZ error au chargement) ──────────────────────────
const sideTabs = [
  { key: "chat" as const, label: "Chat", icon: "pi-comments" },
  { key: "people" as const, label: "Participants", icon: "pi-users" },
  { key: "status" as const, label: "Statut", icon: "pi-shield" },
];
const activeSideTab = ref<"chat" | "people" | "status">("chat");

function handleSendChat() {
  const text = chatDraft.value;
  chatDraft.value = "";
  live.sendChatMessage(text);
}

const unreadChatCount = computed(() =>
  Math.max(0, live.chatMessages.value.length - lastSeenChatCount.value),
);

watch(
  () => live.chatMessages.value.length,
  async () => {
    await nextTick();
    if (chatScrollEl.value) {
      chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight;
    }
    if (activeSideTab.value === "chat") {
      lastSeenChatCount.value = live.chatMessages.value.length;
    }
  },
);

watch(
  () => activeSideTab.value,
  (tab) => {
    if (tab === "chat") lastSeenChatCount.value = live.chatMessages.value.length;
  },
);

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
  if (localStreamPoll) clearInterval(localStreamPoll);
  if (elapsedInterval) clearInterval(elapsedInterval);
  live.disconnect();
});
</script>