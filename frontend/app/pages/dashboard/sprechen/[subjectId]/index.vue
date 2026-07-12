<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden">

    <!-- Connexion -->
    <div v-if="status === 'connecting' || status === 'idle'" class="flex-1 flex items-center justify-center">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Erreur -->
    <div v-else-if="status === 'error'" class="flex-1 flex items-center justify-center">
      <div class="max-w-lg px-6 text-center space-y-4">
        <i class="pi pi-exclamation-circle text-red-400 text-4xl"></i>
        <p class="text-red-600 font-medium">{{ errorMessage || t('sprechen_subject.connection_error') }}</p>
        <Button :label="t('sprechen_subject.back')" outlined @click="router.back()" />
      </div>
    </div>

    <!-- Session active / terminée -->
    <template v-else>

      <!-- Barre de navigation sticky -->
      <div class="shrink-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3">
        <Button icon="pi pi-arrow-left" text rounded @click="confirmLeave" />
        <h1 class="text-sm font-semibold text-gray-800 truncate flex-1">
          {{ currentTeil?.teil_name }}
        </h1>
        <span v-if="currentTeil" class="ml-auto text-xs text-gray-400 shrink-0">
          Teil {{ currentTeil.teil_number }} / {{ totalTeile }}
        </span>
      </div>

      <!-- TAB : session en cours -->
      <div
        v-if="status === 'active' && currentTeil"
        class="flex-1 overflow-y-auto p-6 max-w-2xl mx-auto w-full space-y-4"
      >
        <!-- Consigne -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-5">
          <p class="text-sm text-blue-900 leading-relaxed">{{ currentTeil.instructions }}</p>
        </div>

        <!-- Timer -->
        <span class="inline-flex items-center text-xs font-bold px-3 py-1.5 rounded-full bg-amber-100 text-amber-700">
          <i class="pi pi-clock mr-1.5"></i>
          {{ t('sprechen_subject.time_for_part', { minutes: currentTeil.duration_minutes }) }}
        </span>

        <!-- Points à aborder -->
        <div v-if="currentTeil.content_points.length" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div class="bg-gray-50 border-b border-gray-200 px-5 py-3">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              {{ t('sprechen_subject.points_to_cover') }}
            </p>
          </div>
          <ul class="px-5 py-4 space-y-1.5">
            <li v-for="point in currentTeil.content_points" :key="point" class="flex gap-2 text-sm text-gray-700">
              <span class="font-bold shrink-0">–</span>
              <span>{{ point }}</span>
            </li>
          </ul>
        </div>

        <!-- Indicateur micro -->
        <div class="flex flex-col items-center gap-3 py-8">
          <div
            class="w-20 h-20 rounded-full flex items-center justify-center transition-colors"
            :class="{
              'bg-blue-100': micState === 'agent_speaking',
              'bg-teal-100 animate-pulse': micState === 'student_turn',
              'bg-gray-100': !micState,
            }"
          >
            <i
              class="pi text-2xl"
              :class="micState === 'agent_speaking' ? 'pi-volume-up text-blue-500' : 'pi-microphone text-teal-600'"
            />
          </div>
          <p class="text-sm font-medium text-gray-600">{{ micLabel }}</p>
        </div>

        <!-- Transcript en direct -->
        <div
          v-if="transcript.length"
          class="bg-gray-50 border border-gray-200 rounded-xl p-4 max-h-48 overflow-y-auto space-y-2"
          role="log"
          aria-live="polite"
        >
          <p
            v-for="(line, i) in transcript"
            :key="i"
            class="text-sm"
            :class="line.speaker === 'student' ? 'text-teal-700 text-right' : 'text-gray-700'"
          >
            {{ line.text }}
          </p>
        </div>
      </div>

      <!-- TAB : correction en cours (session terminée, grading pas encore arrivé) -->
      <div v-else-if="status === 'ended' && !gradingResult" class="flex-1 flex flex-col items-center justify-center gap-3">
        <i class="pi pi-spin pi-spinner text-teal-600 text-2xl" />
        <p class="text-sm font-medium text-teal-700">{{ t('sprechen_subject.grading_in_progress') }}</p>
      </div>

      <!-- TAB : résultat -->
      <div v-else-if="status === 'ended' && gradingResult" class="flex-1 overflow-y-auto">
        <div class="max-w-2xl mx-auto px-4 py-8 space-y-5">

          <!-- Hero score, meme langage visuel que resultats.vue -->
          <div class="rounded-2xl overflow-hidden" :class="gradingResult.passed ? 'bg-green-600' : 'bg-orange-500'">
            <div class="px-6 pt-6 pb-4 flex items-start justify-between gap-4">
              <div>
                <p class="text-xs text-white/70 font-semibold uppercase tracking-widest mb-1">
                  {{ gradingResult.provider.toUpperCase() }} · {{ gradingResult.level.toUpperCase() }}
                </p>
                <h1 class="text-2xl font-bold text-white">
                  {{ gradingResult.passed ? '🎉 ' + t('sprechen_subject.passed') : t('sprechen_subject.not_passed') }}
                </h1>
              </div>
              <div class="text-white text-right shrink-0">
                <p class="text-2xl font-bold leading-none">
                  {{ Math.round((gradingResult.total_score / gradingResult.total_max_score) * 100) }}%
                </p>
              </div>
            </div>
            <div class="px-6 py-4 bg-black/10 border-t border-white/10">
              <p class="text-sm text-white/90">
                {{ gradingResult.total_score }} / {{ gradingResult.total_max_score }} {{ t('sprechen_subject.points') }}
              </p>
            </div>
          </div>

          <!-- Détail par Teil -->
          <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
            <div class="px-5 py-4 border-b border-gray-100">
              <h2 class="font-semibold text-gray-800 text-sm">{{ t('sprechen_subject.detail_by_teil') }}</h2>
            </div>
            <div class="divide-y divide-gray-100">
              <div v-for="teil in gradingResult.teile" :key="teil.teil_number" class="px-5 py-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">
                    Teil {{ teil.teil_number }} — {{ teil.teil_name }}
                  </span>
                  <span class="text-xs text-gray-400">{{ teil.teil_score }}/{{ teil.teil_max_score }}</span>
                </div>
                <ul class="space-y-1">
                  <li v-for="c in teil.criteria" :key="c.criterion_name" class="text-xs text-gray-500">
                    {{ c.criterion_name }}: {{ c.score }}/{{ c.max_score }}
                    <span v-if="c.comment">— {{ c.comment }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Points forts / a ameliorer -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-if="gradingResult.strengths.length">
              <p class="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2 flex items-center gap-1">
                <i class="pi pi-check-circle" /> {{ t('sprechen_subject.strengths') }}
              </p>
              <ul class="space-y-1.5">
                <li
                  v-for="(s, i) in gradingResult.strengths"
                  :key="i"
                  class="flex items-start gap-2 text-sm text-gray-700 bg-green-50 rounded-lg px-3 py-2"
                >
                  <i class="pi pi-check text-green-500 mt-0.5 shrink-0 text-xs" />
                  <span>{{ s }}</span>
                </li>
              </ul>
            </div>
            <div v-if="gradingResult.improvement_areas.length">
              <p class="text-xs font-semibold text-orange-700 uppercase tracking-wide mb-2 flex items-center gap-1">
                <i class="pi pi-exclamation-circle" /> {{ t('sprechen_subject.to_improve') }}
              </p>
              <ul class="space-y-1.5">
                <li
                  v-for="(a, i) in gradingResult.improvement_areas"
                  :key="i"
                  class="flex items-start gap-2 text-sm text-gray-700 bg-orange-50 rounded-lg px-3 py-2"
                >
                  <i class="pi pi-times text-orange-400 mt-0.5 shrink-0 text-xs" />
                  <span>{{ a }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pb-8">
            <Button :label="t('sprechen_subject.redo')" icon="pi pi-refresh" outlined class="flex-1" @click="redo" />
            <Button :label="t('sprechen_subject.choose_another')" icon="pi pi-list" class="flex-1" @click="goToList" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';
import { useSprechenSession } from '~/composables/useSprechenSession'; // ADJUST if your path differs
import { createBrowserAudioIO } from '~/composables/audioIO'; // ADJUST if your path differs

definePageMeta({ layout: 'dashboard', middleware: 'auth' });

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const runtimeConfig = useRuntimeConfig();

const subjectId = route.params.subjectId as string;
const wsBaseUrl = runtimeConfig.public.sprechenWsBaseUrl as string;
const audioIO = createBrowserAudioIO();

// No Pinia store here, unlike useSimulatorStore — the live session's
// state genuinely doesn't need to survive a route change (unlike
// Schreiben's correction result, which is read again on the separate
// /resultats route). Everything the result screen needs is already
// held in gradingResult below, in the same page.
const {
  status,
  totalTeile,
  currentTeil,
  micState,
  transcript,
  gradingResult,
  errorMessage,
  connect,
  abandonSession,
  disconnect,
} = useSprechenSession({ subjectId, wsBaseUrl, audioIO });

const micLabel = computed(() => {
  if (micState.value === 'agent_speaking') return t('sprechen_subject.examiner_speaking');
  if (micState.value === 'student_turn') return t('sprechen_subject.your_turn');
  return '';
});

function confirmLeave() {
  if (status.value === 'active' && !window.confirm(t('sprechen_subject.confirm_leave'))) {
    return;
  }
  abandonSession();
  router.back();
}

const goToList = () => router.push('/dashboard/sprechen');
const redo = () => {
  disconnect();
  connect();
};

onMounted(() => connect());
onUnmounted(() => disconnect());

useHead({ title: t('sprechen_subject.page_title') });
</script>