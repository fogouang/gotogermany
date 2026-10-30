<!-- components/start-deutsch/PoolMatchingBlock.vue -->
<!--
  Teil où toutes les questions puisent dans la même liste :
  - image_day_matching (A2 Hören) : images communes, une question par jour ;
  - matching_with_distractor (A2 Lesen) : annonces communes, une question par
    personne, "X" quand aucune annonce ne convient.
  La liste s'affiche une seule fois, chaque question a sa rangée de lettres.
  Une lettre déjà prise par une autre question reste visible, marquée de son numéro.
-->
<template>
  <div
    class="space-y-5 lg:grid lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] lg:items-start lg:gap-6 lg:space-y-0"
  >
    <!-- ── Images : petites, agrandissables, fixes à gauche sur grand écran ── -->
    <div
      v-if="mode === 'images'"
      class="grid grid-cols-3 gap-2 sm:grid-cols-5 sm:gap-3 lg:sticky lg:top-4 lg:grid-cols-3"
    >
      <button
        v-for="img in images"
        :key="img.label"
        type="button"
        class="group relative overflow-hidden rounded-leaf border-2 bg-white transition-colors"
        :class="
          assigned[norm(img.label)]
            ? 'border-primary/50'
            : 'border-line hover:border-primary/40'
        "
        :aria-label="t('start_deutsch.question_ui.zoom', { label: img.label.toUpperCase() })"
        @click="zoomed = img"
      >
        <img
          :src="imageUrl(img.image_file)"
          :alt="`Bild ${img.label}`"
          class="aspect-square w-full object-cover"
          loading="lazy"
        />
        <span
          class="absolute left-1.5 top-1.5 flex size-6 items-center justify-center rounded-full text-xs font-bold uppercase shadow-sm"
          :class="
            assigned[norm(img.label)]
              ? 'bg-primary text-white'
              : 'bg-card text-ink'
          "
        >
          {{ img.label }}
        </span>
        <span
          v-if="assigned[norm(img.label)]"
          class="absolute right-1.5 top-1.5 rounded-full bg-primary/90 px-1.5 text-[10px] font-bold leading-5 text-white"
        >
          {{ assigned[norm(img.label)] }}
        </span>
        <i
          class="pi pi-search-plus absolute bottom-1.5 right-1.5 rounded-full bg-card/90 p-1 text-[11px] text-muted opacity-0 transition-opacity group-hover:opacity-100"
        />
      </button>
    </div>

    <!-- ── Annonces : liste unique, fixe à gauche sur grand écran ── -->
    <div
      v-else
      class="grid gap-2 sm:grid-cols-2 lg:sticky lg:top-4 lg:max-h-[calc(100dvh-12rem)] lg:grid-cols-1 lg:overflow-y-auto"
    >
      <div
        v-for="ad in ads"
        :key="ad.label"
        class="min-w-0 rounded-leaf border p-3 text-sm transition-opacity"
        :class="
          assigned[norm(ad.label)]
            ? 'border-primary/30 bg-primary/5'
            : 'border-line bg-card'
        "
      >
        <div class="flex items-center gap-2">
          <span
            class="flex size-6 shrink-0 items-center justify-center rounded-full bg-card-2 text-xs font-bold uppercase text-ink"
            >{{ ad.label }}</span
          >
          <span class="min-w-0 truncate font-mono text-xs text-primary">{{
            ad.url
          }}</span>
          <span
            v-if="assigned[norm(ad.label)]"
            class="ml-auto shrink-0 rounded-full bg-primary/10 px-1.5 text-[10px] font-bold text-primary"
            >{{ assigned[norm(ad.label)] }}</span
          >
        </div>
        <p class="mt-1.5 text-ink">{{ ad.text }}</p>
      </div>
    </div>

    <!-- ── Une rangée par question ── -->
    <div class="space-y-2">
      <div
        v-for="q in questions"
        :id="`question-${q.id}`"
        :key="q.id"
        class="flex flex-col gap-3 rounded-card border p-3 transition-colors sm:p-4 xl:flex-row xl:items-center"
        :class="valueOf(q) ? 'border-primary/30 bg-primary/5' : 'border-line bg-card'"
      >
        <div class="flex min-w-0 items-start gap-3 xl:w-1/4">
          <span
            class="inline-flex h-6 min-w-6 shrink-0 items-center justify-center rounded-full border border-line bg-card-2 px-1.5 text-[11px] font-bold tabular-nums text-ink"
            >{{ q.question_number }}</span
          >
          <p class="pt-0.5 text-sm font-semibold text-ink">
            {{ q.content?.day ?? q.content?.profile }}
          </p>
        </div>

        <div class="flex flex-wrap gap-1.5 xl:flex-1 xl:justify-end">
          <button
            v-for="key in letters"
            :key="key"
            type="button"
            :aria-pressed="isSel(q, key)"
            class="relative h-9 w-9 rounded-leaf border-2 text-sm font-bold uppercase transition-colors"
            :class="chipClass(q, key)"
            @click="choose(q, key)"
          >
            {{ key }}
            <span
              v-if="!isSel(q, key) && takenBy(q, key)"
              class="absolute -right-1.5 -top-1.5 rounded-full border border-line bg-card-2 px-1 text-[9px] font-semibold leading-4 text-muted"
            >
              {{ takenBy(q, key) }}
            </span>
          </button>
          <!-- Annonces : aucune ne convient -->
          <button
            v-if="mode === 'ads'"
            type="button"
            :aria-pressed="isSel(q, 'X')"
            class="h-9 rounded-leaf border-2 px-3 text-sm font-bold transition-colors"
            :class="
              isSel(q, 'X')
                ? 'border-primary bg-primary text-white'
                : 'border-dashed border-line bg-card text-muted hover:border-primary/40'
            "
            @click="choose(q, 'X')"
          >
            X
          </button>
        </div>
      </div>
    </div>

    <!-- ── Image agrandie ── -->
    <Dialog
      :visible="!!zoomed"
      modal
      dismissable-mask
      :header="zoomed ? zoomed.label.toUpperCase() : ''"
      :style="{ width: '32rem', maxWidth: '95vw' }"
      @update:visible="(v: boolean) => !v && (zoomed = null)"
    >
      <img
        v-if="zoomed"
        :src="imageUrl(zoomed.image_file)"
        :alt="`Bild ${zoomed.label}`"
        class="w-full rounded-leaf bg-white object-contain"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
interface PoolImage {
  label: string;
  image_file: string;
}

interface PoolAd {
  label: string;
  url?: string;
  text: string;
}

const props = withDefaults(
  defineProps<{
    teil: { format_type: string; shared_content?: Record<string, any> | null };
    questions: any[];
    answers: Record<string, any>;
    assetsBaseUrl?: string;
    level?: string;
    subjectNumber?: number;
  }>(),
  { assetsBaseUrl: "", level: "", subjectNumber: 0 },
);

const emit = defineEmits<{ answer: [questionId: string, value: { answer: string }] }>();

const { t } = useI18n();

const mode = computed(() =>
  props.teil.format_type === "image_day_matching" ? "images" : "ads",
);
const images = computed<PoolImage[]>(() => props.teil.shared_content?.images ?? []);
const ads = computed<PoolAd[]>(() => props.teil.shared_content?.ads ?? []);
const letters = computed(() =>
  (mode.value === "images" ? images.value : ads.value).map((x) => x.label),
);

const zoomed = ref<PoolImage | null>(null);

const imageUrl = (file: string) =>
  `${props.assetsBaseUrl}/${props.level.toLowerCase()}/subject${props.subjectNumber}/images/${file}`;

const norm = (v: unknown) => String(v ?? "").trim().toLowerCase();

const valueOf = (q: any): string =>
  String(props.answers[q.id]?.user_answer?.answer ?? "").trim();

const isSel = (q: any, key: string) => valueOf(q) !== "" && norm(valueOf(q)) === norm(key);

const choose = (q: any, key: string) => emit("answer", q.id, { answer: key });

// Lettres prises { lettre: numéro de la question } ("X" peut servir plusieurs fois)
const assigned = computed<Record<string, number>>(() => {
  const out: Record<string, number> = {};
  for (const q of props.questions) {
    const v = norm(valueOf(q));
    if (v && v !== "x") out[v] = q.question_number;
  }
  return out;
});

const takenBy = (q: any, key: string) => {
  const owner = assigned.value[norm(key)];
  return owner && owner !== q.question_number ? owner : null;
};

const chipClass = (q: any, key: string) => {
  if (isSel(q, key)) return "border-primary bg-primary text-white";
  if (takenBy(q, key))
    return "border-dashed border-line bg-card-2 text-faint hover:border-primary/40";
  return "border-line bg-card text-ink hover:border-primary/40";
};
</script>