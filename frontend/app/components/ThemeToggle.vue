<script setup lang="ts">
const { isDark, toggleTheme } = useTheme();
</script>

<template>
  <button
    type="button"
    class="flex size-10 items-center justify-center rounded-leaf border border-line bg-card text-muted shadow-soft transition-colors duration-300 hover:border-primary/30 hover:text-primary"
    :aria-label="isDark ? 'Passer en mode clair' : 'Passer en mode sombre'"
    @click="toggleTheme"
  >
    <i
      class="text-base transition-transform duration-500 ease-spring"
      :class="isDark ? 'pi pi-sun rotate-0' : 'pi pi-moon -rotate-12'"
    />
  </button>
</template>