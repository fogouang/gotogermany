<template>
  <div class="min-h-screen bg-canvas text-ink">
    <!-- Liseré noir-rouge-or : seul rappel de marque pendant l'épreuve -->
    <div class="flag-stripe h-0.5 w-full" />
    <slot />
  </div>
</template>

<script setup lang="ts">
// Layout minimal pour passer l'examen - pas de distraction
</script>