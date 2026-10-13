<template>
  <div>
    <!-- Numéro -->
    <div class="flex items-center gap-2 mb-3">
      <span
        class="inline-flex items-center h-7 min-w-7 px-2.5 justify-center rounded-full bg-card-2 border border-line text-xs font-bold text-ink tabular-nums"
      >
        {{ badge }}
      </span>
      <span
        v-if="c.abschnitt"
        class="text-[11px] font-medium text-muted bg-card-2 border border-line rounded-full px-2 py-0.5"
      >
        {{ t("session.q.abschnitt", { n: c.abschnitt }) }}
      </span>
    </div>

    <!-- richtig_falsch / ja_nein -->
    <div v-if="type === 'richtig_falsch' || type === 'ja_nein'">
      <div v-if="type === 'ja_nein' && c.text" class="mb-4">
        <p v-if="c.author" class="text-sm font-semibold text-ink mb-1">{{ c.author }}</p>
        <p class="text-[15px] text-ink leading-relaxed">{{ c.text }}</p>
      </div>
      <p v-else class="text-[15px] text-ink leading-relaxed mb-4">{{ c.statement || c.text }}</p>

      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="opt in binaryOptions"
          :key="opt.value"
          type="button"
          :class="['py-3 px-4 rounded-leaf border-2 text-sm font-semibold transition-colors', optionClass(isSel(opt.value))]"
          @click="choose(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- qcm_abc -->
    <div v-else-if="type === 'qcm_abc'">
      <p class="text-[15px] text-ink leading-relaxed mb-4">{{ c.stem || c.question }}</p>
      <div class="space-y-2">
        <button
          v-for="(text, key) in c.options"
          :key="key"
          type="button"
          :class="['w-full text-left px-4 py-3 rounded-leaf border-2 text-sm transition-colors flex items-start gap-3', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span :class="keyClass(isSel(key))">{{ String(key).toUpperCase() }}</span>
          <span class="pt-0.5">{{ text }}</span>
        </button>
      </div>
    </div>

    <!-- matching (Goethe) / selektives_matching (TELC) -->
    <div v-else-if="type === 'matching' || type === 'selektives_matching'">
      <p class="text-[15px] text-ink leading-relaxed mb-4">{{ c.situation }}</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="key in adKeys"
          :key="key"
          type="button"
          :class="[
            'w-10 h-10 rounded-leaf border-2 font-bold text-sm transition-colors',
            isSel(key)
              ? 'border-primary bg-primary text-white'
              : key === noMatchKey
                ? 'border-dashed border-line text-muted hover:border-primary/40'
                : 'border-line bg-card text-ink hover:border-primary/40',
          ]"
          @click="choose(key)"
        >
          {{ key === noMatchKey ? key : key.toUpperCase() }}
        </button>
      </div>
      <p class="text-xs text-muted mt-2">
        {{ noMatchKey === "x" ? t("session.q.no_match_x") : t("session.q.no_match_0") }}
      </p>
    </div>

    <!-- zuordnung_speaker -->
    <div v-else-if="type === 'zuordnung_speaker'">
      <p class="text-[15px] text-ink leading-relaxed mb-4">{{ c.statement }}</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
        <button
          v-for="(name, key) in c.speakers"
          :key="key"
          type="button"
          :class="['py-3 px-2 rounded-leaf border-2 text-center transition-colors', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span class="block font-bold text-base">{{ String(key).toUpperCase() }}</span>
          <span class="block text-xs text-muted mt-0.5 leading-tight">{{ speakerName(name) }}</span>
        </button>
      </div>
    </div>

    <!-- zuordnung_titre -->
    <div v-else-if="type === 'zuordnung_titre'">
      <div
        v-if="!stimulusInSide"
        class="rounded-leaf border border-line bg-card-2 p-4 mb-4 text-[15px] text-ink leading-relaxed"
      >
        {{ c.stimulus_text }}
      </div>
      <label class="block text-xs font-semibold uppercase tracking-wide text-muted mb-2">
        {{ t("session.q.choose_title") }}
      </label>
      <select :value="selected" :class="selectClass" @change="onSelect">
        <option value="" disabled>{{ t("session.q.select_placeholder") }}</option>
        <option v-for="(titre, key) in c.titres" :key="key" :value="String(key)">
          {{ key }}) {{ titre }}
        </option>
      </select>
    </div>

    <!-- qcm_gap_fill -->
    <div v-else-if="type === 'qcm_gap_fill'">
      <div
        v-if="!stimulusInSide"
        class="rounded-leaf border border-line bg-card-2 p-4 mb-4 text-sm text-ink leading-loose"
        v-html="highlightGap(c.text_with_gaps, c.gap_number)"
      />
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          v-for="(text, key) in c.options"
          :key="key"
          type="button"
          :class="['px-3 py-2.5 rounded-leaf border-2 text-sm font-medium transition-colors flex items-center gap-2', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span :class="keyClass(isSel(key))">{{ String(key).toUpperCase() }}</span>
          {{ text }}
        </button>
      </div>
    </div>

    <!-- word_bank_gap_fill -->
    <div v-else-if="type === 'word_bank_gap_fill'">
      <div
        v-if="!stimulusInSide"
        class="rounded-leaf border border-line bg-card-2 p-4 mb-4 text-sm text-ink leading-loose"
        v-html="highlightGap(c.text_with_gaps, c.gap_number)"
      />
      <label class="block text-xs font-semibold uppercase tracking-wide text-muted mb-2">
        {{ t("session.q.choose_word") }}
      </label>
      <select :value="selected" :class="selectClass" @change="onSelect">
        <option value="" disabled>{{ t("session.q.select_placeholder") }}</option>
        <option v-for="(word, key) in wordBank" :key="key" :value="String(key)">
          {{ String(key).toUpperCase() }}) {{ word }}
        </option>
      </select>
    </div>

    <!-- zuordnung_personen (Goethe B2 Lesen T1) -->
    <div v-else-if="type === 'zuordnung_personen'">
      <p class="text-[15px] text-ink leading-relaxed mb-4">{{ c.statement }}</p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="(person, key) in c.persons"
          :key="key"
          type="button"
          :class="['p-3 rounded-leaf border-2 text-left transition-colors', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span class="font-semibold">{{ String(key).toUpperCase() }} · {{ person.name }}</span>
          <span v-if="!stimulusInSide" class="block text-xs text-muted mt-1 line-clamp-2">{{ person.text }}</span>
        </button>
      </div>
    </div>

    <!-- lueckentext_saetze (Goethe B2 Lesen T2) -->
    <div v-else-if="type === 'lueckentext_saetze'">
      <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">
        {{ t("session.q.choose_sentence") }}
      </p>
      <div class="space-y-2">
        <button
          v-for="(text, key) in c.candidates"
          :key="key"
          type="button"
          :class="['w-full text-left px-4 py-3 rounded-leaf border-2 text-sm transition-colors flex items-start gap-3', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span :class="keyClass(isSel(key))">{{ String(key).toUpperCase() }}</span>
          <span class="pt-0.5">{{ text }}</span>
        </button>
      </div>
    </div>

    <!-- zuordnung_meinungen (Goethe B2 Lesen T4) -->
    <div v-else-if="type === 'zuordnung_meinungen'">
      <div class="rounded-leaf border border-line bg-card-2 px-4 py-3 mb-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-1">
          {{ t("session.q.title_to_match") }}
        </p>
        <p class="text-[15px] font-semibold text-ink">{{ c.title }}</p>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <button
          v-for="(opinion, key) in c.opinions"
          :key="key"
          type="button"
          :class="['px-3 py-2.5 rounded-leaf border-2 text-left text-sm transition-colors', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span class="font-semibold">{{ String(key).toUpperCase() }} · {{ opinion.author }}</span>
          <span v-if="!stimulusInSide" class="block text-xs text-muted mt-1 line-clamp-2">{{ opinion.text }}</span>
        </button>
      </div>
    </div>

    <!-- zuordnung_paragraphen (Goethe Lesen T5) -->
    <div v-else-if="type === 'zuordnung_paragraphen'">
      <div
        v-if="!stimulusInSide"
        class="rounded-leaf border border-line bg-card-2 p-4 mb-4 text-[15px] text-ink leading-relaxed"
      >
        {{ c.paragraph_text }}
      </div>
      <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">
        {{ t("session.q.choose_heading") }}
      </p>
      <div class="space-y-2">
        <button
          v-for="(heading, key) in c.headings"
          :key="key"
          type="button"
          :class="['w-full text-left px-4 py-2.5 rounded-leaf border-2 text-sm transition-colors flex items-center gap-3', optionClass(isSel(key))]"
          @click="choose(key)"
        >
          <span :class="keyClass(isSel(key))">{{ String(key).toUpperCase() }}</span>
          <span>{{ heading }}</span>
        </button>
      </div>
    </div>

    <!-- gap_fill_letters (ÖSD Lesen T3) -->
    <div v-else-if="type === 'gap_fill_letters'">
      <div class="rounded-leaf border border-line bg-card-2 p-4 mb-4 text-[15px] text-ink leading-relaxed">
        {{ c.visible_text }}
        <span class="inline-block min-w-10 border-b-2 border-primary px-1.5 mx-1 font-bold text-primary">
          {{ textDraft || "___" }}
        </span>
      </div>
      <label class="block text-xs font-semibold uppercase tracking-wide text-muted mb-2">
        {{ t("session.q.letters_hint") }}
      </label>
      <input
        type="text"
        maxlength="6"
        autocomplete="off"
        autocapitalize="off"
        spellcheck="false"
        :value="textDraft"
        :class="[inputClass, 'w-32']"
        @input="onTextInput(($event.target as HTMLInputElement).value.toLowerCase())"
      />
    </div>

    <!-- gap_fill_words (ÖSD Lesen T4) -->
    <div v-else-if="type === 'gap_fill_words'">
      <div
        v-if="!stimulusInSide"
        class="rounded-leaf border border-line bg-card-2 p-4 mb-4 text-sm text-ink leading-loose"
        v-html="highlightGap(c.text_with_gaps, c.gap_number)"
      />
      <label class="block text-xs font-semibold uppercase tracking-wide text-muted mb-2">
        {{ t("session.q.word_hint") }}
      </label>
      <input
        type="text"
        autocomplete="off"
        spellcheck="false"
        :value="textDraft"
        :placeholder="t('session.q.your_answer')"
        :class="[inputClass, 'w-full max-w-xs']"
        @input="onTextInput(($event.target as HTMLInputElement).value)"
      />
    </div>

    <!-- tableau_mixed (ÖSD Hören T2) -->
    <div v-else-if="type === 'tableau_mixed'">
      <p class="text-sm font-semibold text-ink mb-3">{{ c.zeile_name }}</p>

      <div v-if="c.type === 'checkbox'" class="space-y-3">
        <div v-for="col in c.spalten" :key="col" class="rounded-leaf border border-line p-3">
          <p class="text-xs font-semibold text-muted mb-2">{{ col }}</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="opt in c.options"
              :key="opt"
              type="button"
              :class="['px-3 py-1.5 rounded-leaf border-2 text-xs font-medium transition-colors', optionClass(tableauHas(col, opt))]"
              @click="toggleTableauOption(col, opt)"
            >
              {{ opt }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div v-for="col in c.spalten" :key="col">
          <p class="text-xs font-semibold text-muted mb-1">{{ col }}</p>
          <input
            type="text"
            autocomplete="off"
            spellcheck="false"
            :value="tableauDraft[col] ?? ''"
            :placeholder="t('session.q.your_answer')"
            :class="[inputClass, 'w-full']"
            @input="setTableauText(col, ($event.target as HTMLInputElement).value)"
          />
        </div>
      </div>
    </div>

    <!-- Format inconnu -->
    <div v-else class="rounded-leaf border border-amber-500/30 bg-amber-500/10 p-4">
      <p class="text-sm text-amber-700">{{ t("session.q.unsupported", { type }) }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    question: any;
    answer: any;
    teilAnzeigen?: Record<string, any>;
    teilWordBank?: Record<string, string>;
    stimulusInSide?: boolean; // le support est déjà affiché dans la colonne de gauche
  }>(),
  { stimulusInSide: false },
);

const emit = defineEmits<{ answer: [value: any] }>();

const { t } = useI18n();

const type = computed(() => String(props.question.question_type || ""));
const c = computed<Record<string, any>>(() => props.question.content || {});

// ── Sélection ─────────────────────────────────────────

const selected = computed(() =>
  props.answer?.answer != null ? String(props.answer.answer) : "",
);

// Comparaison insensible à la casse (ÖSD : réponses "C" pour la clé "c")
const isSel = (key: string | number) =>
  selected.value !== "" && selected.value.toLowerCase() === String(key).toLowerCase();

const choose = (key: string | number) => emit("answer", { answer: String(key) });

const onSelect = (e: Event) => choose((e.target as HTMLSelectElement).value);

// ── Styles communs ────────────────────────────────────

const optionClass = (sel: boolean) =>
  sel
    ? "border-primary bg-primary/10 text-ink"
    : "border-line bg-card text-ink hover:border-primary/40 hover:bg-card-2";

const keyClass = (sel: boolean) => [
  "shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
  sel ? "bg-primary text-white" : "bg-card-2 text-muted border border-line",
];

const selectClass =
  "w-full rounded-leaf border-2 border-line bg-card px-3 py-2.5 text-sm text-ink outline-none focus:border-primary transition-colors";

const inputClass =
  "px-3 py-2 rounded-leaf border-2 border-line bg-card text-sm font-medium text-ink outline-none focus:border-primary transition-colors";

// ── Libellés ──────────────────────────────────────────

const badge = computed(() => {
  const n = props.question.question_number;
  switch (type.value) {
    case "qcm_gap_fill":
    case "word_bank_gap_fill":
    case "gap_fill_words":
    case "lueckentext_saetze":
      return t("session.q.gap", { n: c.value.gap_number ?? n });
    case "zuordnung_titre":
      return t("session.q.text_n", { n });
    case "zuordnung_paragraphen":
      return t("session.q.paragraph", { n: c.value.paragraph_number ?? n });
    default:
      return String(n);
  }
});

// Vocabulaire de la copie d'examen : reste en allemand
const binaryOptions = computed(() =>
  type.value === "ja_nein"
    ? [{ value: "ja", label: "Ja" }, { value: "nein", label: "Nein" }]
    : [{ value: "richtig", label: "Richtig" }, { value: "falsch", label: "Falsch" }],
);

const noMatchKey = computed(() => (type.value === "matching" ? "0" : "x"));

const adKeys = computed(() => {
  const anzeigen = props.teilAnzeigen || c.value.anzeigen || {};
  return [...Object.keys(anzeigen), noMatchKey.value];
});

const wordBank = computed(() => props.teilWordBank || c.value.word_bank || {});

const speakerName = (speaker: any) =>
  typeof speaker === "object" ? (speaker?.name ?? "") : String(speaker);

// ── Texte à trous (échappé avant v-html) ──────────────

const escapeHtml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const highlightGap = (text: string, gapNumber: number): string => {
  if (!text) return "";
  return escapeHtml(text)
    .replace(/\n/g, "<br>")
    .replace(/\((\d+)\)|_(\d+)_/g, (_m, a, b) => {
      const n = a ?? b;
      return String(n) === String(gapNumber)
        ? `<span class="inline-flex items-center justify-center min-w-6 h-6 px-1.5 mx-0.5 rounded-full bg-primary text-white text-xs font-bold align-middle">${n}</span>`
        : `<span class="text-faint text-xs font-semibold">(${n})</span>`;
    });
};

// ── Réponses tapées : envoi après une pause de frappe ─

const SAVE_DELAY = 500;
const textDraft = ref<string>(props.answer?.answer ?? "");
let textTimer: ReturnType<typeof setTimeout> | null = null;

function onTextInput(value: string) {
  textDraft.value = value;
  if (textTimer) clearTimeout(textTimer);
  textTimer = setTimeout(flushText, SAVE_DELAY);
}

function flushText() {
  if (textTimer) {
    clearTimeout(textTimer);
    textTimer = null;
  }
  emit("answer", { answer: textDraft.value.trim() });
}

// ── tableau_mixed ─────────────────────────────────────

const tableauDraft = reactive<Record<string, any>>({ ...(props.answer?.answers || {}) });
let tableauTimer: ReturnType<typeof setTimeout> | null = null;

const tableauHas = (col: string, opt: string) =>
  ((tableauDraft[col] as string[]) || []).includes(opt);

function toggleTableauOption(col: string, opt: string) {
  const values: string[] = tableauDraft[col] || [];
  tableauDraft[col] = values.includes(opt) ? values.filter((v) => v !== opt) : [...values, opt];
  emit("answer", { answers: { ...tableauDraft } });
}

function setTableauText(col: string, value: string) {
  tableauDraft[col] = value;
  if (tableauTimer) clearTimeout(tableauTimer);
  tableauTimer = setTimeout(flushTableau, SAVE_DELAY);
}

function flushTableau() {
  if (tableauTimer) {
    clearTimeout(tableauTimer);
    tableauTimer = null;
  }
  emit("answer", { answers: { ...tableauDraft } });
}

// Rien ne se perd si l'apprenant change de Teil pendant la frappe
onBeforeUnmount(() => {
  if (textTimer) flushText();
  if (tableauTimer) flushTableau();
});
</script>