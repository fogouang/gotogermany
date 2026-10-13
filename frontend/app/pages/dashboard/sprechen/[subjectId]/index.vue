<template>
  <div
    class="h-screen flex flex-col overflow-hidden transition-colors duration-500"
    :class="
      isCallTheme
        ? 'bg-[radial-gradient(ellipse_at_50%_-10%,#10534a_0%,#0b2b26_50%,#061412_100%)] text-white'
        : 'bg-canvas text-ink'
    "
  >
    <!-- Connexion -->
    <div
      v-if="status === 'connecting' || status === 'idle'"
      class="flex-1 flex items-center justify-center"
    >
      <div class="flex flex-col items-center gap-5">
        <div class="relative w-28 h-28 flex items-center justify-center">
          <span
            class="absolute inset-0 rounded-full bg-teal-400/10 blur-xl animate-pulse"
          />
          <span
            class="absolute inset-2 rounded-full bg-linear-to-br from-teal-400/40 via-emerald-500/20 to-transparent"
          />
          <div
            class="relative w-16 h-16 rounded-full bg-white/10 border border-white/15 backdrop-blur flex items-center justify-center"
          >
            <ProgressSpinner
              style="width: 26px; height: 26px"
              strokeWidth="4"
            />
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
        <div
          class="w-14 h-14 mx-auto rounded-full bg-red-500/10 border border-red-400/20 flex items-center justify-center"
        >
          <i class="pi pi-exclamation-circle text-red-300 text-2xl"></i>
        </div>
        <p class="text-red-200 font-medium">
          {{ errorMessage || t("sprechen_subject.connection_error") }}
        </p>
        <Button
          :label="t('sprechen_subject.back')"
          outlined
          class="border-white/25! text-white!"
          @click="goToList"
        />
      </div>
    </div>

    <!-- Session active / préparation / terminée -->
    <template v-else>
      <!-- Barre d'appel -->
      <div
        class="shrink-0 backdrop-blur border-b px-4 py-3 flex items-center gap-3"
        :class="
          isCallTheme ? 'bg-white/5 border-white/10' : 'bg-card border-line'
        "
      >
        <Button
          icon="pi pi-arrow-left"
          text
          rounded
          :class="isCallTheme ? 'text-white!' : ''"
          :aria-label="t('sprechen_subject.back')"
          @click="confirmLeave"
        />
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <span
            class="w-2 h-2 rounded-full shrink-0"
            :class="
              status === 'active' ? 'bg-red-500 animate-pulse' : 'bg-faint'
            "
          />
          <h1
            class="text-sm font-semibold truncate"
            :class="isCallTheme ? 'text-white/90' : 'text-ink'"
          >
            {{ headerTeilName }}
          </h1>
        </div>
        <span
          v-if="headerTeilNumber"
          class="ml-auto text-xs font-medium shrink-0 rounded-full px-2.5 py-1"
          :class="
            isCallTheme ? 'bg-white/10 text-white/70' : 'bg-card-2 text-muted'
          "
        >
          Teil {{ headerTeilNumber }} / {{ totalTeile }}
        </span>
      </div>

      <!-- ═══════════════ Préparation ═══════════════ -->
      <div
        v-if="status === 'preparing' && preparationInfo"
        class="flex-1 grid grid-cols-1 md:grid-cols-[320px_1fr] overflow-hidden"
      >
        <!-- Consignes -->
        <div
          class="bg-white/5 border-r border-white/10 p-6 flex flex-col gap-5 overflow-y-auto"
        >
          <div>
            <span
              class="text-xs font-medium text-white/50 uppercase tracking-wide"
            >
              Teil {{ preparationInfo.teil_number }}
            </span>
            <h2 class="text-lg font-medium text-white/90 mt-1">
              {{ preparationInfo.teil_name }}
            </h2>
          </div>

          <p class="text-sm text-white/70 leading-relaxed">
            {{ preparationInfo.instructions }}
          </p>

          <div
            v-if="preparationInfo.scenario"
            class="bg-indigo-400/10 border border-indigo-300/20 rounded-xl px-4 py-3"
          >
            <p
              class="text-[11px] font-semibold text-indigo-200/80 uppercase tracking-wide mb-1"
            >
              {{ t("sprechen_subject.scenario_label") }}
            </p>
            <p class="text-sm text-white/85 leading-relaxed">
              {{ preparationInfo.scenario }}
            </p>
          </div>

          <div
            v-if="preparationInfo.stimulus_people?.length"
            class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden"
          >
            <div class="bg-white/5 border-b border-white/10 px-4 py-2">
              <p
                class="text-[11px] font-semibold text-white/50 uppercase tracking-wide"
              >
                {{ t("sprechen_subject.stimulus_people_label") }}
              </p>
            </div>
            <div class="divide-y divide-white/10">
              <div
                v-for="person in preparationInfo.stimulus_people"
                :key="person.name"
                class="px-4 py-3"
              >
                <p class="text-sm font-medium text-white/90">
                  {{ person.name }}
                </p>
                <p class="text-xs text-white/60 italic mt-0.5">
                  „{{ person.opinion }}“
                </p>
              </div>
            </div>
          </div>

          <div
            v-if="preparationInfo.stimulus_text"
            class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden"
          >
            <div class="bg-white/5 border-b border-white/10 px-4 py-2">
              <p
                class="text-[11px] font-semibold text-white/50 uppercase tracking-wide"
              >
                {{ t("sprechen_subject.reading_text_label") }}
              </p>
            </div>
            <p
              class="px-4 py-3 text-sm text-white/80 leading-relaxed whitespace-pre-line max-h-80 overflow-y-auto"
            >
              {{ preparationInfo.stimulus_text }}
            </p>
          </div>

          <ThemeChoicePanel
            v-if="preparationInfo.themes"
            :themes="preparationInfo.themes"
          />
          <div
            v-else-if="preparationInfo.content_points.length"
            class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden"
          >
            <div class="bg-white/5 border-b border-white/10 px-4 py-2">
              <p
                class="text-[11px] font-semibold text-white/50 uppercase tracking-wide"
              >
                {{ t("sprechen_subject.points_to_cover") }}
              </p>
            </div>
            <ul class="px-4 py-3 space-y-1.5">
              <li
                v-for="point in preparationInfo.content_points"
                :key="point"
                class="flex gap-2 text-sm text-white/80"
              >
                <i
                  class="pi pi-circle-fill text-[5px] text-teal-300/80 mt-2 shrink-0"
                ></i>
                <span>{{ point }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Chrono de préparation + démarrage -->
        <div class="flex-1 flex items-center justify-center p-8">
          <div class="flex flex-col items-center gap-6 max-w-sm w-full">
            <div class="flex flex-col items-center gap-1.5">
              <span class="text-3xl font-medium text-white/90 tabular-nums">{{
                prepElapsedLabel
              }}</span>
              <span class="text-xs text-white/40 uppercase tracking-wide">{{
                t("sprechen_subject.preparing")
              }}</span>
            </div>

            <!-- Repère : temps officiel de préparation (jamais imposé) -->
            <span
              v-if="officialPrepSeconds > 0"
              class="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full border transition-colors"
              :class="
                prepSecondsLeft === 0
                  ? 'bg-white/10 text-white/70 border-white/15'
                  : prepTimerIsAlert
                    ? 'bg-red-500/15 text-red-200 border-red-400/30 animate-pulse'
                    : 'bg-amber-400/10 text-amber-200 border-amber-300/20'
              "
            >
              <i class="pi pi-clock text-[11px]"></i>
              {{
                prepSecondsLeft > 0
                  ? t("sprechen_subject.official_prep_left", {
                      time: prepCountdownLabel,
                    })
                  : t("sprechen_subject.official_prep_over")
              }}
            </span>

            <p class="text-sm text-white/60 text-center leading-relaxed">
              {{ t("sprechen_subject.preparation_no_limit") }}
            </p>
            <Button
              :label="t('sprechen_subject.start_now')"
              class="w-full"
              @click="sendReadyToStart"
            />
          </div>
        </div>
      </div>

      <!-- ═══════════════ Session en cours (interface d'appel) ═══════════════ -->
      <div
        v-else-if="status === 'active' && currentTeil"
        class="flex-1 grid grid-cols-1 md:grid-cols-[320px_1fr] overflow-hidden"
      >
        <!-- Consignes -->
        <div
          class="bg-white/5 border-r border-white/10 p-6 flex flex-col gap-5 overflow-y-auto"
        >
          <div>
            <span
              class="text-xs font-medium text-white/50 uppercase tracking-wide"
            >
              Teil {{ currentTeil.teil_number }}
            </span>
            <h2 class="text-lg font-medium text-white/90 mt-1">
              {{ currentTeil.teil_name }}
            </h2>
          </div>

          <p class="text-sm text-white/70 leading-relaxed">
            {{ currentTeil.instructions }}
          </p>

          <span
            class="inline-flex items-center self-start text-xs font-bold px-3 py-1 rounded-full border transition-colors"
            :class="
              teilTimerIsAlert
                ? 'bg-red-500/15 text-red-200 border-red-400/30 animate-pulse'
                : 'bg-amber-400/10 text-amber-200 border-amber-300/20'
            "
          >
            <i class="pi pi-clock mr-1.5"></i>
            {{ teilCountdownLabel }}
          </span>

          <div
            v-if="currentTeil.scenario"
            class="bg-indigo-400/10 border border-indigo-300/20 rounded-xl px-4 py-3"
          >
            <p
              class="text-[11px] font-semibold text-indigo-200/80 uppercase tracking-wide mb-1"
            >
              {{ t("sprechen_subject.scenario_label") }}
            </p>
            <p class="text-sm text-white/85 leading-relaxed">
              {{ currentTeil.scenario }}
            </p>
          </div>

          <div
            v-if="currentTeil.stimulus_people?.length"
            class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden"
          >
            <div class="bg-white/5 border-b border-white/10 px-4 py-2">
              <p
                class="text-[11px] font-semibold text-white/50 uppercase tracking-wide"
              >
                {{ t("sprechen_subject.stimulus_people_label") }}
              </p>
            </div>
            <div class="divide-y divide-white/10">
              <div
                v-for="person in currentTeil.stimulus_people"
                :key="person.name"
                class="px-4 py-3"
              >
                <p class="text-sm font-medium text-white/90">
                  {{ person.name }}
                </p>
                <p class="text-xs text-white/60 italic mt-0.5">
                  „{{ person.opinion }}“
                </p>
              </div>
            </div>
          </div>

          <div
            v-if="currentTeil.stimulus_text"
            class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden"
          >
            <div class="bg-white/5 border-b border-white/10 px-4 py-2">
              <p
                class="text-[11px] font-semibold text-white/50 uppercase tracking-wide"
              >
                {{ t("sprechen_subject.reading_text_label") }}
              </p>
            </div>
            <p
              class="px-4 py-3 text-sm text-white/80 leading-relaxed whitespace-pre-line max-h-80 overflow-y-auto"
            >
              {{ currentTeil.stimulus_text }}
            </p>
          </div>

          <ThemeChoicePanel
            v-if="currentTeil.themes"
            :themes="currentTeil.themes"
          />
          <div
            v-if="currentTeil.content_points.length"
            class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden"
          >
            <div class="bg-white/5 border-b border-white/10 px-4 py-2">
              <p
                class="text-[11px] font-semibold text-white/50 uppercase tracking-wide"
              >
                {{ t("sprechen_subject.points_to_cover") }}
              </p>
            </div>
            <ul class="px-4 py-3 space-y-1.5">
              <li
                v-for="point in currentTeil.content_points"
                :key="point"
                class="flex gap-2 text-sm text-white/80"
              >
                <i
                  class="pi pi-circle-fill text-[5px] text-teal-300/80 mt-2 shrink-0"
                ></i>
                <span>{{ point }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Conversation -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <div
            class="flex items-center justify-center gap-10 pt-6 pb-2 shrink-0"
          >
            <div
              class="flex flex-col items-center gap-2 transition-opacity duration-300"
              :class="
                micState === 'student_turn' ? 'opacity-40' : 'opacity-100'
              "
            >
              <div class="relative w-16 h-16 flex items-center justify-center">
                <span
                  class="absolute inset-0 rounded-full bg-teal-400/40 blur-md transition-opacity duration-300"
                  :class="
                    micState === 'agent_speaking'
                      ? 'opacity-100 animate-pulse'
                      : 'opacity-0'
                  "
                />
                <span
                  class="absolute inset-0 rounded-full border-2 transition-colors duration-300"
                  :class="
                    micState === 'agent_speaking'
                      ? 'border-teal-300/70'
                      : 'border-white/10'
                  "
                />
                <AvatarExaminer
                  class="relative w-[88%] h-[88%]"
                  :talking="micState === 'agent_speaking'"
                />
              </div>
              <p class="text-xs font-medium text-white/60 tracking-wide">
                {{ t("sprechen_subject.examiner") }}
              </p>
            </div>

            <div
              class="flex flex-col items-center gap-2 transition-opacity duration-300"
              :class="
                micState === 'agent_speaking' ? 'opacity-40' : 'opacity-100'
              "
            >
              <div class="relative w-16 h-16 flex items-center justify-center">
                <span
                  class="absolute inset-0 rounded-full bg-emerald-300/35 blur-md transition-opacity duration-300"
                  :class="
                    micState === 'student_turn'
                      ? 'opacity-100 animate-pulse'
                      : 'opacity-0'
                  "
                />
                <span
                  class="absolute inset-0 rounded-full border-2 transition-colors duration-300"
                  :class="
                    micState === 'student_turn'
                      ? 'border-emerald-300/70'
                      : 'border-white/10'
                  "
                />
                <AvatarStudent
                  class="relative w-[88%] h-[88%]"
                  :talking="micState === 'student_turn'"
                />
              </div>
              <p class="text-xs font-medium text-white/60 tracking-wide">
                {{ t("sprechen_subject.you") }}
              </p>
            </div>
          </div>
          <p
            class="text-center text-xs text-white/40 uppercase tracking-widest mb-2 shrink-0"
          >
            {{ micLabel }}
          </p>

          <!-- Fil de discussion -->
          <div class="flex-1 overflow-y-auto px-6 pb-6">
            <div class="max-w-xl mx-auto space-y-3 py-2">
              <div
                v-for="(line, i) in groupedTranscript"
                :key="i"
                class="flex items-end gap-2"
                :class="
                  line.speaker === 'student' ? 'flex-row-reverse' : 'flex-row'
                "
              >
                <div
                  class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 overflow-hidden border"
                  :class="
                    line.speaker === 'student'
                      ? 'border-emerald-300/30'
                      : 'border-white/15'
                  "
                >
                  <AvatarStudent
                    v-if="line.speaker === 'student'"
                    class="w-full h-full"
                  />
                  <AvatarExaminer v-else class="w-full h-full" />
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
      </div>

      <!-- ═══════════════ Notation en cours ═══════════════ -->
      <div
        v-else-if="status === 'ended' && !gradingResult"
        class="flex-1 flex items-center justify-center p-6"
      >
        <div
          class="bg-card text-ink rounded-card p-7 max-w-sm w-full text-center shadow-soft"
        >
          <div
            class="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4"
          >
            <i class="pi pi-comments text-primary text-2xl"></i>
          </div>
          <h3 class="text-base font-semibold text-ink mb-1">
            {{ t("sprechen_subject.grading_modal_title") }}
          </h3>
          <p class="text-sm text-muted mb-5">
            {{ t("sprechen_subject.grading_modal_subtitle") }}
          </p>

          <div class="flex flex-col gap-2 text-left">
            <div
              v-for="(step, i) in gradingSteps"
              :key="step.key"
              class="flex items-center gap-2.5 rounded-leaf px-3 py-2.5 transition-colors"
              :class="gradingStepStateClass(i)"
            >
              <i
                :class="[
                  'text-lg shrink-0',
                  i < gradingStepIndex
                    ? 'pi pi-check-circle text-emerald-600'
                    : '',
                  i === gradingStepIndex
                    ? 'pi pi-spin pi-spinner text-primary'
                    : '',
                  i > gradingStepIndex ? 'pi pi-circle text-faint' : '',
                ]"
              ></i>
              <span
                class="text-sm"
                :class="
                  i <= gradingStepIndex ? 'font-medium text-ink' : 'text-faint'
                "
              >
                {{ t(step.labelKey) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════ Résultat ═══════════════ -->
      <div
        v-else-if="status === 'ended' && gradingResult"
        class="flex-1 overflow-y-auto"
      >
        <div class="max-w-2xl mx-auto px-4 py-8 space-y-5">
          <!-- En-tête -->
          <div
            class="bg-card border border-line rounded-card shadow-soft overflow-hidden"
          >
            <div
              :class="[
                'h-1.5',
                gradingResult.passed ? 'bg-emerald-500' : 'bg-amber-500',
              ]"
            ></div>
            <div class="px-6 py-5 flex items-center justify-between gap-4">
              <div>
                <p
                  class="text-xs font-semibold uppercase tracking-wider text-muted mb-1"
                >
                  {{ gradingResult.provider.toUpperCase() }} ·
                  {{ gradingResult.level.toUpperCase() }} · Sprechen
                </p>
                <h1 class="text-2xl font-bold text-ink">
                  {{
                    gradingResult.passed
                      ? t("sprechen_subject.passed")
                      : t("sprechen_subject.not_passed")
                  }}
                </h1>
                <p class="text-sm text-muted mt-1 tabular-nums">
                  {{ gradingResult.total_score }} /
                  {{ gradingResult.total_max_score }}
                  {{ t("sprechen_subject.points") }}
                </p>
              </div>
              <p
                :class="[
                  'text-3xl font-extrabold tabular-nums shrink-0',
                  gradingResult.passed ? 'text-emerald-600' : 'text-amber-600',
                ]"
              >
                {{ scorePercent }}%
              </p>
            </div>
          </div>

          <!-- Évolution -->
          <div
            v-if="gradingResult.score_delta_percent !== null"
            class="bg-card border border-line rounded-card px-5 py-4 flex items-center justify-between"
          >
            <div>
              <p class="text-xs text-muted mb-0.5">
                {{ t("sprechen_subject.score_delta_since_last") }}
              </p>
              <p class="text-lg font-semibold text-ink tabular-nums">
                {{ Math.round(gradingResult.previous_score_percent!) }}%
              </p>
            </div>
            <span
              class="flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold tabular-nums"
              :class="
                gradingResult.score_delta_percent >= 0
                  ? 'bg-emerald-500/10 text-emerald-700'
                  : 'bg-amber-500/10 text-amber-700'
              "
            >
              <i
                :class="
                  gradingResult.score_delta_percent >= 0
                    ? 'pi pi-arrow-up'
                    : 'pi pi-arrow-down'
                "
              ></i>
              {{ gradingResult.score_delta_percent >= 0 ? "+" : ""
              }}{{ Math.round(gradingResult.score_delta_percent) }}%
            </span>
          </div>

          <!-- Détail par Teil -->
          <div class="bg-card border border-line rounded-card overflow-hidden">
            <div class="px-5 py-4 border-b border-line">
              <h2 class="font-semibold text-ink text-sm">
                {{ t("sprechen_subject.detail_by_teil") }}
              </h2>
            </div>
            <div class="divide-y divide-line">
              <div
                v-for="teil in gradingResult.teile"
                :key="teil.teil_number"
                class="px-5 py-4 space-y-3"
              >
                <div class="flex items-center justify-between gap-3">
                  <span class="text-sm font-semibold text-ink"
                    >Teil {{ teil.teil_number }} · {{ teil.teil_name }}</span
                  >
                  <span
                    class="text-xs font-semibold text-muted tabular-nums shrink-0"
                  >
                    {{ teil.teil_score }} / {{ teil.teil_max_score }}
                  </span>
                </div>

                <div
                  v-for="c in teil.criteria"
                  :key="c.criterion_name"
                  class="rounded-leaf bg-card-2 border border-line p-3.5"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-ink">{{
                      c.criterion_name
                    }}</span>
                    <span
                      class="text-xs font-semibold tabular-nums"
                      :class="
                        c.max_score && c.score / c.max_score >= 0.75
                          ? 'text-emerald-600'
                          : 'text-amber-600'
                      "
                    >
                      {{ c.score }} / {{ c.max_score }}
                    </span>
                  </div>

                  <div
                    v-if="c.issue"
                    class="flex gap-2 rounded-leaf bg-amber-500/10 px-3 py-2 mb-2"
                  >
                    <i
                      class="pi pi-exclamation-circle text-amber-600 text-xs mt-0.5 shrink-0"
                    ></i>
                    <p class="text-xs text-ink leading-relaxed">
                      <span class="font-semibold"
                        >{{
                          t("sprechen_subject.criterion_issue_label")
                        }}
                        :</span
                      >
                      {{ c.issue }}
                    </p>
                  </div>

                  <div
                    v-if="c.model_phrase"
                    class="flex gap-2 rounded-leaf bg-primary/10 px-3 py-2 mb-2"
                  >
                    <i
                      class="pi pi-comment text-primary text-xs mt-0.5 shrink-0"
                    ></i>
                    <p class="text-xs text-ink leading-relaxed italic">
                      <span class="font-semibold not-italic"
                        >{{
                          t("sprechen_subject.criterion_model_phrase_label")
                        }}
                        :</span
                      >
                      „{{ c.model_phrase }}“
                    </p>
                  </div>

                  <div v-if="c.tip" class="flex gap-2 px-1">
                    <i
                      class="pi pi-lightbulb text-faint text-xs mt-0.5 shrink-0"
                    ></i>
                    <p class="text-xs text-muted leading-relaxed">
                      <span class="font-semibold"
                        >{{ t("sprechen_subject.criterion_tip_label") }} :</span
                      >
                      {{ c.tip }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Points forts / à améliorer -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-if="gradingResult.strengths.length">
              <p
                class="text-xs font-semibold text-emerald-600 uppercase tracking-wide mb-2 flex items-center gap-1.5"
              >
                <i class="pi pi-check-circle" />{{
                  t("sprechen_subject.strengths")
                }}
              </p>
              <ul class="space-y-1.5">
                <li
                  v-for="(s, i) in gradingResult.strengths"
                  :key="i"
                  class="flex items-start gap-2 text-sm text-ink bg-emerald-500/10 rounded-leaf px-3 py-2"
                >
                  <i
                    class="pi pi-check text-emerald-600 mt-0.5 shrink-0 text-xs"
                  /><span>{{ s }}</span>
                </li>
              </ul>
            </div>
            <div v-if="gradingResult.improvement_areas.length">
              <p
                class="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-2 flex items-center gap-1.5"
              >
                <i class="pi pi-exclamation-circle" />{{
                  t("sprechen_subject.to_improve")
                }}
              </p>
              <ul class="space-y-1.5">
                <li
                  v-for="(a, i) in gradingResult.improvement_areas"
                  :key="i"
                  class="flex items-start gap-2 text-sm text-ink bg-amber-500/10 rounded-leaf px-3 py-2"
                >
                  <i
                    class="pi pi-arrow-right text-amber-600 mt-0.5 shrink-0 text-xs"
                  /><span>{{ a }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-3 pb-8">
            <Button
              :label="t('sprechen_subject.redo')"
              icon="pi pi-refresh"
              outlined
              severity="secondary"
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
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useSprechenSession } from "~/composables/useSprechenSession";
import { createBrowserAudioIO } from "~/composables/audioIO";
import AvatarExaminer from "~/components/sprechen/AvatarExaminer.vue";
import AvatarStudent from "~/components/sprechen/AvatarStudent.vue";
import ThemeChoicePanel from "~/components/sprechen/ThemeChoicePanel.vue";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const route = useRoute();
const localePath = useLocalePath();
const runtimeConfig = useRuntimeConfig();

const subjectId = route.params.subjectId as string;
const wsBaseUrl = runtimeConfig.public.sprechenWsBaseUrl as string;
const audioIO = createBrowserAudioIO();

const {
  status,
  totalTeile,
  currentTeil,
  preparationInfo,
  micState,
  transcript,
  gradingResult,
  errorMessage,
  connect,
  sendReadyToStart,
  abandonSession,
  disconnect,
} = useSprechenSession({ subjectId, wsBaseUrl, audioIO });

const isCallTheme = computed(
  () =>
    ["idle", "connecting", "preparing", "active", "error"].includes(
      status.value,
    ) ||
    (status.value === "ended" && !gradingResult.value),
);

const headerTeilName = computed(
  () => currentTeil.value?.teil_name ?? preparationInfo.value?.teil_name ?? "",
);
const headerTeilNumber = computed(
  () =>
    currentTeil.value?.teil_number ??
    preparationInfo.value?.teil_number ??
    null,
);

const micLabel = computed(() => {
  if (micState.value === "agent_speaking")
    return t("sprechen_subject.examiner_speaking");
  if (micState.value === "student_turn") return t("sprechen_subject.your_turn");
  return "";
});

const groupedTranscript = computed(() => {
  const groups: { speaker: "student" | "agent"; text: string }[] = [];
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

// Seuil d'alerte visuelle (rien n'est coupé côté backend)
const TIMER_ALERT_THRESHOLD_SECONDS = 30;

const formatClock = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
};

// ── Préparation : temps écoulé (affichage principal, sans limite)
// + repère du temps officiel (preparation_minutes), jamais imposé ──
const prepSecondsElapsed = ref(0);
const prepSecondsLeft = ref(0);
let prepIntervalId: ReturnType<typeof setInterval> | null = null;

const officialPrepSeconds = computed(
  () => (preparationInfo.value?.preparation_minutes ?? 0) * 60,
);

watch(preparationInfo, (info) => {
  if (prepIntervalId) clearInterval(prepIntervalId);
  prepIntervalId = null;
  if (!info) return;
  prepSecondsElapsed.value = 0;
  prepSecondsLeft.value = (info.preparation_minutes ?? 0) * 60;
  prepIntervalId = setInterval(() => {
    prepSecondsElapsed.value += 1;
    if (prepSecondsLeft.value > 0) prepSecondsLeft.value -= 1;
  }, 1000);
});

const prepElapsedLabel = computed(() => formatClock(prepSecondsElapsed.value));
const prepCountdownLabel = computed(() => formatClock(prepSecondsLeft.value));
const prepTimerIsAlert = computed(
  () =>
    prepSecondsLeft.value > 0 &&
    prepSecondsLeft.value <= TIMER_ALERT_THRESHOLD_SECONDS,
);

// ── Compte à rebours du Teil actif (alerte seulement : le backend
// enchaîne lui-même sur le Teil suivant) ──
const teilSecondsLeft = ref(0);
let teilIntervalId: ReturnType<typeof setInterval> | null = null;

watch(currentTeil, (teil) => {
  if (teilIntervalId) clearInterval(teilIntervalId);
  teilIntervalId = null;
  if (!teil) return;
  teilSecondsLeft.value = (teil.duration_minutes || 0) * 60;
  teilIntervalId = setInterval(() => {
    if (teilSecondsLeft.value > 0) teilSecondsLeft.value -= 1;
  }, 1000);
});

const teilCountdownLabel = computed(() => formatClock(teilSecondsLeft.value));
const teilTimerIsAlert = computed(
  () =>
    teilSecondsLeft.value > 0 &&
    teilSecondsLeft.value <= TIMER_ALERT_THRESHOLD_SECONDS,
);

// ── Étapes décoratives pendant la notation ──
const gradingSteps = [
  { key: "listening", labelKey: "sprechen_subject.grading_step_listening" },
  { key: "vocab", labelKey: "sprechen_subject.grading_step_vocab" },
  {
    key: "pronunciation",
    labelKey: "sprechen_subject.grading_step_pronunciation",
  },
  { key: "tips", labelKey: "sprechen_subject.grading_step_tips" },
];
const gradingStepIndex = ref(0);
let gradingIntervalId: ReturnType<typeof setInterval> | null = null;

watch(status, (value) => {
  if (value === "ended" && !gradingResult.value) {
    gradingStepIndex.value = 0;
    gradingIntervalId = setInterval(() => {
      if (gradingStepIndex.value < gradingSteps.length - 1)
        gradingStepIndex.value += 1;
    }, 2500);
  } else if (gradingIntervalId) {
    clearInterval(gradingIntervalId);
    gradingIntervalId = null;
  }

  // currentTeil n'est pas remis à null en fin de session : on arrête ici
  if (value !== "active" && teilIntervalId) {
    clearInterval(teilIntervalId);
    teilIntervalId = null;
  }
  if (value !== "preparing" && prepIntervalId) {
    clearInterval(prepIntervalId);
    prepIntervalId = null;
  }
});

function gradingStepStateClass(i: number) {
  if (i < gradingStepIndex.value) return "bg-emerald-500/10";
  if (i === gradingStepIndex.value) return "bg-primary/10";
  return "";
}

const scorePercent = computed(() => {
  if (!gradingResult.value || !gradingResult.value.total_max_score) return 0;
  return Math.round(
    (gradingResult.value.total_score / gradingResult.value.total_max_score) *
      100,
  );
});

// ── Navigation ──
const goToList = () => navigateTo(localePath("/dashboard/sprechen"));

function confirmLeave() {
  if (
    status.value === "active" &&
    !window.confirm(t("sprechen_subject.confirm_leave"))
  )
    return;
  abandonSession();
  goToList();
}

const redo = () => {
  disconnect();
  connect();
};

onMounted(() => connect());
onUnmounted(() => {
  disconnect();
  if (prepIntervalId) clearInterval(prepIntervalId);
  if (teilIntervalId) clearInterval(teilIntervalId);
  if (gradingIntervalId) clearInterval(gradingIntervalId);
});

useHead({ title: t("sprechen_subject.page_title") });
</script>
