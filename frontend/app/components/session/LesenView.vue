<template>
  <div class="flex flex-col lg:flex-row gap-0 lg:h-[calc(100vh-7rem)]">
    <!-- Colonne gauche : texte stimulus -->
    <div
      v-if="hasStimulus"
      class="lg:w-1/2 bg-white shadow-sm border-r border-gray-200 overflow-y-auto lg:min-h-0"
    >
      <div class="p-6 mx-auto">
        <!-- Instructions -->
        <div class="mb-4 p-3 bg-green-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-green-600 font-medium">
            {{ teil.instructions }}
          </p>
        </div>

        <!-- Stimulus image générique (qcm_abc, richtig_falsch...) -->
        <div v-if="teil.config?.stimulus_image" class="mb-4">
          <img
            :src="`${apiBase}/images/${teil.config.stimulus_image}`"
            alt="Stimulus"
            class="w-full rounded-lg border border-gray-200 object-contain"
          />
        </div>
        <!-- Image générique (fichiers uploadés sans suffixe key, ex: lesen_teil2.png) -->
        <div v-else-if="teil.config?.image" class="mb-4">
          <img
            :src="`${apiBase}/images/${teil.config.image}`"
            alt="Illustration"
            class="w-full rounded-lg border border-gray-200 object-contain"
          />
        </div>
        <!-- Titre article si présent (qcm_abc) -->
        <h3
          v-if="
            teil.config?.article_title &&
            teil.format_type !== 'lueckentext_saetze'
          "
          class="font-bold text-gray-900 text-base mb-3"
        >
          {{ teil.config.article_title }}
        </h3>
        <!-- Stimulus text simple (teil.config) -->
        <div
          v-if="stimulusText"
          class="prose prose-sm text-gray-800 leading-relaxed"
          v-html="formatText(stimulusText)"
        />

        <!-- ✅ NOUVEAU : zuordnung_titre — texte stimulus par question -->
        <div
          v-if="teil.format_type === 'zuordnung_titre'"
          class="space-y-5 mt-2"
        >
          <div
            v-for="q in questions"
            :key="`stimulus-${q.id}`"
            class="bg-white border border-gray-200 rounded-lg p-4"
          >
            <p
              class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2"
            >
              Text {{ q.question_number }}
            </p>
            <div
              class="prose prose-sm text-gray-800 leading-relaxed"
              v-html="formatText(q.content?.stimulus_text || '')"
            />
          </div>
        </div>

        <!-- Article (lueckentext_saetze) -->
        <div v-if="teil.format_type === 'lueckentext_saetze'" class="space-y-2">
          <div v-if="teil.config?.article_image" class="mb-4">
            <img
              :src="`${apiBase}/images/${teil.config.article_image}`"
              alt="Article"
              class="w-full rounded-lg border border-gray-200 object-contain"
            />
          </div>
          <h3 class="font-bold text-gray-900 mb-3">
            {{ teil.config?.article_title }}
          </h3>
          <div
            class="prose prose-sm text-gray-800 leading-relaxed"
            v-html="formatText(teil.config?.article_text || '')"
          />
        </div>

        <!-- Personnes (zuordnung_personen) -->
        <div
          v-else-if="teil.format_type === 'zuordnung_personen'"
          class="space-y-4 mt-2"
        >
          <div
            v-for="(person, key) in teil.config?.persons"
            :key="key"
            class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4"
          >
            <div class="flex gap-3 sm:gap-4 items-start">
              <img
                v-if="person?.image"
                :src="`${apiBase}/images/${person.image}`"
                :alt="person.name"
                class="w-16 h-20 sm:w-28 sm:h-32 object-cover rounded-lg border border-gray-200 shrink-0"
              />
              <div
                v-else
                class="w-16 h-20 sm:w-28 sm:h-32 rounded-lg bg-primary-50 border border-gray-200 flex items-center justify-center shrink-0"
              >
                <span class="font-bold text-primary-400 text-lg sm:text-xl">
                  {{ String(key).toUpperCase() }}
                </span>
              </div>

              <div class="flex-1 min-w-0">
                <p class="font-bold text-gray-900 mb-1 text-sm sm:text-base">
                  {{ String(key).toLowerCase() }}) {{ person.name }}
                </p>
                <p
                  class="text-sm sm:text-base text-gray-700 leading-relaxed text-justify"
                >
                  {{ person.text }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Opinions (zuordnung_meinungen) -->
        <div
          v-else-if="teil.format_type === 'zuordnung_meinungen'"
          class="space-y-4 mt-2"
        >
          <div
            v-for="(opinion, key) in teil.config?.opinions"
            :key="key"
            class="p-4 bg-white border border-gray-200 rounded-lg"
          >
            <div class="flex items-center gap-3 mb-2">
              <img
                v-if="opinion?.image"
                :src="`${apiBase}/images/${opinion.image}`"
                :alt="opinion.author"
                class="w-12 h-12 rounded-full object-cover border border-gray-200 shrink-0"
              />
              <div
                v-else
                class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center shrink-0"
              >
                <span class="font-bold text-primary-700 text-sm">{{
                  String(key).toUpperCase()
                }}</span>
              </div>
              <div class="font-bold text-primary-700">
                {{ String(key).toUpperCase() }}-{{ opinion.author }}
              </div>
            </div>
            <p class="text-sm text-gray-700 leading-relaxed">
              {{ opinion.text }}
            </p>
          </div>
        </div>

        <!-- Paragraphes (zuordnung_paragraphen) -->
        <div
          v-else-if="teil.format_type === 'zuordnung_paragraphen'"
          class="space-y-4 mt-2"
        >
          <div
            v-for="(para, key) in teil.config?.paragraphs"
            :key="key"
            class="p-4 bg-white border border-gray-200 rounded-lg"
          >
            <img
              v-if="para?.image"
              :src="`${apiBase}/images/${para.image}`"
              :alt="para.title"
              class="w-full h-32 object-cover rounded-lg border border-gray-200 mb-2"
            />
            <div class="font-bold text-gray-700 mb-1">{{ para.title }}</div>
            <p class="text-sm text-gray-700 leading-relaxed">{{ para.text }}</p>
          </div>
        </div>

        <!-- Anzeigen (matching + selektives_matching) -->
        <div
          v-else-if="
            teil.format_type === 'matching' ||
            teil.format_type === 'selektives_matching'
          "
          class="space-y-3 mt-4"
        >
          <div
            v-for="(anzeige, key) in teil.config?.anzeigen"
            :key="key"
            class="p-3 bg-white border border-gray-200 rounded-lg"
          >
            <div class="flex items-start gap-2">
              <span class="font-bold text-primary-700 shrink-0">{{
                String(key).toUpperCase()
              }}</span>
              <div class="flex-1 min-w-0">
                <p
                  v-if="getAnzeigeTitle(anzeige)"
                  class="font-semibold text-gray-900 text-sm mb-0.5"
                >
                  {{ getAnzeigeTitle(anzeige) }}
                </p>
                <p class="text-sm text-gray-700 leading-relaxed">
                  {{ getAnzeigeText(anzeige) }}
                </p>
                <p
                  v-if="getAnzeigeContact(anzeige)"
                  class="text-xs text-gray-500 italic mt-1"
                >
                  {{ getAnzeigeContact(anzeige) }}
                </p>
              </div>
              <img
                v-if="getAnzeigeImage(anzeige)"
                :src="`${apiBase}/images/${getAnzeigeImage(anzeige)}`"
                :alt="`Annonce ${key}`"
                class="w-16 h-16 object-cover rounded-lg border border-gray-200 shrink-0"
              />
            </div>
          </div>
        </div>

        <!-- ✅ NOUVEAU : Sprachbausteine — texte avec lacunes numérotées
             (qcm_gap_fill / word_bank_gap_fill) -->
        <div
          v-else-if="
            teil.format_type === 'qcm_gap_fill' ||
            teil.format_type === 'word_bank_gap_fill'
          "
          class="space-y-3"
        >
          <p
            v-if="teil.config?.situation"
            class="text-xs text-gray-500 italic mb-1"
          >
            {{ teil.config.situation }}
          </p>
          <div
            v-if="teil.config?.stimulus_anzeige"
            class="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700 mb-3"
          >
            {{ teil.config.stimulus_anzeige }}
          </div>
          <div
            class="prose prose-sm text-gray-800 leading-relaxed"
            v-html="formatGapText(teil.config?.text_with_gaps || '')"
          />

          <!-- Banque de mots partagée (Lexik / word_bank_gap_fill uniquement) -->
          <div
            v-if="
              teil.format_type === 'word_bank_gap_fill' &&
              teil.config?.word_bank
            "
            class="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-2"
          >
            <div
              v-for="(word, key) in teil.config.word_bank"
              :key="key"
              class="text-xs bg-primary-50 border border-primary-100 rounded-lg px-3 py-2 flex gap-2 items-center"
            >
              <span class="font-bold text-primary-700 shrink-0">{{
                String(key).toUpperCase()
              }}</span>
              <span class="text-gray-700">{{ word }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Colonne droite : questions -->
    <div
      :class="[
        'overflow-y-auto lg:min-h-0',
        hasStimulus ? 'lg:w-1/2' : 'w-full',
      ]"
    >
      <div class="p-6 max-w-2xl mx-auto space-y-6">
        <!-- Instructions si pas de stimulus -->
        <div
          v-if="!hasStimulus"
          class="p-3 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <p class="text-sm text-green-800 font-medium">
            {{ teil.instructions }}
          </p>
        </div>

        <!-- Questions groupées par texte (qcm_abc avec texts[]) -->
        <template v-if="teil.format_type === 'qcm_abc' && hasTexts">
          <div
            v-for="(textBlock, ti) in teil.config?.texts || []"
            :key="ti"
            class="space-y-4"
          >
            <div v-if="textBlock?.image" class="mb-2">
              <img
                :src="`${apiBase}/images/${textBlock.image}`"
                alt="Stimulus"
                class="w-full rounded-lg border border-gray-200 object-contain"
              />
            </div>
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div
                class="prose prose-sm text-gray-800"
                v-html="formatText(textBlock.stimulus_text)"
              />
            </div>
            <div
              v-for="q in getQuestionsForText(textBlock)"
              :key="q.id"
              class="bg-white shadow-md border border-gray-200 rounded-xl p-5"
            >
              <QuestionItem
                :question="q"
                :answer="answers[q.id]?.user_answer"
                @answer="
                  (val: Record<string, any>) => $emit('answer', q.id, val)
                "
              />
            </div>
          </div>
        </template>

        <!-- ✅ zuordnung_titre : on n'affiche QUE le choix de titre ici,
             le stimulus_text est déjà dans la colonne gauche -->
        <template v-else-if="teil.format_type === 'zuordnung_titre'">
          <div
            v-for="q in questions"
            :key="q.id"
            :class="[
              'bg-white border rounded-xl p-5 transition-all scroll-mt-4',
              answers[q.id] ? 'border-primary-300' : 'border-gray-200',
            ]"
            :id="`question-${q.id}`"
          >
            <div class="flex items-center justify-between mb-3">
              <span
                class="text-xs font-semibold text-gray-400 uppercase tracking-wide"
              >
                Text {{ q.question_number }}
              </span>
              <span class="text-xs text-gray-400">{{ q.points }} pt(s)</span>
            </div>
            <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
              Choisissez le titre correspondant :
            </p>
            <div class="grid grid-cols-1 gap-2">
              <button
                v-for="(titre, key) in q.content?.titres"
                :key="key"
                :class="[
                  'w-full text-left px-4 py-3 rounded-lg border-2 text-sm transition-all flex items-center gap-3',
                  answers[q.id]?.user_answer?.answer === String(key)
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-200 hover:bg-gray-50',
                ]"
                @click="$emit('answer', q.id, { answer: String(key) })"
              >
                <span
                  :class="[
                    'shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all',
                    answers[q.id]?.user_answer?.answer === String(key)
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border-2 border-gray-300 text-gray-500',
                  ]"
                  >{{ String(key).toUpperCase() }}</span
                >
                <span
                  :class="
                    answers[q.id]?.user_answer?.answer === String(key)
                      ? 'font-medium text-primary-900'
                      : 'text-gray-700'
                  "
                >
                  {{ titre }}
                </span>
              </button>
            </div>
          </div>
        </template>

        <!-- ✅ NOUVEAU : Sprachbausteine — une carte par lacune,
             sans réafficher le texte (déjà à gauche) -->
        <template
          v-else-if="
            teil.format_type === 'qcm_gap_fill' ||
            teil.format_type === 'word_bank_gap_fill'
          "
        >
          <div
            v-for="q in questions"
            :key="q.id"
            :class="[
              'bg-white border rounded-xl p-5 transition-all scroll-mt-4',
              answers[q.id] ? 'border-primary-300' : 'border-gray-200',
            ]"
            :id="`question-${q.id}`"
          >
            <div class="flex items-center justify-between mb-3">
              <span
                class="text-xs font-semibold text-gray-400 uppercase tracking-wide"
              >
                Lücke {{ q.question_number }}
              </span>
              <span class="text-xs text-gray-400">{{ q.points }} pt(s)</span>
            </div>
            <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
              Choisissez la bonne réponse :
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <button
                v-for="(label, key) in gapOptions(q)"
                :key="key"
                :class="[
                  'px-3 py-2.5 rounded-lg border-2 text-sm font-medium transition-all flex items-center gap-2',
                  answers[q.id]?.user_answer?.answer === String(key)
                    ? 'border-primary-500 bg-primary-50 text-primary-900'
                    : 'border-gray-200 hover:border-primary-200 hover:bg-gray-50 text-gray-700',
                ]"
                @click="$emit('answer', q.id, { answer: String(key) })"
              >
                <span
                  :class="[
                    'shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                    answers[q.id]?.user_answer?.answer === String(key)
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border-2 border-gray-300 text-gray-500',
                  ]"
                  >{{ String(key).toUpperCase() }}</span
                >
                {{ label }}
              </button>
            </div>
          </div>
        </template>

        <!-- Questions normales -->
        <template v-else>
          <div
            v-for="q in questions"
            :key="q.id"
            :class="[
              'bg-white border rounded-xl p-5 transition-all',
              answers[q.id] ? 'border-primary-300' : 'border-gray-200',
            ]"
          >
            <QuestionItem
              :question="q"
              :answer="answers[q.id]?.user_answer"
              :teil-anzeigen="
                teil.format_type === 'selektives_matching'
                  ? teil.config?.anzeigen
                  : undefined
              "
              @answer="(val: Record<string, any>) => $emit('answer', q.id, val)"
            />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionItem from "~/components/session/QuestionItem.vue";

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
}>();

defineEmits<{ answer: [questionId: string, value: any] }>();

const config = useRuntimeConfig();
const apiBase = config.public.apiBaseUrl || "http://localhost:8001";

const hasStimulus = computed(() => {
  const t = props.teil;
  return (
    !!t.config?.stimulus_text ||
    !!t.config?.stimulus_image ||
    !!t.config?.article_text ||
    !!t.config?.image || // ← ajouté
    t.format_type === "matching" ||
    t.format_type === "selektives_matching" ||
    t.format_type === "zuordnung_personen" ||
    t.format_type === "zuordnung_meinungen" ||
    t.format_type === "zuordnung_paragraphen" ||
    t.format_type === "zuordnung_titre" ||
    t.format_type === "lueckentext_saetze" ||
    t.format_type === "qcm_gap_fill" || // ✅ ajouté (Sprachbausteine Grammatik)
    t.format_type === "word_bank_gap_fill" // ✅ ajouté (Sprachbausteine Lexik)
  );
});

const hasTexts = computed(
  () =>
    props.teil.format_type === "qcm_abc" &&
    props.teil.config?.texts?.length > 0,
);

const stimulusText = computed(() => props.teil.config?.stimulus_text || "");

const getQuestionsForText = (textBlock: any) => {
  const numbers = (textBlock.questions || []).map((q: any) => q.number);
  return props.questions.filter((q) => numbers.includes(q.question_number));
};

const formatText = (text: string) => {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
};

// ✅ NOUVEAU : formate le texte à trous en mettant en évidence
// les numéros de lacune (21), (22)... dans le texte source.
const formatGapText = (text: string) => {
  if (!text) return "";
  return formatText(text).replace(
    /\((\d+)\)/g,
    '<span class="inline-flex items-center justify-center w-6 h-6 mx-0.5 rounded-full bg-primary-100 text-primary-700 text-xs font-bold align-middle">$1</span>',
  );
};

// ✅ NOUVEAU : options d'une lacune — propres à la question
// (qcm_gap_fill) ou partagées au niveau du Teil (word_bank_gap_fill).
const gapOptions = (q: any): Record<string, string> => {
  if (props.teil.format_type === "word_bank_gap_fill") {
    return props.teil.config?.word_bank || {};
  }
  return q.content?.options || {};
};

const getAnzeigeText = (anzeige: any): string =>
  typeof anzeige === "object" ? (anzeige?.text ?? "") : String(anzeige);

const getAnzeigeTitle = (anzeige: any): string =>
  typeof anzeige === "object" ? (anzeige?.title ?? "") : "";

const getAnzeigeContact = (anzeige: any): string =>
  typeof anzeige === "object" ? (anzeige?.contact ?? "") : "";

const getAnzeigeImage = (anzeige: any): string | null =>
  typeof anzeige === "object" ? (anzeige?.image ?? null) : null;
</script>