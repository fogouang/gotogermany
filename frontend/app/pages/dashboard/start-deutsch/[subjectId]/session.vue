<!-- pages/dashboard/start-deutsch/[subjectId]/session.vue -->
<template>
  <StartDeutschPlayer :subject-id="String(route.params.subjectId)" />
</template>

<script setup lang="ts">
import StartDeutschPlayer from "~/components/start-deutsch/StartDeutschPlayer.vue";

// Plein écran, comme le lecteur des B
definePageMeta({ layout: false });

const route = useRoute();
</script>