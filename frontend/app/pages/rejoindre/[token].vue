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

        <!-- Lien invalide ou désactivé -->
        <div v-if="error || !info" class="space-y-4 py-6 text-center">
          <span class="mx-auto grid size-14 place-items-center rounded-full bg-red-500/10 text-red-600">
            <i class="pi pi-link text-xl" />
          </span>
          <h1 class="font-heading text-2xl font-extrabold text-ink">{{ t("join_center.invalid_title") }}</h1>
          <p class="text-sm text-muted">{{ t("join_center.invalid_text") }}</p>
          <AppButton variant="secondary" :label="t('join_center.back_home')" @click="navigateTo(localePath('/'))" />
        </div>

        <template v-else>
          <span
            class="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary"
          >
            <i class="pi pi-building text-[11px]" />
            {{ info.center_name }}
          </span>
          <h1 class="mt-3 font-heading text-2xl font-extrabold text-ink sm:text-3xl">
            {{ t("join_center.title", { center: info.center_name }) }}
          </h1>
          <p class="mt-2 text-sm text-muted">{{ t("join_center.subtitle") }}</p>

          <div class="mt-8">
            <SignupForm :join-token="token" :branches="info.branches" @success="onSuccess">
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
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface JoinInfo {
  center_name: string;
  branches: { id: string; name: string }[];
}

const route = useRoute();
const { t } = useI18n();
const localePath = useLocalePath();
const runtimeConfig = useRuntimeConfig();

const token = route.params.token as string;
const base = runtimeConfig.public.apiBaseUrl || "http://localhost:8001";

// Route publique : nom du centre et succursales au choix
const { data: info, error } = await useFetch<JoinInfo>(`${base}/api/v1/centers/join/${token}`, {
  key: `join-center-${token}`,
});

const valeurs = [
  { key: "format", icon: "pi pi-clone" },
  { key: "clarity", icon: "pi pi-chart-bar" },
  { key: "access", icon: "pi pi-mobile" },
];

// Compte créé « en attente » : la page d'attente s'affiche jusqu'à la validation
const onSuccess = () => navigateTo(localePath("/dashboard/en-attente"));

useHead({
  title: computed(() =>
    info.value
      ? t("join_center.page_title", { center: info.value.center_name })
      : t("join_center.page_title_generic"),
  ),
});
</script>