<template>
  <div class="bg-white/8 border border-white/10 rounded-2xl overflow-hidden">
    <div class="bg-white/5 border-b border-white/10 px-4 py-2">
      <p class="text-[11px] font-semibold text-white/50 uppercase tracking-wide">
        {{ t("sprechen_subject.choose_a_topic") }}
      </p>
    </div>
    <div class="divide-y divide-white/10">
      <div v-for="(theme, key) in themes" :key="key" class="px-4 py-3">
        <p class="text-sm font-medium text-white/90 mb-1.5">
          {{ theme.title || theme.titel }}
        </p>
        <p v-if="theme.accroche" class="text-xs text-white/50 italic mb-1.5">
          {{ theme.accroche }}
        </p>
        <ul v-if="theme.leitpunkte || theme.punkte" class="space-y-1">
          <li
            v-for="point in (theme.leitpunkte || theme.punkte)"
            :key="point"
            class="flex gap-2 text-xs text-white/70"
          >
            <span class="font-bold text-teal-300/70 shrink-0">–</span>
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