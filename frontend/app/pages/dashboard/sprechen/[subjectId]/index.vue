<template>
  <div
    class="h-screen flex flex-col overflow-hidden transition-colors duration-500"
    :class="isCallTheme
      ? 'bg-[radial-gradient(ellipse_at_50%_-10%,#10534a_0%,#0b2b26_50%,#061412_100%)] text-white'
      : 'bg-slate-50 text-gray-900'"
  >
    <!-- Connexion -->
    <div
      v-if="status === 'connecting' || status === 'idle'"
      class="flex-1 flex items-center justify-center"
    >
      <div class="flex flex-col items-center gap-5">
        <div class="relative w-28 h-28 flex items-center justify-center">
          <span class="absolute inset-0 rounded-full bg-teal-400/10 blur-xl animate-pulse" />
          <span class="absolute inset-2 rounded-full bg-linear-to-br from-teal-400/40 via-emerald-500/20 to-transparent" />
          <div class="relative w-16 h-16 rounded-full bg-white/10 border border-white/15 backdrop-blur flex items-center justify-center">
            <ProgressSpinner style="width: 26px; height: 26px" strokeWidth="4" />
          </div>
        </div>
        <p class="text-sm font-medium text-white/60 tracking-wide">
          {{ t("sprechen_subject.connecting") }}
        </p>
      </div>
    </div>

    <!-- Erreur -->
    <div
      v-else-if="status === 'error'"
      class="flex-1 flex items-center justify-center"
    >
      <div class="max-w-lg px-6 text-center space-y-4">
        <div class="w-14 h-14 mx-auto rounded-full bg-red-500/10 border border-red-400/20 flex items-center justify-center">
          <i class="pi pi-exclamation-circle text-red-300 text-2xl"></i>
        </div>
        <p class="text-red-200 font-medium">
          {{ errorMessage || t("sprechen_subject.connection_error") }}
        </p>
        <Button
          :label="t('sprechen_subject.back')"
          outlined
          class="border-white/25! text-white!"
          @click="router.back()"
        />
      </div>
    </div>

    <!-- Session active / terminée -->
    <template v-else>
      <!-- Barre d'appel sticky -->
      <div
        class="shrink-0 backdrop-blur border-b px-4 py-3 flex items-center gap-3"
        :class="isCallTheme ? 'bg-white/5 border-white/10' : 'bg-white/95 border-gray-200'"
      >
        <Button
          icon="pi pi-arrow-left"
          text
          rounded
          :class="isCallTheme ? 'text-white!' : ''"
          @click="confirmLeave"
        />
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <span
            class="w-2 h-2 rounded-full shrink-0"
            :class="status === 'active' ? 'bg-red-500 animate-pulse' : 'bg-gray-400'"
          />
          <h1
            class="text-sm font-semibold truncate"
            :class="isCallTheme ? 'text-white/90' : 'text-gray-800'"
          >
            {{ currentTeil?.teil_name }}
          </h1>
        </div>
        <span
          v-if="currentTeil"
          class="ml-auto text-xs font-medium shrink-0 rounded-full px-2.5 py-1"
          :class="isCallTheme ? 'bg-white/10 text-white/70' : 'bg-gray-100 text-gray-400'"
        >
          Teil {{ currentTeil.teil_number }} / {{ totalTeile }}
        </span>
      </div>

      <!-- TAB : session en cours (interface d'appel) -->
      <div
        v-if="status === 'active' && currentTeil"
        class="flex-1 overflow-y-auto"
      >
        <div class="max-w-2xl mx-auto w-full px-4 py-8 space-y-6">
          <!-- Portrait des deux interlocuteurs (examinateur / candidat) -->
          <div class="flex items-center justify-center gap-6 sm:gap-10 pb-2">
            <!-- Examinateur -->
            <div class="flex flex-col items-center gap-2 transition-opacity duration-300"
              :class="micState === 'student_turn' ? 'opacity-40' : 'opacity-100'"
            >
              <div class="relative w-24 h-24 sm:w-28 sm:h-28 flex items-center justify-center">
                <span
                  class="absolute inset-0 rounded-full bg-teal-400/40 blur-md transition-opacity duration-300"
                  :class="micState === 'agent_speaking' ? 'opacity-100 animate-pulse' : 'opacity-0'"
                />
                <span
                  class="absolute inset-0 rounded-full border-2 transition-colors duration-300"
                  :class="micState === 'agent_speaking' ? 'border-teal-300/70' : 'border-white/10'"
                />
                <svg
                  viewBox="0 0 100 100"
                  class="relative w-[88%] h-[88%] rounded-full bg-linear-to-b from-[#173a35] to-[#0c211d] avatar-breathe"
                >
                  <defs>
                    <linearGradient id="skinTone" x1="0" y1="0" x2="0.3" y2="1">
                      <stop offset="0%" stop-color="#f0c49c" />
                      <stop offset="100%" stop-color="#dba876" />
                    </linearGradient>
                    <linearGradient id="brandGrad" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#2dd4bf" />
                      <stop offset="100%" stop-color="#047857" />
                    </linearGradient>
                  </defs>
                  <!-- oreilles -->
                  <circle cx="26" cy="43" r="4.5" fill="url(#skinTone)" />
                  <circle cx="74" cy="43" r="4.5" fill="url(#skinTone)" />
                  <!-- visage -->
                  <circle cx="50" cy="42" r="22" fill="url(#skinTone)" />
                  <ellipse cx="59" cy="48" rx="10" ry="14" fill="#c8935f" opacity="0.18" />
                  <!-- cheveux -->
                  <path d="M27 34 Q29 11 50 11 Q71 11 73 34 Q73 21 50 19 Q27 21 27 34 Z" fill="#23282f" />
                  <!-- sourcils -->
                  <path d="M35 33 Q41 30 47 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
                  <path d="M53 33 Q59 30 65 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
                  <!-- lunettes + yeux -->
                  <circle cx="41" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
                  <circle cx="59" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
                  <line x1="48" y1="41" x2="52" y2="41" stroke="#2b2019" stroke-width="2" />
                  <g class="avatar-eyes">
                    <circle cx="41" cy="41" r="2.6" fill="#2b2019" />
                    <circle cx="59" cy="41" r="2.6" fill="#2b2019" />
                    <circle cx="42" cy="39.5" r="0.8" fill="#fff" />
                    <circle cx="60" cy="39.5" r="0.8" fill="#fff" />
                  </g>
                  <!-- nez -->
                  <path d="M50 42 L48.5 49 Q50 50.5 51.5 49" fill="none" stroke="#c8935f" stroke-width="1.4" stroke-linecap="round" />
                  <!-- bouche -->
                  <rect
                    x="44" y="53" width="12" height="4" rx="2"
                    fill="#a15c46"
                    class="avatar-mouth"
                    :class="micState === 'agent_speaking' ? 'is-talking' : ''"
                  />
                  <!-- costume -->
                  <path d="M14 100 Q20 70 50 70 Q80 70 86 100 Z" fill="#1f2733" />
                  <path d="M40 70 L50 84 L60 70 L54 68 L46 68 Z" fill="#f4f4f4" />
                  <path d="M47 70 L50 92 L53 70 Z" fill="url(#brandGrad)" />
                </svg>
              </div>
              <p class="text-xs font-medium text-white/60 tracking-wide">Examinateur</p>
            </div>

            <!-- Candidat (l'utilisateur) -->
            <div class="flex flex-col items-center gap-2 transition-opacity duration-300"
              :class="micState === 'agent_speaking' ? 'opacity-40' : 'opacity-100'"
            >
              <div class="relative w-24 h-24 sm:w-28 sm:h-28 flex items-center justify-center">
                <span
                  class="absolute inset-0 rounded-full bg-emerald-300/35 blur-md transition-opacity duration-300"
                  :class="micState === 'student_turn' ? 'opacity-100 animate-pulse' : 'opacity-0'"
                />
                <span
                  class="absolute inset-0 rounded-full border-2 transition-colors duration-300"
                  :class="micState === 'student_turn' ? 'border-emerald-300/70' : 'border-white/10'"
                />
                <svg
                  viewBox="0 0 100 100"
                  class="relative w-[88%] h-[88%] rounded-full bg-linear-to-b from-[#173a35] to-[#0c211d] avatar-breathe"
                >
                  <defs>
                    <linearGradient id="skinTone2" x1="0" y1="0" x2="0.3" y2="1">
                      <stop offset="0%" stop-color="#f0c49c" />
                      <stop offset="100%" stop-color="#dba876" />
                    </linearGradient>
                    <linearGradient id="brandGrad2" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#2dd4bf" />
                      <stop offset="100%" stop-color="#047857" />
                    </linearGradient>
                  </defs>
                  <circle cx="26" cy="44" r="4.5" fill="url(#skinTone2)" />
                  <circle cx="74" cy="44" r="4.5" fill="url(#skinTone2)" />
                  <circle cx="50" cy="42" r="22" fill="url(#skinTone2)" />
                  <ellipse cx="59" cy="48" rx="10" ry="14" fill="#c8935f" opacity="0.18" />
                  <path d="M27 37 Q26 14 50 13 Q74 14 73 37 Q73 30 62 25 Q56 33 50 25 Q44 33 38 25 Q27 30 27 37 Z" fill="#5c3a20" />
                  <path d="M35 33 Q41 30.5 47 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
                  <path d="M53 33 Q59 30.5 65 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
                  <g class="avatar-eyes">
                    <circle cx="41" cy="41" r="2.6" fill="#2b2019" />
                    <circle cx="59" cy="41" r="2.6" fill="#2b2019" />
                    <circle cx="42" cy="39.5" r="0.8" fill="#fff" />
                    <circle cx="60" cy="39.5" r="0.8" fill="#fff" />
                  </g>
                  <path d="M50 42 L48.5 49 Q50 50.5 51.5 49" fill="none" stroke="#c8935f" stroke-width="1.4" stroke-linecap="round" />
                  <rect
                    x="44" y="53" width="12" height="4" rx="2"
                    fill="#a15c46"
                    class="avatar-mouth"
                    :class="micState === 'student_turn' ? 'is-talking' : ''"
                  />
                  <!-- casque audio -->
                  <path d="M25 28 Q50 8 75 28" fill="none" stroke="#374151" stroke-width="5" stroke-linecap="round" />
                  <circle cx="25" cy="32" r="6" fill="url(#brandGrad2)" />
                  <circle cx="75" cy="32" r="6" fill="url(#brandGrad2)" />
                  <!-- sweat -->
                  <path d="M12 100 Q20 68 50 68 Q80 68 88 100 Z" fill="url(#brandGrad2)" />
                </svg>
              </div>
              <p class="text-xs font-medium text-white/60 tracking-wide">Vous</p>
            </div>
          </div>
          <p class="text-center text-xs text-white/40 uppercase tracking-widest -mt-3">{{ micLabel }}</p>

          <!-- Message "consignes" de l'examinateur (épinglé) -->
          <div class="flex items-start gap-2.5">
            <div class="w-8 h-8 rounded-full overflow-hidden shrink-0 mt-0.5 border border-white/15">
              <svg viewBox="0 0 100 100" class="w-full h-full bg-linear-to-b from-[#173a35] to-[#0c211d]">
                <circle cx="50" cy="42" r="22" fill="#e0b48c" />
                <path d="M27 34 Q29 11 50 11 Q71 11 73 34 Q73 21 50 19 Q27 21 27 34 Z" fill="#23282f" />
                <circle cx="41" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
                <circle cx="59" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
                <line x1="48" y1="41" x2="52" y2="41" stroke="#2b2019" stroke-width="2" />
                <path d="M14 100 Q20 70 50 70 Q80 70 86 100 Z" fill="#1f2733" />
              </svg>
            </div>
            <div class="min-w-0 space-y-2">
              <div class="bg-white/8 border border-white/10 backdrop-blur rounded-2xl rounded-tl-sm px-4 py-3">
                <p class="text-sm text-white/85 leading-relaxed">
                  {{ currentTeil.instructions }}
                </p>
              </div>
              <span
                class="inline-flex items-center text-xs font-bold px-3 py-1 rounded-full bg-amber-400/10 text-amber-200 border border-amber-300/20"
              >
                <i class="pi pi-clock mr-1.5"></i>
                {{
                  t("sprechen_subject.time_for_part", {
                    minutes: currentTeil.duration_minutes,
                  })
                }}
              </span>

              <!-- Points à aborder -->
              <div
                v-if="currentTeil.content_points.length"
                class="bg-white/8 border border-white/10 backdrop-blur rounded-2xl rounded-tl-sm overflow-hidden"
              >
                <div class="bg-white/5 border-b border-white/10 px-4 py-2">
                  <p class="text-[11px] font-semibold text-white/50 uppercase tracking-wide">
                    {{ t("sprechen_subject.points_to_cover") }}
                  </p>
                </div>
                <ul class="px-4 py-3 space-y-1.5">
                  <li
                    v-for="point in currentTeil.content_points"
                    :key="point"
                    class="flex gap-2 text-sm text-white/80"
                  >
                    <span class="font-bold text-teal-300/80 shrink-0">–</span>
                    <span>{{ point }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Fil de discussion (transcript live) -->
          <div class="space-y-3 py-2">
            <div
              v-for="(line, i) in groupedTranscript"
              :key="i"
              class="flex items-end gap-2"
              :class="line.speaker === 'student' ? 'flex-row-reverse' : 'flex-row'"
            >
              <div
                class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 overflow-hidden border"
                :class="line.speaker === 'student' ? 'border-emerald-300/30' : 'border-white/15'"
              >
                <svg v-if="line.speaker === 'student'" viewBox="0 0 100 100" class="w-full h-full bg-linear-to-b from-[#173a35] to-[#0c211d]">
                  <defs>
                    <linearGradient id="brandGradMiniS" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#2dd4bf" />
                      <stop offset="100%" stop-color="#047857" />
                    </linearGradient>
                  </defs>
                  <circle cx="50" cy="42" r="22" fill="#e0b48c" />
                  <path d="M27 37 Q26 14 50 13 Q74 14 73 37 Q73 30 62 25 Q56 33 50 25 Q44 33 38 25 Q27 30 27 37 Z" fill="#5c3a20" />
                  <path d="M25 28 Q50 8 75 28" fill="none" stroke="#374151" stroke-width="4" stroke-linecap="round" />
                  <circle cx="25" cy="32" r="5" fill="url(#brandGradMiniS)" />
                  <circle cx="75" cy="32" r="5" fill="url(#brandGradMiniS)" />
                  <path d="M12 100 Q20 68 50 68 Q80 68 88 100 Z" fill="url(#brandGradMiniS)" />
                </svg>
                <svg v-else viewBox="0 0 100 100" class="w-full h-full bg-linear-to-b from-[#173a35] to-[#0c211d]">
                  <circle cx="50" cy="42" r="22" fill="#e0b48c" />
                  <path d="M27 34 Q29 11 50 11 Q71 11 73 34 Q73 21 50 19 Q27 21 27 34 Z" fill="#23282f" />
                  <circle cx="41" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
                  <circle cx="59" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
                  <line x1="48" y1="41" x2="52" y2="41" stroke="#2b2019" stroke-width="2" />
                  <path d="M14 100 Q20 70 50 70 Q80 70 86 100 Z" fill="#1f2733" />
                </svg>
              </div>
              <div
                class="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
                :class="
                  line.speaker === 'student'
                    ? 'bg-linear-to-br from-[#eafaf5] to-[#d3f1e8] text-[#0b2420] rounded-br-sm shadow-md shadow-black/20'
                    : 'bg-white/10 border border-white/10 backdrop-blur text-white/85 rounded-bl-sm'
                "
              >
                {{ line.text }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB : correction en cours (bulle "en train d'écrire") -->
      <div
        v-else-if="status === 'ended' && !gradingResult"
        class="flex-1 flex flex-col items-center justify-center gap-4"
      >
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full overflow-hidden border border-white/15">
            <svg viewBox="0 0 100 100" class="w-full h-full bg-linear-to-b from-[#173a35] to-[#0c211d]">
              <circle cx="50" cy="42" r="22" fill="#e0b48c" />
              <path d="M27 34 Q29 11 50 11 Q71 11 73 34 Q73 21 50 19 Q27 21 27 34 Z" fill="#23282f" />
              <circle cx="41" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
              <circle cx="59" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
              <line x1="48" y1="41" x2="52" y2="41" stroke="#2b2019" stroke-width="2" />
              <path d="M14 100 Q20 70 50 70 Q80 70 86 100 Z" fill="#1f2733" />
            </svg>
          </div>
          <div class="bg-white/8 border border-white/10 backdrop-blur rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1.5">
            <span class="typing-dot"></span>
            <span class="typing-dot" style="animation-delay: 0.15s"></span>
            <span class="typing-dot" style="animation-delay: 0.3s"></span>
          </div>
        </div>
        <p class="text-sm font-medium text-teal-300/80">
          {{ t("sprechen_subject.grading_in_progress") }}
        </p>
      </div>

      <!-- TAB : résultat -->
      <div
        v-else-if="status === 'ended' && gradingResult"
        class="flex-1 overflow-y-auto"
      >
        <div class="max-w-2xl mx-auto px-4 py-8 space-y-5">
          <!-- Hero score -->
          <div
            class="rounded-2xl overflow-hidden shadow-sm"
            :class="gradingResult.passed ? 'bg-green-600' : 'bg-orange-500'"
          >
            <div class="px-6 pt-6 pb-4 flex items-start justify-between gap-4">
              <div>
                <p class="text-xs text-white/70 font-semibold uppercase tracking-widest mb-1">
                  {{ gradingResult.provider.toUpperCase() }} ·
                  {{ gradingResult.level.toUpperCase() }}
                </p>
                <h1 class="text-2xl font-bold text-white">
                  {{
                    gradingResult.passed
                      ? "🎉 " + t("sprechen_subject.passed")
                      : t("sprechen_subject.not_passed")
                  }}
                </h1>
              </div>
              <div class="text-white text-right shrink-0">
                <p class="text-2xl font-bold leading-none">
                  {{
                    Math.round(
                      (gradingResult.total_score /
                        gradingResult.total_max_score) *
                        100,
                    )
                  }}%
                </p>
              </div>
            </div>
            <div class="px-6 py-4 bg-black/10 border-t border-white/10">
              <p class="text-sm text-white/90">
                {{ gradingResult.total_score }} /
                {{ gradingResult.total_max_score }}
                {{ t("sprechen_subject.points") }}
              </p>
            </div>
          </div>

          <!-- Détail par Teil -->
          <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-5 py-4 border-b border-gray-100">
              <h2 class="font-semibold text-gray-800 text-sm">
                {{ t("sprechen_subject.detail_by_teil") }}
              </h2>
            </div>
            <div class="divide-y divide-gray-100">
              <div
                v-for="teil in gradingResult.teile"
                :key="teil.teil_number"
                class="px-5 py-4"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">
                    Teil {{ teil.teil_number }} — {{ teil.teil_name }}
                  </span>
                  <span class="text-xs text-gray-400"
                    >{{ teil.teil_score }}/{{ teil.teil_max_score }}</span
                  >
                </div>
                <ul class="space-y-1">
                  <li
                    v-for="c in teil.criteria"
                    :key="c.criterion_name"
                    class="text-xs text-gray-500"
                  >
                    {{ c.criterion_name }}: {{ c.score }}/{{ c.max_score }}
                    <span v-if="c.comment">— {{ c.comment }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Points forts / à améliorer -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-if="gradingResult.strengths.length">
              <p class="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2 flex items-center gap-1">
                <i class="pi pi-check-circle" />
                {{ t("sprechen_subject.strengths") }}
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
                <i class="pi pi-exclamation-circle" />
                {{ t("sprechen_subject.to_improve") }}
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
            <Button
              :label="t('sprechen_subject.redo')"
              icon="pi pi-refresh"
              outlined
              class="flex-1"
              @click="redo"
            />
            <Button
              :label="t('sprechen_subject.choose_another')"
              icon="pi pi-list"
              class="flex-1"
              @click="goToList"
            />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";
import { useSprechenSession } from "~/composables/useSprechenSession"; // ADJUST if your path differs
import { createBrowserAudioIO } from "~/composables/audioIO"; // ADJUST if your path differs

definePageMeta({ layout: "dashboard", middleware: "auth" });

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

// Display-only: whether we're in the immersive "call" theme (connecting,
// active session, error, and the brief grading-in-progress moment) vs.
// the light report theme (final result). Purely a presentational
// grouping of the existing `status`/`gradingResult` values.
const isCallTheme = computed(() =>
  ["idle", "connecting", "active", "error"].includes(status.value) ||
  (status.value === "ended" && !gradingResult.value),
);

const micLabel = computed(() => {
  if (micState.value === "agent_speaking")
    return t("sprechen_subject.examiner_speaking");
  if (micState.value === "student_turn") return t("sprechen_subject.your_turn");
  return "";
});

// Display-only grouping: the transcript can arrive as many small chunks
// (streaming words/segments) for the same turn. We merge consecutive
// chunks from the same speaker into a single bubble for rendering,
// without altering the underlying transcript data from the composable.
const groupedTranscript = computed(() => {
  const groups: { speaker: string; text: string }[] = [];
  for (const line of transcript.value) {
    const last = groups[groups.length - 1];
    if (last && last.speaker === line.speaker) {
      last.text = `${last.text} ${line.text}`.replace(/\s+/g, " ").trim();
    } else {
      groups.push({ speaker: line.speaker, text: line.text.trim() });
    }
  }
  return groups;
});

function confirmLeave() {
  if (
    status.value === "active" &&
    !window.confirm(t("sprechen_subject.confirm_leave"))
  ) {
    return;
  }
  abandonSession();
  router.back();
}

const goToList = () => router.push("/dashboard/sprechen");
const redo = () => {
  disconnect();
  connect();
};

onMounted(() => connect());
onUnmounted(() => disconnect());

useHead({ title: t("sprechen_subject.page_title") });
</script>

<style scoped>
.avatar-breathe {
  animation: avatar-breathe 4s ease-in-out infinite;
  transform-origin: 50% 100%;
}
@keyframes avatar-breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

.avatar-eyes {
  animation: avatar-blink 4.5s ease-in-out infinite;
  transform-origin: 50px 40px;
}
@keyframes avatar-blink {
  0%, 92%, 100% { transform: scaleY(1); }
  96% { transform: scaleY(0.1); }
}

.avatar-mouth {
  transform-origin: 50px 54px;
  transition: transform 0.15s ease;
}
.avatar-mouth.is-talking {
  animation: avatar-talk 0.42s ease-in-out infinite;
}
@keyframes avatar-talk {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(2.2); }
}

.wave-bar-sm {
  height: 6px;
  animation: wave-sm 0.9s ease-in-out infinite;
}
@keyframes wave-sm {
  0%, 100% { height: 4px; }
  50% { height: 10px; }
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background-color: rgba(255, 255, 255, 0.5);
  display: inline-block;
  animation: typing-bounce 1s infinite ease-in-out;
}
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-4px); opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .wave-bar-sm, .typing-dot, .avatar-breathe, .avatar-eyes, .avatar-mouth.is-talking {
    animation: none !important;
  }
}
</style>