<template>
  <div class="bg-hero relative flex min-h-screen items-center justify-center overflow-hidden bg-canvas px-4 py-12">
    <span
      aria-hidden="true"
      class="pointer-events-none absolute -bottom-6 left-1/2 -translate-x-1/2 select-none whitespace-nowrap font-heading text-[6rem] font-extrabold leading-none tracking-tighter text-ink/5 sm:text-[11rem]"
    >
      Willkommen
    </span>

    <div class="relative grid w-full max-w-5xl overflow-hidden rounded-card border border-line bg-card shadow-lift lg:grid-cols-[1fr_1.1fr]">
      <!-- Panneau marque -->
      <aside class="relative hidden flex-col overflow-hidden bg-zinc-950 p-10 text-white lg:flex">
        <div class="flag-stripe absolute inset-x-0 top-0 h-1" aria-hidden="true" />
        <div
          class="pointer-events-none absolute -right-20 -top-20 size-72 rounded-full bg-accent-500/20 blur-3xl"
          aria-hidden="true"
        />

        <NuxtLink :to="localePath('/')" class="relative font-heading text-2xl font-extrabold tracking-tight">
          GoTo<span class="text-accent-500">Germany</span>
        </NuxtLink>

        <div class="relative mt-auto">
          <h2 class="font-heading text-3xl font-extrabold leading-tight">
            {{ t("about.mission.title") }}
          </h2>
          <p class="mt-4 leading-relaxed text-white/70">
            {{ t("about.mission.p2") }}
          </p>

          <ul class="mt-8 space-y-5">
            <li v-for="v in valeurs" :key="v.key" class="flex gap-3">
              <span class="grid size-9 shrink-0 place-items-center rounded-leaf bg-accent-500/15 text-accent-400">
                <i :class="[v.icon, 'text-sm']" />
              </span>
              <div>
                <p class="text-sm font-semibold">{{ t(`about.values.items.${v.key}.title`) }}</p>
                <p class="mt-0.5 text-sm text-white/60">{{ t(`about.values.items.${v.key}.desc`) }}</p>
              </div>
            </li>
          </ul>
        </div>
      </aside>

      <!-- Formulaire -->
      <div class="p-6 sm:p-10">
        <NuxtLink
          :to="localePath('/')"
          class="mb-8 inline-block font-heading text-xl font-extrabold tracking-tight text-ink lg:hidden"
        >
          GoTo<span class="text-accent-500">Germany</span>
        </NuxtLink>

        <h1 class="font-heading text-2xl font-extrabold text-ink sm:text-3xl">
          {{ t("auth.signup_title") }}
        </h1>
        <p class="mt-2 text-sm text-muted">{{ t("auth.signup_subtitle") }}</p>

        <div class="mt-8">
          <SignupForm :referral-code="referralCode" @success="onSuccess">
            <template #footer>
              <p class="mt-2 text-center text-sm text-muted">
                {{ t("auth.have_account") }}
                <NuxtLink :to="localePath('/')" class="font-semibold text-primary hover:underline">
                  {{ t("auth.login_link") }}
                </NuxtLink>
              </p>
            </template>
          </SignupForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const { t } = useI18n();
const localePath = useLocalePath();
const { cheminApresConnexion } = useChoixExamen();

const referralCookie = useCookie<string | null>("referral_code", {
  maxAge: 60 * 60 * 24 * 30,
});

// Enregistré dès le rendu pour que la bannière de parrainage s'affiche tout de suite
const refQuery = route.query.ref;
if (typeof refQuery === "string" && refQuery) referralCookie.value = refQuery;

const referralCode = computed(() => referralCookie.value);

const PAGES_INVITE = ["/register"];

const valeurs = [
  { key: "format", icon: "pi pi-clone" },
  { key: "clarity", icon: "pi pi-chart-bar" },
  { key: "access", icon: "pi pi-mobile" },
];

const onSuccess = () => {
  referralCookie.value = null;
  navigateTo(cheminApresConnexion());
};
</script>