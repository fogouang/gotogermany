<template>
  <div class="space-y-4">
    <div class="h-32 animate-pulse rounded-card bg-card-2" />
    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="n in 6" :key="n" class="h-24 animate-pulse rounded-card bg-card-2" />
    </div>
  </div>
</template>

<script setup lang="ts">
// Point d'entrée "Examens" : on va droit au niveau actif de l'étudiant.
definePageMeta({ layout: "dashboard" });

const localePath = useLocalePath();
const authStore = useAuthStore();
const { activeOption, needsOnboarding, ensureCatalog } = useActiveLevel();

onMounted(async () => {
  if (!authStore.user) await authStore.fetchUser();
  await ensureCatalog();

  if (needsOnboarding.value) {
    return navigateTo(localePath("/dashboard/bienvenue"), { replace: true });
  }

  const target = activeOption.value
    ? `/dashboard/examens/${activeOption.value.exam.slug}`
    : "/dashboard/examens/catalogue";
  return navigateTo(localePath(target), { replace: true });
});
</script>