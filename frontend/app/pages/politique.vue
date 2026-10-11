<template>
  <div class="bg-canvas">
    <!-- En-tête -->
    <AppPageHero
      icon="pi pi-shield"
      watermark="Datenschutz"
      :eyebrow="c.badge"
      :title="c.titre"
    >
      <p class="mt-4 inline-flex items-center gap-2 text-sm text-faint">
        <i class="pi pi-calendar text-xs" />
        {{ c.majLabel }} {{ c.maj }}
      </p>
    </AppPageHero>

    <section class="pb-16 sm:pb-24">
      <div
        class="mx-auto grid max-w-6xl gap-8 px-4 sm:px-6 lg:grid-cols-[16rem_1fr] lg:gap-12"
      >
        <!-- Sommaire -->
        <nav class="lg:sticky lg:top-24 lg:self-start" :aria-label="c.sommaire">
          <div class="rounded-card border border-line bg-card p-5 shadow-soft">
            <p
              class="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-faint"
            >
              {{ c.sommaire }}
            </p>
            <ol class="space-y-1">
              <li v-for="(s, i) in sectionsAvecContact" :key="s.id">
                <a
                  :href="`#${s.id}`"
                  class="flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm text-muted transition-colors hover:bg-card-2 hover:text-ink"
                >
                  <span
                    class="font-heading text-xs font-bold text-accent-600 dark:text-accent-400"
                  >
                    {{ String(i + 1).padStart(2, "0") }}
                  </span>
                  {{ s.titre }}
                </a>
              </li>
            </ol>
          </div>
        </nav>

        <!-- Contenu -->
        <article class="legal space-y-6">
          <p
            class="rounded-card border border-line bg-card p-6 text-base leading-relaxed text-ink shadow-soft sm:p-8"
            v-html="c.introduction"
          />

          <section
            v-for="(s, i) in c.sections"
            :id="s.id"
            :key="s.id"
            class="scroll-mt-24 rounded-card border border-line bg-card p-6 shadow-soft sm:p-8"
          >
            <div class="mb-5 flex items-center gap-3">
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary-50 text-primary-700"
              >
                <i :class="s.icone" />
              </span>
              <h2 class="font-heading text-xl font-bold text-ink sm:text-2xl">
                {{ i + 1 }}. {{ s.titre }}
              </h2>
            </div>

            <p
              v-if="s.important"
              class="mb-4 flex items-center gap-2 rounded-leaf bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300"
            >
              <i class="pi pi-check-circle text-xs" />
              {{ s.important }}
            </p>
            <p
              v-if="s.intro"
              class="mb-4 text-sm leading-relaxed text-muted sm:text-base"
            >
              {{ s.intro }}
            </p>

            <!-- Listes -->
            <div v-if="s.groupes" class="space-y-5">
              <div v-for="(g, gi) in s.groupes" :key="gi">
                <h3 v-if="g.titre" class="mb-2 text-sm font-semibold text-ink">
                  {{ g.titre }}
                </h3>
                <ul class="space-y-2">
                  <li
                    v-for="(item, ii) in g.items"
                    :key="ii"
                    class="flex items-start gap-2.5 text-sm leading-relaxed text-muted"
                  >
                    <i
                      class="pi pi-angle-right mt-1 text-[10px] text-accent-500"
                    />
                    <span v-html="item" />
                  </li>
                </ul>
              </div>
            </div>

            <!-- Droits -->
            <div v-if="s.droits" class="grid gap-3 sm:grid-cols-2">
              <div
                v-for="d in s.droits"
                :key="d.titre"
                class="rounded-leaf border border-line bg-card-2 p-4"
              >
                <p
                  class="flex items-center gap-2 text-sm font-semibold text-ink"
                >
                  <i
                    class="pi pi-check text-xs text-emerald-600 dark:text-emerald-400"
                  />
                  {{ d.titre }}
                </p>
                <p class="mt-1 text-sm text-muted">{{ d.texte }}</p>
              </div>
            </div>

            <!-- Encadré -->
            <div
              v-if="s.encadre"
              class="mt-5 rounded-leaf border-l-4 border-accent-500 bg-accent-500/10 px-4 py-3"
            >
              <p class="text-sm font-semibold text-ink">
                {{ s.encadre.titre }}
              </p>
              <p class="mt-1 text-sm text-muted" v-html="s.encadre.texte" />
            </div>
          </section>

          <!-- Contact -->
          <section
            id="contact"
            class="relative scroll-mt-24 overflow-hidden rounded-card bg-zinc-950 p-6 text-white shadow-lift sm:p-8"
          >
            <div
              class="flag-stripe absolute inset-x-0 top-0 h-1"
              aria-hidden="true"
            />
            <div class="mb-5 flex items-center gap-3">
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-accent-500 text-accent-950"
              >
                <i class="pi pi-envelope" />
              </span>
              <h2 class="font-heading text-xl font-bold sm:text-2xl">
                {{ c.sections.length + 1 }}. {{ c.contact.titre }}
              </h2>
            </div>
            <p class="mb-5 text-sm text-white/70">{{ c.contact.intro }}</p>
            <dl class="grid gap-4 text-sm sm:grid-cols-3">
              <div>
                <dt class="text-xs uppercase tracking-wider text-white/50">
                  {{ c.contact.email }}
                </dt>
                <dd class="mt-1">
                  <a
                    :href="`mailto:${CONTACT_POLITIQUE.email}`"
                    class="font-semibold text-accent-400 hover:underline"
                  >
                    {{ CONTACT_POLITIQUE.email }}
                  </a>
                </dd>
              </div>
              <div>
                <dt class="text-xs uppercase tracking-wider text-white/50">
                  {{ c.contact.telephone }}
                </dt>
                <dd class="mt-1 space-y-0.5">
                  <a
                    v-for="tel in CONTACT_POLITIQUE.telephones"
                    :key="tel"
                    :href="`tel:${tel.replace(/\s/g, '')}`"
                    class="block font-semibold hover:text-accent-400"
                  >
                    {{ tel }}
                  </a>
                </dd>
              </div>
              <div>
                <dt class="text-xs uppercase tracking-wider text-white/50">
                  {{ c.contact.adresse }}
                </dt>
                <dd class="mt-1 font-semibold">
                  {{ c.contact.adresseValeur }}
                </dd>
              </div>
            </dl>
          </section>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { POLITIQUE, CONTACT_POLITIQUE } from "~/content/politique";

const { locale } = useI18n();

// Version de la langue active (repli sur le français)
const c = computed(
  () => POLITIQUE[locale.value as keyof typeof POLITIQUE] ?? POLITIQUE.fr,
);

const sectionsAvecContact = computed(() => [
  ...c.value.sections.map((s) => ({ id: s.id, titre: s.titre })),
  { id: "contact", titre: c.value.contact.titre },
]);

useHead({
  title: () => c.value.metaTitre,
  meta: [{ name: "description", content: () => c.value.metaDescription }],
});
</script>

<style scoped>
/* Liens et gras dans le texte HTML du contenu */
.legal :deep(a) {
  color: var(--color-accent-600);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.legal :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}
</style>
