<template>
  <section
    class="relative overflow-hidden bg-canvas pt-10 pb-16 sm:pt-14 lg:pb-24"
  >
    <!-- Décor : halos -->
    <div
      class="pointer-events-none absolute -top-40 -left-40 size-120 rounded-full bg-accent-500/15 blur-3xl"
      aria-hidden="true"
    />
    <div
      class="pointer-events-none absolute -right-40 -bottom-48 size-136 rounded-full bg-primary/10 blur-3xl"
      aria-hidden="true"
    />

    <div
      class="relative mx-auto flex w-full max-w-7xl flex-col items-center gap-12 px-6 md:flex-row md:justify-between md:gap-8"
    >
      <!-- Texte -->
      <div class="fade-in-up w-full md:max-w-xl">
        <h1
          class="font-heading text-3xl leading-tight font-bold tracking-tight text-ink sm:text-4xl lg:text-5xl lg:leading-[1.1]"
        >
          {{ t("hero.title") }}
        </h1>
        <p
          class="mt-5 max-w-lg text-base leading-relaxed text-muted sm:text-lg"
        >
          {{ t("hero.subtitle") }}
        </p>

        <!-- CTA -->
        <div class="mt-8 flex flex-wrap items-center gap-3">
          <AppButton
            variant="gradient"
            size="large"
            icon="pi pi-arrow-right"
            icon-pos="right"
            :label="t('hero.cta')"
            @click="handleCta"
          />
          <button
            type="button"
            class="inline-flex h-12 items-center gap-2.5 rounded-leaf border border-line bg-card px-5 text-sm font-semibold text-ink shadow-soft transition-colors hover:border-accent-500/50"
            @click="demoOpen = true"
          >
            <span
              class="flex size-7 items-center justify-center rounded-full bg-accent-500 text-accent-950"
            >
              <i class="pi pi-play text-[10px]" />
            </span>
            {{ t("hero.demo") }}
          </button>
        </div>

        <!-- Encart Premium : mène à la section tarifs de la page -->
        <a
          v-if="minPrice"
          href="#tarifs"
          class="mt-6 flex max-w-lg flex-col gap-2 rounded-card border border-accent-500/40 bg-accent-500/5 p-5 transition-colors hover:border-accent-500 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <p
              class="font-heading text-lg font-bold text-accent-700 dark:text-accent-400"
            >
              {{
                t("hero.premium_from", {
                  price: minPrice.toLocaleString("fr-FR"),
                })
              }}
            </p>
            <p class="mt-0.5 text-sm text-muted">
              {{ t("hero.premium_desc") }}
            </p>
          </div>
          <span
            class="inline-flex shrink-0 items-center gap-1.5 text-sm font-semibold text-primary underline-offset-4 hover:underline"
          >
            {{ t("hero.see_prices") }}
            <i class="pi pi-arrow-down text-xs" />
          </span>
        </a>

        <!-- Preuve sociale -->
        <div class="mt-8 flex items-center gap-3">
          <div class="flex items-center gap-0.5">
            <i
              v-for="i in 5"
              :key="i"
              class="pi pi-star-fill text-sm text-accent-500"
            />
          </div>
          <p class="text-sm">
            <span class="font-semibold text-ink">5.0</span>
            <span class="text-muted"> · {{ t("hero.social_proof") }}</span>
          </p>
        </div>

        <!-- Organismes préparés -->
        <div class="mt-6 flex flex-wrap items-center gap-2">
          <span
            v-for="org in ['Goethe', 'telc', 'ÖSD', 'TestDaF', 'ECL']"
            :key="org"
            class="inline-flex items-center gap-1.5 rounded-full border border-line bg-card px-3 py-1 text-xs font-semibold text-ink shadow-soft"
          >
            <i
              class="pi pi-check-circle text-[11px] text-emerald-600 dark:text-emerald-400"
            />
            {{ org }}
          </span>
          <span
            class="inline-flex items-center rounded-full bg-primary-50 px-3 py-1 text-xs font-bold text-primary-700"
          >
            B1 · B2
          </span>
        </div>
      </div>

      <!-- Image -->
      <div class="relative w-full max-w-xl md:max-w-160">
        <!-- Halo + anneau doré -->
        <div
          class="pointer-events-none absolute inset-[8%] rounded-full bg-accent-500/20 blur-2xl"
          aria-hidden="true"
        />
        <div
          class="pointer-events-none absolute inset-[4%] rounded-full border border-dashed border-accent-500/40"
          aria-hidden="true"
        />

        <img
          :alt="t('hero.image_alt')"
          draggable="false"
          class="relative z-10 h-full w-full select-none drop-shadow-[0_30px_60px_rgba(24,24,27,0.25)]"
          src="/images/hero-student.png"
          fetchpriority="high"
        />
      </div>
    </div>

    <!-- Démo vidéo (rendue dans <body> par PrimeVue) -->
    <Dialog
      v-model:visible="demoOpen"
      modal
      dismissableMask
      :header="t('hero.demo_title')"
      :style="{ width: '95vw', maxWidth: '60rem' }"
      @hide="pauseVideo"
    >
      <div class="space-y-4">
        <div v-if="demos.length > 1" class="flex justify-center">
          <SelectButton
            v-model="selectedDemo"
            :options="demoOptions"
            optionLabel="label"
            optionValue="value"
            :allowEmpty="false"
          />
        </div>
        <video
          ref="videoEl"
          :key="currentDemo.src"
          :src="currentDemo.src"
          :poster="currentDemo.poster"
          controls
          playsinline
          preload="metadata"
          class="aspect-video w-full rounded-card bg-black"
        />
      </div>
    </Dialog>
  </section>
</template>

<script setup lang="ts">
import { useAuthDialog } from "~/composables/useAuthDialog";

const { t } = useI18n();

const authStore = useAuthStore();
const { openSignup } = useAuthDialog();
const { activePlans, loadPlans } = usePlans();

// Prix d'appel : la formule la moins chère, tous parcours confondus
const minPrice = computed(() => {
  const prices = activePlans.value.map((p) => p.price).filter((p) => p > 0);
  return prices.length ? Math.min(...prices) : null;
});

// Connecté : direction son espace ; invité : inscription
const handleCta = () => {
  if (authStore.isAuthenticated) {
    if (authStore.isAdmin) navigateTo("/admin");
    else if (authStore.isDirector) navigateTo("/centre/dashboard");
    else if (authStore.isSecretary) navigateTo("/centre/etudiants");
    else if (authStore.isTeacher) navigateTo("/enseignant/sessions");
    else navigateTo("/dashboard");
  } else {
    openSignup();
  }
};

onMounted(() => {
  if (!activePlans.value.length) loadPlans();
});

// ── Démo vidéo ──
const demoOpen = ref(false);
const videoEl = ref<HTMLVideoElement | null>(null);

// Retire une ligne tant que la vidéo correspondante n'est pas prête
const demos = [
  { value: "sujet", src: "/videos/demo-sujet.mp4", poster: "/videos/demo-sujet.jpg" },
  { value: "schreiben", src: "/videos/demo-schreiben.mp4", poster: "/videos/demo-schreiben.jpg" },
  { value: "sprechen", src: "/videos/demo-sprechen.mp4", poster: "/videos/demo-sprechen.jpg" },
];

const selectedDemo = ref(demos[0]?.value ?? "sujet");

const demoOptions = computed(() =>
  demos.map((d) => ({ label: t(`hero.demo_${d.value}`), value: d.value })),
);

const currentDemo = computed(
  () => demos.find((d) => d.value === selectedDemo.value) ?? demos[0]!,
);

// Fermeture : on coupe le son
const pauseVideo = () => videoEl.value?.pause();
</script>