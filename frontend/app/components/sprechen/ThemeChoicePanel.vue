<template>
  <div class="overflow-hidden rounded-card border border-line bg-card-2">
    <div class="border-b border-line px-4 py-2">
      <p class="text-[11px] font-semibold uppercase tracking-wide text-faint">
        {{ t("sprechen_subject.choose_a_topic") }}
      </p>
    </div>
    <div class="divide-y divide-line">
      <div v-for="(theme, key) in themes" :key="key" class="px-4 py-3">
        <p class="mb-1.5 text-sm font-medium text-ink">
          {{ theme.title || theme.titel }}
        </p>
        <p v-if="theme.accroche" class="mb-1.5 text-xs italic text-muted">
          {{ theme.accroche }}
        </p>
        <ul v-if="theme.leitpunkte || theme.punkte" class="space-y-1">
          <li
            v-for="point in theme.leitpunkte || theme.punkte"
            :key="point"
            class="flex gap-2 text-xs text-muted"
          >
            <span class="shrink-0 font-bold text-primary">–</span>
            <span>{{ point }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ThemeOption } from "#shared/sprechenWebSocketTypes";

defineProps<{ themes: Record<string, ThemeOption> }>();
const { t } = useI18n();
</script>