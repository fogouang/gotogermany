<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    to: string;
    label: string;
    icon?: string;
    iconPos?: "left" | "right";
    external?: boolean;
    variant?: "gradient" | "light" | "outline" | "accent";
    size?: "md" | "lg";
  }>(),
  {
    iconPos: "right",
    external: false,
    variant: "gradient",
    size: "lg",
  },
);

const variantClass = computed(() => {
  switch (props.variant) {
    case "light":
      // Posé sur fond sombre (hero) : reste blanc dans les deux modes
      return "bg-white text-zinc-900 shadow-lift hover:bg-zinc-100";
    case "outline":
      return "border border-line bg-card text-ink shadow-soft hover:border-primary hover:text-primary";
    case "accent":
      return "bg-accent-400 text-accent-950 shadow-lift hover:bg-accent-500";
    default:
      return "brand-gradient text-primary-contrast shadow-brand hover:brightness-110 hover:shadow-lift";
  }
});

const sizeClass = computed(() =>
  props.size === "md" ? "h-11 px-5 text-sm" : "h-14 px-7 text-base",
);
</script>

<template>
  <NuxtLink
    :to="to"
    :external="external"
    class="inline-flex select-none items-center justify-center gap-2 whitespace-nowrap font-semibold rounded-leaf
           transition-all duration-200 ease-spring active:scale-[0.97]
           focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent-500"
    :class="[variantClass, sizeClass]"
  >
    <i v-if="icon && iconPos === 'left'" :class="icon" />
    <span>{{ label }}</span>
    <i v-if="icon && iconPos === 'right'" :class="icon" />
  </NuxtLink>
</template>