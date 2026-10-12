<!-- pages/enseignant/live/[id].vue -->
<template>
  <div>
    <!-- ── Chargement ── -->
    <div v-if="loadingSession" class="flex flex-col items-center gap-3 py-20">
      <ProgressSpinner style="width: 42px; height: 42px" stroke-width="3" />
      <p class="text-sm text-muted">{{ t("teacher.live.loading") }}</p>
    </div>

    <template v-else-if="session">
      <!-- ── En-tête ── -->
      <div class="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-primary">
            {{ t("teacher.live.eyebrow") }}
          </p>
          <h1 class="mt-0.5 text-xl font-bold text-ink">
            {{ session.student_name || t("teacher.live.candidate") }}
          </h1>
        </div>
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold"
          :class="statusTone"
        >
          <span class="size-1.5 rounded-full bg-current" />
          {{ t(`teacher.live.status.${connectionStatus}`) }}
        </span>
      </div>

      <div
        class="lg:grid lg:grid-cols-[1fr_380px] lg:items-start lg:gap-6 2xl:grid-cols-[1fr_440px]"
      >
        <!-- ══ Colonne gauche : état / vidéo (reste visible au défilement) ══ -->
        <div class="space-y-4 lg:sticky lg:top-0">
          <!-- En attente du candidat -->
          <div
            v-if="
              connectionStatus === 'connecting' || connectionStatus === 'idle'
            "
            class="rounded-card border border-line bg-card px-6 py-14 text-center shadow-soft"
          >
            <div class="relative mx-auto mb-5 size-14">
              <span
                class="absolute inset-0 animate-ping rounded-full bg-primary/30"
              />
              <span
                class="relative flex size-14 items-center justify-center rounded-full bg-primary/10"
              >
                <i class="pi pi-wifi text-lg text-primary" />
              </span>
            </div>
            <p class="text-sm font-medium text-ink">
              {{ t("teacher.live.waiting_title") }}
            </p>
            <p class="mt-1 text-xs text-muted">
              {{ t("teacher.live.waiting_text", teileCount) }}
            </p>
          </div>

          <!-- Préparation du candidat -->
          <div
            v-else-if="connectionStatus === 'preparing'"
            class="overflow-hidden rounded-card border border-amber-500/30 bg-card shadow-soft"
          >
            <div
              class="flex items-center gap-2 border-b border-amber-500/20 bg-amber-500/10 px-6 py-3"
            >
              <i class="pi pi-pencil text-xs text-amber-600" />
              <p
                class="text-xs font-bold uppercase tracking-wide text-amber-600"
              >
                {{ t("teacher.live.preparation_title") }}
              </p>
            </div>
            <div class="px-6 py-10 text-center">
              <i class="pi pi-clock mb-2 block text-2xl text-amber-500" />
              <p class="text-sm text-ink">
                {{
                  t(
                    "teacher.live.preparation_text",
                    {
                      minutes:
                        live.preparationInfo.value?.duration_minutes ?? "-",
                    },
                    teileCount,
                  )
                }}
              </p>
            </div>
          </div>

          <!-- En direct : la zone vidéo reste sombre dans les deux thèmes -->
          <div
            v-else-if="connectionStatus === 'live'"
            class="relative overflow-hidden rounded-card border border-line bg-[#0b1220] shadow-lg"
          >
            <div
              class="absolute inset-x-0 top-0 z-10 flex flex-wrap items-center justify-between gap-2 bg-linear-to-b from-black/70 to-transparent px-4 py-3"
            >
              <span
                class="inline-flex items-center gap-1.5 rounded-full bg-red-600 px-2.5 py-1 text-[11px] font-bold uppercase tracking-widest text-white"
              >
                <span class="size-2 animate-pulse rounded-full bg-white" />
                {{ t("teacher.live.on_air") }}
              </span>
              <span
                class="rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold tabular-nums text-white backdrop-blur"
              >
                {{ elapsedTime }}
              </span>
            </div>

            <!-- Flux principal : candidat -->
            <div class="relative aspect-video w-full bg-gray-950">
              <video
                ref="remoteVideoEl"
                autoplay
                playsinline
                class="h-full w-full object-cover"
              />
              <div
                v-if="live.peerSpeaking.value"
                class="absolute top-16 left-4 flex items-end gap-1"
              >
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
                class="absolute right-4 bottom-4 flex items-center gap-1.5 rounded-full bg-black/60 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm"
              >
                <i class="pi pi-user text-[10px]" />
                {{ session.student_name || t("teacher.live.candidate") }}
              </span>

              <!-- Vignette locale -->
              <div
                class="absolute bottom-4 left-4 h-28 w-44 overflow-hidden rounded-xl border-2 border-white/30 bg-gray-900 shadow-lg sm:h-32 sm:w-52"
              >
                <video
                  ref="localVideoEl"
                  autoplay
                  muted
                  playsinline
                  class="h-full w-full object-cover"
                  :class="
                    live.localSpeaking.value
                      ? 'ring-2 ring-inset ring-primary'
                      : ''
                  "
                />
                <span
                  class="absolute bottom-1.5 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] font-semibold text-white"
                >
                  <i
                    class="pi pi-microphone text-[10px]"
                    :class="{ 'text-red-400': !micEnabled }"
                  />
                  {{ t("teacher.live.you") }}
                </span>
              </div>
            </div>

            <!-- Commandes -->
            <div
              class="flex items-center justify-center gap-3 bg-gray-900 py-4"
            >
              <button
                type="button"
                class="flex size-11 items-center justify-center rounded-full transition-colors focus-visible:outline focus-visible:outline-primary"
                :class="
                  cameraEnabled
                    ? 'bg-gray-700 hover:bg-gray-600'
                    : 'bg-red-500 hover:bg-red-600'
                "
                :aria-label="t('teacher.live.toggle_camera')"
                v-tooltip.top="t('teacher.live.toggle_camera')"
                @click="toggleCamera"
              >
                <i class="pi pi-video text-sm text-white" />
              </button>
              <button
                type="button"
                class="flex size-11 items-center justify-center rounded-full transition-colors focus-visible:outline focus-visible:outline-primary"
                :class="
                  micEnabled
                    ? 'bg-gray-700 hover:bg-gray-600'
                    : 'bg-red-500 hover:bg-red-600'
                "
                :aria-label="t('teacher.live.toggle_mic')"
                v-tooltip.top="t('teacher.live.toggle_mic')"
                @click="toggleMic"
              >
                <i class="pi pi-microphone text-sm text-white" />
              </button>
              <button
                type="button"
                class="ml-2 flex size-12 items-center justify-center rounded-full bg-red-500 transition-colors hover:bg-red-600 focus-visible:outline focus-visible:outline-red-300"
                :aria-label="t('teacher.live.end')"
                v-tooltip.top="t('teacher.live.end')"
                @click="confirmEnd"
              >
                <i
                  class="pi pi-phone text-base text-white"
                  style="transform: rotate(135deg)"
                />
              </button>
            </div>
          </div>

          <!-- Terminée -->
          <div
            v-else-if="connectionStatus === 'ended'"
            class="rounded-card border border-line bg-card px-8 py-10 text-center shadow-soft"
          >
            <div
              class="mx-auto mb-4 flex size-14 items-center justify-center rounded-full bg-emerald-500/10"
            >
              <i class="pi pi-check text-2xl text-emerald-600" />
            </div>
            <p class="text-lg font-semibold text-ink">
              {{ t("teacher.live.ended_title") }}
            </p>
            <p class="mt-1 text-sm text-muted">
              {{ t("teacher.live.ended_text") }}
            </p>
          </div>

          <!-- Erreur -->
          <div
            v-else-if="connectionStatus === 'error'"
            class="rounded-card border border-red-500/30 bg-red-500/5 px-6 py-10 text-center"
          >
            <i
              class="pi pi-exclamation-triangle mb-2 block text-2xl text-red-500"
            />
            <p class="text-sm text-red-600">{{ live.errorMessage.value }}</p>
          </div>
        </div>

        <!-- ══ Colonne droite : notes + onglets ══ -->
        <div class="mt-6 space-y-4 lg:mt-0">
          <!-- Notes de correction -->
          <section
            class="space-y-3 rounded-card border border-line bg-card p-5 shadow-soft"
          >
            <div>
              <h2 class="text-sm font-semibold text-ink">
                {{ t("teacher.live.notes_title") }}
              </h2>
              <p class="mt-0.5 text-xs text-muted">
                {{ t("teacher.live.notes_text") }}
              </p>
            </div>
            <Textarea
              v-model="notes"
              rows="8"
              class="w-full"
              :placeholder="t('teacher.live.notes_placeholder')"
            />
            <div class="flex items-center gap-3">
              <Button
                :label="t('common.save')"
                icon="pi pi-check"
                :loading="savingNotes"
                :disabled="notes === savedNotes"
                @click="handleSaveNotes"
              />
              <span
                v-if="notes === savedNotes && savedNotes"
                class="text-xs text-emerald-600"
              >
                <i class="pi pi-check text-[10px]" />
                {{ t("teacher.live.notes_saved") }}
              </span>
              <span
                v-else-if="notes !== savedNotes"
                class="text-xs text-amber-600"
              >
                {{ t("centre.settings.preview_pending") }}
              </span>
            </div>
            <p v-if="notesError" class="text-xs text-red-600">
              {{ notesError }}
            </p>
          </section>

          <!-- Onglets Chat / Sujet / Statut -->
          <section
            class="flex min-h-100 flex-col overflow-hidden rounded-card border border-line bg-card shadow-soft"
          >
            <div class="flex gap-1 border-b border-line p-2" role="tablist">
              <button
                v-for="opt in sideTabs"
                :key="opt.key"
                type="button"
                role="tab"
                :aria-selected="activeSideTab === opt.key"
                class="relative flex flex-1 items-center justify-center gap-1.5 rounded-leaf px-3 py-2 text-xs font-semibold transition-colors"
                :class="
                  activeSideTab === opt.key
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted hover:bg-card-2 hover:text-ink'
                "
                @click="activeSideTab = opt.key"
              >
                <i :class="['pi', opt.icon]" />
                {{ t(`teacher.live.tabs.${opt.key}`) }}
                <span
                  v-if="
                    opt.key === 'chat' &&
                    unreadChatCount > 0 &&
                    activeSideTab !== 'chat'
                  "
                  class="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white"
                >
                  {{ unreadChatCount }}
                </span>
              </button>
            </div>

            <!-- Chat : relayé en temps réel par le backend, rien n'est conservé -->
            <div v-if="activeSideTab === 'chat'" class="flex flex-1 flex-col">
              <div
                ref="chatScrollEl"
                class="max-h-80 flex-1 space-y-3 overflow-y-auto p-4"
              >
                <p
                  v-if="live.chatMessages.value.length === 0"
                  class="py-6 text-center text-xs text-muted"
                >
                  {{ t("teacher.live.chat_empty") }}
                </p>
                <div
                  v-for="(m, i) in live.chatMessages.value"
                  :key="i"
                  class="flex"
                  :class="
                    m.from === 'examiner' ? 'justify-end' : 'justify-start'
                  "
                >
                  <div
                    class="max-w-[85%] rounded-2xl px-3.5 py-2 text-sm"
                    :class="
                      m.from === 'examiner'
                        ? 'bg-primary/15 text-ink'
                        : 'border border-line bg-card-2 text-ink'
                    "
                  >
                    <p
                      v-if="m.from !== 'examiner'"
                      class="mb-0.5 text-[11px] font-bold text-muted"
                    >
                      {{ session.student_name || t("teacher.live.candidate") }}
                    </p>
                    {{ m.text }}
                  </div>
                </div>
              </div>
              <form
                class="flex gap-2 border-t border-line p-3"
                @submit.prevent="handleSendChat"
              >
                <InputText
                  v-model="chatDraft"
                  class="min-w-0 flex-1"
                  :placeholder="t('teacher.live.chat_placeholder')"
                  :aria-label="t('teacher.live.chat_placeholder')"
                />
                <Button
                  type="submit"
                  icon="pi pi-send"
                  :disabled="!chatDraft.trim()"
                  :aria-label="t('teacher.live.send')"
                />
              </form>
            </div>

            <!-- Sujet -->
            <div
              v-else-if="activeSideTab === 'subject'"
              class="max-h-100 flex-1 space-y-3 overflow-y-auto p-4"
            >
              <p
                v-if="!subjectContent"
                class="py-6 text-center text-xs text-muted"
              >
                {{ t("teacher.live.subject_empty") }}
              </p>
              <div
                v-for="teil in subjectContent?.teile"
                :key="teil.teil_number"
                class="rounded-leaf bg-card-2 p-4"
              >
                <div class="mb-1 flex items-center gap-2">
                  <span
                    class="flex size-5 shrink-0 items-center justify-center rounded-full bg-ink text-[10px] font-bold text-card"
                  >
                    {{ teil.teil_number }}
                  </span>
                  <p class="text-sm font-semibold text-ink">
                    Teil {{ teil.teil_number
                    }}<span v-if="teil.name"> - {{ teil.name }}</span>
                  </p>
                </div>
                <p
                  v-if="teil.instructions"
                  class="mb-2 pl-7 text-sm text-muted"
                >
                  {{ teil.instructions }}
                </p>

                <!-- Thèmes au choix (ex : telc B2 Teil 1) -->
                <div v-if="teil.themes" class="mt-2 space-y-2 pl-7">
                  <div
                    v-for="(theme, key) in teil.themes"
                    :key="key"
                    class="rounded-leaf bg-card px-3 py-2"
                  >
                    <p class="text-sm font-medium text-ink">
                      {{ theme.titel || theme.title }}
                    </p>
                    <ul
                      v-if="theme.leitpunkte?.length || theme.punkte?.length"
                      class="mt-1 list-inside list-disc text-sm text-muted"
                    >
                      <li
                        v-for="(p, i) in theme.leitpunkte || theme.punkte"
                        :key="i"
                      >
                        {{ p }}
                      </li>
                    </ul>
                  </div>
                </div>

                <!-- Discussion (ex : telc B2 Teil 2) -->
                <div v-if="teil.diskussion_titel" class="mt-2 pl-7">
                  <p class="text-sm font-medium text-ink">
                    {{ teil.diskussion_titel }}
                  </p>
                  <p
                    v-if="teil.diskussion_thema"
                    class="mt-1 text-sm text-muted"
                  >
                    {{ teil.diskussion_thema }}
                  </p>
                </div>

                <!-- Scénario (ex : Teil « problème à résoudre ») -->
                <p v-if="teil.scenario" class="mt-2 pl-7 text-sm text-muted">
                  {{ teil.scenario }}
                </p>

                <ul
                  v-if="teil.content_points?.length"
                  class="mt-2 list-inside list-disc space-y-0.5 pl-7 text-sm text-muted"
                >
                  <li v-for="(point, i) in teil.content_points" :key="i">
                    {{ point }}
                  </li>
                </ul>

                <ul
                  v-if="teil.tasks?.length"
                  class="mt-2 list-inside list-disc space-y-0.5 pl-7 text-sm text-muted"
                >
                  <li v-for="(task, i) in teil.tasks" :key="i">{{ task }}</li>
                </ul>
              </div>
            </div>

            <!-- Statut : signaux réels uniquement -->
            <div
              v-else-if="activeSideTab === 'status'"
              class="flex-1 space-y-3 overflow-y-auto p-4"
            >
              <div
                class="flex items-center justify-between rounded-leaf border p-3 text-sm"
                :class="
                  micEnabled
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600'
                    : 'border-red-500/30 bg-red-500/10 text-red-600'
                "
              >
                <span class="font-semibold">{{ t("teacher.live.mic") }}</span>
                <span class="text-xs font-bold uppercase tracking-widest">
                  {{
                    micEnabled
                      ? t("teacher.live.mic_on")
                      : t("teacher.live.mic_off")
                  }}
                </span>
              </div>
              <div
                class="flex items-center justify-between rounded-leaf border p-3 text-sm"
                :class="
                  cameraEnabled
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600'
                    : 'border-red-500/30 bg-red-500/10 text-red-600'
                "
              >
                <span class="font-semibold">{{
                  t("teacher.live.camera")
                }}</span>
                <span class="text-xs font-bold uppercase tracking-widest">
                  {{
                    cameraEnabled
                      ? t("teacher.live.camera_on")
                      : t("teacher.live.camera_off")
                  }}
                </span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>

    <!-- ── Introuvable ── -->
    <div v-else class="py-20 text-center">
      <i class="pi pi-inbox mb-3 block text-3xl text-muted" />
      <p class="text-sm text-muted">{{ t("teacher.live.not_found") }}</p>
      <NuxtLink
        :to="localePath('/enseignant/sessions')"
        class="mt-3 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
      >
        <i class="pi pi-arrow-left text-xs" />
        {{ t("teacher.nav.classes") }}
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLiveSession } from "~/composables/useLiveSession";
// createBrowserAudioIO() est typé pour SprechenAudioIO côté source, mais
// LiveSessionAudioIO a exactement la même forme (mêmes 4 méthodes/signatures) :
// accepté par typage structurel TS, pas de cast nécessaire.
import { createBrowserAudioIO } from "~/composables/audioIO";
import {
  createLiveVideoCapture,
  createLiveVideoPlayback,
} from "~/composables/useLiveVideo";
import type { LiveSessionResponse } from "#shared/api";

definePageMeta({ layout: "enseignant", watermark: "Sprechen" });

const { t } = useI18n();
const localePath = useLocalePath();
const confirm = useConfirm();
const route = useRoute();
const liveSessionId = route.params.id as string;

const liveSessionStore = useLiveSessionStore();
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const loadingSession = ref(true);
const session = ref<LiveSessionResponse | null>(null);
const subjectContent = ref<any>(null);

// Nombre réel de Teile du sujet (au lieu d'un « 3 » écrit en dur)
const teileCount = computed(() => subjectContent.value?.teile?.length ?? 0);

// ── Notes ──
const notes = ref("");
const savedNotes = ref("");
const savingNotes = ref(false);
const notesError = ref<string | null>(null);

// wsBaseUrl dérivé de apiBaseUrl (http(s) -> ws(s)) : même convention qu'avant.
const wsBaseUrl = computed(() => {
  const base = config.public.apiBaseUrl || "http://localhost:8001";
  return base.replace(/^http/, "ws") + "/api/v1/live-session";
});

const videoCapture = createLiveVideoCapture();
const videoPlayback = createLiveVideoPlayback();
const audioIO = createBrowserAudioIO({
  captureSampleRate: 16000,
  playbackSampleRate: 16000,
});
const localVideoEl = ref<HTMLVideoElement | null>(null);
const remoteVideoEl = ref<HTMLVideoElement | null>(null);
const cameraEnabled = ref(true);
const micEnabled = ref(true);

function toggleCamera() {
  cameraEnabled.value = !cameraEnabled.value;
  videoCapture
    .getLocalStream()
    ?.getVideoTracks()
    .forEach((track) => {
      track.enabled = cameraEnabled.value;
    });
}

function toggleMic() {
  micEnabled.value = !micEnabled.value;
  audioIO
    .getLocalStream()
    ?.getAudioTracks()
    .forEach((track) => {
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
// composable (getUserMedia est async) : on sonde jusqu'à ce qu'il soit prêt.
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

const statusTone = computed(() => {
  switch (connectionStatus.value) {
    case "live":
      return "bg-red-500/10 text-red-600";
    case "preparing":
      return "bg-amber-500/10 text-amber-600";
    case "ended":
      return "bg-emerald-500/10 text-emerald-600";
    case "error":
      return "bg-red-500/10 text-red-600";
    default:
      return "bg-card-2 text-muted";
  }
});

// ── Chronomètre pendant le direct (affichage seulement) ──
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

// ── Onglets (déclarés avant les watch qui les utilisent) ──
const sideTabs = [
  { key: "chat" as const, icon: "pi-comments" },
  { key: "subject" as const, icon: "pi-book" },
  { key: "status" as const, icon: "pi-shield" },
];
const activeSideTab = ref<"chat" | "subject" | "status">("chat");

// ── Chat : lu directement depuis `live` (WebSocket relayé, sans persistance) ──
const chatDraft = ref("");
const chatScrollEl = ref<HTMLElement | null>(null);
const lastSeenChatCount = ref(0);

function handleSendChat() {
  const text = chatDraft.value.trim();
  if (!text) return;
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
    if (chatScrollEl.value)
      chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight;
    if (activeSideTab.value === "chat")
      lastSeenChatCount.value = live.chatMessages.value.length;
  },
);

watch(activeSideTab, (tab) => {
  if (tab === "chat") lastSeenChatCount.value = live.chatMessages.value.length;
});

// ── Fin de session : confirmation, pour éviter un clic malheureux en plein oral ──
function confirmEnd() {
  confirm.require({
    header: t("teacher.live.end"),
    message: t("teacher.live.end_confirm"),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: t("teacher.live.end"),
    rejectLabel: t("common.cancel"),
    acceptClass: "p-button-danger",
    accept: () => live.endSession(),
  });
}

async function handleSaveNotes() {
  savingNotes.value = true;
  notesError.value = null;
  const result = await liveSessionStore.submitNotes(liveSessionId, {
    notes: notes.value,
  });
  savingNotes.value = false;
  if (result.success) {
    savedNotes.value = notes.value;
  } else {
    notesError.value =
      (result as { error?: string }).error || t("centre.settings.save_error");
  }
}

onMounted(async () => {
  const result = await liveSessionStore.getSession(liveSessionId);
  if (result.success && result.session) {
    session.value = result.session;
    notes.value = result.session.examiner_notes || "";
    savedNotes.value = notes.value;
  }

  const contentResult = await liveSessionStore.getSubjectContent(liveSessionId);
  if (contentResult.success) subjectContent.value = contentResult.content;

  loadingSession.value = false;

  live.connect();
});

onBeforeUnmount(() => {
  if (localStreamPoll) clearInterval(localStreamPoll);
  if (elapsedInterval) clearInterval(elapsedInterval);
  live.disconnect();
});
</script>
