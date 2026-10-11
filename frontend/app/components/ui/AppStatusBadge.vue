<script setup lang="ts">
type Tone = "success" | "warning" | "danger" | "info" | "brand" | "neutral";

const props = withDefaults(
  defineProps<{
    label: string;
    tone?: Tone;
    /** Icône PrimeIcons complète ; "none" pour ne rien afficher */
    icon?: string;
    size?: "sm" | "md";
  }>(),
  {
    tone: "neutral",
    size: "sm",
  },
);

const STYLES: Record<Tone, { classe: string; icone?: string }> = {
  success: {
    classe: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
    icone: "pi pi-check-circle",
  },
  warning: {
    classe: "bg-accent-500/15 text-accent-800 dark:text-accent-300",
    icone: "pi pi-clock",
  },
  danger: {
    classe: "bg-red-500/10 text-red-700 dark:text-red-400",
    icone: "pi pi-times-circle",
  },
  info: {
    classe: "bg-secondary-500/10 text-secondary-700 dark:text-secondary-300",
    icone: "pi pi-info-circle",
  },
  brand: {
    classe: "bg-primary-50 text-primary-700",
  },
  neutral: {
    classe: "bg-card-2 text-muted",
    icone: "pi pi-minus-circle",
  },
};

const style = computed(() => STYLES[props.tone]);

const iconeAffichee = computed(() => {
  if (props.icon === "none") return null;
  return props.icon ?? style.value.icone ?? null;
});
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full font-semibold"
    :class="[
      style.classe,
      size === 'md' ? 'px-3 py-1 text-sm' : 'px-2.5 py-0.5 text-xs',
    ]"
  >
    <i v-if="iconeAffichee" :class="[iconeAffichee, size === 'md' ? 'text-sm' : 'text-[11px]']" />
    {{ label }}
  </span>
</template>