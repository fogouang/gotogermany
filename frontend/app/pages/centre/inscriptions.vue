<!-- pages/centre/inscriptions.vue -->
<template>
  <div class="space-y-5">
    <CentreJoinLinkCard />
    <CentreJoinRequestsPanel />
  </div>
</template>

<script setup lang="ts">
import CentreJoinLinkCard from "~/components/centre/JoinLinkCard.vue";
import CentreJoinRequestsPanel from "~/components/centre/JoinRequestsPanel.vue";

definePageMeta({ layout: "centre", watermark: "Anmeldungen" });
</script>