<!-- components/start-deutsch/MatchingWithDistractorQuestion.vue -->
<!--
  Nécessite teil.shared_content.ads = [{label, url, text}, ...] : le pool
  d'annonces est commun à toutes les questions du Teil.
-->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <p class="text-base font-semibold text-ink">{{ question.content.profile }}</p>

    <div class="mt-4 grid gap-2 sm:grid-cols-2">
      <button
        v-for="ad in sharedAds"
        :key="ad.label"
        type="button"
        class="min-w-0 rounded-leaf border p-3 text-left text-sm transition-colors"
        :class="
          modelValue === ad.label
            ? 'border-primary bg-primary/10'
            : 'border-line bg-card hover:border-primary/30'
        "
        @click="$emit('update:modelValue', ad.label)"
      >
        <span class="mr-1.5 font-semibold uppercase text-faint">{{ ad.label }})</span>
        <span class="break-all font-mono text-xs text-faint">{{ ad.url }}</span>
        <p class="mt-1 text-ink">{{ ad.text }}</p>
      </button>

      <button
        type="button"
        class="flex items-center justify-center gap-2 rounded-leaf border border-dashed p-3 text-sm font-semibold transition-colors"
        :class="
          modelValue === 'X'
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-line text-muted hover:border-primary/30'
        "
        @click="$emit('update:modelValue', 'X')"
      >
        <i class="pi pi-ban" /> {{ t("start_deutsch.question_ui.none_solution") }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface SharedAd {
  label: string;
  url: string;
  text: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { profile: string };
  };
  teil: {
    shared_content?: { ads?: SharedAd[] } | null;
  };
  modelValue: string | null;
}

const props = defineProps<Props>();
defineEmits<{ "update:modelValue": [value: string] }>();

const { t } = useI18n();

const sharedAds = computed(() => props.teil.shared_content?.ads ?? []);
</script>