<!-- pages/dashboard/sessions-live/[id].vue -->
<template>
  <div class="space-y-6">
    <!-- ── Chargement ── -->
    <div v-if="loadingSession" class="flex flex-col items-center gap-3 py-20">
      <ProgressSpinner style="width: 42px; height: 42px" stroke-width="3" />
      <p class="text-sm text-muted">{{ t("live_session.room.loading") }}</p>
    </div>

    <template v-else-if="session">
      <!-- En-tête -->
      <header>
        <p class="text-xs font-bold uppercase tracking-widest text-primary">Sprechen · Live-Prüfung</p>
        <h1 class="mt-0.5 text-xl font-bold text-ink">{{ t("live_session.room.title") }}</h1>
        <p class="mt-0.5 text-sm text-muted">{{ t("live_session.room.subtitle") }}</p>
      </header>

      <!-- ══ Connexion ══ -->
      <div
        v-if="connectionStatus === 'connecting'"
        class="rounded-card border border-line bg-card px-6 py-14 text-center shadow-soft"
      >
        <div class="relative mx-auto mb-5 size-14">
          <span class="absolute inset-0 animate-ping rounded-full bg-primary/30 opacity-60" />
          <span class="relative flex size-14 items-center justify-center rounded-full bg-primary/10">
            <i class="pi pi-wifi text-lg text-primary" />
          </span>
        </div>
        <p class="text-sm font-medium text-ink">{{ t("live_session.room.connecting_title") }}</p>
        <p class="mt-1 text-xs text-muted">{{ t("live_session.room.connecting_hint") }}</p>
      </div>

      <!-- ══ Préparation ══ -->
      <div
        v-else-if="connectionStatus === 'preparing'"
        class="overflow-hidden rounded-card border border-primary/30 bg-card shadow-soft"
      >
        <div class="flex items-center gap-2 border-b border-primary/20 bg-primary/10 px-6 py-3">
          <i class="pi pi-pencil text-xs text-primary" />
          <p class="text-xs font-bold uppercase tracking-wide text-primary">Vorbereitungszeit</p>
        </div>

        <div class="space-y-5 px-6 py-8 text-center">
          <i18n-t
            keypath="live_session.room.prep_text"
            tag="p"
            class="mx-auto max-w-sm text-sm leading-relaxed text-muted"
          >
            <template #duration>
              <strong class="text-ink">
                {{ t("live_session.room.prep_minutes", { n: live.preparationInfo.value?.duration_minutes ?? 0 }) }}
              </strong>
            </template>
          </i18n-t>

          <div class="relative mx-auto flex size-32 items-center justify-center">
            <span class="absolute inset-0 rounded-full border-4 border-primary/15" />
            <span
              class="absolute inset-0 animate-[spin_6s_linear_infinite] rounded-full border-4 border-primary border-t-transparent"
            />
            <span class="text-2xl font-bold tabular-nums text-ink">{{ formattedTimeLeft }}</span>
          </div>

          <Button :label="t('live_session.room.ready')" icon="pi pi-check" @click="live.sendReadyToStart" />
        </div>
      </div>

      <!-- ══ En direct ══ -->
      <section v-else-if="connectionStatus === 'live'" class="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <!-- Scène principale -->
        <div class="min-w-0 space-y-4">
          <!-- Fond sombre volontaire : c'est une scène vidéo, identique en clair et en sombre -->
          <div class="relative overflow-hidden rounded-card border border-line bg-[#0b1220] shadow-soft">
            <!-- Bandeau live -->
            <div
              class="absolute inset-x-0 top-0 z-10 flex flex-wrap items-center justify-between gap-2 bg-linear-to-b from-black/70 to-transparent px-4 py-3"
            >
              <div class="flex items-center gap-2">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full bg-red-600 px-2.5 py-1 text-[11px] font-bold uppercase tracking-widest text-white"
                >
                  <span class="size-2 animate-pulse rounded-full bg-white" />
                  {{ t("live_session.room.live_badge") }}
                </span>
                <span class="rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur">
                  Sprechen · Prüfung
                </span>
              </div>
              <span
                class="rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold tabular-nums text-white backdrop-blur"
              >
                {{ elapsedTime }}
              </span>
            </div>

            <!-- Flux principal : examinateur -->
            <div class="relative aspect-video w-full bg-black">
              <video ref="remoteVideoEl" autoplay playsinline class="h-full w-full object-cover" />

              <!-- Examinateur : indicateur de parole au-dessus de son étiquette -->
              <div v-if="live.peerSpeaking.value" class="absolute bottom-14 right-4 flex items-end gap-1">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="w-1.5 rounded-full bg-white/90"
                  :style="{
                    height: `${8 + (i % 3) * 8}px`,
                    animation: `pulse 0.6s ease-in-out ${i * 90}ms infinite alternate`,
                  }"
                />
              </div>
              <span
                class="absolute bottom-4 right-4 flex items-center gap-1.5 rounded-full bg-black/60 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm"
              >
                <i class="pi pi-verified text-[10px]" />
                {{ t("live_session.room.examiner") }}
              </span>

              <!-- Vignette locale -->
              <div
                class="absolute bottom-4 left-4 h-24 w-36 overflow-hidden rounded-leaf border-2 border-white/30 bg-black shadow-lg sm:h-32 sm:w-52"
              >
                <video
                  ref="localVideoEl"
                  autoplay
                  muted
                  playsinline
                  class="h-full w-full object-cover"
                  :class="live.localSpeaking.value ? 'ring-2 ring-inset ring-primary' : ''"
                />
                <span
                  class="absolute bottom-1.5 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] font-semibold text-white"
                >
                  <i class="pi pi-microphone text-[10px]" :class="micEnabled ? '' : 'text-red-400'" />
                  {{ t("live_session.room.you") }}
                </span>
              </div>

              <span
                v-if="handRaised"
                class="absolute left-4 top-16 inline-flex items-center gap-2 rounded-full bg-amber-500 px-3 py-1.5 text-xs font-bold text-white"
              >
                ✋ {{ t("live_session.room.hand_raised") }}
              </span>
            </div>
          </div>

          <!-- Barre de contrôle -->
          <div class="flex flex-wrap items-center justify-center gap-2 rounded-card border border-line bg-card p-3 shadow-soft">
            <button
              type="button"
              class="rounded-leaf border p-3 transition-all hover:-translate-y-0.5"
              :class="micEnabled ? 'border-line bg-card-2 text-ink' : 'border-transparent bg-red-600 text-white'"
              :aria-label="micEnabled ? t('live_session.room.mic_off') : t('live_session.room.mic_on')"
              :title="micEnabled ? t('live_session.room.mic_off') : t('live_session.room.mic_on')"
              @click="toggleMic"
            >
              <i class="pi pi-microphone" />
            </button>
            <button
              type="button"
              class="rounded-leaf border p-3 transition-all hover:-translate-y-0.5"
              :class="cameraEnabled ? 'border-line bg-card-2 text-ink' : 'border-transparent bg-red-600 text-white'"
              :aria-label="cameraEnabled ? t('live_session.room.cam_off') : t('live_session.room.cam_on')"
              :title="cameraEnabled ? t('live_session.room.cam_off') : t('live_session.room.cam_on')"
              @click="toggleCamera"
            >
              <i class="pi pi-video" />
            </button>
            <button
              type="button"
              class="rounded-leaf border p-3 transition-all hover:-translate-y-0.5"
              :class="handRaised ? 'border-transparent bg-amber-500 text-white' : 'border-line bg-card-2 text-ink'"
              :aria-label="t('live_session.room.raise_hand')"
              :title="t('live_session.room.raise_hand')"
              @click="handRaised = !handRaised"
            >
              ✋
            </button>
            <button
              type="button"
              class="ml-1 inline-flex items-center gap-2 rounded-leaf bg-red-600 px-5 py-3 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5"
              :aria-label="t('live_session.room.leave_aria')"
              @click="live.endSession"
            >
              <i class="pi pi-phone text-sm" style="transform: rotate(135deg)" />
              {{ t("live_session.room.leave") }}
            </button>
          </div>

          <p
            class="flex items-center gap-2 rounded-card border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs font-medium text-amber-700"
          >
            <i class="pi pi-exclamation-triangle shrink-0" />
            {{ t("live_session.room.stay_visible") }}
          </p>
        </div>

        <!-- Panneau latéral -->
        <aside class="flex min-h-130 min-w-0 flex-col rounded-card border border-line bg-card shadow-soft">
          <div class="flex gap-1 border-b border-line p-2">
            <button
              v-for="opt in sideTabs"
              :key="opt.key"
              type="button"
              class="relative flex flex-1 items-center justify-center gap-1.5 rounded-leaf px-3 py-2 text-xs font-semibold transition-colors"
              :class="activeSideTab === opt.key ? 'bg-primary/10 text-primary' : 'text-muted hover:bg-card-2'"
              @click="activeSideTab = opt.key"
            >
              <i :class="['pi', opt.icon]" />
              {{ opt.label }}
              <span
                v-if="opt.key === 'chat' && unreadChatCount > 0 && activeSideTab !== 'chat'"
                class="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white"
              >
                {{ unreadChatCount }}
              </span>
            </button>
          </div>

          <!-- Chat : relayé en temps réel par le backend, rien n'est persisté -->
          <div v-if="activeSideTab === 'chat'" class="flex flex-1 flex-col">
            <div ref="chatScrollEl" class="flex-1 space-y-3 overflow-y-auto p-4">
              <p v-if="live.chatMessages.value.length === 0" class="py-6 text-center text-xs text-faint">
                {{ t("live_session.room.chat_empty") }}
              </p>
              <div
                v-for="(m, i) in live.chatMessages.value"
                :key="i"
                class="flex"
                :class="m.from === 'student' ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-[85%] rounded-card px-3.5 py-2 text-sm"
                  :class="m.from === 'student' ? 'bg-primary text-white' : 'border border-line bg-card-2 text-ink'"
                >
                  <p v-if="m.from !== 'student'" class="mb-0.5 text-[11px] font-bold text-faint">
                    {{ t("live_session.room.examiner") }}
                  </p>
                  {{ m.text }}
                </div>
              </div>
            </div>
            <form class="flex gap-2 border-t border-line p-3" @submit.prevent="handleSendChat">
              <input
                id="live-chat-input"
                v-model="chatDraft"
                type="text"
                :placeholder="t('live_session.room.chat_placeholder')"
                :aria-label="t('live_session.room.chat_label')"
                class="min-w-0 flex-1 rounded-leaf border border-line bg-card-2 px-3 py-2 text-sm text-ink outline-none focus:border-primary"
              />
              <button
                type="submit"
                :aria-label="t('live_session.room.send')"
                class="rounded-leaf bg-primary px-3.5 text-white"
              >
                <i class="pi pi-send text-sm" />
              </button>
            </form>
          </div>

          <!-- Participants -->
          <ul v-else-if="activeSideTab === 'people'" class="flex-1 space-y-2 overflow-y-auto p-4">
            <li class="flex items-center gap-3 rounded-leaf border border-primary/30 bg-primary/10 p-3">
              <span class="flex size-10 items-center justify-center rounded-full bg-primary text-sm font-black text-white">
                {{ authStore.userName?.slice(0, 2).toUpperCase() || "??" }}
              </span>
              <p class="min-w-0 truncate text-sm font-bold text-ink">
                {{ authStore.userName }} · {{ t("live_session.room.candidate") }}
              </p>
            </li>
            <li class="flex items-center gap-3 rounded-leaf border border-line p-3">
              <span class="flex size-10 items-center justify-center rounded-full bg-card-2 text-sm text-muted">
                <i class="pi pi-verified" />
              </span>
              <p class="min-w-0 truncate text-sm font-semibold text-ink">{{ t("live_session.room.examiner") }}</p>
              <span class="ml-auto text-faint">
                <i :class="live.peerSpeaking.value ? 'pi pi-volume-up text-emerald-600' : 'pi pi-volume-off'" />
              </span>
            </li>
          </ul>

          <!-- Statut : signaux réels uniquement -->
          <div v-else-if="activeSideTab === 'status'" class="flex-1 space-y-3 overflow-y-auto p-4">
            <div
              class="flex items-center justify-between rounded-leaf border p-3 text-sm"
              :class="micEnabled ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600' : 'border-red-500/30 bg-red-500/10 text-red-600'"
            >
              <span class="font-semibold">{{ t("live_session.room.mic") }}</span>
              <span class="text-xs font-bold uppercase tracking-widest">
                {{ micEnabled ? t("live_session.room.mic_state_on") : t("live_session.room.mic_state_off") }}
              </span>
            </div>
            <div
              class="flex items-center justify-between rounded-leaf border p-3 text-sm"
              :class="cameraEnabled ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600' : 'border-red-500/30 bg-red-500/10 text-red-600'"
            >
              <span class="font-semibold">{{ t("live_session.room.camera") }}</span>
              <span class="text-xs font-bold uppercase tracking-widest">
                {{ cameraEnabled ? t("live_session.room.cam_state_on") : t("live_session.room.cam_state_off") }}
              </span>
            </div>
            <p class="rounded-leaf border border-line bg-card-2 p-3 text-xs text-muted">
              {{ t("live_session.room.status_note") }}
            </p>
          </div>
        </aside>
      </section>

      <!-- ══ Terminée ══ -->
      <div v-else-if="connectionStatus === 'ended'" class="space-y-5">
        <div class="rounded-card border border-primary/20 bg-primary/10 px-8 py-10 text-center">
          <div class="mx-auto mb-4 flex size-14 items-center justify-center rounded-full bg-card">
            <i class="pi pi-check text-2xl text-primary" />
          </div>
          <p class="text-lg font-semibold text-ink">{{ t("live_session.room.ended_title") }}</p>
          <p class="mt-1 text-sm text-muted">{{ t("live_session.room.ended_text") }}</p>
        </div>

        <div v-if="session.examiner_notes" class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
          <div class="flex items-center gap-3 border-b border-line bg-card-2 px-5 py-4">
            <div class="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm text-primary">
              <i class="pi pi-user" />
            </div>
            <div>
              <p class="text-sm font-semibold text-ink">{{ t("live_session.room.feedback_title") }}</p>
              <p v-if="session.notes_sent_at" class="text-xs text-faint">{{ formatDate(session.notes_sent_at) }}</p>
            </div>
          </div>
          <p class="whitespace-pre-wrap px-5 py-4 text-sm leading-relaxed text-ink">{{ session.examiner_notes }}</p>
        </div>
        <div v-else class="rounded-card border border-dashed border-line bg-card px-6 py-10 text-center">
          <i class="pi pi-clock mb-2 block text-2xl text-faint" />
          <p class="text-sm text-muted">{{ t("live_session.room.no_notes") }}</p>
        </div>

        <div class="flex justify-center">
          <NuxtLink
            :to="localePath('/dashboard/sessions-live')"
            class="flex items-center gap-1.5 rounded px-1 text-sm font-medium text-primary hover:underline"
          >
            <i class="pi pi-arrow-left text-xs" />
            {{ t("live_session.room.back") }}
          </NuxtLink>
        </div>
      </div>

      <!-- ══ Erreur ══ -->
      <div
        v-else-if="connectionStatus === 'error'"
        class="rounded-card border border-red-500/30 bg-red-500/5 px-6 py-10 text-center"
      >
        <i class="pi pi-exclamation-triangle mb-2 block text-2xl text-red-500" />
        <p class="text-sm text-red-600">{{ live.errorMessage.value }}</p>
      </div>

      <!-- Sujet : visible uniquement pendant la préparation. Bloc indépendant de
           la chaîne connecting/preparing/live/ended/error ci-dessus (ne jamais
           l'imbriquer au milieu : ça casse le v-else-if suivant) -->
      <div v-if="connectionStatus === 'preparing' && subjectContent" class="mt-6 space-y-3">
        <p class="px-1 text-xs font-bold uppercase tracking-widest text-faint">
          {{ t("live_session.room.subject_to_prepare") }}
        </p>

        <div
          v-for="teil in subjectContent.teile"
          :key="teil.teil_number"
          class="rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <div class="mb-2 flex items-center gap-2">
            <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-white">
              {{ teil.teil_number }}
            </span>
            <p class="text-sm font-semibold text-ink">
              Teil {{ teil.teil_number }}<span v-if="teil.name"> · {{ teil.name }}</span>
            </p>
          </div>
          <p v-if="teil.instructions" class="mb-2 pl-8 text-sm text-muted">{{ teil.instructions }}</p>

          <!-- Thèmes au choix (ex. telc B2 Teil 1) -->
          <div v-if="teil.themes" class="mt-2 space-y-2 pl-8">
            <div v-for="(theme, key) in teil.themes" :key="key" class="rounded-leaf bg-card-2 px-3 py-2">
              <p class="text-sm font-medium text-ink">{{ theme.titel || theme.title }}</p>
              <ul
                v-if="theme.leitpunkte?.length || theme.punkte?.length"
                class="mt-1 list-inside list-disc text-sm text-muted"
              >
                <li v-for="(p, i) in theme.leitpunkte || theme.punkte" :key="i">{{ p }}</li>
              </ul>
            </div>
          </div>

          <!-- Discussion (ex. telc B2 Teil 2) -->
          <div v-if="teil.diskussion_titel" class="mt-2 pl-8">
            <p class="text-sm font-medium text-ink">{{ teil.diskussion_titel }}</p>
            <p v-if="teil.diskussion_thema" class="mt-1 text-sm text-muted">{{ teil.diskussion_thema }}</p>
          </div>

          <!-- Scénario (ex. Teil « problème à résoudre ») -->
          <p v-if="teil.scenario" class="mt-2 pl-8 text-sm text-muted">{{ teil.scenario }}</p>

          <ul v-if="teil.content_points?.length" class="mt-2 list-inside list-disc space-y-0.5 pl-8 text-sm text-muted">
            <li v-for="(point, i) in teil.content_points" :key="i">{{ point }}</li>
          </ul>

          <ul v-if="teil.tasks?.length" class="mt-2 list-inside list-disc space-y-0.5 pl-8 text-sm text-muted">
            <li v-for="(task, i) in teil.tasks" :key="i">{{ task }}</li>
          </ul>
        </div>
      </div>
    </template>

    <!-- ── Introuvable ── -->
    <div v-else class="py-20 text-center">
      <i class="pi pi-inbox mb-3 block text-3xl text-faint" />
      <p class="text-sm text-muted">{{ t("live_session.room.not_found") }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLiveSession } from "~/composables/useLiveSession";
// createBrowserAudioIO() est typé pour SprechenAudioIO, mais LiveSessionAudioIO
// a exactement la même forme : accepté par typage structurel, pas de cast.
import { createBrowserAudioIO } from "~/composables/audioIO";
import { createLiveVideoCapture, createLiveVideoPlayback } from "~/composables/useLiveVideo";
import type { LiveSessionResponse } from "#shared/api";

definePageMeta({ layout: "dashboard" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
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

// Compte à rebours de préparation, purement informatif : le candidat peut
// cliquer « Je suis prêt(e) » à tout moment (sendReadyToStart).
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
  const m = Math.floor(secondsLeft.value / 60).toString().padStart(2, "0");
  const s = (secondsLeft.value % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
});

function formatDate(d: string) {
  return new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ── Temps écoulé pendant le live (affichage seulement) ──
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

// ── Chat : canal WebSocket relayé par le backend, sans persistance ──
const chatDraft = ref("");
const chatScrollEl = ref<HTMLElement | null>(null);
const lastSeenChatCount = ref(0);

// ── Main levée (cosmétique : aucun signal envoyé à l'examinateur) ──
const handRaised = ref(false);

// ── Onglets du panneau latéral (déclarés avant les watch qui les utilisent) ──
type SideTab = "chat" | "people" | "status";
const sideTabs = computed(() => [
  { key: "chat" as SideTab, label: t("live_session.room.tab_chat"), icon: "pi-comments" },
  { key: "people" as SideTab, label: t("live_session.room.tab_people"), icon: "pi-users" },
  { key: "status" as SideTab, label: t("live_session.room.tab_status"), icon: "pi-shield" },
]);
const activeSideTab = ref<SideTab>("chat");

function handleSendChat() {
  const text = chatDraft.value.trim();
  chatDraft.value = "";
  if (text) live.sendChatMessage(text);
}

const unreadChatCount = computed(() =>
  Math.max(0, live.chatMessages.value.length - lastSeenChatCount.value),
);

watch(
  () => live.chatMessages.value.length,
  async () => {
    await nextTick();
    if (chatScrollEl.value) chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight;
    if (activeSideTab.value === "chat") lastSeenChatCount.value = live.chatMessages.value.length;
  },
);

watch(
  () => activeSideTab.value,
  (tab) => {
    if (tab === "chat") lastSeenChatCount.value = live.chatMessages.value.length;
  },
);

// Une fois « ended », recharger la session : les notes de l'examinateur
// peuvent arriver après la fin (submit_notes après mark_ended).
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