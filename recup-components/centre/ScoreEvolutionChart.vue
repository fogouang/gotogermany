<!-- components/centre/ScoreEvolutionChart.vue -->
<template>
  <div class="relative">
    <svg :viewBox="`0 0 ${width} ${height}`" class="w-full h-auto">
      <!-- Lignes de grille horizontales -->
      <line
        v-for="tick in yTicks"
        :key="`grid-${tick}`"
        :x1="padding.left"
        :x2="width - padding.right"
        :y1="yScale(tick)"
        :y2="yScale(tick)"
        stroke="#f3f4f6"
        stroke-width="1"
      />
      <!-- Labels axe Y -->
      <text
        v-for="tick in yTicks"
        :key="`label-${tick}`"
        :x="padding.left - 8"
        :y="yScale(tick) + 4"
        text-anchor="end"
        class="fill-gray-400"
        font-size="11"
      >
        {{ tick }}
      </text>

      <!-- Ligne de seuil de réussite (60) -->
      <line
        :x1="padding.left"
        :x2="width - padding.right"
        :y1="yScale(60)"
        :y2="yScale(60)"
        stroke="#f59e0b"
        stroke-width="1"
        stroke-dasharray="4 3"
      />

      <!-- Ligne d'évolution -->
      <polyline
        v-if="points.length > 1"
        :points="linePoints"
        fill="none"
        stroke="#10b981"
        stroke-width="2.5"
      />

      <!-- Points + tooltip au survol -->
      <g v-for="(p, i) in points" :key="i">
        <circle
          :cx="p.x"
          :cy="p.y"
          r="4"
          fill="#10b981"
          stroke="white"
          stroke-width="2"
          class="cursor-pointer"
          @mouseenter="hoveredIndex = i"
          @mouseleave="hoveredIndex = null"
        />
      </g>
    </svg>

    <!-- Tooltip -->
    <div
      v-if="hoveredPoint"
      class="absolute bg-gray-900 text-white text-xs rounded-lg px-3 py-2 pointer-events-none shadow-lg"
      :style="tooltipStyle"
    >
      <p class="font-semibold">{{ hoveredPoint.score.toFixed(0) }}/100</p>
      <p class="text-gray-300">{{ hoveredPoint.exam_name }}</p>
      <p class="text-gray-400">{{ formatDate(hoveredPoint.date) }}</p>
    </div>

    <div
      v-if="data.length === 0"
      class="text-center text-sm text-gray-400 py-8"
    >
      Pas encore assez de données pour afficher un graphique.
    </div>
  </div>
</template>

<script setup lang="ts">
interface ScorePoint {
  date: string;
  score: number;
  exam_name: string;
}

const props = defineProps<{ data: ScorePoint[] }>();

const width = 600;
const height = 220;
const padding = { top: 16, right: 16, bottom: 24, left: 36 };

const hoveredIndex = ref<number | null>(null);

const yTicks = [0, 25, 50, 75, 100];

function yScale(value: number) {
  const usableHeight = height - padding.top - padding.bottom;
  return padding.top + usableHeight - (value / 100) * usableHeight;
}

function xScale(index: number) {
  const usableWidth = width - padding.left - padding.right;
  const count = props.data.length;
  if (count <= 1) return padding.left + usableWidth / 2;
  return padding.left + (index / (count - 1)) * usableWidth;
}

const points = computed(() =>
  props.data.map((d, i) => ({
    x: xScale(i),
    y: yScale(d.score),
  })),
);

const linePoints = computed(() =>
  points.value.map((p) => `${p.x},${p.y}`).join(" "),
);

const hoveredPoint = computed(() => {
  if (hoveredIndex.value === null) return null;
  return props.data[hoveredIndex.value] ?? null;
});

const tooltipStyle = computed(() => {
  if (hoveredIndex.value === null) return {};
  const p = points.value[hoveredIndex.value];
  if (!p) return {};
  const leftPercent = (p.x / width) * 100;
  const topPercent = (p.y / height) * 100;
  return {
    left: `${leftPercent}%`,
    top: `${Math.max(topPercent - 18, 0)}%`,
    transform: "translateX(-50%)",
  };
});

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
  });
}
</script>
