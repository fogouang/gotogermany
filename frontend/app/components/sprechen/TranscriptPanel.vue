<script setup lang="ts">
const props = defineProps<{
  lines: { speaker: "student" | "agent"; text: string }[];
}>();

const { t } = useI18n();

const scroller = ref<HTMLDivElement | null>(null);

// Défile automatiquement vers le dernier message
watch(
  () => props.lines.map((l) => l.text.length).join(","),
  async () => {
    await nextTick();
    scroller.value?.scrollTo({
      top: scroller.value.scrollHeight,
      behavior: "smooth",
    });
  },
);
</script>

<template>
  <div
    class="flex min-h-0 flex-col overflow-hidden rounded-card border border-line bg-card/80 shadow-soft backdrop-blur"
  >
    <div class="flex items-center gap-2 border-b border-line px-4 py-3">
      <i class="pi pi-align-left text-xs text-faint" />
      <p class="text-xs font-bold uppercase tracking-wider text-faint">
        {{ t("sprechen_subject.call.transcript") }}
      </p>
    </div>

    <div ref="scroller" class="flex-1 space-y-3 overflow-y-auto p-4">
      <p v-if="!lines.length" class="pt-6 text-center text-xs text-faint">
        {{ t("sprechen_subject.call.transcript_empty") }}
      </p>

      <div
        v-for="(line, i) in lines"
        :key="i"
        class="flex"
        :class="line.speaker === 'student' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[85%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed"
          :class="
            line.speaker === 'student'
              ? 'rounded-br-sm bg-primary text-primary-950 shadow-soft'
              : 'rounded-bl-sm border border-line bg-card-2 text-ink'
          "
        >
          {{ line.text }}
        </div>
      </div>
    </div>
  </div>
</template>