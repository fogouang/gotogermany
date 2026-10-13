<template>
  <div class="space-y-5 pb-10">
    <p class="text-sm text-muted">{{ t("dashboard_exams.subtitle") }}</p>

    <!-- ── Filtres (inutiles s'il n'y a qu'un examen, cas de l'élève de centre) ── -->
    <div v-if="visibleCatalog.length > 1" class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in providerOptions"
          :key="p.value"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="selectedProvider === p.value ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="selectedProvider = p.value"
        >
          {{ p.label }}
        </button>
        <span class="mx-1 hidden h-7 w-px bg-line sm:block" />
        <button
          v-for="l in levelOptions"
          :key="l.value"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="selectedLevel === l.value ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="selectedLevel = l.value"
        >
          {{ l.label }}
        </button>
      </div>

      <IconField class="w-full xl:w-72">
        <InputIcon class="pi pi-search" />
        <InputText v-model="searchQuery" class="w-full" :placeholder="t('dashboard_exams.search_placeholder')" />
      </IconField>
    </div>

    <!-- ── Chargement ── -->
    <div v-if="examsStore.loading && visibleCatalog.length === 0" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div v-for="n in 6" :key="n" class="h-40 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Élève de centre sans examen attribué ── -->
    <div
      v-else-if="isCenterStudent && !authStore.targetLevelId"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-14 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-amber-500/15 text-amber-600">
        <i class="pi pi-info-circle" />
      </span>
      <p class="font-medium text-ink">{{ t("dashboard.status.no_level_title") }}</p>
      <p class="max-w-md text-sm text-muted">{{ t("dashboard.status.no_level_text") }}</p>
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="groups.length === 0"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-14 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-card-2 text-muted">
        <i class="pi pi-inbox" />
      </span>
      <template v-if="hasFilters">
        <p class="font-medium text-ink">{{ t("dashboard_exams.empty_title") }}</p>
        <p class="text-sm text-muted">{{ t("dashboard_exams.empty_subtitle") }}</p>
        <Button :label="t('dashboard_exams.reset')" icon="pi pi-filter-slash" size="small" outlined @click="resetFilters" />
      </template>
      <p v-else class="text-sm text-muted">{{ t("dashboard.no_exams") }}</p>
    </div>

    <!-- ── Catalogue groupé par organisme ── -->
    <div v-else class="space-y-8">
      <section v-for="group in groups" :key="group.key" class="space-y-3">
        <header class="flex items-center gap-3">
          <span class="size-2.5 shrink-0 rounded-full" :class="providerStyle(group.key).dot" />
          <h2 class="text-sm font-semibold text-ink">{{ providerName(group.key) }}</h2>
          <span class="h-px flex-1 bg-line" />
          <span v-if="group.cards.length" class="text-xs text-faint">{{ group.cards.length }}</span>
        </header>

        <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <!-- Organisme pas encore au catalogue -->
          <article
            v-if="group.comingSoon"
            class="flex items-center gap-4 rounded-card border border-dashed border-line bg-card/60 p-5"
          >
            <span
              class="flex size-14 shrink-0 items-center justify-center rounded-leaf text-sm font-extrabold opacity-60"
              :class="providerStyle(group.key).badge"
            >
              {{ providerShort(group.key) }}
            </span>
            <div class="min-w-0">
              <p class="font-semibold text-ink">{{ providerName(group.key) }}</p>
              <p class="mt-0.5 text-xs text-muted">{{ t("dashboard_exams.coming_soon_text") }}</p>
              <span class="mt-2 inline-flex items-center gap-1 rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted">
                <i class="pi pi-clock text-[9px]" />
                {{ t("dashboard_exams.coming_soon") }}
              </span>
            </div>
          </article>

          <!-- Une carte par niveau -->
          <article
            v-for="card in group.cards"
            :key="card.level.id"
            class="group flex flex-col overflow-hidden rounded-card border bg-card shadow-soft transition-colors"
            :class="card.state === 'soon' ? 'border-dashed border-line opacity-75' : 'border-line hover:border-primary/40'"
          >
            <component
              :is="card.state === 'soon' ? 'div' : NuxtLink"
              :to="card.state === 'soon' ? undefined : localePath(`/dashboard/examens/${card.exam.slug}`)"
              class="flex flex-1 items-start gap-4 p-5"
            >
              <span
                class="flex size-14 shrink-0 flex-col items-center justify-center rounded-leaf"
                :class="providerStyle(card.exam.provider).badge"
              >
                <span class="text-lg font-extrabold leading-none">{{ card.level.cefr_code }}</span>
                <span class="mt-0.5 text-[9px] font-bold uppercase tracking-wider opacity-75">
                  {{ providerShort(card.exam.provider) }}
                </span>
              </span>
              <span class="min-w-0 flex-1">
                <span
                  class="line-clamp-2 block font-semibold leading-snug text-ink"
                  :class="{ 'transition-colors group-hover:text-primary': card.state !== 'soon' }"
                >
                  {{ card.exam.name }}
                </span>
                <span class="mt-1 block text-xs text-muted">
                  {{ providerName(card.exam.provider) }}
                  <template v-if="card.state !== 'soon'"> · {{ card.level.subject_count }} {{ t("payment.subjet") }}</template>
                </span>
                <span v-if="card.exam.description" class="mt-1.5 line-clamp-2 block text-xs text-faint">
                  {{ card.exam.description }}
                </span>
              </span>
            </component>

            <footer class="flex min-h-12 items-center gap-2 border-t border-line px-5 py-2.5">
              <!-- Bientôt -->
              <span v-if="card.state === 'soon'" class="inline-flex items-center gap-1 text-xs font-medium text-muted">
                <i class="pi pi-clock text-[10px]" />
                {{ t("dashboard_exams.coming_soon") }}
              </span>

              <!-- Accès ouvert -->
              <template v-else-if="card.state === 'open'">
                <span class="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600">
                  <i class="pi pi-check-circle text-[9px]" />
                  {{ card.level.is_free ? t("dashboard.level_free") : t("dashboard.level_active") }}
                </span>
                <NuxtLink
                  :to="localePath(`/dashboard/examens/${card.exam.slug}`)"
                  class="ml-auto inline-flex items-center gap-1 text-sm font-semibold text-primary"
                >
                  {{ t("dashboard.start") }}
                  <i class="pi pi-arrow-right text-[10px] transition-transform group-hover:translate-x-0.5" />
                </NuxtLink>
              </template>

              <!-- Verrouillé : essai gratuit + déblocage -->
              <template v-else>
                <span class="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600">
                  <i class="pi pi-lock text-[9px]" />
                  {{ t("dashboard.level_preview") }}
                </span>
                <NuxtLink
                  v-if="!isCenterStudent"
                  :to="localePath(`/dashboard/paiement?level_id=${card.level.id}`)"
                  class="ml-auto inline-flex items-center gap-1.5 rounded-leaf bg-primary px-3 py-1.5 text-xs font-semibold text-white transition-opacity hover:opacity-90"
                >
                  <i class="pi pi-unlock text-[10px]" />
                  {{ card.level.price ? t("dashboard_exams.unlock_price", { price: fcfa(card.level.price) }) : t("dashboard.unlock") }}
                </NuxtLink>
              </template>
            </footer>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NuxtLink } from "#components";
import type { ExamCatalogResponse, LevelAccessResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Prüfungen" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const examsStore = useExamsStore();
const { visibleCatalog, isCenterStudent } = useVisibleCatalog();

// ── Format ──
const intlLocale = computed(() => ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ?? "en-GB");
const fcfa = (n: number) => `${Math.round(n).toLocaleString(intlLocale.value)} FCFA`;

// ── Organismes (clé normalisée : minuscules, sans accent) ──
const norm = (p?: string | null) =>
  (p ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

const PROVIDERS: Record<string, { name: string; short: string; badge: string; dot: string }> = {
  goethe: { name: "Goethe-Institut", short: "GI", badge: "bg-emerald-500/10 text-emerald-600", dot: "bg-emerald-500" },
  telc: { name: "telc", short: "TE", badge: "bg-red-500/10 text-red-600", dot: "bg-red-500" },
  osd: { name: "ÖSD", short: "ÖSD", badge: "bg-sky-500/10 text-sky-600", dot: "bg-sky-500" },
  testdaf: { name: "TestDaF", short: "TD", badge: "bg-violet-500/10 text-violet-600", dot: "bg-violet-500" },
  ecl: { name: "ECL", short: "ECL", badge: "bg-amber-500/15 text-amber-600", dot: "bg-amber-500" },
};
const PROVIDER_ORDER = Object.keys(PROVIDERS);
const orderOf = (key: string) => PROVIDER_ORDER.indexOf(key) + 1 || 99;

const providerName = (p: string) => PROVIDERS[norm(p)]?.name ?? p;
const providerShort = (p: string) => PROVIDERS[norm(p)]?.short ?? p.slice(0, 2).toUpperCase();
const providerStyle = (p: string) => PROVIDERS[norm(p)] ?? { badge: "bg-primary/10 text-primary", dot: "bg-primary" };

// ── Filtres construits à partir du catalogue réel ──
const searchQuery = ref("");
const selectedProvider = ref("");
const selectedLevel = ref("");

const hasFilters = computed(() => !!(searchQuery.value || selectedProvider.value || selectedLevel.value));

const providerOptions = computed(() => {
  const present = [...new Set(visibleCatalog.value.map((e) => norm(e.provider)))].sort((a, b) => orderOf(a) - orderOf(b));
  return [
    { label: t("dashboard_exams.all_providers"), value: "" },
    ...present.map((p) => ({ label: PROVIDERS[p]?.name ?? p, value: p })),
  ];
});

const levelOptions = computed(() => {
  const codes = [...new Set(visibleCatalog.value.flatMap((e) => (e.levels ?? []).map((l) => l.cefr_code)))].sort();
  return [{ label: t("dashboard_exams.all_levels"), value: "" }, ...codes.map((c) => ({ label: c, value: c }))];
});

// ── Cartes : une par niveau ──
type CardState = "open" | "locked" | "soon";
type Card = { exam: ExamCatalogResponse; level: LevelAccessResponse; state: CardState };

const stateOf = (level: LevelAccessResponse): CardState => {
  if (!level.subject_count) return "soon";
  return level.has_access || level.is_free ? "open" : "locked";
};

const cards = computed<Card[]>(() => {
  const q = searchQuery.value.trim().toLowerCase();
  return visibleCatalog.value
    .filter(
      (e) =>
        (!q ||
          e.name.toLowerCase().includes(q) ||
          e.description?.toLowerCase().includes(q) ||
          e.provider.toLowerCase().includes(q)) &&
        (!selectedProvider.value || norm(e.provider) === selectedProvider.value),
    )
    .flatMap((exam) =>
      [...(exam.levels ?? [])]
        .filter((l) => !selectedLevel.value || l.cefr_code === selectedLevel.value)
        .sort((a, b) => a.display_order - b.display_order)
        .map((level) => ({ exam, level, state: stateOf(level) })),
    );
});

// Ouverts d'abord, puis verrouillés, puis à venir
const STATE_ORDER: Record<CardState, number> = { open: 0, locked: 1, soon: 2 };

const groups = computed(() => {
  const map = new Map<string, Card[]>();
  for (const card of cards.value) {
    const key = norm(card.exam.provider) || "-";
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(card);
  }

  const list = [...map.entries()].map(([key, list]) => ({
    key,
    comingSoon: false,
    cards: list.sort(
      (a, b) => STATE_ORDER[a.state] - STATE_ORDER[b.state] || a.level.cefr_code.localeCompare(b.level.cefr_code),
    ),
  }));

  // Organismes connus mais absents du catalogue : visibles comme "bientôt"
  // (pas pour l'élève de centre, ni quand un filtre est actif)
  if (!isCenterStudent.value && !hasFilters.value) {
    for (const key of PROVIDER_ORDER) {
      if (!map.has(key)) list.push({ key, comingSoon: true, cards: [] });
    }
  }

  return list.sort((a, b) => orderOf(a.key) - orderOf(b.key));
});

const resetFilters = () => {
  searchQuery.value = "";
  selectedProvider.value = "";
  selectedLevel.value = "";
};

onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
});
</script>