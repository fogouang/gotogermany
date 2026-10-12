<!-- components/ui/AppLangSwitcher.vue -->
<template>
  <button
    type="button"
    class="flex h-10 items-center gap-1.5 rounded-leaf border border-line bg-card px-3 text-xs font-semibold uppercase text-muted shadow-soft transition-colors hover:border-primary/30 hover:text-primary"
    :aria-label="t('common.language')"
    aria-haspopup="true"
    @click="menu?.toggle($event)"
  >
    <i class="pi pi-globe text-sm" />
    {{ locale }}
  </button>

  <Menu ref="menu" :model="items" popup>
    <template #item="{ item, props }">
      <a v-bind="props.action" class="flex items-center justify-between gap-8">
        <span>{{ item.label }}</span>
        <i
          v-if="item.code === locale"
          class="pi pi-check text-xs text-primary"
        />
      </a>
    </template>
  </Menu>
</template>

<script setup lang="ts">
const { t, locale, locales, setLocale } = useI18n();
const menu = ref<{ toggle: (e: Event) => void } | null>(null);

// Même cookie que la Navbar de la landing et le plugin i18n-locale.client.ts
const localeCookie = useCookie("app_locale", { maxAge: 60 * 60 * 24 * 365 });

type AppLocale = "en" | "fr" | "de";

// Noms affichés dans leur propre langue, quelle que soit la langue courante
const NOMS: Record<string, string> = {
  fr: "Français",
  en: "English",
  de: "Deutsch",
};

async function changeLocale(code: string) {
  localeCookie.value = code;
  await setLocale(code as AppLocale);
}

const items = computed(() =>
  (locales.value as { code: string; name?: string }[]).map((l) => ({
    label: NOMS[l.code] ?? l.name ?? l.code.toUpperCase(),
    code: l.code,
    command: () => changeLocale(l.code),
  })),
);
</script>
