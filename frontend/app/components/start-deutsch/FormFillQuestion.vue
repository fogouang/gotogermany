<!-- components/start-deutsch/FormFillQuestion.vue -->
<!--
  content = { prompt_text: string, fields: [{ number, label }, ...] }
  user_answer = { "1": "...", "2": "...", ... } — clé = field.number en string
-->
<template>
  <div class="question-container">
    <p class="whitespace-pre-line text-sm leading-relaxed text-ink-secondary">
      {{ question.content.prompt_text }}
    </p>

    <div class="mt-5 space-y-3 rounded-lg border border-line bg-hover/40 p-4">
      <div
        v-for="field in question.content.fields"
        :key="field.number"
        class="grid grid-cols-[1fr_2fr] items-center gap-3 sm:grid-cols-[160px_1fr]"
      >
        <label
          :for="`field-${question.id}-${field.number}`"
          class="text-sm font-semibold text-ink"
        >
          {{ field.label }}
        </label>
        <InputText
          :id="`field-${question.id}-${field.number}`"
          :model-value="localAnswers[field.number] ?? ''"
          size="small"
          @update:model-value="onFieldChange(field.number, $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

interface FormField {
  number: number | string;
  label: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { prompt_text: string; fields: FormField[] };
  };
  modelValue: Record<string, string> | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  "update:modelValue": [value: Record<string, string>];
}>();

const localAnswers = reactive<Record<string, string>>({
  ...(props.modelValue ?? {}),
});

watch(
  () => props.modelValue,
  (val) => {
    Object.assign(localAnswers, val ?? {});
  },
);

function onFieldChange(
  fieldNumber: number | string,
  value: string | undefined,
) {
  localAnswers[String(fieldNumber)] = value ?? "";
  emit("update:modelValue", { ...localAnswers });
}
</script>
