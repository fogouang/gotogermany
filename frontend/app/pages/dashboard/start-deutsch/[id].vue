<!-- pages/dashboard/devoirs/start-deutsch/[id].vue -->
<template>
  <StartDeutschPlayer :assignment-id="String(route.params.id)" />
</template>

<script setup lang="ts">
import StartDeutschPlayer from "~/components/start-deutsch/StartDeutschPlayer.vue";

// Devoir Start Deutsch : même lecteur, sans Sprechen ni correction IA
definePageMeta({ layout: false });

const route = useRoute();
</script>