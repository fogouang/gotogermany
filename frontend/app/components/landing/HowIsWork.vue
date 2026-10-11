<template>
  <section class="relative overflow-hidden bg-canvas py-16 sm:py-24">
    <div class="mx-auto max-w-6xl px-6">
      <div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
        <!-- Image -->
        <div class="relative mx-auto flex w-full max-w-sm items-center justify-center lg:max-w-none">
          <div
            class="pointer-events-none absolute inset-[10%] rounded-full bg-accent-500/20 blur-2xl"
            aria-hidden="true"
          />
          <div
            class="pointer-events-none absolute inset-[6%] animate-[spin_60s_linear_infinite] rounded-full border-2 border-dashed border-accent-500/30"
            aria-hidden="true"
          />
          <img
            src="/images/works.png"
            :alt="t('how_it_works.title')"
            loading="lazy"
            draggable="false"
            class="relative z-10 w-full max-w-md select-none object-contain drop-shadow-[0_30px_60px_rgba(24,24,27,0.2)] lg:max-w-lg"
          />
        </div>

        <!-- Contenu -->
        <div>
          <p
            class="mb-3 inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-primary"
          >
            <span class="h-px w-6 bg-accent-500" />
            {{ t("how_it_works.title") }}
          </p>
          <h2 class="font-heading text-3xl font-bold leading-tight tracking-tight text-ink sm:text-4xl">
            {{ t("how_it_works.subtitle1") }}
            <span class="text-accent-600 dark:text-accent-400">{{ t("how_it_works.subtitle2") }}</span>{{ t("how_it_works.subtitle3") }}
          </h2>

          <!-- Étapes -->
          <ol class="relative mt-10 space-y-4">
            <!-- Ligne de liaison -->
            <span
              class="absolute top-8 bottom-8 left-7 w-px bg-linear-to-b from-accent-500/60 via-line to-line"
              aria-hidden="true"
            />

            <li
              v-for="(step, index) in steps"
              :key="step.key"
              class="group relative flex items-start gap-5 rounded-card border border-transparent p-3 transition-all duration-300 ease-spring hover:border-line hover:bg-card hover:shadow-soft"
            >
              <span
                class="relative z-10 flex size-14 shrink-0 items-center justify-center rounded-leaf border border-line bg-card text-primary-700 shadow-soft transition-all duration-300 group-hover:border-transparent group-hover:bg-accent-500 group-hover:text-accent-950"
              >
                <i :class="[step.icon, 'text-xl']" />
              </span>
              <div class="min-w-0 pt-1">
                <p class="font-heading text-xs font-bold tracking-[0.18em] text-accent-600 dark:text-accent-400">
                  {{ String(index + 1).padStart(2, "0") }}
                </p>
                <h3 class="mt-0.5 font-heading text-lg font-bold text-ink">
                  {{ t(`how_it_works.steps.${step.key}.title`) }}
                </h3>
                <p class="mt-1 text-sm leading-relaxed text-muted">
                  {{ t(`how_it_works.steps.${step.key}.description`) }}
                </p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n();

const steps = [
  { key: "account", icon: "pi pi-user-plus" },
  { key: "exam", icon: "pi pi-book" },
  { key: "progress", icon: "pi pi-chart-line" },
];
</script>