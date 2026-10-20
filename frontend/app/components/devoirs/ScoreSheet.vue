<!-- components/devoirs/ScoreSheet.vue : relevé de points d'un devoir -->
<template>
  <div
    class="relative overflow-hidden rounded-card border border-line bg-card p-6 sm:p-8"
  >
    <div class="flag-stripe absolute inset-x-0 top-0 h-1" aria-hidden="true" />

    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-faint">
      {{ t("student_assignments.sheet.kicker") }}
    </p>
    <h2 class="mt-1 font-heading text-2xl font-bold text-ink">{{ title }}</h2>
    <p class="text-sm text-muted">{{ subtitle }}</p>

    <!-- Épreuve écrite -->
    <div class="mt-6">
      <div
        class="flex items-baseline justify-between border-b border-line pb-2"
      >
        <p class="text-sm font-bold text-ink">
          {{ t("student_assignments.sheet.written") }}
        </p>
        <p class="text-sm font-bold tabular-nums text-ink">
          {{ fmt(sheet.total_points) }}
          <span class="font-normal text-muted"
            >/ {{ fmt(sheet.total_max) }}</span
          >
        </p>
      </div>

      <ul class="mt-2 space-y-2">
        <li
          v-for="m in sheet.modules"
          :key="m.name"
          class="flex items-baseline gap-2 text-sm"
        >
          <span class="text-muted">•</span>
          <span class="text-ink">{{ m.name }}</span>
          <span
            class="mx-1 flex-1 border-b border-dotted border-line"
            aria-hidden="true"
          />
          <span v-if="m.points !== null" class="tabular-nums text-ink">
            {{ fmt(m.points) }}
            <span class="text-muted">/ {{ fmt(m.max_score) }}</span>
          </span>
          <span
            v-else
            class="inline-flex items-center gap-1 text-xs font-medium text-amber-600"
          >
            <i class="pi pi-hourglass text-[10px]" />
            {{ t("student_assignments.sheet.pending") }}
          </span>
        </li>
      </ul>
    </div>

    <!-- Résultat -->
    <div
      class="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-leaf bg-card-2 px-4 py-3"
    >
      <p class="text-sm font-semibold text-ink">
        {{ t("student_assignments.sheet.result") }}
      </p>
      <span
        v-if="sheet.is_final && sheet.passed !== null"
        class="rounded-full px-3 py-1 text-xs font-bold"
        :class="
          sheet.passed
            ? 'bg-emerald-500/10 text-emerald-600'
            : 'bg-red-500/10 text-red-600'
        "
      >
        {{
          sheet.passed
            ? t("student_assignments.sheet.passed")
            : t("student_assignments.sheet.failed")
        }}
      </span>
      <span
        v-else
        class="rounded-full bg-amber-500/15 px-3 py-1 text-xs font-bold text-amber-600"
      >
        {{ t("student_assignments.sheet.provisional") }}
      </span>
    </div>

    <p v-if="!sheet.is_final" class="mt-3 text-xs text-muted">
      {{ t("student_assignments.sheet.provisional_hint") }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { StudentScoreSheet } from "#shared/api";

defineProps<{
  sheet: StudentScoreSheet;
  title: string;
  subtitle: string;
}>();

const { t, locale } = useI18n();

const fmt = (n: number) =>
  new Intl.NumberFormat(locale.value, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(n);
</script>
