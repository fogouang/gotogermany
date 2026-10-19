<template>
  <div class="bg-hero flex min-h-screen items-center justify-center bg-canvas px-4 py-12">
    <div class="w-full max-w-md rounded-card border border-line bg-card p-8 text-center shadow-lift">
      <span class="mx-auto grid size-16 place-items-center rounded-full bg-primary/10 text-primary">
        <i class="pi pi-hourglass text-2xl" />
      </span>

      <h1 class="mt-5 font-heading text-2xl font-extrabold text-ink">
        {{ t("pending_join.title") }}
      </h1>
      <p class="mt-2 text-sm leading-relaxed text-muted">
        {{ t("pending_join.text", { name: firstName }) }}
      </p>

      <ol class="mt-6 space-y-3 text-left">
        <li v-for="(step, i) in steps" :key="step" class="flex items-start gap-3">
          <span
            class="grid size-6 shrink-0 place-items-center rounded-full bg-card-2 text-xs font-bold text-muted"
          >
            {{ i + 1 }}
          </span>
          <span class="pt-0.5 text-sm text-ink">{{ t(step) }}</span>
        </li>
      </ol>

      <div class="mt-8 flex flex-col gap-2">
        <AppButton
          variant="gradient"
          block
          icon="pi pi-refresh"
          :label="t('pending_join.refresh')"
          :loading="refreshing"
          @click="refresh"
        />
        <AppButton variant="ghost" block :label="t('pending_join.logout')" @click="logout" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });

const { t } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();

const firstName = computed(() => authStore.userName.split(/\s+/)[0] ?? "");

const steps = [
  "pending_join.step_1",
  "pending_join.step_2",
  "pending_join.step_3",
];

const refreshing = ref(false);

// Le middleware renvoie ici tant que l'inscription n'est pas validée
async function refresh() {
  refreshing.value = true;
  await authStore.fetchUser();
  refreshing.value = false;
  await navigateTo(localePath("/dashboard"));
}

async function logout() {
  await authStore.logout();
  await navigateTo(localePath("/"));
}

useHead({ title: t("pending_join.page_title") });
</script>