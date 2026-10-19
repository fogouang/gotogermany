<!-- pages/dashboard/bienvenue.vue -->
<template>
  <div class="min-h-screen bg-canvas">
    <!-- En-tête minimal -->
    <header class="border-b border-line bg-card">
      <div
        class="mx-auto flex h-16 max-w-3xl items-center justify-between px-4"
      >
        <span class="flex items-center gap-2 font-bold text-ink">
          <span
            class="flex size-8 items-center justify-center rounded-leaf bg-primary text-sm text-white"
            >G</span
          >
          GoToGermany
        </span>
        <button
          v-if="step !== 'community'"
          type="button"
          class="text-sm font-medium text-muted hover:text-ink disabled:opacity-50"
          :disabled="saving"
          @click="skip"
        >
          {{ t("onboarding.skip") }}
        </button>
      </div>
    </header>

    <!-- ══════════ Étape 3 : communauté ══════════ -->
    <main
      v-if="step === 'community'"
      class="mx-auto flex max-w-lg flex-col items-center px-4 py-16 text-center"
    >
      <span
        class="flex size-16 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600"
      >
        <i class="pi pi-check-circle text-3xl" />
      </span>
      <h1 class="mt-5 text-2xl font-bold text-ink">
        {{ t("onboarding.community_title") }}
      </h1>
      <p class="mt-2 text-sm text-muted">
        {{ t("onboarding.community_text", { level: chosenLabel }) }}
      </p>

      <div
        class="mt-8 w-full rounded-card border border-emerald-500/30 bg-emerald-500/10 p-5 text-left"
      >
        <p class="flex items-center gap-2 font-semibold text-ink">
          <i class="pi pi-whatsapp text-emerald-600" />
          {{ t("dashboard.community_title") }}
        </p>
        <p class="mt-1 text-sm text-muted">
          {{ t("dashboard.community_text") }}
        </p>
        <a
          :href="SITE.whatsappCommunity"
          target="_blank"
          rel="noopener"
          class="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-leaf bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
          @click="joinCommunity"
        >
          <i class="pi pi-whatsapp" />
          {{ t("dashboard.community_btn") }}
        </a>
      </div>

      <Button
        :label="t('onboarding.go_dashboard')"
        icon="pi pi-arrow-right"
        icon-pos="right"
        text
        class="mt-4"
        @click="goDashboard"
      />
    </main>

    <!-- ══════════ Étape 1 : parcours ══════════ -->
    <main v-else-if="step === 'track'" class="mx-auto max-w-3xl px-4 py-10">
      <h1 class="text-2xl font-bold text-ink sm:text-3xl">
        {{ t("onboarding.track_title") }}
      </h1>
      <p class="mt-1 text-sm text-muted">
        {{ t("onboarding.track_subtitle") }}
      </p>

      <div class="mt-8 grid gap-4 sm:grid-cols-2">
        <button
          v-for="opt in trackOptions"
          :key="opt.value"
          type="button"
          class="flex flex-col items-start gap-3 rounded-card border-2 bg-card p-5 text-left transition-colors"
          :class="
            selectedTrack === opt.value
              ? 'border-primary bg-primary/10'
              : 'border-line hover:border-primary/40'
          "
          @click="selectedTrack = opt.value"
        >
          <span class="flex w-full items-center justify-between">
            <span
              class="rounded-leaf bg-primary/10 px-3 py-1.5 text-sm font-extrabold text-primary"
            >
              {{ opt.badge }}
            </span>
            <i
              v-if="selectedTrack === opt.value"
              class="pi pi-check-circle text-primary"
            />
          </span>
          <span class="font-semibold text-ink">{{ opt.title }}</span>
          <span class="text-sm text-muted">{{ opt.text }}</span>
        </button>
      </div>

      <Button
        :label="t('onboarding.continue')"
        icon="pi pi-arrow-right"
        icon-pos="right"
        size="large"
        class="mt-8 w-full"
        :disabled="!selectedTrack || loading"
        @click="confirmTrack"
      />
    </main>

    <!-- ══════════ Étape 2 : niveau (parcours examen) ══════════ -->
    <main v-else class="mx-auto max-w-3xl px-4 py-10">
      <button
        type="button"
        class="mb-4 inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
        @click="step = 'track'"
      >
        <i class="pi pi-arrow-left text-xs" />
        {{ t("onboarding.back") }}
      </button>

      <h1 class="text-2xl font-bold text-ink sm:text-3xl">
        {{ t("onboarding.title") }}
      </h1>
      <p class="mt-1 text-sm text-muted">{{ t("onboarding.subtitle") }}</p>

      <!-- Chargement -->
      <div v-if="loading" class="mt-8 grid gap-3 sm:grid-cols-2">
        <div
          v-for="n in 6"
          :key="n"
          class="h-20 animate-pulse rounded-card bg-card-2"
        />
      </div>

      <p
        v-else-if="options.length === 0"
        class="mt-8 rounded-card border border-dashed border-line bg-card px-6 py-10 text-center text-sm text-muted"
      >
        {{ t("onboarding.empty") }}
      </p>

      <!-- Choix groupé par organisme -->
      <div v-else class="mt-8 space-y-6">
        <section v-for="group in groups" :key="group.key" class="space-y-2">
          <h2
            class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted"
          >
            <span class="size-2 rounded-full" :class="info(group.key).dot" />
            {{ info(group.key).name }}
          </h2>
          <div class="grid gap-3 sm:grid-cols-2">
            <button
              v-for="o in group.items"
              :key="o.level.id"
              type="button"
              class="flex items-center gap-4 rounded-card border-2 bg-card p-4 text-left transition-colors"
              :class="
                selectedId === o.level.id
                  ? 'border-primary bg-primary/10'
                  : 'border-line hover:border-primary/40'
              "
              @click="selectedId = o.level.id"
            >
              <span
                class="flex size-12 shrink-0 items-center justify-center rounded-leaf text-base font-extrabold"
                :class="info(o.exam.provider).badge"
              >
                {{ o.level.cefr_code }}
              </span>
              <span class="min-w-0 flex-1">
                <span class="block font-semibold text-ink"
                  >{{ info(o.exam.provider).brand }}
                  {{ o.level.cefr_code }}</span
                >
                <span class="block truncate text-xs text-muted">
                  {{ levelName(o.level.cefr_code) || o.exam.name }} ·
                  {{ t("payment.subjet") }}: {{ o.level.subject_count }}
                </span>
              </span>
              <i
                v-if="selectedId === o.level.id"
                class="pi pi-check-circle text-primary"
              />
            </button>
          </div>
        </section>
      </div>

      <Message v-if="error" severity="error" :closable="false" class="mt-6">{{
        error
      }}</Message>

      <Button
        :label="t('onboarding.continue')"
        icon="pi pi-arrow-right"
        icon-pos="right"
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
import { SITE } from "~/config/site";
import type { LearningTrack } from "~/composables/useLearningTrack";

definePageMeta({ layout: false });

const { t, te } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const authStore = useAuthStore();
const { info, orderOf } = useProviders();
const { options, defaultOption, ensureCatalog, setActiveLevel, canSwitch } =
  useActiveLevel();

const { track, hasChosen, setTrack } = useLearningTrack();

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const selectedId = ref<string | null>(null);
const selectedTrack = ref<LearningTrack | null>(null);
const step = ref<"track" | "level" | "community">("track");

const levelName = (code: string) =>
  te(`exam_detail.level_names.${code}`)
    ? t(`exam_detail.level_names.${code}`)
    : "";

// ── Parcours ──
const trackOptions = computed(() => [
  {
    value: "exam" as const,
    badge: "B1 · B2",
    title: t("onboarding.track_exam_title"),
    text: t("onboarding.track_exam_text"),
  },
  {
    value: "start_deutsch" as const,
    badge: "A1 · A2",
    title: t("onboarding.track_start_title"),
    text: t("onboarding.track_start_text"),
  },
]);

function confirmTrack() {
  if (!selectedTrack.value) return;
  setTrack(selectedTrack.value);
  // Start Deutsch n'a pas de niveau du catalogue à choisir
  step.value = selectedTrack.value === "start_deutsch" ? "community" : "level";
}

// ── Niveaux (parcours examen) ──
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
      items: items.sort((a, b) =>
        a.level.cefr_code.localeCompare(b.level.cefr_code),
      ),
    }))
    .sort((a, b) => orderOf(a.key) - orderOf(b.key));
});

/** Libellé de ce qui a été choisi, ex. "Goethe B2" ou "Start Deutsch A1 / A2" */
const chosenLabel = computed(() => {
  if (track.value === "start_deutsch") return "Start Deutsch A1 / A2";
  const o = options.value.find((x) => x.level.id === selectedId.value);
  return o ? `${info(o.exam.provider).brand} ${o.level.cefr_code}` : "";
});

const goDashboard = () =>
  navigateTo(localePath("/dashboard"), { replace: true });

/**
 * Enregistre le niveau actif (parcours examen).
 * withCommunity : après "Continuer", on propose la communauté ; après "Passer", on va droit au tableau de bord.
 */
async function confirm(levelId: string, withCommunity = true) {
  saving.value = true;
  error.value = "";
  const result = await setActiveLevel(levelId);
  saving.value = false;
  if (!result.success) {
    error.value = result.error || t("onboarding.error");
    return;
  }
  if (withCommunity) step.value = "community";
  else goDashboard();
}

/** "Passer" : parcours examen avec le niveau par défaut, pour ne plus reposer la question */
async function skip() {
  setTrack("exam");
  if (defaultOption.value) {
    selectedId.value = defaultOption.value.level.id;
    return confirm(defaultOption.value.level.id, false);
  }
  goDashboard();
}

/** Même clé que la carte du tableau de bord : elle ne réapparaîtra pas */
function joinCommunity() {
  try {
    localStorage.setItem("gtg_community_hidden", "1");
  } catch {
    /* stockage indisponible : sans conséquence */
  }
  goDashboard();
}

onMounted(async () => {
  if (!authStore.user) await authStore.fetchUser();
  // Élève de centre : son niveau est fixé, rien à choisir ici
  if (!canSwitch.value) return goDashboard();

  selectedTrack.value = hasChosen.value ? track.value : null;

  // Venu de « Je prépare plutôt le B1 ou le B2 » : directement au choix de l'examen.
  // Le parcours ne passe en examen qu'une fois l'examen choisi (setActiveLevel).
  if (route.query.step === "level") {
    selectedTrack.value = "exam";
    step.value = "level";
  }

  await ensureCatalog();
  // Présélection uniquement si l'élève a déjà choisi un niveau : jamais un niveau imposé
  selectedId.value = authStore.targetLevelId ?? null;
  loading.value = false;
});
</script>
