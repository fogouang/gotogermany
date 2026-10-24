<template>
  <figure class="rounded-card border border-line bg-card-2 p-4">
    <figcaption class="mb-4">
      <p class="font-bold text-ink text-sm">{{ g.title }}</p>
      <p v-if="g.subtitle" class="text-xs text-muted mt-0.5">
        {{ g.subtitle }}
      </p>
      <p v-if="axisNote" class="text-xs text-muted mt-0.5">{{ axisNote }}</p>
    </figcaption>

    <!-- Légende (plusieurs séries) -->
    <div v-if="series.length > 1" class="flex flex-wrap gap-x-4 gap-y-1 mb-3">
      <span
        v-for="(s, si) in series"
        :key="s.name"
        class="flex items-center gap-1.5 text-xs text-ink"
      >
        <span :class="['w-3 h-3 rounded-sm', BG[si % BG.length]]"></span>
        {{ s.name }}
      </span>
    </div>

    <!-- Barres horizontales (une ou plusieurs séries) -->
    <div
      v-if="kind === 'bar_horizontal' || kind === 'bar_stacked'"
      class="space-y-2.5"
    >
      <div v-for="(label, li) in labels" :key="label">
        <p class="text-xs text-ink mb-1">{{ label }}</p>
        <div
          v-for="(s, si) in series"
          :key="`${label}-${s.name}`"
          class="flex items-center gap-2 mb-0.5"
        >
          <div class="flex-1 h-3.5 rounded-sm bg-card overflow-hidden">
            <div
              :class="['h-full rounded-sm', barColor(label, si)]"
              :style="{ width: pct(s.values[li]) }"
            ></div>
          </div>
          <span class="w-16 shrink-0 text-right text-xs tabular-nums text-ink">
            {{ fmt(s.values[li]) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Barres verticales -->
    <div v-else-if="kind === 'bar'" class="overflow-x-auto">
      <div class="flex items-end gap-3 h-48 min-w-max px-1">
        <div
          v-for="(label, li) in labels"
          :key="label"
          class="flex flex-col items-center justify-end h-full w-16"
        >
          <div class="flex items-end gap-0.5 h-full w-full justify-center">
            <div
              v-for="(s, si) in series"
              :key="`${label}-${s.name}`"
              class="flex flex-col items-center justify-end h-full flex-1"
            >
              <span class="text-[10px] tabular-nums text-ink mb-0.5">
                {{ fmt(s.values[li]) }}
              </span>
              <div
                :class="['w-full rounded-t-sm', barColor(label, si)]"
                :style="{ height: pct(s.values[li]) }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      <div class="flex gap-3 min-w-max px-1 mt-1.5">
        <p
          v-for="label in labels"
          :key="`l-${label}`"
          class="w-16 text-center text-[11px] leading-tight text-ink"
        >
          {{ label }}
        </p>
      </div>
    </div>

    <!-- Camembert -->
    <div
      v-else-if="kind === 'pie'"
      class="flex flex-col sm:flex-row items-center gap-4"
    >
      <svg viewBox="0 0 42 42" class="w-40 h-40 shrink-0 -rotate-90">
        <circle
          v-for="(seg, si) in pieSegments"
          :key="si"
          cx="21"
          cy="21"
          r="15.915"
          fill="none"
          stroke="currentColor"
          stroke-width="8"
          :class="TEXT[si % TEXT.length]"
          :stroke-dasharray="`${seg.size} ${100 - seg.size}`"
          :stroke-dashoffset="-seg.offset"
        />
      </svg>
      <ul class="space-y-1">
        <li
          v-for="(label, li) in labels"
          :key="label"
          class="flex items-center gap-2 text-xs text-ink"
        >
          <span
            :class="['w-3 h-3 rounded-sm shrink-0', BG[li % BG.length]]"
          ></span>
          <span class="flex-1">{{ label }}</span>
          <span class="tabular-nums font-semibold">{{
            fmt(series[0]?.values[li])
          }}</span>
        </li>
      </ul>
    </div>

    <!-- Frise chronologique -->
    <ol v-else-if="kind === 'timeline'" class="relative border-l-2 border-primary/30 ml-2 space-y-3">
      <li v-for="item in g.items || []" :key="item.label" class="pl-4 relative">
        <span
          class="absolute -left-[7px] top-1 w-3 h-3 rounded-full bg-primary"
        ></span>
        <p class="text-xs font-semibold text-primary">{{ item.label }}</p>
        <p class="text-sm text-ink">{{ item.text }}</p>
      </li>
    </ol>

    <p
      v-if="g.footnote || g.note || g.source"
      class="mt-3 text-[11px] text-muted space-x-2"
    >
      <span v-if="g.footnote">{{ g.footnote }}</span>
      <span v-if="g.note">{{ g.note }}</span>
      <span v-if="g.source">Quelle: {{ g.source }}</span>
    </p>
  </figure>
</template>

<script setup lang="ts">
type Series = { name: string; values: number[] };

const props = defineProps<{ grafik: Record<string, any> }>();

const g = computed(() => props.grafik || {});
const kind = computed(() => String(g.value.type || "bar_horizontal"));
const labels = computed<string[]>(() => g.value.labels || []);
const series = computed<Series[]>(() => g.value.series || []);

// Couleurs des séries (Tailwind v4, palette du projet en premier)
const BG = [
  "bg-primary",
  "bg-amber-500",
  "bg-emerald-500",
  "bg-sky-500",
  "bg-rose-500",
  "bg-violet-500",
];
const TEXT = [
  "text-primary",
  "text-amber-500",
  "text-emerald-500",
  "text-sky-500",
  "text-rose-500",
  "text-violet-500",
];

const highlight = computed<string[]>(() => g.value.highlight || []);

// Une seule série : barre mise en avant (ex. « Durchschnitt ») en ambre
const barColor = (label: string, si: number) =>
  series.value.length === 1
    ? highlight.value.includes(label)
      ? "bg-amber-500"
      : "bg-primary"
    : BG[si % BG.length];

const maxValue = computed(() =>
  Math.max(1, ...series.value.flatMap((s) => s.values || [])),
);

const pct = (v?: number) =>
  `${Math.max(0, Math.min(100, ((Number(v) || 0) / maxValue.value) * 100))}%`;

const unit = computed(() => String(g.value.unit || ""));

const fmt = (v?: number) => {
  if (v == null) return "";
  const n = Number(v).toLocaleString("de-DE");
  return unit.value === "%" ? `${n} %` : n;
};

// Unité hors % et intitulés d'axes, sous le titre
const axisNote = computed(() =>
  [
    unit.value && unit.value !== "%" ? unit.value : "",
    g.value.y_label,
    g.value.x_label,
  ]
    .filter(Boolean)
    .join(" · "),
);

// Camembert : parts ramenées à 100
const pieSegments = computed(() => {
  const values = series.value[0]?.values || [];
  const total = values.reduce((a, b) => a + (Number(b) || 0), 0) || 1;
  let offset = 0;
  return values.map((v) => {
    const size = ((Number(v) || 0) / total) * 100;
    const seg = { size, offset };
    offset += size;
    return seg;
  });
});
</script>