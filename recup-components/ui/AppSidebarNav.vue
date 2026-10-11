<script setup lang="ts">
import type {
  NavItemResolu,
  NavSectionResolue,
} from "~/composables/useNavigation";

const props = withDefaults(
  defineProps<{
    /** Sections déjà traduites, fournies par useNavigation() */
    sections: NavSectionResolue[];
    collapsed?: boolean;
    /** Sections dépliables (le titre devient un bouton). Désactivé par défaut. */
    collapsible?: boolean;
  }>(),
  {
    collapsed: false,
    collapsible: false,
  },
);

const route = useRoute();

function isActive(item: NavItemResolu) {
  const path = route.path.replace(/\/$/, "") || "/";
  if (item.exact) return path === item.to;
  return path === item.to || path.startsWith(`${item.to}/`);
}

function sectionKey(section: NavSectionResolue, i: number) {
  return section.title ?? `section-${i}`;
}

// Seule la section qui contient la page active s'ouvre par défaut,
// les autres se déroulent au clic.
const openSections = ref<Record<string, boolean>>({});

watch(
  [() => props.sections, () => route.path],
  ([sections]) => {
    sections.forEach((section, i) => {
      const key = sectionKey(section, i);
      if (section.items.some(isActive)) {
        openSections.value[key] = true;
      } else if (!(key in openSections.value)) {
        openSections.value[key] = false;
      }
    });
  },
  { immediate: true },
);

function toggleSection(key: string) {
  openSections.value[key] = !openSections.value[key];
}

// Une section est dépliée si le repli est désactivé, si elle n'a pas de
// titre, ou si la sidebar est réduite en icônes (tout reste accessible).
function isOpen(section: NavSectionResolue, i: number) {
  if (!props.collapsible || !section.title || props.collapsed) return true;
  return !!openSections.value[sectionKey(section, i)];
}
</script>

<template>
  <nav class="flex flex-col gap-4">
    <div
      v-for="(section, i) in sections"
      :key="sectionKey(section, i)"
      class="flex flex-col gap-1"
    >
      <template v-if="section.title && !collapsed">
        <button
          v-if="collapsible"
          type="button"
          class="mb-1 flex w-full items-center justify-between px-3 text-[11px] font-semibold uppercase tracking-wider text-faint transition-colors hover:text-ink"
          @click="toggleSection(sectionKey(section, i))"
        >
          <span>{{ section.title }}</span>
          <i
            class="pi pi-chevron-down text-[10px] transition-transform duration-200"
            :class="{ 'rotate-180': isOpen(section, i) }"
          />
        </button>
        <p
          v-else
          class="mb-1 px-3 text-[11px] font-semibold uppercase tracking-wider text-faint"
        >
          {{ section.title }}
        </p>
      </template>
      <div v-else-if="i > 0" class="mx-3 mb-1 h-px bg-line" />

      <div
        class="grid transition-[grid-template-rows] duration-200 ease-in-out"
        :class="isOpen(section, i) ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
      >
        <div class="flex flex-col gap-1 overflow-hidden">
          <NuxtLink
            v-for="item in section.items"
            :key="item.to"
            v-tooltip.right="{ value: item.label, disabled: !collapsed }"
            :to="item.to"
            class="relative flex h-10 shrink-0 items-center gap-3 rounded-xl text-sm font-medium transition-colors duration-200"
            :class="[
              collapsed ? 'justify-center' : 'px-3',
              isActive(item)
                ? 'bg-primary-50 text-primary-700 font-semibold'
                : 'text-muted hover:bg-card-2 hover:text-ink',
            ]"
          >
            <!-- Indicateur actif doré : signature de la marque -->
            <span
              v-if="isActive(item)"
              class="absolute inset-y-2 left-0 w-1 rounded-r-full bg-accent-500"
            />
            <i :class="[item.icon, 'text-base']" />
            <span v-if="!collapsed" class="flex-1 truncate">{{
              item.label
            }}</span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </nav>
</template>
