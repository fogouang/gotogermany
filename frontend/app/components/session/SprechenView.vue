<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <!-- Instructions -->
    <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-sm text-blue-800 font-medium">{{ teil.instructions }}</p>
    </div>

    <!-- Temps -->
    <div
      class="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg"
    >
      <i class="pi pi-clock text-amber-600"></i>
      <span class="text-sm text-amber-800 font-medium">
        Vous avez {{ teil.time_minutes }} minutes pour cette partie
      </span>
    </div>

    <div
      v-if="teil.config?.image"
      class="rounded-xl overflow-hidden border border-gray-200"
    >
      <img
        :src="`${apiBase}/images/${teil.config.image}`"
        alt="Illustration"
        class="w-full object-contain max-h-64"
      />
    </div>

    <!-- oral_kennenlernen — TELC Teil 1 -->
    <div v-if="teil.format_type === 'oral_kennenlernen'" class="space-y-5">
      <div class="bg-white border border-gray-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-gray-700 mb-4">
          Thèmes de conversation :
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="(topic, i) in question?.content?.topics"
            :key="i"
            class="flex items-center gap-3 p-3 bg-primary-50 border border-primary-100 rounded-lg"
          >
            <span
              class="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            >
              {{ (i as number) + 1 }}
            </span>
            <span class="text-sm text-gray-800 font-medium">{{ topic }}</span>
          </div>
        </div>
      </div>

      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre présentation :
        </p>
        <AudioRecorder :teil-number="teil.teil_number" @recorded="onRecorded" />
      </div>
    </div>

    <!-- oral_interaction — planification commune -->
    <div v-else-if="teil.format_type === 'oral_interaction'" class="space-y-5">
      <div
        v-if="question?.content?.scenario"
        class="bg-amber-50 border border-amber-200 rounded-xl p-5"
      >
        <p class="text-sm font-semibold text-amber-800 mb-3">Scénario :</p>
        <p class="text-sm text-amber-900">{{ question.content.scenario }}</p>
      </div>

      <div
        v-if="question?.content?.prompts?.length"
        class="bg-white border border-gray-200 rounded-xl p-5"
      >
        <p class="text-sm font-semibold text-gray-700 mb-3">
          Points à aborder :
        </p>
        <ul class="space-y-2">
          <li
            v-for="(prompt, i) in question.content.prompts"
            :key="i"
            class="flex gap-3 text-sm text-gray-700"
          >
            <span
              class="w-5 h-5 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            >
              {{ (i as number) + 1 }}
            </span>
            {{ prompt }}
          </li>
        </ul>
      </div>

      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre réponse :
        </p>
        <AudioRecorder :teil-number="teil.teil_number" @recorded="onRecorded" />
      </div>
    </div>

    <!-- oral_monologue — présentation avec slides -->
    <div v-else-if="teil.format_type === 'oral_monologue'" class="space-y-5">
      <!-- Image config du Teil (Sprechen Teil 2) -->
      <div
        v-if="teil.config?.image"
        class="rounded-xl overflow-hidden border border-gray-200"
      >
        <img
          :src="`${apiBase}/images/${teil.config.image}`"
          alt="Thème"
          class="w-full object-contain max-h-64"
        />
      </div>

      <!-- Goethe B2 : candidate_a / candidate_b -->
      <template v-if="hasGoetheThemes">
        <div v-if="!selectedTheme" class="space-y-3">
          <p class="text-sm font-semibold text-gray-700">
            Choisissez votre thème :
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              v-for="(theme, key) in goetheThemes"
              :key="key"
              class="p-5 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-primary-400 transition-colors"
              @click="selectedTheme = key as string"
            >
              <p class="font-semibold text-gray-900 mb-2">{{ theme.title }}</p>
              <p class="text-xs text-gray-500 line-clamp-3">{{ theme.task }}</p>
            </button>
          </div>
        </div>

        <div v-else class="space-y-5">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">
              {{ goetheThemes?.[selectedTheme]?.title }}
            </h3>
            <button
              class="text-xs text-gray-400 hover:text-gray-600"
              @click="selectedTheme = null"
            >
              Changer de thème
            </button>
          </div>

          <div
            class="bg-amber-50 border border-amber-200 rounded-xl p-5 text-sm text-amber-900"
          >
            {{ goetheThemes?.[selectedTheme]?.task }}
          </div>

          <div
            v-if="goetheThemes?.[selectedTheme]?.keywords?.length"
            class="flex flex-wrap gap-2"
          >
            <span
              v-for="kw in goetheThemes[selectedTheme].keywords"
              :key="kw"
              class="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-xs font-medium border border-primary-100"
            >
              {{ kw }}
            </span>
          </div>

          <NotesArea
            :question="question"
            :answer="answers[question?.id]?.user_answer"
            @answer="onNotes"
          />

          <div>
            <p class="text-sm font-semibold text-gray-700 mb-3">
              <i class="pi pi-microphone mr-2"></i>Enregistrez votre
              présentation :
            </p>
            <AudioRecorder
              :teil-number="teil.teil_number"
              @recorded="onRecorded"
            />
          </div>
        </div>
      </template>

      <!-- TELC B2 / Goethe B1 : themes standard avec slides -->
      <template v-else>
        <div v-if="!selectedTheme" class="space-y-3">
          <p class="text-sm font-semibold text-gray-700">
            Choisissez votre thème :
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              v-for="(theme, key) in question?.content?.themes"
              :key="key"
              class="p-5 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-primary-400 transition-colors"
              @click="selectedTheme = key as string"
            >
              <p class="font-semibold text-gray-900">{{ theme.title }}</p>
              <p class="text-xs text-gray-500 mt-1">
                {{ theme.slides?.length }} point(s)
              </p>
            </button>
          </div>
        </div>

        <div v-else class="space-y-5">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">
              {{ question?.content?.themes?.[selectedTheme]?.title }}
            </h3>
            <button
              class="text-xs text-gray-400 hover:text-gray-600"
              @click="selectedTheme = null"
            >
              Changer de thème
            </button>
          </div>

          <!-- Slides navigation -->
          <div class="flex gap-2 overflow-x-auto pb-2">
            <button
              v-for="(slide, i) in currentSlides"
              :key="i"
              :class="[
                'shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
                activeSlide === (i as number)
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 text-gray-500 hover:border-gray-300',
              ]"
              @click="activeSlide = i as number"
            >
              Folie {{ (i as number) + 1 }}
            </button>
          </div>

          <!-- Folie active -->
          <div
            class="bg-white border-2 border-primary-200 rounded-xl p-6 min-h-24"
          >
            <div class="flex items-start gap-3">
              <span
                class="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0"
              >
                {{ activeSlide + 1 }}
              </span>
              <p class="text-base text-gray-800 font-medium">
                {{ currentSlides[activeSlide] }}
              </p>
            </div>
          </div>

          <NotesArea
            :question="question"
            :answer="answers[question?.id]?.user_answer"
            @answer="onNotes"
          />

          <div>
            <p class="text-sm font-semibold text-gray-700 mb-3">
              <i class="pi pi-microphone mr-2"></i>Enregistrez votre
              présentation :
            </p>
            <AudioRecorder
              :teil-number="teil.teil_number"
              @recorded="onRecorded"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- oral_thema — TELC B1 Teil 2 -->
    <div v-else-if="teil.format_type === 'oral_thema'" class="space-y-5">
      <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-amber-800 mb-2">Thème :</p>
        <p class="text-base font-bold text-amber-900">
          {{ question?.content?.topic }}
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="bg-white border border-gray-200 rounded-xl p-4">
          <p class="text-xs font-bold text-gray-500 uppercase mb-2">
            {{ question?.content?.opinion_a?.person }}
          </p>
          <p class="text-sm text-gray-700 italic">
            {{ question?.content?.opinion_a?.text }}
          </p>
        </div>
        <div class="bg-white border border-gray-200 rounded-xl p-4">
          <p class="text-xs font-bold text-gray-500 uppercase mb-2">
            {{ question?.content?.opinion_b?.person }}
          </p>
          <p class="text-sm text-gray-700 italic">
            {{ question?.content?.opinion_b?.text }}
          </p>
        </div>
      </div>

      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre prise de
          position :
        </p>
        <AudioRecorder :teil-number="teil.teil_number" @recorded="onRecorded" />
      </div>
    </div>

    <!-- oral_discussion — Goethe B2 Teil 2 -->
    <div v-else-if="teil.format_type === 'oral_discussion'" class="space-y-5">
      <div class="bg-white border border-gray-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-gray-700 mb-3">
          Question à débattre :
        </p>
        <p class="text-base font-bold text-gray-900">
          {{ question?.content?.question }}
        </p>
      </div>

      <div
        v-if="question?.content?.tasks?.length"
        class="bg-white border border-gray-200 rounded-xl p-5"
      >
        <p class="text-sm font-semibold text-gray-700 mb-3">Tâches :</p>
        <ul class="space-y-2">
          <li
            v-for="(task, i) in question.content.tasks"
            :key="i"
            class="flex gap-3 text-sm text-gray-700"
          >
            <span
              class="w-5 h-5 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            >
              {{ (i as number) + 1 }}
            </span>
            {{ task }}
          </li>
        </ul>
      </div>

      <div v-if="question?.content?.hints?.length" class="flex flex-wrap gap-2">
        <span
          v-for="(hint, i) in question.content.hints"
          :key="i"
          class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium"
        >
          {{ hint }}
        </span>
      </div>

      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre prise de
          position :
        </p>
        <AudioRecorder :teil-number="teil.teil_number" @recorded="onRecorded" />
      </div>
    </div>

    <!-- oral_feedback — Goethe B1 Teil 3 -->
    <div v-else-if="teil.format_type === 'oral_feedback'" class="space-y-5">
      <div class="bg-white border border-gray-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-gray-700 mb-3">Tâches :</p>
        <ul class="space-y-2">
          <li
            v-for="(task, i) in question?.content?.tasks"
            :key="i"
            class="flex gap-3 text-sm text-gray-700"
          >
            <span
              class="w-5 h-5 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            >
              {{ (i as number) + 1 }}
            </span>
            {{ task }}
          </li>
        </ul>
      </div>

      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre réaction :
        </p>
        <AudioRecorder :teil-number="teil.teil_number" @recorded="onRecorded" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AudioRecorder from "~/components/session/AudioRecorder.vue";
import NotesArea from "~/components/session/NotesArea.vue";

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
  sessionId?: string;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const runtimeConfig = useRuntimeConfig();
const apiBase =
  (runtimeConfig.public.apiBaseUrl as string) || "http://localhost:8001";

const selectedTheme = ref<string | null>(null);
const activeSlide = ref(0);

const question = computed(() => props.questions[0]);

// ✅ Détecte le format Goethe B2 (candidate_a / candidate_b)
const hasGoetheThemes = computed(() => {
  const content = question.value?.content;
  return !!(content?.candidate_a || content?.candidate_b);
});

// ✅ Fusionne candidate_a et candidate_b en un objet de thèmes
const goetheThemes = computed(() => {
  const content = question.value?.content;
  if (!content) return {};
  const themes: Record<string, any> = {};
  if (content.candidate_a) {
    Object.entries(content.candidate_a).forEach(([key, val]) => {
      themes[`a_${key}`] = val;
    });
  }
  if (content.candidate_b) {
    Object.entries(content.candidate_b).forEach(([key, val]) => {
      themes[`b_${key}`] = val;
    });
  }
  return themes;
});

const currentSlides = computed(() => {
  if (!selectedTheme.value) return [];
  return question.value?.content?.themes?.[selectedTheme.value]?.slides || [];
});

const onNotes = (val: any) => {
  if (!question.value) return;
  const existing = props.answers[question.value.id]?.user_answer || {};
  emit("answer", question.value.id, { ...existing, text: val.text });
};

const onRecorded = () => {
  if (!question.value) return;
  const existing = props.answers[question.value.id]?.user_answer || {};
  emit("answer", question.value.id, { ...existing, recorded: true });
};
</script>
