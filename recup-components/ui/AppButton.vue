<script setup lang="ts">
type Variant = "primary" | "secondary" | "ghost" | "accent" | "gradient" | "danger";

const props = withDefaults(
  defineProps<{
    label?: string;
    icon?: string;
    iconPos?: "left" | "right";
    variant?: Variant;
    size?: "small" | "large";
    loading?: boolean;
    disabled?: boolean;
    block?: boolean;
    type?: "button" | "submit" | "reset";
  }>(),
  {
    variant: "primary",
    iconPos: "left",
    type: "button",
  },
);

// Ce que PrimeVue sait déjà faire : on passe par ses props
const primeProps = computed(() => {
  switch (props.variant) {
    case "secondary":
      return { severity: "secondary", outlined: true };
    case "ghost":
      return { severity: "secondary", text: true };
    case "danger":
      return { severity: "danger" };
    default:
      return {};
  }
});

// Ce que PrimeVue ne connaît pas : on ajoute des classes Tailwind
// gradient : anthracite + texte blanc en clair, or + texte anthracite en sombre
const variantClass = computed(() => {
  switch (props.variant) {
    case "accent":
      return "bg-accent-400 border-accent-400 text-accent-950 hover:bg-accent-500 hover:border-accent-500 hover:text-accent-950";
    case "gradient":
      return "brand-gradient border-transparent text-primary-contrast shadow-brand hover:brightness-110 hover:border-transparent hover:text-primary-contrast";
    default:
      return "";
  }
});
</script>

<template>
  <Button
    v-bind="primeProps"
    :label="label"
    :icon="icon"
    :icon-pos="iconPos"
    :size="size"
    :loading="loading"
    :disabled="disabled"
    :type="type"
    :class="[variantClass, { 'w-full': block }]"
  />
</template>