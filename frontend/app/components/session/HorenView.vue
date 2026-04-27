<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <!-- Instructions -->
    <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-sm text-blue-800 font-medium">{{ teil.instructions }}</p>
    </div>

    <!-- ── Cas 1 : Multi-audio (Teil 1 et Teil 3) ──────────────────
         Les questions sont groupées par audio_file via audioGroups     -->
    <div v-if="isMultiAudio" class="space-y-8">
      <div
        v-for="(group, gi) in audioGroups"
        :key="gi"
        class="bg-white border border-gray-200 rounded-xl overflow-hidden"
      >
        <!-- Header groupe audio -->
        <div
          class="bg-gray-50 border-b border-gray-200 px-5 py-3 flex items-center gap-3"
        >
          <span
            class="w-7 h-7 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0"
          >
            {{ group.audio_number || gi + 1 }}
          </span>
          <span class="text-sm font-medium text-gray-700">
            {{
              group.questions[0]?.content?.audio_type ||
              `Audio ${group.audio_number || gi + 1}`
            }}
          </span>
          <span class="ml-auto text-xs text-gray-400">
            {{ group.questions.length }} question(s)
          </span>
        </div>

        <div class="p-5 space-y-4">
          <!-- Conseil lecture -->
          <div
            class="flex items-center gap-2 text-amber-700 bg-amber-50 px-3 py-2 rounded-lg text-xs"
          >
            <i class="pi pi-info-circle"></i>
            Lisez d'abord les questions, puis écoutez l'audio
          </div>

          <!-- Questions de ce groupe -->
          <div class="space-y-4">
            <div
              v-for="q in group.questions"
              :key="q.id"
              :class="[
                'border rounded-lg p-4 transition-all',
                answers[q.id]
                  ? 'border-teal-300 bg-teal-50/30'
                  : 'border-gray-100',
              ]"
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

          <!-- Player audio -->
          <div v-if="group.audio_file">
            <AudioPlayer
              :src="audioUrl(group.audio_file)"
              :max-plays="99"
              :read-time="0"
            />
          </div>
          <div
            v-else
            class="flex items-center gap-2 text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm"
          >
            <i class="pi pi-exclamation-triangle"></i>
            Audio non disponible pour ce groupe
          </div>
        </div>
      </div>
    </div>

    <!-- ── Cas 2 : Audio unique (Teil 2) ───────────────────────────
         1 seul audio long + toutes les questions dessous            -->
    <div v-else class="space-y-4">
      <!-- Player audio unique -->
      <div
        v-if="singleAudioFile"
        class="bg-white border border-gray-200 rounded-xl p-5"
      >
        <div
          class="flex items-center gap-2 text-amber-700 bg-amber-50 px-3 py-2 rounded-lg text-xs mb-4"
        >
          <i class="pi pi-info-circle"></i>
          Écoutez l'audio, puis répondez aux questions
        </div>
        <AudioPlayer
          :src="audioUrl(singleAudioFile)"
          :max-plays="99"
          :read-time="0"
        />
      </div>
      <div
        v-else
        class="flex items-center gap-2 text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm"
      >
        <i class="pi pi-exclamation-triangle"></i>
        Audio non disponible pour ce teil
      </div>

      <!-- Questions -->
      <div
        v-for="q in questions"
        :key="q.id"
        :class="[
          'bg-white border rounded-xl p-5 transition-all',
          answers[q.id] ? 'border-teal-300' : 'border-gray-200',
        ]"
      >
        <QuestionItem
          :question="q"
          :answer="answers[q.id]?.user_answer"
          @answer="(val: Record<string, any>) => $emit('answer', q.id, val)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuestionItem from "~/components/session/QuestionItem.vue";
import AudioPlayer from "~/components/session/AudioPlayer.vue";

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
}>();

defineEmits<{ answer: [questionId: string, value: any] }>();

// ── URL audio ────────────────────────────────────────
const audioUrl = (path: string): string => {
  if (!path) return "";
  const clean = path.replace(/\\/g, "/");
  const config = useRuntimeConfig();
  const base = (config.public.apiBaseUrl as string) || "http://localhost:8001";
  return `${base}/audio/${clean}`;
};

// ── Groupes audio ────────────────────────────────────
// Regroupe les questions par audio_file (pour Teil 1 et 3 — multi-audio)
const isMultiAudio = computed(() => {
  const groups = audioGroups.value;
  return groups.length > 1 || (groups.length === 1 && !!groups[0]?.audio_file);
});

const audioGroups = computed(() => {
  if (!props.questions.length) return [];

  const groups = new Map<
    string,
    {
      audio_file: string;
      audio_number: number;
      questions: any[];
    }
  >();

  for (const q of props.questions) {
    const audioFile = q.audio_file || "";
    const audioNumber = q.content?.audio_number ?? 0;
    const key = audioFile || `no_audio_${audioNumber}`;

    if (!groups.has(key)) {
      groups.set(key, {
        audio_file: audioFile,
        audio_number: audioNumber,
        questions: [],
      });
    }
    groups.get(key)!.questions.push(q);
  }

  return [...groups.values()].sort((a, b) => a.audio_number - b.audio_number);
});

// ── Audio unique (Teil 2) ─────────────────────────────
// Si toutes les questions partagent le même audio_file
const singleAudioFile = computed(() => {
  if (!props.questions.length) return "";

  // Chercher d'abord dans teil.config.audio_file (Teil 2 Goethe)
  if (props.teil.config?.audio_file) return props.teil.config.audio_file;

  // Sinon prendre le premier audio_file des questions (Teil 2 TELC)
  const first = props.questions.find((q) => q.audio_file);
  return first?.audio_file || "";
});
</script>
