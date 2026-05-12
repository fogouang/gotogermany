<template>
  <div class="flex flex-col lg:flex-row gap-0 min-h-[calc(100vh-7rem)]">
    <!-- Colonne gauche : texte stimulus -->
    <div
      v-if="hasStimulus"
      class="lg:w-1/2 bg-gray-50 border-r border-gray-200 overflow-y-auto"
    >
      <div class="p-6 max-w-prose mx-auto">
        <!-- Instructions -->
        <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-blue-800 font-medium">
            {{ teil.instructions }}
          </p>
        </div>

        <!-- Stimulus text simple -->
        <div
          v-if="stimulusText"
          class="prose prose-sm text-gray-800 leading-relaxed"
          v-html="formatText(stimulusText)"
        />

        <!-- Article (lueckentext_saetze) -->
        <div v-if="teil.format_type === 'lueckentext_saetze'" class="space-y-2">
          <h3 class="font-bold text-gray-900 mb-3">{{ teil.config?.article_title }}</h3>
          <div
            class="prose prose-sm text-gray-800 leading-relaxed"
            v-html="formatText(teil.config?.article_text || '')"
          />
        </div>

        <!-- Personnes (zuordnung_personen) -->
        <div v-else-if="teil.format_type === 'zuordnung_personen'" class="space-y-4 mt-2">
          <div
            v-for="(person, key) in teil.config?.persons"
            :key="key"
            class="p-4 bg-white border border-gray-200 rounded-lg"
          >
            <div class="font-bold text-primary-700 mb-2">
              {{ String(key).toUpperCase() }} — {{ person.name }}
            </div>
            <p class="text-sm text-gray-700 leading-relaxed">{{ person.text }}</p>
          </div>
        </div>

        <!-- Opinions (zuordnung_meinungen) -->
        <div v-else-if="teil.format_type === 'zuordnung_meinungen'" class="space-y-4 mt-2">
          <div
            v-for="(opinion, key) in teil.config?.opinions"
            :key="key"
            class="p-4 bg-white border border-gray-200 rounded-lg"
          >
            <div class="font-bold text-primary-700 mb-2">
              {{ String(key).toUpperCase() }} — {{ opinion.author }}
            </div>
            <p class="text-sm text-gray-700 leading-relaxed">{{ opinion.text }}</p>
          </div>
        </div>

        <!-- Paragraphes (zuordnung_paragraphen) -->
        <div v-else-if="teil.format_type === 'zuordnung_paragraphen'" class="space-y-4 mt-2">
          <div
            v-for="(para, key) in teil.config?.paragraphs"
            :key="key"
            class="p-4 bg-white border border-gray-200 rounded-lg"
          >
            <div class="font-bold text-gray-700 mb-2">{{ para.title }}</div>
            <p class="text-sm text-gray-700 leading-relaxed">{{ para.text }}</p>
          </div>
        </div>

        <!-- Anzeigen (matching + selektives_matching) -->
        <div
          v-else-if="teil.format_type === 'matching' || teil.format_type === 'selektives_matching'"
          class="space-y-3 mt-4"
        >
          <div
            v-for="(text, key) in teil.config?.anzeigen"
            :key="key"
            class="p-3 bg-white border border-gray-200 rounded-lg"
          >
            <span class="font-bold text-primary-700 mr-2">{{ String(key).toUpperCase() }}</span>
            <span class="text-sm text-gray-700">{{ text }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Colonne droite : questions -->
    <div :class="['overflow-y-auto', hasStimulus ? 'lg:w-1/2' : 'w-full']">
      <div class="p-6 max-w-2xl mx-auto space-y-6">
        <!-- Instructions si pas de stimulus -->
        <div
          v-if="!hasStimulus"
          class="p-3 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <p class="text-sm text-blue-800 font-medium">
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
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div
                class="prose prose-sm text-gray-800"
                v-html="formatText(textBlock.stimulus_text)"
              />
            </div>
            <div
              v-for="q in getQuestionsForText(textBlock)"
              :key="q.id"
              class="bg-white border border-gray-200 rounded-xl p-5"
            >
              <QuestionItem
                :question="q"
                :answer="answers[q.id]?.user_answer"
                @answer="(val: Record<string, any>) => $emit('answer', q.id, val)"
              />
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

const hasStimulus = computed(() => {
  const t = props.teil;
  return (
    !!t.config?.stimulus_text ||
    !!t.config?.article_text ||
    t.format_type === 'matching' ||
    t.format_type === 'selektives_matching' ||
    t.format_type === 'zuordnung_personen' ||
    t.format_type === 'zuordnung_meinungen' ||
    t.format_type === 'zuordnung_paragraphen' ||
    t.format_type === 'lueckentext_saetze'
  );
});

const hasTexts = computed(
  () => props.teil.format_type === 'qcm_abc' && props.teil.config?.texts?.length > 0,
);

const stimulusText = computed(() => props.teil.config?.stimulus_text || '');

watch(
  () => props.teil,
  (newTeil) => {
    console.log('teil changed:', newTeil?.id);
    console.log('stimulus_text:', newTeil?.config?.stimulus_text);
    console.log('hasStimulus:', !!newTeil?.config?.stimulus_text);
  },
  { deep: true },
);

const getQuestionsForText = (textBlock: any) => {
  const numbers = (textBlock.questions || []).map((q: any) => q.number);
  return props.questions.filter((q) => numbers.includes(q.question_number));
};

const formatText = (text: string) => {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
};
</script>