<template>
  <div class="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <!-- Consigne -->
    <div class="rounded-leaf border border-primary/20 bg-primary/5 px-4 py-3">
      <p class="text-sm font-medium text-ink whitespace-pre-line">{{ teil.instructions }}</p>
      <p class="mt-1.5 text-xs text-muted">
        <i class="pi pi-headphones text-[11px] mr-1"></i>
        {{ t("session.horen.plays_rule", { n: maxPlays }, maxPlays) }}
      </p>
    </div>

    <!-- Statut (reste visible pendant le défilement) -->
    <div class="sticky top-0 z-10 -mx-1 px-1 pt-1 pb-2 bg-canvas">
      <div
        v-if="!teilProgress.read"
        class="flex items-center gap-3 rounded-leaf border border-amber-500/30 bg-amber-500/10 px-4 py-3"
      >
        <i class="pi pi-eye text-amber-600"></i>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-ink">{{ t("session.horen.reading_title") }}</p>
          <p class="text-xs text-muted">{{ t("session.horen.reading_hint") }}</p>
        </div>
        <span class="font-mono text-2xl font-bold text-amber-600 tabular-nums">{{ readLeft }}</span>
      </div>

      <div
        v-else-if="activeIndex >= 0"
        class="flex items-center gap-3 rounded-leaf border border-primary/30 bg-card px-4 py-3 shadow-soft"
      >
        <span class="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
        <p class="text-sm font-medium text-ink">
          {{
            tracks.length > 1
              ? t("session.horen.listening_track", { n: activeIndex + 1, total: tracks.length })
              : t("session.horen.listening")
          }}
        </p>
      </div>

      <div
        v-else
        class="flex items-center gap-3 rounded-leaf border border-emerald-500/30 bg-emerald-500/10 px-4 py-3"
      >
        <i class="pi pi-check-circle text-emerald-600"></i>
        <p class="text-sm font-medium text-ink">{{ t("session.horen.all_done") }}</p>
      </div>
    </div>

    <!-- Intervenants (zuordnung_speaker) -->
    <div
      v-if="teil.format_type === 'zuordnung_speaker' && speakersDict"
      class="bg-card border border-line rounded-card p-5"
    >
      <p class="text-xs text-center font-semibold text-muted uppercase tracking-wide mb-4">
        {{ t("session.horen.speakers") }}
      </p>
      <div class="flex flex-wrap justify-center gap-6">
        <div
          v-for="(speaker, key) in speakersDict"
          :key="key"
          class="flex flex-col items-center gap-2 w-28"
        >
          <img
            v-if="getSpeakerImage(speaker)"
            :src="`${apiBase}/images/${getSpeakerImage(speaker)}`"
            :alt="getSpeakerName(speaker)"
            class="w-28 h-36 object-cover rounded-leaf border border-line"
          />
          <div
            v-else
            class="w-28 h-36 rounded-leaf bg-primary/5 border-2 border-dashed border-line flex items-center justify-center"
          >
            <span class="font-bold text-primary/60 text-2xl">{{ String(key).toUpperCase() }}</span>
          </div>
          <div class="text-center">
            <span class="text-xs font-bold text-primary border border-primary/30 bg-primary/10 px-1.5 py-0.5 rounded mr-1">
              {{ String(key) }}
            </span>
            <span class="text-sm font-medium text-ink">{{ getSpeakerName(speaker) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Plusieurs audios (Teil 1 / Teil 3) ── -->
    <div v-if="isMultiAudio" class="space-y-6">
      <div v-if="!hasAudioImages && sceneImage" class="bg-card border border-line rounded-card p-4">
        <img :src="`${apiBase}/images/${sceneImage}`" alt="" class="w-full rounded-leaf object-contain max-h-72" />
      </div>

      <section
        v-for="(track, gi) in tracks"
        :key="track.key"
        :ref="(el) => setTrackRef(el, gi)"
        :class="[
          'bg-card border rounded-card overflow-hidden scroll-mt-24 transition-colors',
          gi === activeIndex ? 'border-primary/40 shadow-soft' : 'border-line',
        ]"
      >
        <div class="bg-card-2 border-b border-line px-5 py-3 flex items-center gap-3">
          <span class="w-7 h-7 bg-primary text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">
            {{ track.audio_number || gi + 1 }}
          </span>
          <span class="text-sm font-medium text-ink truncate">
            {{ track.questions[0]?.content?.audio_type || t("session.horen.text_n", { n: track.audio_number || gi + 1 }) }}
          </span>
          <span class="ml-auto text-xs text-faint whitespace-nowrap">
            {{ t("session.horen.questions_count", { n: track.questions.length }, track.questions.length) }}
          </span>
        </div>

        <div class="p-4 sm:p-5 space-y-4">
          <img
            v-if="getAudioImage(track, gi)"
            :src="`${apiBase}/images/${getAudioImage(track, gi)}`"
            alt=""
            class="w-full rounded-leaf border border-line object-contain max-h-56"
          />

          <AudioPlayer
            v-if="track.audio_file"
            :key="`player-${track.key}`"
            :src="audioUrl(track.audio_file)"
            :max-plays="maxPlays"
            :plays-used="playsOf(track)"
            :active="gi === activeIndex"
            :gap-seconds="GAP_SECONDS"
            @start="markStarted(track)"
            @done="markFinished(track)"
          />
          <div
            v-else
            class="flex items-center gap-2 text-amber-600 bg-amber-500/10 border border-amber-500/30 rounded-leaf px-4 py-3 text-sm"
          >
            <i class="pi pi-exclamation-triangle"></i>
            {{ t("session.horen.audio_missing") }}
          </div>

          <div class="space-y-3">
            <div
              v-for="q in track.questions"
              :key="q.id"
              :class="[
                'border rounded-leaf p-4 transition-colors',
                answers[q.id] ? 'border-primary/30 bg-primary/5' : 'border-line bg-card',
              ]"
            >
              <QuestionItem
                :question="q"
                :answer="answers[q.id]?.user_answer"
                @answer="(val: Record<string, any>) => emit('answer', q.id, val)"
              />
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- ── Un seul audio (Teil 2) ── -->
    <div v-else class="space-y-4">
      <div v-if="sceneImage" class="bg-card border border-line rounded-card p-4">
        <img :src="`${apiBase}/images/${sceneImage}`" alt="" class="w-full rounded-leaf object-contain max-h-72" />
      </div>

      <AudioPlayer
        v-if="singleTrack?.audio_file"
        :key="`player-${singleTrack.key}`"
        :src="audioUrl(singleTrack.audio_file)"
        :max-plays="maxPlays"
        :plays-used="playsOf(singleTrack)"
        :active="activeIndex === 0"
        :gap-seconds="GAP_SECONDS"
        @start="markStarted(singleTrack)"
        @done="markFinished(singleTrack)"
      />
      <div
        v-else
        class="flex items-center gap-2 text-amber-600 bg-amber-500/10 border border-amber-500/30 rounded-leaf px-4 py-3 text-sm"
      >
        <i class="pi pi-exclamation-triangle"></i>
        {{ t("session.horen.audio_missing") }}
      </div>

      <div
        v-for="q in questions"
        :key="q.id"
        :class="[
          'border rounded-card p-5 transition-colors',
          answers[q.id] ? 'border-primary/30 bg-primary/5' : 'border-line bg-card',
        ]"
      >
        <QuestionItem
          :question="q"
          :answer="answers[q.id]?.user_answer"
          @answer="(val: Record<string, any>) => emit('answer', q.id, val)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionItem from "~/components/session/QuestionItem.vue";
import AudioPlayer from "~/components/session/AudioPlayer.vue";

type Track = { key: string; audio_file: string; audio_number: number; questions: any[] };
type TeilProgress = { read: boolean; plays: Record<string, number>; finished: string[] };

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
  sessionId?: string | null;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const { t } = useI18n();
const config = useRuntimeConfig();
const apiBase = (config.public.apiBaseUrl as string) || "http://localhost:8001";

const DEFAULT_READ_SECONDS = 30;
const GAP_SECONDS = 5;

// ── Règles de l'examen (données du sujet) ─────────────

const maxPlays = computed(() => {
  const raw = props.teil.config?.max_plays ?? props.questions[0]?.content?.max_plays ?? 2;
  return Math.max(1, Number(raw) || 1);
});

const readSeconds = computed(() =>
  Math.max(0, Number(props.teil.config?.reading_time_seconds ?? DEFAULT_READ_SECONDS) || 0),
);

// ── Intervenants / images ─────────────────────────────

const speakersDict = computed(() => {
  const s = props.teil.config?.speakers;
  return s && typeof s === "object" && !Array.isArray(s) ? s : null;
});

const getSpeakerImage = (speaker: any): string | null =>
  typeof speaker === "object" ? (speaker?.image ?? null) : null;

const getSpeakerName = (speaker: any): string =>
  typeof speaker === "object" ? (speaker?.name ?? "") : String(speaker);

const sceneImage = computed(
  () => props.teil.config?.image || props.teil.config?.stimulus_image || "",
);

const hasAudioImages = computed(() => {
  const images = props.teil.config?.audio_images;
  return !!images && Object.keys(images).length > 0;
});

const getAudioImage = (track: Track, gi: number): string => {
  const images = props.teil.config?.audio_images;
  if (!images) return "";
  return images[String(track.audio_number || gi + 1)] || "";
};

const audioUrl = (path: string): string =>
  path ? `${apiBase}/audio/${path.replace(/\\/g, "/")}` : "";

// ── Pistes audio ──────────────────────────────────────

const audioGroups = computed<Track[]>(() => {
  const groups = new Map<string, Track>();
  for (const q of props.questions) {
    const audioFile = q.audio_file || "";
    const audioNumber = q.content?.audio_number ?? 0;
    const key = audioFile || `no_audio_${audioNumber}`;
    if (!groups.has(key)) {
      groups.set(key, { key, audio_file: audioFile, audio_number: audioNumber, questions: [] });
    }
    groups.get(key)!.questions.push(q);
  }
  return [...groups.values()].sort((a, b) => a.audio_number - b.audio_number);
});

const isMultiAudio = computed(() => {
  const groups = audioGroups.value;
  return groups.length > 1 || (groups.length === 1 && !!groups[0]?.audio_file);
});

const singleAudioFile = computed(() => {
  if (!props.questions.length) return "";
  if (props.teil.config?.audio_file) return props.teil.config.audio_file as string;
  return props.questions.find((q) => q.audio_file)?.audio_file || "";
});

const tracks = computed<Track[]>(() =>
  isMultiAudio.value
    ? audioGroups.value
    : [{ key: "single", audio_file: singleAudioFile.value, audio_number: 1, questions: props.questions }],
);

const singleTrack = computed(() => tracks.value[0]);

// ── Avancement (gardé par session + Teil, survit à la navigation) ──

const STORAGE_KEY = "gtg_horen_progress";
const allProgress = useState<Record<string, TeilProgress>>("horen-progress", () => ({}));
const progressKey = computed(() => `${props.sessionId ?? "local"}:${props.teil.id}`);

const emptyProgress = (): TeilProgress => ({ read: false, plays: {}, finished: [] });

const teilProgress = computed<TeilProgress>(
  () => allProgress.value[progressKey.value] ?? emptyProgress(),
);

function persist() {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(allProgress.value));
  } catch {
    /* stockage indisponible : l'état reste en mémoire */
  }
}

function restore() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) allProgress.value = { ...JSON.parse(raw), ...allProgress.value };
  } catch {
    /* ignore */
  }
}

function update(mutate: (p: TeilProgress) => void) {
  const current = allProgress.value[progressKey.value] ?? emptyProgress();
  const next: TeilProgress = {
    read: current.read,
    plays: { ...current.plays },
    finished: [...current.finished],
  };
  mutate(next);
  allProgress.value = { ...allProgress.value, [progressKey.value]: next };
  persist();
}

const playsOf = (track?: Track) => (track ? teilProgress.value.plays[track.key] ?? 0 : 0);

const isFinished = (track: Track) =>
  !track.audio_file || teilProgress.value.finished.includes(track.key);

// Piste en cours : la première non terminée, une fois la lecture finie
const activeIndex = computed(() =>
  teilProgress.value.read ? tracks.value.findIndex((tr) => !isFinished(tr)) : -1,
);

function markStarted(track?: Track) {
  if (!track) return;
  update((p) => {
    p.plays[track.key] = (p.plays[track.key] ?? 0) + 1;
  });
}

function markFinished(track?: Track) {
  if (!track) return;
  update((p) => {
    if (!p.finished.includes(track.key)) p.finished.push(track.key);
  });
}

// ── Temps de lecture ──────────────────────────────────

const readLeft = ref(0);
let readTimer: ReturnType<typeof setInterval> | null = null;

function startReading() {
  if (teilProgress.value.read) return;
  if (readSeconds.value <= 0) {
    update((p) => { p.read = true; });
    return;
  }
  readLeft.value = readSeconds.value;
  readTimer = setInterval(() => {
    readLeft.value--;
    if (readLeft.value <= 0) {
      if (readTimer) clearInterval(readTimer);
      readTimer = null;
      update((p) => { p.read = true; });
    }
  }, 1000);
}

// ── Défilement vers la piste en cours ─────────────────

const trackRefs: (Element | null)[] = [];

function setTrackRef(el: any, index: number) {
  trackRefs[index] = (el as Element) ?? null;
}

watch(activeIndex, async (idx) => {
  if (idx < 0 || !isMultiAudio.value) return;
  await nextTick();
  trackRefs[idx]?.scrollIntoView({ behavior: "smooth", block: "start" });
});

onMounted(() => {
  restore();
  startReading();
});

onBeforeUnmount(() => {
  if (readTimer) clearInterval(readTimer);
});
</script>