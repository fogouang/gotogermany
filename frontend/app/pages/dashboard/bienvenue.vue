<template>
  <div class="min-h-screen bg-canvas">
    <!-- En-tête minimal -->
    <header class="border-b border-line bg-card">
      <div class="mx-auto flex h-16 max-w-3xl items-center justify-between px-4">
        <span class="flex items-center gap-2 font-bold text-ink">
          <span class="flex size-8 items-center justify-center rounded-leaf bg-primary text-sm text-white">G</span>
          GoToGermany
        </span>
        <button
          type="button"
          class="text-sm font-medium text-muted hover:text-ink disabled:opacity-50"
          :disabled="saving"
          @click="skip"
        >
          {{ t("onboarding.skip") }}
        </button>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-10">
      <h1 class="text-2xl font-bold text-ink sm:text-3xl">{{ t("onboarding.title") }}</h1>
      <p class="mt-1 text-sm text-muted">{{ t("onboarding.subtitle") }}</p>

      <!-- Chargement -->
      <div v-if="loading" class="mt-8 grid gap-3 sm:grid-cols-2">
        <div v-for="n in 6" :key="n" class="h-20 animate-pulse rounded-card bg-card-2" />
      </div>

      <p v-else-if="options.length === 0" class="mt-8 rounded-card border border-dashed border-line bg-card px-6 py-10 text-center text-sm text-muted">
        {{ t("onboarding.empty") }}
      </p>

      <!-- Choix groupé par organisme -->
      <div v-else class="mt-8 space-y-6">
        <section v-for="group in groups" :key="group.key" class="space-y-2">
          <h2 class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
            <span class="size-2 rounded-full" :class="info(group.key).dot" />
            {{ info(group.key).name }}
          </h2>
          <div class="grid gap-3 sm:grid-cols-2">
            <button
              v-for="o in group.items"
              :key="o.level.id"
              type="button"
              class="flex items-center gap-4 rounded-card border-2 bg-card p-4 text-left transition-colors"
              :class="selectedId === o.level.id ? 'border-primary bg-primary/10' : 'border-line hover:border-primary/40'"
              @click="selectedId = o.level.id"
            >
              <span class="flex size-12 shrink-0 items-center justify-center rounded-leaf text-base font-extrabold" :class="info(o.exam.provider).badge">
                {{ o.level.cefr_code }}
              </span>
              <span class="min-w-0 flex-1">
                <span class="block font-semibold text-ink">{{ info(o.exam.provider).brand }} {{ o.level.cefr_code }}</span>
                <span class="block truncate text-xs text-muted">
                  {{ levelName(o.level.cefr_code) || o.exam.name }} · {{ o.level.subject_count }} {{ t("payment.subjet") }}
                </span>
              </span>
              <i v-if="selectedId === o.level.id" class="pi pi-check-circle text-primary" />
            </button>
          </div>
        </section>
      </div>

      <Message v-if="error" severity="error" :closable="false" class="mt-6">{{ error }}</Message>

      <Button
        :label="t('onboarding.continue')"
        icon="pi pi-arrow-right"
        iconPos="right"
        size="large"
        class="mt-8 w-full"
        :disabled="!selectedId"
        :loading="saving"
        @click="confirm(selectedId!)"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });

const { t, te } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const { info, orderOf } = useProviders();
const { options, defaultOption, ensureCatalog, setActiveLevel, canSwitch } = useActiveLevel();

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const selectedId = ref<string | null>(null);

const levelName = (code: string) => (te(`exam_detail.level_names.${code}`) ? t(`exam_detail.level_names.${code}`) : "");

const groups = computed(() => {
  const map = new Map<string, typeof options.value>();
  for (const o of options.value) {
    const key = normProvider(o.exam.provider);
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(o);
  }
  return [...map.entries()]
    .map(([key, items]) => ({
      key,
      items: items.sort((a, b) => a.level.cefr_code.localeCompare(b.level.cefr_code)),
    }))
    .sort((a, b) => orderOf(a.key) - orderOf(b.key));
});

const goDashboard = () => navigateTo(localePath("/dashboard"), { replace: true });

async function confirm(levelId: string) {
  saving.value = true;
  error.value = "";
  const result = await setActiveLevel(levelId);
  saving.value = false;
  if (!result.success) {
    error.value = result.error || t("onboarding.error");
    return;
  }
  goDashboard();
}

/** "Passer" : on applique le niveau par défaut pour ne plus reposer la question */
async function skip() {
  if (defaultOption.value) return confirm(defaultOption.value.level.id);
  goDashboard();
}

onMounted(async () => {
  if (!authStore.user) await authStore.fetchUser();
  // Élève de centre : son niveau est fixé, rien à choisir ici
  if (!canSwitch.value) return goDashboard();
  await ensureCatalog();
  selectedId.value = authStore.targetLevelId ?? defaultOption.value?.level.id ?? null;
  loading.value = false;
});
</script>