<template>
  <div>
    <!-- Numéro + points -->
    <div class="flex items-center justify-between mb-3">
      <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">
        Question {{ question.question_number }}
      </span>
      <span class="text-xs text-gray-400">{{ question.points }} pt(s)</span>
    </div>

    <!-- richtig_falsch / ja_nein -->
    <div v-if="['richtig_falsch', 'ja_nein'].includes(question.question_type)">
      <p class="text-base text-gray-900 mb-4">
        {{ question.content.statement || question.content.text }}
      </p>
      <div class="flex gap-3">
        <button
          v-for="opt in rfOptions"
          :key="opt.value"
          :class="[
            'flex-1 py-3 px-4 rounded-lg border-2 font-medium text-sm transition-all',
            answer?.answer === opt.value
              ? opt.value === 'richtig' || opt.value === 'ja'
                ? 'border-green-500 bg-green-50 text-green-800'
                : 'border-green-500 bg-green-50 text-green-800'
              : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: opt.value })"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- qcm_abc -->
    <div v-else-if="question.question_type === 'qcm_abc'">
      <p class="text-base text-gray-900 mb-4">
        {{ question.content.stem || question.content.question }}
      </p>
      <div class="space-y-2">
        <button
          v-for="(text, key) in question.content.options"
          :key="key"
          :class="[
            'w-full text-left px-4 py-3 rounded-lg border-2 text-sm transition-all flex items-start gap-3',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <span
            :class="[
              'shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
              answer?.answer === String(key)
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-600',
            ]"
          >
            {{ String(key).toUpperCase() }}
          </span>
          <span>{{ text }}</span>
        </button>
      </div>
    </div>

    <!-- matching (Goethe) -->
    <div v-else-if="question.question_type === 'matching'">
      <p class="text-base text-gray-900 mb-4">
        {{ question.content.situation }}
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="key in matchingKeys"
          :key="key"
          :class="[
            'w-10 h-10 rounded-lg border-2 font-bold text-sm transition-all',
            answer?.answer === key
              ? 'border-primary-600 bg-primary-600 text-white'
              : 'border-gray-300 text-gray-700 hover:border-primary-400',
          ]"
          @click="$emit('answer', { answer: key })"
        >
          {{ key === "0" ? "0" : key.toUpperCase() }}
        </button>
      </div>
    </div>

    <!-- zuordnung_speaker -->
    <div v-else-if="question.question_type === 'zuordnung_speaker'">
      <p class="text-base text-gray-900 mb-4">
        {{ question.content.statement }}
      </p>
      <div class="flex gap-3">
        <button
          v-for="(name, key) in question.content.speakers"
          :key="key"
          :class="[
            'flex-1 py-3 px-2 rounded-lg border-2 text-center transition-all',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <div class="font-bold text-lg text-gray-900">
            {{ String(key).toUpperCase() }}
          </div>
          <div class="text-xs text-gray-500 mt-1 leading-tight">{{ name }}</div>
        </button>
      </div>
    </div>

    <!-- zuordnung_titre -->
<div v-else-if="question.question_type === 'zuordnung_titre'">
  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4 text-sm text-gray-800 leading-relaxed">
    {{ question.content.stimulus_text }}
  </div>
  <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
    Choisissez le titre correspondant :
  </p>
  <div class="grid grid-cols-1 gap-2">
    <button
      v-for="(titre, key) in question.content.titres"
      :key="key"
      :class="[
        'w-full text-left px-4 py-3 rounded-lg border-2 text-sm transition-all flex items-center gap-3',
        answer?.answer === String(key)
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-200 hover:border-primary-200 hover:bg-gray-50',
      ]"
      @click="$emit('answer', { answer: String(key) })"
    >
      <span
        :class="[
          'shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all',
          answer?.answer === String(key)
            ? 'bg-primary-600 text-white'
            : 'bg-white border-2 border-gray-300 text-gray-500',
        ]"
        >{{ String(key).toUpperCase() }}</span
      >
      <span :class="answer?.answer === String(key) ? 'font-medium text-primary-900' : 'text-gray-700'">
        {{ titre }}
      </span>
    </button>
  </div>
</div>

    <!-- selektives_matching -->
    <div v-else-if="question.question_type === 'selektives_matching'">
      <p class="text-base text-gray-900 mb-4">
        {{ question.content.situation }}
      </p>
      <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
        Quelle annonce correspond ?
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="key in selektivesKeys"
          :key="key"
          :class="[
            'w-10 h-10 rounded-lg border-2 font-bold text-sm transition-all uppercase',
            answer?.answer === key
              ? 'border-primary-600 bg-primary-600 text-white'
              : key === 'x'
                ? 'border-gray-400 text-gray-500 hover:border-gray-500'
                : 'border-gray-300 text-gray-700 hover:border-primary-400',
          ]"
          @click="$emit('answer', { answer: key })"
        >
          {{ key }}
        </button>
      </div>
    </div>

    <!-- qcm_gap_fill -->
    <div v-else-if="question.question_type === 'qcm_gap_fill'">
      <div
        class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 text-sm text-gray-800 leading-relaxed"
      >
        <span
          v-html="
            highlightGap(
              question.content.text_with_gaps,
              question.content.gap_number,
            )
          "
        ></span>
      </div>
      <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
        Lacune {{ question.content.gap_number }} — Choisissez la bonne réponse :
      </p>
      <div class="flex gap-3">
        <button
          v-for="(text, key) in question.content.options"
          :key="key"
          :class="[
            'flex-1 py-3 px-3 rounded-lg border-2 text-sm font-medium transition-all text-center',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50 text-primary-800'
              : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <span class="font-bold">{{ String(key).toUpperCase() }}</span>
          <span class="ml-2">{{ text }}</span>
        </button>
      </div>
    </div>

    <!-- word_bank_gap_fill -->
    <div v-else-if="question.question_type === 'word_bank_gap_fill'">
      <div
        class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 text-sm text-gray-800 leading-relaxed"
      >
        <span
          v-html="
            highlightGap(
              question.content.text_with_gaps,
              question.content.gap_number,
            )
          "
        ></span>
      </div>
      <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
        Lacune {{ question.content.gap_number }} — Choisissez le mot :
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="(word, key) in question.content.word_bank"
          :key="key"
          :class="[
            'px-3 py-2 rounded-lg border-2 text-sm font-medium transition-all',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50 text-primary-800'
              : 'border-gray-200 text-gray-700 hover:border-primary-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <span class="text-xs text-gray-400 mr-1">{{
            String(key).toUpperCase()
          }}</span>
          {{ word }}
        </button>
      </div>
    </div>

    <!-- zuordnung_personen — Goethe B2 Lesen Teil 1 -->
    <div v-else-if="question.question_type === 'zuordnung_personen'">
      <p class="text-base text-gray-900 mb-4">
        {{ question.content.statement }}
      </p>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="(person, key) in question.content.persons"
          :key="key"
          :class="[
            'p-3 rounded-lg border-2 text-left transition-all',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <div class="font-bold text-primary-700 mb-1">
            {{ String(key).toUpperCase() }} — {{ person.name }}
          </div>
          <p class="text-xs text-gray-600 line-clamp-2">{{ person.text }}</p>
        </button>
      </div>
    </div>

    <!-- lueckentext_saetze — Goethe B2 Lesen Teil 2 -->
    <div v-else-if="question.question_type === 'lueckentext_saetze'">
      <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
        Lacune [{{ question.content.gap_number }}] — Choisissez la phrase :
      </p>
      <div class="space-y-2">
        <button
          v-for="(text, key) in question.content.candidates"
          :key="key"
          :class="[
            'w-full text-left px-4 py-3 rounded-lg border-2 text-sm transition-all flex items-start gap-3',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <span
            :class="[
              'shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
              answer?.answer === String(key)
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-600',
            ]"
            >{{ String(key).toUpperCase() }}</span
          >
          <span>{{ text }}</span>
        </button>
      </div>
    </div>

    <!-- zuordnung_meinungen — Goethe B2 Lesen Teil 4 -->
    <div v-else-if="question.question_type === 'zuordnung_meinungen'">
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
        <p class="text-xs font-semibold text-gray-500 uppercase mb-1">
          Titre à associer :
        </p>
        <p class="text-base font-semibold text-gray-900">
          {{ question.content.title }}
        </p>
      </div>
      <div class="space-y-2">
        <button
          v-for="(opinion, key) in question.content.opinions"
          :key="key"
          :class="[
            'w-full text-left px-4 py-3 rounded-lg border-2 text-sm transition-all',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <div class="flex items-center gap-2 mb-1">
            <span
              :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                answer?.answer === String(key)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-600',
              ]"
              >{{ String(key).toUpperCase() }}</span
            >
            <span class="font-semibold text-gray-700">{{
              opinion.author
            }}</span>
          </div>
          <p class="text-xs text-gray-500 line-clamp-2 ml-8">
            {{ opinion.text }}
          </p>
        </button>
      </div>
    </div>

    <!-- zuordnung_paragraphen — Goethe B2 Lesen Teil 5 -->
    <div v-else-if="question.question_type === 'zuordnung_paragraphen'">
      <div
        class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4 text-sm text-gray-800 leading-relaxed"
      >
        <p class="text-xs font-semibold text-gray-500 uppercase mb-2">
          {{ question.content.paragraph_title }}
        </p>
        <p>{{ question.content.paragraph_text }}</p>
      </div>
      <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
        Choisissez le titre correspondant :
      </p>
      <div class="grid grid-cols-1 gap-2">
        <button
          v-for="(heading, key) in question.content.headings"
          :key="key"
          :class="[
            'w-full text-left px-4 py-2.5 rounded-lg border-2 text-sm transition-all flex items-center gap-3',
            answer?.answer === String(key)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50',
          ]"
          @click="$emit('answer', { answer: String(key) })"
        >
          <span
            :class="[
              'shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
              answer?.answer === String(key)
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-600',
            ]"
            >{{ String(key).toUpperCase() }}</span
          >
          <span>{{ heading }}</span>
        </button>
      </div>
    </div>

    <!-- Fallback -->
    <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <p class="text-yellow-700 text-sm">
        Type non supporté : <code>{{ question.question_type }}</code>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  question: any;
  answer: any;
  teilAnzeigen?: Record<string, string>;
}>();

defineEmits<{ answer: [value: any] }>();

const rfOptions = computed(() => {
  const isJaNein = props.question.question_type === "ja_nein";
  return isJaNein
    ? [
        { value: "ja", label: "Ja ✓" },
        { value: "nein", label: "Nein ✗" },
      ]
    : [
        { value: "richtig", label: "Richtig ✓" },
        { value: "falsch", label: "Falsch ✗" },
      ];
});

const matchingKeys = computed(() => {
  const anzeigen = props.question.content.anzeigen || {};
  return [...Object.keys(anzeigen), "0"];
});

const selektivesKeys = computed(() => {
  const anzeigen = props.teilAnzeigen || props.question.content.anzeigen || {};
  return [...Object.keys(anzeigen), "x"];
});

const highlightGap = (text: string, gapNumber: number): string => {
  if (!text) return "";
  const marker = `_${gapNumber}_`;
  return text.replace(
    marker,
    `<span class="inline-block bg-primary-200 text-primary-900 font-bold px-2 py-0.5 rounded mx-1">[${gapNumber}]</span>`,
  );
};
</script>
