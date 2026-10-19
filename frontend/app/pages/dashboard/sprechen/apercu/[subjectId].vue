<script setup lang="ts">
import ThemeChoicePanel from "~/components/sprechen/ThemeChoicePanel.vue";

definePageMeta({ layout: "dashboard" });

interface PreviewTeil {
  teil_number: number;
  name: string;
  format_type: string;
  instructions: string;
  duration_minutes: number;
  max_score: number | null;
  content_points: string[];
  themes: Record<string, any> | null;
  scenario: string | null;
  stimulus_people: { name: string; opinion: string }[] | null;
  stimulus_text: string | null;
}

interface PreviewResponse {
  subject_id: string;
  provider: string;
  level: string;
  total_minutes: number;
  teile: PreviewTeil[];
  credit_cost: number;
  credits_available: number;
  can_start: boolean;
}

const { t } = useI18n();
const route = useRoute();
const localePath = useLocalePath();
const runtimeConfig = useRuntimeConfig();
const { info } = useProviders();

const subjectId = route.params.subjectId as string;
const tokenCookie = useCookie("access_token");

const preview = ref<PreviewResponse | null>(null);
const loading = ref(true);
const loadError = ref(false);

async function load() {
  loading.value = true;
  loadError.value = false;
  try {
    const base = runtimeConfig.public.apiBaseUrl || "http://localhost:8001";
    preview.value = await $fetch<PreviewResponse>(
      `${base}/api/v1/sprechen-simulator/subjects/${subjectId}/preview`,
      {
        headers: tokenCookie.value
          ? { Authorization: `Bearer ${tokenCookie.value}` }
          : {},
      },
    );
  } catch {
    loadError.value = true;
  } finally {
    loading.value = false;
  }
}

const totalPoints = computed(
  () =>
    preview.value?.teile.reduce(
      (sum, teil) => sum + (teil.max_score ?? 0),
      0,
    ) ?? 0,
);

const peopleLabel = (teil: PreviewTeil) =>
  teil.format_type === "oral_thema"
    ? t("sprechen_preview.your_text")
    : t("sprechen_subject.stimulus_people_label");

const goToList = () => navigateTo(localePath("/dashboard/sprechen"));
const startOral = () =>
  navigateTo(localePath(`/dashboard/sprechen/${subjectId}`));

onMounted(load);

useHead({ title: t("sprechen_preview.page_title") });
</script>

<template>
  <div class="space-y-6 pb-10">
    <button
      type="button"
      class="inline-flex items-center gap-2 text-sm font-medium text-muted transition-colors hover:text-ink"
      @click="goToList"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("sprechen_preview.back") }}
    </button>

    <!-- Chargement -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
    </div>

    <!-- Erreur -->
    <div
      v-else-if="loadError || !preview"
      class="rounded-card border border-line bg-card p-8 text-center"
    >
      <i class="pi pi-exclamation-circle mb-3 block text-3xl text-faint" />
      <p class="mb-4 font-medium text-ink">
        {{ t("sprechen_preview.load_error") }}
      </p>
      <Button
        :label="t('sprechen_preview.back')"
        outlined
        severity="secondary"
        @click="goToList"
      />
    </div>

    <template v-else>
      <!-- En-tête -->
      <div class="rounded-card border border-line bg-card p-5 shadow-soft">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex items-start gap-3">
            <span
              class="flex size-11 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary"
            >
              <i class="pi pi-microphone" />
            </span>
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-wider text-faint"
              >
                {{ t("sprechen_preview.page_title") }}
              </p>
              <div class="mt-1 flex flex-wrap items-center gap-1.5">
                <span
                  :class="[
                    'rounded-full px-2 py-0.5 text-[11px] font-semibold',
                    info(preview.provider).badge,
                  ]"
                >
                  {{ info(preview.provider).name }}
                </span>
                <span
                  class="rounded-full border border-line bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-ink"
                >
                  {{ preview.level }}
                </span>
              </div>
              <p class="mt-2 text-sm text-muted">
                {{ preview.teile.length }}
                {{
                  preview.teile.length > 1
                    ? t("sprechen.teile_plural")
                    : t("sprechen.teil")
                }}
                · {{ preview.total_minutes }} min
                <template v-if="totalPoints">
                  · {{ totalPoints }}
                  {{ t("sprechen_subject.points") }}</template
                >
              </p>
            </div>
          </div>

          <div class="flex flex-col items-end gap-2">
            <!-- Solde toujours visible, même sans crédit suffisant -->
            <span
              class="inline-flex items-center gap-1.5 rounded-full border border-line bg-card-2 px-3 py-1 text-xs font-semibold text-ink"
            >
              <i class="pi pi-wallet text-[0.7rem] text-primary" />
              {{
                t("sprechen_preview.balance", {
                  credits: preview.credits_available,
                })
              }}
            </span>
            <Button
              v-if="preview.can_start"
              :label="t('sprechen_preview.start')"
              icon="pi pi-play"
              @click="startOral"
            />
            <span class="text-xs text-faint">
              {{
                t("sprechen_preview.cost_only", { cost: preview.credit_cost })
              }}
            </span>
          </div>
        </div>

        <!-- Pas assez de crédits : on lit quand même -->
        <div
          v-if="!preview.can_start"
          class="mt-4 flex gap-3 rounded-leaf border border-primary/25 bg-primary/10 px-4 py-3"
        >
          <i class="pi pi-lock mt-0.5 shrink-0 text-primary" />
          <div>
            <p class="text-sm font-semibold text-ink">
              {{
                t("sprechen_preview.no_credit_title", {
                  cost: preview.credit_cost,
                })
              }}
            </p>
            <p class="mt-0.5 text-sm text-muted">
              {{ t("sprechen_preview.no_credit_text") }}
            </p>
          </div>
        </div>
      </div>

      <!-- Teile -->
      <article
        v-for="teil in preview.teile"
        :key="teil.teil_number"
        class="space-y-4 rounded-card border border-line bg-card p-5"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary"
            >
              {{ teil.teil_number }}
            </span>
            <h2 class="font-semibold text-ink">{{ teil.name }}</h2>
          </div>
          <span class="shrink-0 text-xs font-semibold tabular-nums text-muted">
            {{ teil.duration_minutes }} min
            <template v-if="teil.max_score">
              · {{ teil.max_score }}
              {{ t("sprechen_subject.points") }}</template
            >
          </span>
        </div>

        <p class="text-sm leading-relaxed text-muted">
          {{ teil.instructions }}
        </p>

        <div
          v-if="teil.scenario"
          class="rounded-leaf border border-primary/20 bg-primary/10 px-4 py-3"
        >
          <p
            class="mb-1 text-[11px] font-semibold uppercase tracking-wide text-primary"
          >
            {{ t("sprechen_subject.scenario_label") }}
          </p>
          <p class="text-sm leading-relaxed text-ink">{{ teil.scenario }}</p>
        </div>

               <div
          v-if="teil.stimulus_people?.length"
          class="overflow-hidden rounded-card border border-line bg-card-2"
        >
          <div class="border-b border-line px-4 py-2">
            <p class="text-[11px] font-semibold uppercase tracking-wide text-faint">
              {{ t("sprechen_subject.stimulus_people_label") }}
            </p>
          </div>
          <div class="divide-y divide-line">
            <div
              v-for="(person, i) in teil.stimulus_people"
              :key="person.name"
              class="px-4 py-4"
            >
              <p
                v-if="teil.format_type === 'oral_thema'"
                class="mb-1.5 text-[11px] font-semibold uppercase tracking-wide"
                :class="i === 0 ? 'text-primary' : 'text-faint'"
              >
                {{ i === 0 ? t("sprechen_preview.your_text") : t("sprechen_preview.partner_text") }}
              </p>
              <p class="text-sm font-semibold text-ink">{{ person.name }}</p>
              <p class="mt-1.5 text-base italic leading-relaxed text-ink">
                „{{ person.opinion }}“
              </p>
            </div>
          </div>
        </div>

        <div
          v-if="teil.stimulus_text"
          class="overflow-hidden rounded-card border border-line bg-card-2"
        >
          <div class="border-b border-line px-4 py-2">
            <p
              class="text-[11px] font-semibold uppercase tracking-wide text-faint"
            >
              {{ t("sprechen_subject.reading_text_label") }}
            </p>
          </div>
          <p
            class="whitespace-pre-line px-4 py-3 text-sm leading-relaxed text-ink"
          >
            {{ teil.stimulus_text }}
          </p>
        </div>

        <ThemeChoicePanel v-if="teil.themes" :themes="teil.themes" />

        <div
          v-if="teil.content_points.length"
          class="overflow-hidden rounded-card border border-line bg-card-2"
        >
          <div class="border-b border-line px-4 py-2">
            <p
              class="text-[11px] font-semibold uppercase tracking-wide text-faint"
            >
              {{ t("sprechen_subject.points_to_cover") }}
            </p>
          </div>
          <ul class="space-y-1.5 px-4 py-3">
            <li
              v-for="point in teil.content_points"
              :key="point"
              class="flex gap-2 text-sm text-ink"
            >
              <span class="mt-2 size-1.5 shrink-0 rounded-full bg-primary" />
              <span>{{ point }}</span>
            </li>
          </ul>
        </div>
      </article>

      <!-- Rappel de l'action en bas -->
      <div v-if="preview.can_start" class="flex justify-end">
        <Button
          :label="t('sprechen_preview.start')"
          icon="pi pi-play"
          @click="startOral"
        />
      </div>
    </template>
  </div>
</template>
