<template>
  <div class="lg:h-full flex flex-col">
    <div class="flex-1 min-h-0 flex flex-col lg:flex-row">
      <!-- ── Colonne gauche : consigne + audios ── -->
      <section
        class="bg-card border-line lg:w-1/2 lg:border-r lg:overflow-y-auto lg:min-h-0"
      >
        <div class="p-5 sm:p-6 space-y-4">
          <!-- Consigne -->
          <div
            class="rounded-leaf border border-primary/20 bg-primary/5 px-4 py-3"
          >
            <p class="text-sm font-medium text-ink whitespace-pre-line">
              {{ teil.instructions }}
            </p>
            <p class="mt-1.5 text-xs text-muted">
              <i class="pi pi-headphones text-[11px] mr-1"></i>
              {{ t("session.horen.plays_rule", { n: maxPlays }, maxPlays) }}
            </p>
          </div>

          <!-- Temps de lecture / fin des écoutes -->
          <div
            v-if="!teilProgress.read"
            class="flex items-center gap-3 rounded-leaf border border-amber-500/30 bg-amber-500/10 px-4 py-3"
          >
            <i class="pi pi-eye text-amber-600"></i>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-ink">
                {{ t("session.horen.reading_title") }}
              </p>
              <p class="text-xs text-muted">
                {{ t("session.horen.reading_hint") }}
              </p>
            </div>
            <span
              class="font-mono text-2xl font-bold text-amber-600 tabular-nums"
              >{{ readLeft }}</span
            >
          </div>
          <div
            v-else-if="activeIndex < 0"
            class="flex items-center gap-3 rounded-leaf border border-emerald-500/30 bg-emerald-500/10 px-4 py-3"
          >
            <i class="pi pi-check-circle text-emerald-600"></i>
            <p class="text-sm font-medium text-ink">
              {{ t("session.horen.all_done") }}
            </p>
          </div>

          <!-- Intervenants (zuordnung_speaker) -->
          <div
            v-if="teil.format_type === 'zuordnung_speaker' && speakersDict"
            class="rounded-card border border-line bg-card-2 p-4"
          >
            <p
              class="text-xs text-center font-semibold text-muted uppercase tracking-wide mb-3"
            >
              {{ t("session.horen.speakers") }}
            </p>
            <div class="flex flex-wrap justify-center gap-4">
              <div
                v-for="(speaker, key) in speakersDict"
                :key="key"
                class="flex flex-col items-center gap-2 w-24"
              >
                <img
                  v-if="getSpeakerImage(speaker)"
                  :src="`${apiBase}/images/${getSpeakerImage(speaker)}`"
                  :alt="getSpeakerName(speaker)"
                  class="w-24 h-28 object-cover rounded-leaf border border-line"
                />
                <div
                  v-else
                  class="w-24 h-28 rounded-leaf bg-primary/5 border-2 border-dashed border-line flex items-center justify-center"
                >
                  <span class="font-bold text-primary/60 text-2xl">{{
                    String(key).toUpperCase()
                  }}</span>
                </div>
                <div class="text-center">
                  <span
                    class="text-xs font-bold text-primary border border-primary/30 bg-primary/10 px-1.5 py-0.5 rounded mr-1"
                  >
                    {{ String(key) }}
                  </span>
                  <span class="text-sm font-medium text-ink">{{
                    getSpeakerName(speaker)
                  }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tableau à compléter (TestDaF Hören 1 et 5) -->
          <div
            v-if="cfg.slide || cfg.tabelle?.rows"
            class="rounded-card border border-line bg-card-2 p-4 space-y-3"
          >
            <p
              v-if="cfg.slide"
              class="rounded-leaf border border-line bg-card px-3 py-2 text-sm font-semibold text-ink"
            >
              {{ cfg.slide }}
            </p>
            <template v-if="cfg.tabelle?.rows">
              <p v-if="cfg.tabelle.title" class="font-bold text-ink text-sm">
                {{ cfg.tabelle.title }}
              </p>
              <table class="w-full text-sm">
                <tbody>
                  <tr
                    v-for="(row, ri) in cfg.tabelle.rows"
                    :key="ri"
                    class="border-t border-line first:border-t-0"
                  >
                    <td class="py-1.5 pr-3 align-top text-muted">
                      {{ row.left }}
                    </td>
                    <td
                      class="py-1.5 align-top text-ink"
                      v-html="formatGapText(row.right || '')"
                    />
                  </tr>
                </tbody>
              </table>
            </template>
          </div>

          <!-- Image de la scène -->
          <img
            v-if="sceneImage && (!isMultiAudio || !hasAudioImages)"
            :src="`${apiBase}/images/${sceneImage}`"
            alt=""
            class="w-full rounded-leaf border border-line object-contain max-h-64"
          />

          <!-- Textes et lecteurs -->
          <div class="space-y-3">
            <div
              v-for="(track, gi) in tracks"
              :key="`row-${track.key}`"
              :class="[
                'rounded-leaf border p-3 space-y-2 transition-all',
                gi === activeIndex
                  ? 'border-primary/40 bg-card shadow-soft'
                  : 'border-line bg-card',
                isFinished(track) && gi !== activeIndex ? 'opacity-70' : '',
              ]"
            >
              <div v-if="tracks.length > 1" class="flex items-center gap-2">
                <span
                  :class="[
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                    isFinished(track) && gi !== activeIndex
                      ? 'bg-emerald-500/10 text-emerald-600'
                      : 'bg-primary text-white',
                  ]"
                >
                  <i
                    v-if="isFinished(track) && gi !== activeIndex"
                    class="pi pi-check text-[10px]"
                  ></i>
                  <template v-else>{{ trackNumber(track, gi) }}</template>
                </span>
                <span class="text-sm font-semibold text-ink truncate">{{
                  trackTitle(track, gi)
                }}</span>
                <span class="ml-auto text-xs text-faint whitespace-nowrap">
                  {{
                    t(
                      "session.horen.questions_count",
                      { n: track.questions.length },
                      track.questions.length,
                    )
                  }}
                </span>
              </div>

              <img
                v-if="getAudioImage(track, gi)"
                :src="`${apiBase}/images/${getAudioImage(track, gi)}`"
                alt=""
                class="w-full rounded-leaf border border-line object-contain max-h-40"
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
            </div>
          </div>
        </div>
      </section>

      <!-- ── Colonne droite : affirmations ── -->
      <section class="lg:w-1/2 lg:overflow-y-auto lg:min-h-0">
        <div class="p-5 sm:p-6 max-w-2xl mx-auto space-y-6">
          <!-- Exemple 0 (ECL) -->
          <div
            v-if="beispiel"
            class="rounded-card border border-dashed border-line bg-card-2 p-4"
          >
            <p
              class="text-xs font-semibold uppercase tracking-wide text-faint mb-2"
            >
              {{ t("session.q.example") }} 0
            </p>
            <p
              v-if="beispiel.stem || beispiel.prompt"
              class="text-sm text-ink mb-2"
            >
              {{ beispiel.stem || beispiel.prompt }}
            </p>
            <ul v-if="beispiel.options" class="space-y-1">
              <li
                v-for="(txt, key) in beispiel.options"
                :key="key"
                :class="[
                  'text-sm',
                  String(key).toLowerCase() ===
                  String(beispiel.answer).toLowerCase()
                    ? 'font-semibold text-primary'
                    : 'text-muted',
                ]"
              >
                {{ String(key).toUpperCase() }}) {{ txt }}
              </li>
            </ul>
            <p v-else-if="beispiel.answer" class="text-sm text-ink">
              → <strong class="text-primary">{{ beispiel.answer }}</strong>
            </p>
          </div>

          <!-- Résumé à corriger (TestDaF Hören 3) : affiché après l'écoute -->
          <FehlerZusammenfassung
            v-if="fmt === 'fehler_in_zusammenfassung'"
            :teil="teil"
            :questions="questions"
            :answers="answers"
            :hidden="summaryHidden"
            @answer="(id: string, val: any) => emit('answer', id, val)"
          />

          <!-- Mots à marquer pendant l'écoute (TestDaF Hören 7) -->
          <WoerterImTranskript
            v-else-if="fmt === 'woerter_im_transkript'"
            :text="cfg.transcript_shown || ''"
            :questions="questions"
            :answers="answers"
            @answer="(id: string, val: any) => emit('answer', id, val)"
          />

                    <!-- Associations (TestDaF Lesen 4/5/6, Hören 4) : options affichées une seule fois -->
          <ZuordnungBlock
            v-else-if="fmt === 'zuordnung'"
            :teil="teil"
            :questions="questions"
            :answers="answers"
            @answer="(id: string, val: any) => emit('answer', id, val)"
          />
          
          <!-- Tous les autres formats -->
          <template v-else>
            <div
              v-for="(track, gi) in tracks"
              :key="`questions-${track.key}`"
              :ref="(el) => setTrackRef(el, gi)"
              class="scroll-mt-4 space-y-2"
            >
              <p
                v-if="tracks.length > 1"
                :class="[
                  'flex items-center gap-2 text-xs font-semibold uppercase tracking-wide',
                  gi === activeIndex ? 'text-primary' : 'text-faint',
                ]"
              >
                <span
                  v-if="gi === activeIndex"
                  class="w-2 h-2 rounded-full bg-primary animate-pulse"
                ></span>
                {{ trackNumber(track, gi) }} · {{ trackTitle(track, gi) }}
              </p>

              <ul
                :class="[
                  'divide-y divide-line overflow-hidden rounded-card border transition-colors',
                  gi === activeIndex
                    ? 'border-primary/40 shadow-soft'
                    : 'border-line',
                ]"
              >
                <li
                  v-for="q in track.questions"
                  :key="q.id"
                  :id="`question-${q.id}`"
                  :class="[
                    'px-4 py-3 sm:px-5 transition-colors',
                    answers[q.id] ? 'bg-primary/5' : 'bg-card',
                  ]"
                >
                  <QuestionItem
                    :question="q"
                    :answer="answers[q.id]?.user_answer"
                    compact
                    @answer="
                      (val: Record<string, any>) => emit('answer', q.id, val)
                    "
                  />
                </li>
              </ul>
            </div>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionItem from "~/components/session/QuestionItem.vue";
import AudioPlayer from "~/components/session/AudioPlayer.vue";
import FehlerZusammenfassung from "~/components/session/FehlerZusammenfassung.vue";
import WoerterImTranskript from "~/components/session/WoerterImTranskript.vue";
import ZuordnungBlock from "~/components/session/ZuordnungBlock.vue";

type Track = {
  key: string;
  audio_file: string;
  audio_number: number;
  questions: any[];
};
type TeilProgress = {
  read: boolean;
  plays: Record<string, number>;
  finished: string[];
};

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

const cfg = computed<Record<string, any>>(() => props.teil.config || {});
const fmt = computed(() => String(props.teil.format_type || ""));

// Exemple 0 (ECL) : QCM ou réponse courte
const beispiel = computed(() => {
  const b = cfg.value.beispiel;
  return b && typeof b === "object" && (b.stem || b.prompt || b.answer)
    ? b
    : null;
});

// ── Règles de l'examen (données du sujet) ─────────────

const maxPlays = computed(() => {
  const raw =
    props.teil.config?.max_plays ?? props.questions[0]?.content?.max_plays ?? 2;
  return Math.max(1, Number(raw) || 1);
});

const readSeconds = computed(() =>
  Math.max(
    0,
    Number(props.teil.config?.reading_time_seconds ?? DEFAULT_READ_SECONDS) ||
      0,
  ),
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

const trackNumber = (track: Track, gi: number) => track.audio_number || gi + 1;

const trackTitle = (track: Track, gi: number) =>
  track.questions[0]?.content?.audio_type ||
  t("session.horen.text_n", { n: trackNumber(track, gi) });

// ── Pistes audio ──────────────────────────────────────

const audioGroups = computed<Track[]>(() => {
  const groups = new Map<string, Track>();
  for (const q of props.questions) {
    const audioFile = q.audio_file || "";
    const audioNumber = q.content?.audio_number ?? 0;
    const key = audioFile || `no_audio_${audioNumber}`;
    if (!groups.has(key)) {
      groups.set(key, {
        key,
        audio_file: audioFile,
        audio_number: audioNumber,
        questions: [],
      });
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
  if (props.teil.config?.audio_file)
    return props.teil.config.audio_file as string;
  return props.questions.find((q) => q.audio_file)?.audio_file || "";
});

const tracks = computed<Track[]>(() =>
  isMultiAudio.value
    ? audioGroups.value
    : [
        {
          key: "single",
          audio_file: singleAudioFile.value,
          audio_number: 1,
          questions: props.questions,
        },
      ],
);

const singleTrack = computed(() => tracks.value[0]);

// ── Avancement (gardé par session + Teil, survit à la navigation) ──

const STORAGE_KEY = "gtg_horen_progress";
const allProgress = useState<Record<string, TeilProgress>>(
  "horen-progress",
  () => ({}),
);
const progressKey = computed(
  () => `${props.sessionId ?? "local"}:${props.teil.id}`,
);

const emptyProgress = (): TeilProgress => ({
  read: false,
  plays: {},
  finished: [],
});

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

const playsOf = (track?: Track) =>
  track ? (teilProgress.value.plays[track.key] ?? 0) : 0;

const isFinished = (track: Track) =>
  !track.audio_file || teilProgress.value.finished.includes(track.key);

// Piste en cours : la première non terminée, une fois la lecture finie
const activeIndex = computed(() =>
  teilProgress.value.read
    ? tracks.value.findIndex((tr) => !isFinished(tr))
    : -1,
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

// TestDaF Hören 3 : résumé masqué jusqu'à la fin de l'écoute
const summaryHidden = computed(
  () =>
    !!cfg.value.summary_hidden_while_listening &&
    !(teilProgress.value.read && tracks.value.every((tr) => isFinished(tr))),
);

// Tableau : numéros de lacune _36_ mis en évidence (texte échappé avant v-html)
const escapeHtml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const formatGapText = (text: string) =>
  escapeHtml(text).replace(
    /_(\d+)_/g,
    (_m, n) =>
      `<span class="inline-flex items-center justify-center min-w-6 h-6 px-1 mx-0.5 rounded-full bg-primary/10 text-primary text-xs font-bold align-middle">${n}</span>`,
  );

// ── Temps de lecture ──────────────────────────────────

const readLeft = ref(0);
let readTimer: ReturnType<typeof setInterval> | null = null;

function startReading() {
  if (teilProgress.value.read) return;
  if (readSeconds.value <= 0) {
    update((p) => {
      p.read = true;
    });
    return;
  }
  readLeft.value = readSeconds.value;
  readTimer = setInterval(() => {
    readLeft.value--;
    if (readLeft.value <= 0) {
      if (readTimer) clearInterval(readTimer);
      readTimer = null;
      update((p) => {
        p.read = true;
      });
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