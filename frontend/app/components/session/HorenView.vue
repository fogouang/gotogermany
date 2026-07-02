<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <!-- Instructions -->
    <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-sm text-blue-800 font-medium">{{ teil.instructions }}</p>
    </div>

    <!-- ── Cas 1 : Multi-audio (Teil 1 et Teil 3) ──────────────────
         Les questions sont groupées par audio_file via audioGroups     -->
    <div v-if="isMultiAudio" class="space-y-8">
      <!-- ✅ Image de scène générique (fallback si pas d'image par audio) -->
      <div
        v-if="!hasAudioImages && sceneImage"
        class="bg-white border border-gray-200 rounded-xl p-4"
      >
        <img
          :src="`${apiBase}/images/${sceneImage}`"
          alt="Illustration"
          class="w-full rounded-lg object-contain max-h-72"
        />
      </div>

      <div
        v-if="teil.format_type === 'zuordnung_speaker' && teil.config?.speakers"
        class="bg-white border border-gray-200 rounded-xl p-5"
      >
        <p
          class="text-xs text-center font-bold text-gray-700 uppercase tracking-wide mb-3"
        >
          Intervenants
        </p>

        <div class="flex flex-wrap justify-center gap-8">
          <div
            v-for="(speaker, key) in teil.config.speakers"
            :key="key"
            class="flex flex-col items-center gap-2 w-32"
          >
            <!-- Image grande (portrait individuel si fourni) -->
            <img
              v-if="getSpeakerImage(speaker)"
              :src="`${apiBase}/images/${getSpeakerImage(speaker)}`"
              :alt="getSpeakerName(speaker)"
              class="w-32 h-40 object-cover rounded-lg border border-gray-200"
            />
            <div
              v-else
              class="w-32 h-40 rounded-lg bg-teal-50 border-2 border-dashed border-gray-200 flex items-center justify-center"
            >
              <span class="font-bold text-teal-400 text-2xl">{{
                String(key).toUpperCase()
              }}</span>
            </div>

            <!-- Label + nom en dessous -->
            <div class="text-center">
              <span
                class="text-xs font-bold text-teal-600 border border-teal-200 bg-teal-50 px-1.5 py-0.5 rounded mr-1"
              >
                {{ String(key) }}
              </span>
              <span class="text-sm font-medium text-gray-700">{{
                getSpeakerName(speaker)
              }}</span>
            </div>
          </div>
        </div>
      </div>
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
          <!-- ✅ Image spécifique à ce groupe audio (ex: horen_teil1_audio1.png) -->
          <div v-if="getAudioImage(group, gi)" class="mb-2">
            <img
              :src="`${apiBase}/images/${getAudioImage(group, gi)}`"
              alt="Illustration audio"
              class="w-full rounded-lg border border-gray-200 object-contain max-h-56"
            />
          </div>

          <!-- Conseil lecture -->
          <div
            class="flex items-center gap-2 text-amber-700 bg-amber-50 px-3 py-2 rounded-lg text-xs"
          >
            <i class="pi pi-info-circle"></i>
            Lisez d'abord les questions, puis écoutez l'audio
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
        </div>
      </div>
    </div>

    <!-- ── Cas 2 : Audio unique (Teil 2) ───────────────────────────
         1 seul audio long + toutes les questions dessous            -->
    <div v-else class="space-y-4">
      <!-- ✅ Image de scène générique (illustration du contexte, ex: horen_teil2.png) -->
      <div
        v-if="sceneImage"
        class="bg-white border border-gray-200 rounded-xl p-4"
      >
        <img
          :src="`${apiBase}/images/${sceneImage}`"
          alt="Illustration"
          class="w-full rounded-lg object-contain max-h-72"
        />
      </div>

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

const config = useRuntimeConfig();
const apiBase = (config.public.apiBaseUrl as string) || "http://localhost:8001";

const getSpeakerImage = (speaker: any): string | null =>
  typeof speaker === "object" ? (speaker?.image ?? null) : null;

const getSpeakerName = (speaker: any): string =>
  typeof speaker === "object" ? (speaker?.name ?? "") : String(speaker);

// ── Image de scène générique ──────────────────────────
// Couvre les fichiers uploadés sans suffixe (ex: horen_teil2.png)
// stockés en config.image, ainsi que config.stimulus_image si utilisé.
const sceneImage = computed(
  () => props.teil.config?.image || props.teil.config?.stimulus_image || "",
);

// ── Images par groupe audio (Teil 1/3) ────────────────
// config.audio_images = { "1": "path...", "2": "path...", ... }
// alimenté par des fichiers du type horen_teil1_audio1.png, _audio2.png...
const hasAudioImages = computed(() => {
  const images = props.teil.config?.audio_images;
  return !!images && Object.keys(images).length > 0;
});

const getAudioImage = (group: any, gi: number): string => {
  const images = props.teil.config?.audio_images;
  if (!images) return "";
  const num = group.audio_number || gi + 1;
  return images[String(num)] || "";
};

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
