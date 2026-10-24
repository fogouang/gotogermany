<template>
  <div class="lg:h-full flex flex-col">
    <!-- Onglets mobile -->
    <div
      v-if="hasStimulus"
      class="lg:hidden sticky top-0 z-10 bg-canvas border-b border-line px-4 py-2"
    >
      <div class="grid grid-cols-2 gap-1 p-1 rounded-leaf bg-card-2">
        <button
          type="button"
          :class="tabClass('text')"
          @click="mobileTab = 'text'"
        >
          {{ t("session.q.tab_text") }}
        </button>
        <button
          type="button"
          :class="tabClass('tasks')"
          @click="mobileTab = 'tasks'"
        >
          {{
            t("session.q.tab_tasks", {
              answered: answeredCount,
              total: questions.length,
            })
          }}
        </button>
      </div>
    </div>

    <div class="flex-1 min-h-0 flex flex-col lg:flex-row">
      <!-- ── Colonne gauche : textes ── -->
      <section
        v-if="hasStimulus"
        :class="[
          'bg-card lg:w-1/2 lg:border-r border-line lg:overflow-y-auto lg:min-h-0',
          mobileTab === 'text' ? 'block' : 'hidden lg:block',
        ]"
      >
        <div class="p-5 sm:p-6 space-y-4">
          <div
            class="rounded-leaf border border-primary/20 bg-primary/5 px-4 py-3"
          >
            <p class="text-sm font-medium text-ink whitespace-pre-line">
              {{ teil.instructions }}
            </p>
          </div>

          <p v-if="contextLine || docLabel" class="text-xs text-muted">
            <span v-if="docLabel" class="font-semibold text-ink">{{
              docLabel
            }}</span>
            <span v-if="docLabel && contextLine"> · </span>
            <span v-if="contextLine">{{ contextLine }}</span>
          </p>

          <img
            v-if="cfg.stimulus_image || cfg.image"
            :src="`${apiBase}/images/${cfg.stimulus_image || cfg.image}`"
            alt=""
            class="w-full rounded-leaf border border-line object-contain"
          />

          <h3
            v-if="cfg.article_title && fmt !== 'lueckentext_saetze'"
            class="font-bold text-ink text-base"
          >
            {{ cfg.article_title }}
          </h3>

          <div
            v-if="cfg.stimulus_text"
            class="text-[15px] text-ink leading-relaxed"
            v-html="formatText(cfg.stimulus_text)"
          />

          <!-- Grafik (TestDaF Lesen 7) -->
          <GrafikChart v-if="cfg.grafik" :grafik="cfg.grafik" />

          <!-- zuordnung_titre : titres puis textes -->
          <template v-if="fmt === 'zuordnung_titre'">
            <div class="rounded-card border border-line bg-card-2 p-4">
              <p
                class="text-xs font-semibold uppercase tracking-wide text-faint mb-2"
              >
                {{ t("session.q.headings") }}
              </p>
              <ul class="space-y-1.5">
                <li
                  v-for="(titre, key) in titres"
                  :key="key"
                  class="flex items-start gap-2 text-sm transition-opacity"
                  :class="
                    assignedTitres[String(key).toLowerCase()]
                      ? 'text-faint opacity-60'
                      : 'text-ink'
                  "
                >
                  <span class="font-bold text-primary w-5 shrink-0">{{
                    String(key)
                  }}</span>
                  <span class="flex-1">{{ titre }}</span>
                  <span
                    v-if="assignedTitres[String(key).toLowerCase()]"
                    class="shrink-0 rounded-full border border-line bg-card px-1.5 text-[10px] font-semibold text-muted"
                  >
                    {{
                      t("session.q.text_n", {
                        n: assignedTitres[String(key).toLowerCase()],
                      })
                    }}
                  </span>
                </li>
              </ul>
            </div>
            <div
              v-for="q in questions"
              :key="`stim-${q.id}`"
              class="rounded-card border border-line p-4"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wide text-faint mb-2"
              >
                {{ t("session.q.text_n", { n: q.question_number }) }}
              </p>
              <div
                class="text-[15px] text-ink leading-relaxed"
                v-html="formatText(q.content?.stimulus_text || '')"
              />
            </div>
          </template>

          <!-- lueckentext_saetze : article à trous -->
          <template v-else-if="fmt === 'lueckentext_saetze'">
            <img
              v-if="cfg.article_image"
              :src="`${apiBase}/images/${cfg.article_image}`"
              alt=""
              class="w-full rounded-leaf border border-line object-contain"
            />
            <h3 class="font-bold text-ink">{{ cfg.article_title }}</h3>
            <div
              class="text-[15px] text-ink leading-relaxed"
              v-html="formatGapText(cfg.article_text || '')"
            />
          </template>

          <!-- zuordnung_personen -->
          <template v-else-if="fmt === 'zuordnung_personen'">
            <div
              v-for="(person, key) in cfg.persons"
              :key="key"
              class="rounded-card border border-line p-4 flex gap-3 sm:gap-4 items-start"
            >
              <img
                v-if="person?.image"
                :src="`${apiBase}/images/${person.image}`"
                :alt="person.name"
                class="w-16 h-20 sm:w-24 sm:h-28 object-cover rounded-leaf border border-line shrink-0"
              />
              <div
                v-else
                class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center shrink-0"
              >
                <span class="font-bold text-primary">{{
                  String(key).toUpperCase()
                }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-ink mb-1">
                  {{ String(key).toLowerCase() }}) {{ person.name }}
                </p>
                <p class="text-[15px] text-ink leading-relaxed">
                  {{ person.text }}
                </p>
              </div>
            </div>
          </template>

          <!-- zuordnung_meinungen -->
          <template v-else-if="fmt === 'zuordnung_meinungen'">
            <div
              v-for="(opinion, key) in cfg.opinions"
              :key="key"
              class="rounded-card border border-line p-4"
            >
              <div class="flex items-center gap-3 mb-2">
                <img
                  v-if="opinion?.image"
                  :src="`${apiBase}/images/${opinion.image}`"
                  :alt="opinion.author"
                  class="w-10 h-10 rounded-full object-cover border border-line shrink-0"
                />
                <span
                  v-else
                  class="w-10 h-10 rounded-full bg-primary/10 text-primary font-bold text-sm flex items-center justify-center shrink-0"
                >
                  {{ String(key).toUpperCase() }}
                </span>
                <p class="font-semibold text-ink">
                  {{ String(key).toUpperCase() }} · {{ opinion.author }}
                </p>
              </div>
              <p class="text-[15px] text-ink leading-relaxed">
                {{ opinion.text }}
              </p>
            </div>
          </template>

          <!-- zuordnung_paragraphen -->
          <template v-else-if="fmt === 'zuordnung_paragraphen'">
            <div
              v-for="(para, key) in cfg.paragraphs"
              :key="key"
              class="rounded-card border border-line p-4"
            >
              <img
                v-if="para?.image"
                :src="`${apiBase}/images/${para.image}`"
                alt=""
                class="w-full h-32 object-cover rounded-leaf border border-line mb-2"
              />
              <p
                class="text-xs font-semibold uppercase tracking-wide text-faint mb-1"
              >
                {{
                  t("session.q.paragraph", {
                    n: String(key).replace(/^p/i, ""),
                  })
                }}
                <span v-if="para.title"> · {{ para.title }}</span>
              </p>
              <p class="text-[15px] text-ink leading-relaxed">
                {{ para.text }}
              </p>
            </div>
          </template>

          <!-- textabschnitte_ordnen : les textes à remettre dans l'ordre -->
          <template v-else-if="fmt === 'textabschnitte_ordnen'">
            <div
              v-for="(segment, key) in cfg.segments"
              :key="key"
              class="rounded-card border border-line p-4 transition-opacity"
              :class="
                assignedTitres[String(key).toLowerCase()] ? 'opacity-60' : ''
              "
            >
              <p class="flex items-center gap-2 mb-1">
                <span class="font-bold text-primary">{{ String(key) }}</span>
                <span
                  v-if="assignedTitres[String(key).toLowerCase()]"
                  class="rounded-full border border-line bg-card px-1.5 text-[10px] font-semibold text-muted"
                >
                  {{
                    t("session.q.position", {
                      n: assignedTitres[String(key).toLowerCase()],
                    })
                  }}
                </span>
              </p>
              <p class="text-[15px] text-ink leading-relaxed">{{ segment }}</p>
            </div>
          </template>

          <!-- Annonces (matching / selektives_matching) -->
          <template
            v-else-if="fmt === 'matching' || fmt === 'selektives_matching'"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-faint">
              {{ t("session.q.ads") }}
            </p>
            <div
              v-for="(anzeige, key) in cfg.anzeigen"
              :key="key"
              class="rounded-card border border-line p-4 flex items-start gap-3"
            >
              <span class="font-bold text-primary w-5 shrink-0">{{
                String(key).toUpperCase()
              }}</span>
              <div class="flex-1 min-w-0">
                <p
                  v-if="anzeigeField(anzeige, 'title')"
                  class="font-semibold text-ink text-sm mb-0.5"
                >
                  {{ anzeigeField(anzeige, "title") }}
                </p>
                <p class="text-sm text-ink leading-relaxed">
                  {{ anzeigeText(anzeige) }}
                </p>
                <p
                  v-if="anzeigeField(anzeige, 'contact')"
                  class="text-xs text-muted italic mt-1"
                >
                  {{ anzeigeField(anzeige, "contact") }}
                </p>
              </div>
              <img
                v-if="anzeigeField(anzeige, 'image')"
                :src="`${apiBase}/images/${anzeigeField(anzeige, 'image')}`"
                alt=""
                class="w-16 h-16 object-cover rounded-leaf border border-line shrink-0"
              />
            </div>
          </template>

          <!-- Sprachbausteine : texte à trous -->
          <template
            v-else-if="fmt === 'qcm_gap_fill' || fmt === 'word_bank_gap_fill'"
          >
            <p v-if="cfg.situation" class="text-xs text-muted italic">
              {{ cfg.situation }}
            </p>
            <div
              v-if="cfg.stimulus_anzeige"
              class="rounded-leaf border border-line bg-card-2 p-3 text-sm text-ink"
            >
              {{ cfg.stimulus_anzeige }}
            </div>
            <div
              class="text-[15px] text-ink leading-loose"
              v-html="formatGapText(cfg.text_with_gaps || '')"
            />
            <div v-if="fmt === 'word_bank_gap_fill' && cfg.word_bank">
              <p
                class="text-xs font-semibold uppercase tracking-wide text-faint mb-2"
              >
                {{ t("session.q.word_bank") }}
              </p>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div
                  v-for="(word, key) in cfg.word_bank"
                  :key="key"
                  class="text-xs rounded-leaf border border-line bg-card-2 px-3 py-2 flex gap-2 items-center transition-opacity"
                  :class="{
                    'opacity-50': assignedTitres[String(key).toLowerCase()],
                  }"
                >
                  <span class="font-bold text-primary shrink-0">{{
                    String(key).toUpperCase()
                  }}</span>
                  <span
                    class="flex-1"
                    :class="
                      assignedTitres[String(key).toLowerCase()]
                        ? 'text-faint line-through'
                        : 'text-ink'
                    "
                  >
                    {{ word }}
                  </span>
                  <span
                    v-if="assignedTitres[String(key).toLowerCase()]"
                    class="shrink-0 rounded-full bg-primary/10 px-1.5 text-[10px] font-bold text-primary"
                  >
                    {{ assignedTitres[String(key).toLowerCase()] }}
                  </span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </section>

      <!-- ── Colonne droite : questions ── -->
      <section
        :class="[
          'lg:overflow-y-auto lg:min-h-0',
          hasStimulus ? 'lg:w-1/2' : 'w-full',
          hasStimulus && mobileTab === 'text' ? 'hidden lg:block' : 'block',
        ]"
      >
        <div class="p-5 sm:p-6 max-w-2xl mx-auto space-y-4">
          <div
            v-if="!hasStimulus"
            class="rounded-leaf border border-primary/20 bg-primary/5 px-4 py-3"
          >
            <p class="text-sm font-medium text-ink whitespace-pre-line">
              {{ teil.instructions }}
            </p>
            <p v-if="contextLine || docLabel" class="text-xs text-muted mt-1">
              {{ [docLabel, contextLine].filter(Boolean).join(" · ") }}
            </p>
          </div>

          <!-- Question commune (Goethe B1 Lesen T4) -->
          <div
            v-if="cfg.fragestellung"
            class="rounded-leaf border border-line bg-card-2 px-4 py-3 text-sm font-semibold text-ink"
          >
            {{ cfg.fragestellung }}
          </div>

          <!-- Tableau à compléter (TestDaF Lesen 6) -->
          <div
            v-if="cfg.tabelle_title || cfg.begriffspaar"
            class="rounded-leaf border border-line bg-card-2 px-4 py-3"
          >
            <p v-if="cfg.tabelle_title" class="text-sm font-bold text-ink">
              {{ cfg.tabelle_title }}
            </p>
            <p v-if="cfg.begriffspaar" class="text-xs text-muted mt-0.5">
              {{ cfg.begriffspaar.join(" · ") }}
            </p>
          </div>

          <!-- Exemple 0 (ÖSD, ECL) -->
          <div
            v-if="beispiel"
            class="rounded-card border border-dashed border-line bg-card-2 p-4"
          >
            <p
              class="text-xs font-semibold uppercase tracking-wide text-faint mb-2"
            >
              {{ t("session.q.example") }} 0
            </p>
            <p v-if="beispiel.stem" class="text-sm text-ink mb-2">
              {{ beispiel.stem }}
            </p>
            <p v-if="beispiel.prompt" class="text-sm text-ink mb-2">
              {{ beispiel.prompt }}
            </p>
            <p v-if="beispiel.context" class="text-sm text-ink mb-2">
              {{ beispiel.context }}
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
                {{ key }}) {{ txt }}
              </li>
            </ul>
            <p v-else-if="beispiel.answer" class="text-sm text-ink">
              → <strong class="text-primary">{{ beispiel.answer }}</strong>
              <span v-if="beispiel.text" class="text-muted">
                · {{ beispiel.text }}</span
              >
            </p>
          </div>

          <!-- QCM avec plusieurs textes (Goethe B1 Lesen T2) -->
          <template v-if="hasTexts">
            <div
              v-for="(textBlock, ti) in cfg.texts"
              :key="ti"
              class="space-y-3"
            >
              <img
                v-if="textBlock?.image"
                :src="`${apiBase}/images/${textBlock.image}`"
                alt=""
                class="w-full rounded-leaf border border-line object-contain"
              />
              <div class="rounded-card border border-line bg-card p-4">
                <p v-if="textBlock.source" class="text-xs text-faint mb-2">
                  {{ textBlock.source }}
                </p>
                <div
                  class="text-[15px] text-ink leading-relaxed"
                  v-html="formatText(textBlock.stimulus_text)"
                />
              </div>
              <div
                v-for="q in questionsForText(textBlock)"
                :id="`question-${q.id}`"
                :key="q.id"
                :class="cardClass(q)"
              >
                <QuestionItem
                  :question="q"
                  :answer="answers[q.id]?.user_answer"
                  @answer="
                    (val: Record<string, any>) => emit('answer', q.id, val)
                  "
                />
              </div>
            </div>
          </template>

          <!-- Résumé à corriger (TestDaF Lesen 7) -->
          <FehlerZusammenfassung
            v-else-if="fmt === 'fehler_in_zusammenfassung'"
            :teil="teil"
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
              v-for="q in questions"
              :id="`question-${q.id}`"
              :key="q.id"
              :class="cardClass(q)"
            >
              <QuestionItem
                :question="q"
                :answer="answers[q.id]?.user_answer"
                :stimulus-in-side="hasStimulus"
                :teil-anzeigen="cfg.anzeigen"
                :teil-word-bank="cfg.word_bank"
                :taken-titres="takenTitresFor(q)"
                @answer="
                  (val: Record<string, any>) => emit('answer', q.id, val)
                "
              />
            </div>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionItem from "~/components/session/QuestionItem.vue";
import FehlerZusammenfassung from "~/components/session/FehlerZusammenfassung.vue";
import GrafikChart from "~/components/session/GrafikChart.vue";
import ZuordnungBlock from "~/components/session/ZuordnungBlock.vue";

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const { t } = useI18n();
const config = useRuntimeConfig();
const apiBase = (config.public.apiBaseUrl as string) || "http://localhost:8001";

const mobileTab = ref<"text" | "tasks">("text");

const cfg = computed<Record<string, any>>(() => props.teil.config || {});
const fmt = computed(() => String(props.teil.format_type || ""));

// Formats dont le support se lit dans la colonne de gauche
const SIDE_FORMATS = new Set([
  "matching",
  "selektives_matching",
  "zuordnung_personen",
  "zuordnung_meinungen",
  "zuordnung_paragraphen",
  "zuordnung_titre",
  "lueckentext_saetze",
  "qcm_gap_fill",
  "word_bank_gap_fill",
  "textabschnitte_ordnen",
]);

const hasStimulus = computed(
  () =>
    !!cfg.value.stimulus_text ||
    !!cfg.value.stimulus_image ||
    !!cfg.value.article_text ||
    !!cfg.value.image ||
    SIDE_FORMATS.has(fmt.value),
);

const hasTexts = computed(
  () =>
    fmt.value === "qcm_abc" &&
    Array.isArray(cfg.value.texts) &&
    cfg.value.texts.length > 0,
);

const titres = computed(
  () => cfg.value.titres || props.questions[0]?.content?.titres || {},
);

// Formats où chaque proposition ne sert qu'une fois
const UNIQUE_CHOICE_FORMATS = new Set([
  "zuordnung_titre",
  "word_bank_gap_fill",
  "textabschnitte_ordnen",
]);
// TestDaF zuordnung : options uniques sauf si options_reusable (Lesen 5)
const isUniqueChoice = computed(
  () =>
    UNIQUE_CHOICE_FORMATS.has(fmt.value) ||
    (fmt.value === "zuordnung" && cfg.value.options_reusable === false),
);

// Numéro affiché : texte (titres), lacune (banque de mots) ou position (textes à ordonner)
const choiceNumber = (q: any) =>
  q.content?.gap_number ??
  q.content?.position ??
  q.content?.display_number ??
  q.question_number;

// Lettre choisie par chaque question
const chosenTitre = (q: any): string | null => {
  const key = props.answers[q.id]?.user_answer?.answer;
  return key ? String(key).toLowerCase() : null;
};

// Titres déjà attribués { lettre: numéro du texte }, pour la liste de gauche
const assignedTitres = computed<Record<string, number>>(() => {
  if (!isUniqueChoice.value) return {};
  const out: Record<string, number> = {};
  for (const q of props.questions) {
    const key = chosenTitre(q);
    if (key) out[key] = choiceNumber(q);
  }
  return out;
});

// Pour un texte : les lettres prises par les AUTRES textes
const takenTitresFor = (q: any): Record<string, number> => {
  if (!isUniqueChoice.value) return {};
  const out: Record<string, number> = {};
  for (const other of props.questions) {
    if (other.id === q.id) continue;
    const key = chosenTitre(other);
    if (key) out[key] = choiceNumber(other);
  }
  return out;
};

const contextLine = computed(
  () => cfg.value.topic || cfg.value.thema || cfg.value.context || "",
);

const docLabel = computed(() =>
  [cfg.value.document_type, cfg.value.institution].filter(Boolean).join(" · "),
);

const beispiel = computed(() => {
  const b = cfg.value.beispiel;
  return b &&
    typeof b === "object" &&
    (b.stem || b.prompt || b.context || b.answer)
    ? b
    : null;
});

const answeredCount = computed(
  () => props.questions.filter((q) => props.answers[q.id]).length,
);

const questionsForText = (textBlock: any) => {
  const numbers = (textBlock.questions || []).map((q: any) => q.number);
  return props.questions.filter((q) => numbers.includes(q.question_number));
};

const cardClass = (q: any) => [
  "border rounded-card p-4 sm:p-5 scroll-mt-4 transition-colors",
  props.answers[q.id]
    ? "border-primary/30 bg-primary/5"
    : "border-line bg-card",
];

const tabClass = (tab: "text" | "tasks") => [
  "py-2 rounded-lg text-sm font-medium transition-colors",
  mobileTab.value === tab ? "bg-card text-ink shadow-soft" : "text-muted",
];

// ── Formatage (texte échappé avant v-html) ────────────

const escapeHtml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const formatText = (text: string) => {
  if (!text) return "";
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
};

// Numéros de lacune (21) ou _21_ mis en évidence
const formatGapText = (text: string) =>
  formatText(text).replace(
    /\((\d+)\)|_(\d+)_/g,
    (_m, a, b) =>
      `<span class="inline-flex items-center justify-center min-w-6 h-6 px-1 mx-0.5 rounded-full bg-primary/10 text-primary text-xs font-bold align-middle">${a ?? b}</span>`,
  );

// ── Annonces (string ou {title, text, contact, image}) ──

const anzeigeText = (anzeige: any): string =>
  typeof anzeige === "object" ? (anzeige?.text ?? "") : String(anzeige);

const anzeigeField = (
  anzeige: any,
  field: "title" | "contact" | "image",
): string => (typeof anzeige === "object" ? (anzeige?.[field] ?? "") : "");
</script>
