<template>
  <div class="bg-canvas">
    <!-- En-tête -->
    <section class="relative overflow-hidden pt-12 pb-10 sm:pt-16">
      <div
        class="pointer-events-none absolute inset-0 bg-grid opacity-40 mask-[radial-gradient(ellipse_at_top,black,transparent_70%)]"
        aria-hidden="true"
      />
      <div
        class="pointer-events-none absolute -top-32 left-1/2 size-120 -translate-x-1/2 rounded-full bg-accent-500/15 blur-3xl"
        aria-hidden="true"
      />

      <div class="relative mx-auto max-w-3xl px-4 text-center sm:px-6">
        <p
          class="mb-3 inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-primary"
        >
          <span class="h-px w-6 bg-accent-500" />
          {{ t("faq.badge") }}
          <span class="h-px w-6 bg-accent-500" />
        </p>
        <h1 class="font-heading text-3xl font-bold tracking-tight text-ink sm:text-5xl">
          {{ t("faq.title") }}
        </h1>
        <p class="mt-4 text-base text-muted sm:text-lg">
          {{ t("faq.subtitle") }}
        </p>

        <!-- Recherche -->
        <div class="relative mx-auto mt-8 max-w-xl">
          <i
            class="pi pi-search pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 text-faint"
          />
          <input
            v-model="recherche"
            type="search"
            :placeholder="t('faq.search_placeholder')"
            class="h-12 w-full rounded-card border border-line bg-card pr-4 pl-11 text-sm text-ink shadow-soft outline-none transition-colors placeholder:text-faint focus:border-accent-500"
          />
        </div>
      </div>
    </section>

    <!-- Contenu -->
    <section class="pb-16 sm:pb-24">
      <div class="mx-auto max-w-3xl px-4 sm:px-6">
        <!-- Catégories -->
        <div class="-mx-4 mb-8 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:flex-wrap sm:justify-center sm:px-0">
          <button
            v-for="category in categories"
            :key="category.id"
            type="button"
            class="inline-flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition-all duration-200"
            :class="
              selectedCategory === category.id
                ? 'border-transparent bg-zinc-900 text-white shadow-soft dark:bg-accent-500 dark:text-accent-950'
                : 'border-line bg-card text-muted hover:border-accent-500/50 hover:text-ink'
            "
            @click="selectedCategory = category.id"
          >
            <i :class="[category.icon, 'text-xs']" />
            {{ category.label }}
            <span
              class="rounded-full px-1.5 text-[11px] font-bold"
              :class="selectedCategory === category.id ? 'bg-white/20' : 'bg-card-2 text-faint'"
            >
              {{ category.count }}
            </span>
          </button>
        </div>

        <!-- Questions -->
        <div v-if="filteredFaqs.length" class="space-y-3">
          <div
            v-for="faq in filteredFaqs"
            :key="faq.key"
            class="overflow-hidden rounded-card border bg-card transition-all duration-300"
            :class="
              ouverte === faq.key
                ? 'border-accent-500/50 shadow-lift'
                : 'border-line shadow-soft hover:border-accent-500/30'
            "
          >
            <button
              type="button"
              class="flex w-full items-center gap-4 px-5 py-4 text-left sm:px-6"
              :aria-expanded="ouverte === faq.key"
              @click="basculer(faq.key)"
            >
              <span
                class="flex size-9 shrink-0 items-center justify-center rounded-leaf transition-colors duration-300"
                :class="
                  ouverte === faq.key
                    ? 'bg-accent-500 text-accent-950'
                    : 'bg-primary-50 text-primary-700'
                "
              >
                <i class="pi pi-question text-sm" />
              </span>
              <span class="flex-1 font-heading font-semibold text-ink">{{ faq.question }}</span>
              <i
                class="pi pi-chevron-down text-xs text-faint transition-transform duration-300 ease-spring"
                :class="{ 'rotate-180 text-accent-600': ouverte === faq.key }"
              />
            </button>

            <div
              class="grid transition-[grid-template-rows] duration-300 ease-spring"
              :class="ouverte === faq.key ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
            >
              <div class="overflow-hidden">
                <div
                  class="faq-answer border-t border-line px-5 py-4 text-sm leading-relaxed text-muted sm:ml-13 sm:px-6"
                  v-html="faq.answer"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Aucun résultat -->
        <div
          v-else
          class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
        >
          <span class="flex size-12 items-center justify-center rounded-leaf bg-primary-50 text-primary-700">
            <i class="pi pi-search text-xl" />
          </span>
          <p class="text-sm text-muted">{{ t("faq.no_results") }}</p>
        </div>

        <!-- Contact -->
        <div
          class="relative mt-14 overflow-hidden rounded-card bg-zinc-950 px-6 py-10 text-center text-white shadow-lift sm:px-10"
        >
          <div class="flag-stripe absolute inset-x-0 top-0 h-1" aria-hidden="true" />
          <div
            class="pointer-events-none absolute -top-20 -right-20 size-64 rounded-full bg-accent-500/20 blur-3xl"
            aria-hidden="true"
          />
          <span
            class="relative mx-auto mb-4 flex size-14 items-center justify-center rounded-leaf bg-accent-500 text-accent-950"
          >
            <i class="pi pi-headphones text-2xl" />
          </span>
          <h2 class="relative font-heading text-2xl font-bold">{{ t("faq.cta_title") }}</h2>
          <p class="relative mx-auto mt-3 max-w-xl text-sm text-white/70">{{ t("faq.cta_desc") }}</p>
          <div class="relative mt-6 flex flex-wrap justify-center gap-3">
            <AppButton
              variant="accent"
              icon="pi pi-envelope"
              :label="t('faq.cta_btn')"
              @click="navigateTo(localePath('/contact'))"
            />
            <a
              :href="`https://wa.me/${SITE.phone}`"
              target="_blank"
              rel="noopener"
              class="inline-flex h-10 items-center gap-2 rounded-leaf border border-white/15 bg-white/5 px-4 text-sm font-semibold transition-colors hover:border-white/30 hover:bg-white/10"
            >
              <i class="pi pi-whatsapp text-emerald-400" />
              WhatsApp
            </a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { SITE } from "~/config/site";

const { t } = useI18n();
const localePath = useLocalePath();

useHead({
  title: t("faq.page_title"),
  meta: [{ name: "description", content: t("faq.page_desc") }],
});

// Clés des questions par catégorie : ajouter une question = ajouter sa clé ici
const QUESTIONS: Record<string, string[]> = {
  exams: ["exams_1", "exams_2", "exams_3", "exams_4", "exams_5"],
  account: ["account_1", "account_2", "account_3", "account_4"],
  technical: ["technical_1", "technical_2", "technical_3"],
};

const selectedCategory = ref("all");
const recherche = ref("");
const ouverte = ref<string | null>(null);

const faqs = computed(() =>
  Object.entries(QUESTIONS).flatMap(([category, keys]) =>
    keys.map((key) => ({
      key,
      category,
      question: t(`faq.questions.${key}.q`),
      answer: t(`faq.questions.${key}.a`),
    })),
  ),
);

const categories = computed(() => [
  { id: "all", label: t("faq.categories.all"), icon: "pi pi-list", count: faqs.value.length },
  { id: "exams", label: t("faq.categories.exams"), icon: "pi pi-book", count: QUESTIONS.exams!.length },
  { id: "account", label: t("faq.categories.account"), icon: "pi pi-user", count: QUESTIONS.account!.length },
  { id: "technical", label: t("faq.categories.technical"), icon: "pi pi-cog", count: QUESTIONS.technical!.length },
]);

// Texte sans balises HTML (recherche + données structurées Google)
const sansHtml = (html: string) => html.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();

const filteredFaqs = computed(() => {
  const q = recherche.value.trim().toLowerCase();
  return faqs.value.filter((f) => {
    const dansCategorie = selectedCategory.value === "all" || f.category === selectedCategory.value;
    const correspond =
      !q || f.question.toLowerCase().includes(q) || sansHtml(f.answer).toLowerCase().includes(q);
    return dansCategorie && correspond;
  });
});

function basculer(key: string) {
  ouverte.value = ouverte.value === key ? null : key;
}

// Changer de catégorie ou de recherche referme la question ouverte
watch([selectedCategory, recherche], () => {
  ouverte.value = null;
});

// Données structurées FAQPage : Google peut afficher les questions dans ses résultats
useHead({
  script: [
    {
      type: "application/ld+json",
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: faqs.value.map((f) => ({
          "@type": "Question",
          name: f.question,
          acceptedAnswer: { "@type": "Answer", text: sansHtml(f.answer) },
        })),
      }),
    },
  ],
});
</script>

<style scoped>
/* Mise en forme du HTML des réponses (liens, listes, gras) */
.faq-answer :deep(a) {
  color: var(--color-accent-600);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.faq-answer :deep(strong) {
  color: var(--text-primary);
}
.faq-answer :deep(ul) {
  margin-top: 0.5rem;
  list-style: disc;
  padding-left: 1.25rem;
}
.faq-answer :deep(li) {
  margin-top: 0.25rem;
}
</style>