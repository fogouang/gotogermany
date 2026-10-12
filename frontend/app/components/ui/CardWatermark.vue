<!-- components/ui/CardWatermark.vue -->
<!--
  Filigrane décoratif en fond de carte, dans le style du PageHeader.
  La carte parente doit avoir : relative isolate overflow-hidden

  variant   : "outline" (contour, comme le header) | "solid" (plein, très pâle)
  placement : "fill"   texte centré en très grand sur toute la carte
              "center" texte à droite, centré verticalement
              "bottom" texte en bas à droite
  glow      : "corner" halo dans le coin | "full" dégradé sur toute la carte | "none"
-->
<template>
  <div aria-hidden="true" class="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
    <!-- Dégradé sur toute la carte -->
    <div v-if="glow === 'full'" class="absolute inset-0 bg-linear-to-br" :class="fullClass" />

    <!-- Halo dans le coin -->
    <div
      v-else-if="glow === 'corner'"
      class="absolute -right-12 -top-16 size-48 rounded-full blur-3xl"
      :class="cornerClass"
    />

    <!-- Texte géant (ex. niveau B1) -->
    <span
      v-if="text"
      class="absolute select-none whitespace-nowrap font-heading font-extrabold leading-none tracking-tighter"
      :class="[placementClass, variantClass]"
    >
      {{ text }}
    </span>

    <!-- Sinon, icône géante -->
    <i
      v-else-if="icon"
      :class="[icon, placementClass]"
      class="absolute text-ink opacity-[0.06] dark:opacity-10"
    />
  </div>
</template>

<script setup lang="ts">
type Tone = "primary" | "emerald" | "sky" | "amber" | "neutral";
type Placement = "fill" | "center" | "bottom";
type Glow = "corner" | "full" | "none";
type Variant = "outline" | "solid";

const props = withDefaults(
  defineProps<{
    text?: string | null;
    icon?: string;
    tone?: Tone;
    placement?: Placement;
    glow?: Glow;
    variant?: Variant;
  }>(),
  {
    text: null,
    icon: undefined,
    tone: "primary",
    placement: "bottom",
    glow: "corner",
    variant: "outline",
  },
);

// Classes écrites en entier pour que Tailwind les détecte
const cornerClass = computed(
  () =>
    ({
      primary: "bg-primary/15",
      emerald: "bg-emerald-500/15",
      sky: "bg-sky-500/15",
      amber: "bg-amber-500/15",
      neutral: "bg-ink/5",
    })[props.tone],
);

const fullClass = computed(
  () =>
    ({
      primary: "from-primary/12 via-primary/[0.04] to-transparent",
      emerald: "from-emerald-500/12 via-emerald-500/[0.04] to-transparent",
      sky: "from-sky-500/12 via-sky-500/[0.04] to-transparent",
      amber: "from-amber-500/12 via-amber-500/[0.04] to-transparent",
      neutral: "from-ink/[0.05] via-ink/[0.02] to-transparent",
    })[props.tone],
);

// Même rendu que le watermark du PageHeader
const variantClass = computed(() =>
  props.variant === "outline"
    ? "text-transparent opacity-15 [-webkit-text-stroke:1.5px_var(--color-ink)] dark:opacity-20"
    : "text-ink opacity-[0.06] dark:opacity-10",
);

const placementClass = computed(
  () =>
    ({
      fill: "left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[9rem] sm:text-[11rem]",
      center: "right-4 top-[42%] -translate-y-1/2 text-[6rem]",
      bottom: "-bottom-6 -right-1 text-[7.5rem]",
    })[props.placement],
);
</script>