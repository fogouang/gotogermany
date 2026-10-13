<template>
  <div class="lg:h-full flex flex-col">
    <!-- Onglets mobile -->
    <div class="lg:hidden sticky top-0 z-10 bg-canvas border-b border-line px-4 py-2">
      <div class="grid grid-cols-2 gap-1 p-1 rounded-leaf bg-card-2">
        <button type="button" :class="tabClass('task')" @click="mobileTab = 'task'">
          {{ t("session.writing.tab_task") }}
        </button>
        <button type="button" :class="tabClass('write')" @click="mobileTab = 'write'">
          {{ t("session.writing.tab_write") }}
        </button>
      </div>
    </div>

    <div class="flex-1 min-h-0 flex flex-col lg:flex-row">
      <!-- ── Colonne gauche : sujet ── -->
      <section
        :class="[
          'bg-card lg:w-[45%] lg:border-r border-line lg:overflow-y-auto lg:min-h-0',
          mobileTab === 'task' ? 'block' : 'hidden lg:block',
        ]"
      >
        <div class="p-5 sm:p-6 space-y-4">
          <div class="rounded-leaf border border-primary/20 bg-primary/5 px-4 py-3">
            <p class="text-sm font-medium text-ink whitespace-pre-line">{{ teil.instructions }}</p>
          </div>

          <SprachlicheMittelPanel :mittel-key="mittelKey" />

          <div v-for="q in questions" :key="q.id" class="space-y-4">
            <!-- ══ Choix entre 2 sujets (TELC / ÖSD B2 : themen) ══ -->
            <template v-if="q.content.themes">
              <div v-if="!choice[q.id]" class="space-y-3">
                <p class="text-sm font-semibold text-ink">{{ t("session.writing.choose_theme") }}</p>
                <button
                  v-for="(theme, key) in q.content.themes"
                  :key="key"
                  type="button"
                  class="w-full p-4 rounded-card border-2 border-line bg-card text-left hover:border-primary/40 transition-colors"
                  @click="selectChoice(q, String(key))"
                >
                  <p class="font-semibold text-ink mb-1">
                    {{ t("session.writing.aufgabe", { n: key }) }} · {{ theme.titel }}
                  </p>
                  <p class="text-xs text-muted line-clamp-2">{{ stimulusString(theme.stimulus) }}</p>
                </button>
              </div>

              <template v-else>
                <div class="flex items-center justify-between gap-3">
                  <p class="text-sm font-semibold text-ink">
                    {{ t("session.writing.aufgabe", { n: choice[q.id] }) }} ·
                    {{ activeTheme(q)?.titel }}
                  </p>
                  <button
                    type="button"
                    class="text-xs font-medium text-primary hover:underline disabled:text-faint disabled:no-underline disabled:cursor-not-allowed shrink-0"
                    :disabled="!!drafts[q.id]?.trim()"
                    :title="drafts[q.id]?.trim() ? t('session.writing.change_locked') : ''"
                    @click="resetChoice(q)"
                  >
                    {{ t("session.writing.change_theme") }}
                  </button>
                </div>

                <!-- Support (annonce) -->
                <div class="rounded-card border border-line bg-card-2 p-5">
                  <p class="text-[15px] text-ink leading-relaxed whitespace-pre-line">
                    {{ stimulusString(activeTheme(q)?.stimulus) }}
                  </p>
                </div>

                <!-- Points à traiter -->
                <div class="rounded-card border border-amber-500/30 bg-amber-500/5 p-5 space-y-3">
                  <p class="text-sm font-semibold text-ink">{{ t("session.writing.leitpunkte") }}</p>
                  <ul class="space-y-1.5">
                    <li
                      v-for="(prompt, i) in activeTheme(q)?.prompts"
                      :key="i"
                      class="flex gap-2 text-sm text-ink"
                    >
                      <i class="pi pi-circle-fill text-[5px] text-amber-600 mt-2 shrink-0"></i>
                      <span>{{ prompt }}</span>
                    </li>
                  </ul>
                  <p v-if="isTelc" class="text-xs text-muted">{{ t("session.writing.telc_rule") }}</p>
                  <p v-if="isTelc" class="text-xs text-muted">{{ t("session.writing.letter_form") }}</p>
                  <p v-if="q.content.word_count_target" class="text-xs font-semibold text-amber-700">
                    {{ t("schreiben.approx") }} {{ q.content.word_count_target }} {{ t("schreiben.words") }}
                  </p>
                </div>
              </template>
            </template>

            <!-- ══ Choix entre 2 variantes d'opinion (ÖSD) ══ -->
            <template v-else-if="q.content.opinion_variants">
              <div v-if="!choice[q.id]" class="space-y-3">
                <p class="text-sm font-semibold text-ink">{{ t("session.writing.choose_theme") }}</p>
                <button
                  v-for="(variant, key) in q.content.opinion_variants"
                  :key="key"
                  type="button"
                  class="w-full p-4 rounded-card border-2 border-line bg-card text-left hover:border-primary/40 transition-colors"
                  @click="selectChoice(q, String(key))"
                >
                  <p class="font-semibold text-ink">{{ variant.thema }}</p>
                </button>
              </div>

              <template v-else>
                <div class="flex items-center justify-between gap-3">
                  <p class="text-sm font-semibold text-ink">{{ activeVariant(q)?.thema }}</p>
                  <button
                    type="button"
                    class="text-xs font-medium text-primary hover:underline disabled:text-faint disabled:no-underline disabled:cursor-not-allowed shrink-0"
                    :disabled="!!drafts[q.id]?.trim()"
                    :title="drafts[q.id]?.trim() ? t('session.writing.change_locked') : ''"
                    @click="resetChoice(q)"
                  >
                    {{ t("session.writing.change_theme") }}
                  </button>
                </div>

                <div v-if="activeVariant(q)?.aussagen?.length" class="space-y-2">
                  <p class="text-xs font-semibold uppercase tracking-wide text-faint">
                    {{
                      activeVariant(q)?.type === "schlagzeilen"
                        ? t("session.writing.headlines")
                        : t("session.writing.opinions")
                    }}
                  </p>
                  <div
                    v-for="(aussage, i) in activeVariant(q)?.aussagen"
                    :key="i"
                    :class="[
                      'rounded-leaf border border-line bg-card-2 p-3 text-sm text-ink',
                      activeVariant(q)?.type === 'schlagzeilen' ? 'font-semibold' : 'italic',
                    ]"
                  >
                    <template v-if="activeVariant(q)?.type === 'schlagzeilen'">{{ aussage }}</template>
                    <template v-else>„{{ aussage }}“</template>
                  </div>
                </div>

                <div
                  v-if="q.content.leitpunkte?.length"
                  class="rounded-card border border-amber-500/30 bg-amber-500/5 p-5 space-y-3"
                >
                  <p class="text-sm font-semibold text-ink">{{ t("session.writing.leitpunkte") }}</p>
                  <ul class="space-y-1.5">
                    <li v-for="(punkt, i) in q.content.leitpunkte" :key="i" class="flex gap-2 text-sm text-ink">
                      <i class="pi pi-circle-fill text-[5px] text-amber-600 mt-2 shrink-0"></i>
                      <span>{{ punkt }}</span>
                    </li>
                  </ul>
                  <p v-if="q.content.word_count_target" class="text-xs font-semibold text-amber-700">
                    {{ t("schreiben.approx") }} {{ q.content.word_count_target }} {{ t("schreiben.words") }}
                  </p>
                </div>
              </template>
            </template>

            <!-- ══ Formats simples (Goethe, TELC message unique, ÖSD réclamation) ══ -->
            <template v-else>
              <!-- E-mail reçu (TELC) -->
              <div
                v-if="q.content.stimulus_email?.sender || q.content.stimulus_email?.subject || q.content.stimulus_email?.body"
                class="rounded-card border border-line overflow-hidden"
              >
                <div class="bg-card-2 border-b border-line px-5 py-3 space-y-1 text-sm">
                  <p v-if="q.content.stimulus_email.sender">
                    <span class="font-semibold text-muted inline-block w-16">Von:</span>
                    <span class="text-ink font-medium">{{ q.content.stimulus_email.sender }}</span>
                  </p>
                  <p v-if="q.content.stimulus_email.subject">
                    <span class="font-semibold text-muted inline-block w-16">Betreff:</span>
                    <span class="text-ink">{{ q.content.stimulus_email.subject }}</span>
                  </p>
                </div>
                <p class="px-5 py-4 text-[15px] text-ink whitespace-pre-line leading-relaxed">
                  {{ q.content.stimulus_email.body }}
                </p>
              </div>

              <!-- Message de forum (Goethe) -->
              <div v-else-if="q.content.stimulus" class="rounded-card border border-line bg-card-2 p-5">
                <div class="flex items-center gap-2 mb-2">
                  <i class="pi pi-comment text-muted"></i>
                  <span class="text-sm font-semibold text-ink">
                    {{ stimulusAuthor(q) || t("schreiben.comment") }}
                  </span>
                </div>
                <p v-if="stimulusTitle(q)" class="text-xs font-semibold text-muted mb-2">{{ stimulusTitle(q) }}</p>
                <p class="text-[15px] text-ink italic leading-relaxed">{{ stimulusString(q.content.stimulus) }}</p>
              </div>

              <!-- Destinataire -->
              <div v-if="q.content.recipient" class="rounded-leaf border border-line bg-card-2 px-4 py-2 text-sm">
                <span class="font-semibold text-muted">An:</span>
                <span class="text-ink ml-2">{{ q.content.recipient }}</span>
              </div>

              <!-- Réclamation (ÖSD : promesses / réalité) -->
              <div v-if="q.content.info_comparison" class="rounded-card border border-line overflow-hidden">
                <div class="bg-card-2 border-b border-line px-5 py-3">
                  <p class="text-sm font-semibold text-ink">{{ q.content.info_comparison.anbieter }}</p>
                  <p class="text-xs text-muted mt-1">{{ q.content.info_comparison.situation }}</p>
                </div>
                <div class="px-5 py-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-2">
                      {{ t("session.writing.promised") }}
                    </p>
                    <ul class="space-y-1.5">
                      <li v-for="(v, i) in q.content.info_comparison.versprechen" :key="i" class="flex gap-2 text-sm text-ink">
                        <i class="pi pi-check text-[10px] text-emerald-600 mt-1.5 shrink-0"></i>
                        <span>{{ v }}</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-red-600 mb-2">
                      {{ t("session.writing.reality") }}
                    </p>
                    <ul class="space-y-1.5">
                      <li v-for="(p, i) in q.content.info_comparison.probleme" :key="i" class="flex gap-2 text-sm text-ink">
                        <i class="pi pi-times text-[10px] text-red-500 mt-1.5 shrink-0"></i>
                        <span>{{ p }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
                <p
                  v-if="q.content.info_comparison.kontakt"
                  class="px-5 py-3 bg-card-2 border-t border-line text-xs text-muted"
                >
                  {{ t("session.writing.contact") }} : {{ q.content.info_comparison.kontakt }}
                </p>
              </div>

              <!-- Thème / situation / points -->
              <div
                v-if="q.content.topic || q.content.scenario || q.content.prompts?.length || q.content.word_count_target"
                class="rounded-card border border-amber-500/30 bg-amber-500/5 p-5 space-y-3"
              >
                <p v-if="q.content.topic" class="text-base font-bold text-ink">{{ q.content.topic }}</p>
                <p v-if="q.content.scenario" class="text-sm text-ink leading-relaxed">{{ q.content.scenario }}</p>
                <template v-if="q.content.prompts?.length">
                  <p class="text-sm font-semibold text-ink">{{ t("session.writing.leitpunkte") }}</p>
                  <ul class="space-y-1.5">
                    <li v-for="(prompt, i) in q.content.prompts" :key="i" class="flex gap-2 text-sm text-ink">
                      <i class="pi pi-circle-fill text-[5px] text-amber-600 mt-2 shrink-0"></i>
                      <span>{{ prompt }}</span>
                    </li>
                  </ul>
                </template>
                <p v-if="q.content.word_count_target" class="text-xs font-semibold text-amber-700">
                  {{ t("schreiben.approx") }} {{ q.content.word_count_target }} {{ t("schreiben.words") }}
                  <span v-if="isFormal(q)"> · {{ t("schreiben.formal_required") }}</span>
                </p>
              </div>
            </template>
          </div>
        </div>
      </section>

      <!-- ── Colonne droite : rédaction ── -->
      <section
        :class="[
          'bg-canvas lg:w-[55%] lg:overflow-y-auto lg:min-h-0',
          mobileTab === 'write' ? 'block' : 'hidden lg:block',
        ]"
      >
        <div class="p-5 sm:p-6 space-y-4 max-w-2xl mx-auto">
          <div
            v-for="q in questions"
            :key="`input-${q.id}`"
            class="bg-card border-2 border-line rounded-card overflow-hidden transition-colors focus-within:border-primary/50"
          >
            <textarea
              v-if="isUnlocked(q)"
              :value="drafts[q.id]"
              :placeholder="t('schreiben.placeholder')"
              rows="14"
              spellcheck="false"
              autocomplete="off"
              autocorrect="off"
              autocapitalize="off"
              data-gramm="false"
              data-gramm_editor="false"
              data-enable-grammarly="false"
              class="block w-full min-h-72 resize-y bg-card px-5 py-4 text-[15px] leading-8 text-ink outline-none placeholder:text-faint"
              @input="onInput(q, ($event.target as HTMLTextAreaElement).value)"
            />
            <div v-else class="flex items-center gap-3 px-5 py-10 text-sm text-muted">
              <i class="pi pi-lock text-faint"></i>
              <span>{{ t("session.writing.choose_first") }}</span>
            </div>

            <div class="border-t border-line bg-card-2 px-4 py-2.5 flex flex-wrap items-center gap-x-4 gap-y-2">
              <!-- Compteur de mots -->
              <div class="flex items-center gap-2">
                <span
                  :class="[
                    'text-sm font-semibold tabular-nums',
                    reachedTarget(q) ? 'text-emerald-600' : 'text-ink',
                  ]"
                >
                  {{ t("session.writing.words", { n: wordCount(q) }, wordCount(q)) }}
                </span>
                <template v-if="q.content.word_count_target">
                  <div class="w-20 h-1.5 rounded-full bg-line/60 overflow-hidden">
                    <div
                      :class="['h-full rounded-full transition-all', reachedTarget(q) ? 'bg-emerald-500' : 'bg-primary']"
                      :style="{ width: `${Math.min((wordCount(q) / q.content.word_count_target) * 100, 100)}%` }"
                    />
                  </div>
                  <span class="text-xs text-muted">
                    {{ t("session.writing.target", { n: q.content.word_count_target }) }}
                  </span>
                </template>
              </div>

              <!-- État d'enregistrement -->
              <span class="text-xs text-faint">
                <template v-if="pending[q.id]">{{ t("session.writing.saving") }}</template>
                <template v-else-if="drafts[q.id]">
                  <i class="pi pi-check text-[10px] mr-1"></i>{{ t("session.writing.saved") }}
                </template>
              </span>

              <Button
                class="ml-auto"
                icon="pi pi-download"
                label="PDF"
                outlined
                size="small"
                severity="secondary"
                :loading="downloading"
                :disabled="!drafts[q.id]?.trim()"
                v-tooltip.top="t('schreiben.download_pdf')"
                @click="downloadPDF(q)"
              />
            </div>
          </div>

          <p class="text-xs text-faint flex items-center gap-1.5">
            <i class="pi pi-info-circle text-[11px]"></i>
            {{ t("session.writing.no_spellcheck") }}
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import SprachlicheMittelPanel from "~/components/session/SprachlicheMittelPanel.vue";
import { resolveMittelKey } from "#shared/sprachlicheMittel";

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
  sessionId: string;
  examName?: string;
  /** true quand le temps du bloc Schreiben est écoulé */
  timeExpired?: boolean;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const { t, locale } = useI18n();

const mobileTab = ref<"task" | "write">("task");
const downloading = ref(false);

const tabClass = (tab: "task" | "write") => [
  "py-2 rounded-lg text-sm font-medium transition-colors",
  mobileTab.value === tab ? "bg-card text-ink shadow-soft" : "text-muted",
];

// ── Examen (pour Sprachliche Mittel et règles TELC) ───

function parseExamInfo(name?: string) {
  const n = (name || "").toLowerCase();
  let provider = "";
  if (n.includes("ösd") || n.includes("osd")) provider = "ÖSD";
  else if (n.includes("goethe")) provider = "Goethe";
  else if (n.includes("telc")) provider = "TELC";
  const cefrMatch = n.match(/b1|b2/);
  return { provider, cefrCode: cefrMatch ? cefrMatch[0].toUpperCase() : "" };
}

const examInfo = computed(() => parseExamInfo(props.examName));
const isTelc = computed(() => examInfo.value.provider === "TELC");

const mittelKey = computed(() =>
  resolveMittelKey({
    provider: examInfo.value.provider,
    cefrCode: examInfo.value.cefrCode,
    moduleSlug: "schreiben",
    formatType: props.teil?.format_type,
    teilNumber: props.teil?.teil_number,
  }),
);

const isFormal = (q: any) => String(q.content.register || "").toLowerCase().startsWith("formell");

// ── Brouillons, choix du sujet, enregistrement ────────

const drafts = reactive<Record<string, string>>({});
const choice = reactive<Record<string, string | null>>({});
const pending = reactive<Record<string, boolean>>({});

for (const q of props.questions) {
  const saved = props.answers[q.id]?.user_answer || {};
  drafts[q.id] = saved.text || "";
  choice[q.id] = saved.theme ?? saved.variant ?? null;
}

const choiceKind = (q: any): "theme" | "variant" | null =>
  q.content.themes ? "theme" : q.content.opinion_variants ? "variant" : null;

const activeTheme = (q: any) => {
  const key = choice[q.id];
  return key && q.content.themes ? q.content.themes[key] : null;
};

const activeVariant = (q: any) => {
  const key = choice[q.id];
  return key && q.content.opinion_variants ? q.content.opinion_variants[key] : null;
};

const isUnlocked = (q: any) => (choiceKind(q) ? !!choice[q.id] : true);

const payload = (q: any) => {
  const kind = choiceKind(q);
  const key = choice[q.id];
  return {
    text: drafts[q.id] || "",
    ...(kind && key ? { [kind]: key } : {}),
  };
};

const SAVE_DELAY = 800;
const timers = new Map<string, ReturnType<typeof setTimeout>>();

function flush(q: any) {
  const timer = timers.get(q.id);
  if (timer) {
    clearTimeout(timer);
    timers.delete(q.id);
  }
  pending[q.id] = false;
  emit("answer", q.id, payload(q));
}

function flushAll() {
  for (const q of props.questions) {
    if (timers.has(q.id)) flush(q);
  }
}

function onInput(q: any, value: string) {
  drafts[q.id] = value;
  pending[q.id] = true;
  const existing = timers.get(q.id);
  if (existing) clearTimeout(existing);
  timers.set(q.id, setTimeout(() => flush(q), SAVE_DELAY));
}

function selectChoice(q: any, key: string) {
  choice[q.id] = key;
  flush(q);
}

function resetChoice(q: any) {
  if (drafts[q.id]?.trim()) return;
  choice[q.id] = null;
  flush(q);
}

// ── Mots ──────────────────────────────────────────────

const wordCount = (q: any): number => {
  const text = (drafts[q.id] || "").trim();
  return text ? text.split(/\s+/).filter(Boolean).length : 0;
};

const reachedTarget = (q: any) =>
  !!q.content.word_count_target && wordCount(q) >= q.content.word_count_target;

// ── Fin du temps : on enregistre puis PDF automatique ─

const autoDownloaded = ref(false);

watch(
  () => props.timeExpired,
  async (expired) => {
    if (!expired) return;
    flushAll();
    if (autoDownloaded.value) return;
    autoDownloaded.value = true;
    for (const q of props.questions) {
      if ((drafts[q.id] || "").trim()) await downloadPDF(q);
    }
  },
);

onBeforeUnmount(flushAll);

// ── Message de forum : string ou {text, title, author} ─

const parseStimulus = (raw: any): { text: string; title?: string; author?: string } => {
  if (!raw) return { text: "" };
  if (typeof raw === "object") return { text: raw.text || "", title: raw.title, author: raw.author };
  const trimmed = String(raw).trim();
  if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
    try {
      const parsed = JSON.parse(trimmed);
      return { text: parsed.text || trimmed, title: parsed.title, author: parsed.author };
    } catch {
      return { text: trimmed };
    }
  }
  return { text: trimmed };
};

const stimulusString = (raw: any) => parseStimulus(raw).text;
const stimulusAuthor = (q: any) => parseStimulus(q.content.stimulus).author || q.content.stimulus_author || "";
const stimulusTitle = (q: any) => parseStimulus(q.content.stimulus).title || "";

// ── PDF de la copie ───────────────────────────────────

const BRAND = { name: "GoToGermany", site: "prep-telc-osd.com" };

function taskOf(q: any) {
  const key = choice[q.id];
  const theme = activeTheme(q);
  const variant = activeVariant(q);
  const info = q.content.info_comparison;

  const title = theme
    ? `Aufgabe ${key}: ${theme.titel || ""}`
    : variant?.thema || q.content.topic || "";

  const context =
    stimulusString(theme?.stimulus) ||
    q.content.scenario ||
    (info ? `${info.anbieter}: ${info.situation}` : "") ||
    stimulusString(q.content.stimulus) ||
    q.content.stimulus_email?.body ||
    "";

  const points: string[] =
    theme?.prompts || (variant ? q.content.leitpunkte : null) || q.content.prompts || q.content.leitpunkte || [];

  return { title, context, points };
}

async function downloadPDF(q: any) {
  downloading.value = true;
  try {
    const { jsPDF } = await import("jspdf");
    const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxW = pageW - margin * 2;
    const bottom = pageH - 20;
    let y = 0;

    const ensureSpace = (h: number) => {
      if (y + h > bottom) {
        doc.addPage();
        y = margin;
      }
    };

    // En-tête
    doc.setFillColor(15, 23, 42);
    doc.rect(0, 0, pageW, 26, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(15);
    doc.text(BRAND.name, margin, 12);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(props.examName || "", margin, 19);
    doc.text(
      new Date().toLocaleDateString(locale.value, { day: "2-digit", month: "long", year: "numeric" }),
      pageW - margin,
      19,
      { align: "right" },
    );
    y = 38;

    // Titre
    doc.setTextColor(30, 41, 59);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.text(`SCHREIBEN · Teil ${props.teil.teil_number}`, margin, y);
    y += 3;
    doc.setDrawColor(203, 213, 225);
    doc.setLineWidth(0.4);
    doc.line(margin, y, pageW - margin, y);
    y += 8;

    // Consigne
    if (props.teil.instructions) {
      doc.setFont("helvetica", "italic");
      doc.setFontSize(9);
      doc.setTextColor(71, 85, 105);
      const lines = doc.splitTextToSize(props.teil.instructions, maxW);
      ensureSpace(lines.length * 4.5);
      doc.text(lines, margin, y);
      y += lines.length * 4.5 + 5;
    }

    // Aufgabe
    const task = taskOf(q);
    doc.setTextColor(30, 41, 59);
    if (task.title) {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      const lines = doc.splitTextToSize(task.title, maxW);
      ensureSpace(lines.length * 5);
      doc.text(lines, margin, y);
      y += lines.length * 5 + 2;
    }
    if (task.context) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9.5);
      const lines = doc.splitTextToSize(task.context, maxW);
      for (const line of lines) {
        ensureSpace(5);
        doc.text(line, margin, y);
        y += 5;
      }
      y += 2;
    }
    if (task.points.length) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9.5);
      for (const point of task.points) {
        const lines = doc.splitTextToSize(String(point), maxW - 6);
        ensureSpace(lines.length * 5);
        doc.text("-", margin + 1, y);
        doc.text(lines, margin + 5, y);
        y += lines.length * 5 + 1;
      }
    }
    if (q.content.word_count_target) {
      ensureSpace(6);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(9);
      doc.text(`ca. ${q.content.word_count_target} Wörter`, margin, y + 1);
      y += 6;
    }
    y += 4;

    // Réponse
    ensureSpace(14);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("Meine Antwort", margin, y);
    y += 3;
    doc.line(margin, y, pageW - margin, y);
    y += 7;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10.5);
    doc.setTextColor(15, 23, 42);
    const answerLines = doc.splitTextToSize(drafts[q.id] || "", maxW);
    for (const line of answerLines) {
      ensureSpace(6.5);
      doc.text(line, margin, y);
      y += 6.5;
    }

    ensureSpace(10);
    y += 3;
    doc.setDrawColor(203, 213, 225);
    doc.line(margin, y, pageW - margin, y);
    y += 5;
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8.5);
    doc.setTextColor(100, 116, 139);
    doc.text(
      `${wordCount(q)} Wörter${q.content.word_count_target ? ` / ca. ${q.content.word_count_target}` : ""}`,
      margin,
      y,
    );

    // Pied de page sur chaque page
    const pages = doc.getNumberOfPages();
    for (let i = 1; i <= pages; i++) {
      doc.setPage(i);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(7.5);
      doc.setTextColor(148, 163, 184);
      doc.text(`${BRAND.name} · ${BRAND.site}`, margin, pageH - 8);
      doc.text(`Seite ${i} / ${pages}`, pageW - margin, pageH - 8, { align: "right" });
    }

    doc.save(`schreiben_teil${props.teil.teil_number}_${Date.now()}.pdf`);
  } catch (err) {
    console.error("Erreur génération PDF:", err);
  } finally {
    downloading.value = false;
  }
}
</script>