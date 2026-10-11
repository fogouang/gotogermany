<script setup lang="ts">
import {
  CONDITIONS,
  CONTACT_CONDITIONS,
  type Langue,
} from "@/content/conditions";

const { locale } = useI18n();
const localePath = useLocalePath();

const contenu = computed(
  () => CONDITIONS[locale.value as Langue] ?? CONDITIONS.fr,
);

useSeo({
  title: contenu.value.seoTitre,
  description: contenu.value.seoDescription,
});

const sectionActive = ref(contenu.value.sections[0]?.id ?? "");

onMounted(() => {
  const observer = new IntersectionObserver(
    (entrees) => {
      for (const entree of entrees) {
        if (entree.isIntersecting) sectionActive.value = entree.target.id;
      }
    },
    { rootMargin: "-30% 0px -60% 0px" },
  );
  contenu.value.sections.forEach((s) => {
    const el = document.getElementById(s.id);
    if (el) observer.observe(el);
  });
  onBeforeUnmount(() => observer.disconnect());
});

function allerA(id: string) {
  document
    .getElementById(id)
    ?.scrollIntoView({ behavior: "smooth", block: "start" });
}
</script>

<template>
  <div class="bg-canvas">
    <!-- En-tête -->
    <AppPageHero
      icon="pi pi-file-check"
      watermark="Bedingungen"
      :eyebrow="contenu.eyebrow"
      :title="contenu.titre"
      :subtitle="contenu.intro"
    >
      <p class="mt-4 inline-flex items-center gap-2 text-sm text-faint">
        <i class="pi pi-calendar text-xs" />
        {{ contenu.maj }}
      </p>
    </AppPageHero>

    <div
      class="mx-auto grid max-w-5xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[220px_1fr]"
    >
      <!-- Sommaire -->
      <aside class="hidden lg:block">
        <nav class="sticky top-24">
          <p
            class="mb-3 text-xs font-semibold uppercase tracking-wider text-faint"
          >
            {{ contenu.sommaire }}
          </p>
          <ul class="space-y-1 border-l border-line">
            <li v-for="s in contenu.sections" :key="s.id">
              <button
                type="button"
                class="-ml-px block w-full border-l-2 py-1.5 pl-4 text-left text-sm transition-colors"
                :class="
                  sectionActive === s.id
                    ? 'border-accent-500 font-semibold text-ink'
                    : 'border-transparent text-muted hover:text-ink'
                "
                @click="allerA(s.id)"
              >
                {{ s.titre }}
              </button>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Sections -->
      <div class="space-y-6">
        <article
          v-for="s in contenu.sections"
          :id="s.id"
          :key="s.id"
          class="scroll-mt-24 rounded-card border border-line bg-card p-6 shadow-soft sm:p-8"
        >
          <h2 class="font-heading text-xl font-bold text-ink">{{ s.titre }}</h2>

          <p
            v-for="(p, i) in s.paragraphes"
            :key="`p-${i}`"
            class="mt-3 leading-relaxed text-muted"
          >
            {{ p }}
          </p>

          <ul v-if="s.liste?.length" class="mt-4 space-y-2.5">
            <li
              v-for="(item, i) in s.liste"
              :key="`l-${i}`"
              class="flex gap-3 leading-relaxed text-muted"
            >
              <i class="pi pi-check-circle mt-1 text-sm text-accent-500" />
              <span>{{ item }}</span>
            </li>
          </ul>

          <NuxtLink
            v-if="s.lien"
            :to="localePath(s.lien.to)"
            class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline"
          >
            {{ s.lien.label }}
            <i class="pi pi-arrow-right text-xs" />
          </NuxtLink>
        </article>

        <!-- Contact -->
        <div
          class="relative overflow-hidden rounded-card bg-zinc-950 p-6 text-white sm:p-8"
        >
          <div
            class="flag-stripe absolute inset-x-0 top-0 h-1"
            aria-hidden="true"
          />
          <h2 class="font-heading text-xl font-bold">
            {{ contenu.contact.titre }}
          </h2>
          <p class="mt-2 text-zinc-400">{{ contenu.contact.texte }}</p>

          <div class="mt-6 flex flex-wrap gap-3">
            <a
              :href="`mailto:${CONTACT_CONDITIONS.email}`"
              class="inline-flex items-center gap-2 rounded-xl bg-accent-500 px-4 py-2.5 text-sm font-semibold text-zinc-950 transition hover:bg-accent-400"
            >
              <i class="pi pi-envelope" />
              {{ contenu.contact.email }}
            </a>
            <a
              :href="`https://wa.me/${CONTACT_CONDITIONS.whatsapp}`"
              target="_blank"
              rel="noopener"
              class="inline-flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2.5 text-sm font-semibold transition hover:bg-white/10"
            >
              <i class="pi pi-whatsapp" />
              {{ contenu.contact.whatsapp }}
            </a>
          </div>

          <div
            class="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm text-zinc-400"
          >
            <a
              v-for="tel in CONTACT_CONDITIONS.telephones"
              :key="tel"
              :href="`tel:${tel.replace(/\s/g, '')}`"
              class="inline-flex items-center gap-2 hover:text-white"
            >
              <i class="pi pi-phone text-xs" />
              {{ tel }}
            </a>
            <span class="inline-flex items-center gap-2">
              <i class="pi pi-map-marker text-xs" />
              {{ CONTACT_CONDITIONS.ville }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
