<template>
  <div v-if="activeOption">
    <!-- Élève de centre : niveau affiché mais verrouillé -->
    <span
      v-if="!canSwitch"
      v-tooltip.bottom="t('level_switch.locked')"
      class="inline-flex items-center gap-2 rounded-full border border-line bg-card px-3 py-1.5 text-sm font-semibold text-ink"
    >
      <span
        class="flex size-6 items-center justify-center rounded-full text-[10px] font-extrabold"
        :class="info(activeOption.exam.provider).badge"
      >
        {{ activeOption.level.cefr_code }}
      </span>
      <span class="hidden sm:inline">{{ label(activeOption) }}</span>
      <i class="pi pi-lock text-[10px] text-faint" />
    </span>

    <!-- Étudiant individuel : menu de changement -->
    <template v-else>
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3 py-1.5 text-sm font-semibold text-primary transition-colors hover:border-primary"
        :aria-label="t('level_switch.title')"
        @click="popover?.toggle($event)"
      >
        <span
          class="flex size-6 items-center justify-center rounded-full bg-primary text-[10px] font-extrabold text-white"
        >
          {{ activeOption.level.cefr_code }}
        </span>
        <span class="hidden sm:inline">{{ label(activeOption) }}</span>
        <i class="pi pi-chevron-down text-[10px]" />
      </button>

      <Popover ref="popover">
        <div class="w-64">
          <p class="px-1 pb-2 text-xs font-semibold text-muted">
            {{ t("level_switch.title") }}
          </p>
          <ul class="max-h-80 space-y-0.5 overflow-y-auto">
            <li v-for="o in sortedOptions" :key="o.level.id">
              <button
                type="button"
                class="flex w-full items-center gap-3 rounded-leaf px-2 py-2 text-left text-sm transition-colors"
                :class="
                  o.level.id === activeOption.level.id
                    ? 'bg-primary/10 text-primary'
                    : 'text-ink hover:bg-card-2'
                "
                :disabled="!!switching"
                @click="choose(o.level.id)"
              >
                <span
                  class="flex size-7 shrink-0 items-center justify-center rounded-full text-[10px] font-extrabold"
                  :class="
                    o.level.id === activeOption.level.id
                      ? 'bg-primary text-white'
                      : info(o.exam.provider).badge
                  "
                >
                  {{ o.level.cefr_code }}
                </span>
                <span class="min-w-0 flex-1 truncate font-medium">{{
                  label(o)
                }}</span>
                <i
                  v-if="switching === o.level.id"
                  class="pi pi-spin pi-spinner text-xs"
                />
                <i
                  v-else-if="o.level.id === activeOption.level.id"
                  class="pi pi-check text-xs"
                />
              </button>
            </li>
          </ul>
          <p class="mt-2 border-t border-line px-1 pt-2 text-[11px] text-muted">
            {{ t("level_switch.note") }}
          </p>
          <NuxtLink
            :to="localePath('/dashboard/examens/catalogue')"
            class="mt-1 block px-1 py-1 text-xs font-semibold text-primary hover:underline"
            @click="popover?.hide()"
          >
            {{ t("level_switch.all_exams") }}
          </NuxtLink>
        </div>
      </Popover>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { LevelOption } from "~/composables/useActiveLevel";

const { t } = useI18n();
const localePath = useLocalePath();
const toast = useToast();
const notify = useNotify();
const { info, orderOf } = useProviders();
const { options, activeOption, canSwitch, ensureCatalog, setActiveLevel } =
  useActiveLevel();

const popover = ref<{ toggle: (e: Event) => void; hide: () => void } | null>(
  null,
);
const switching = ref<string | null>(null);

const label = (o: LevelOption) =>
  `${info(o.exam.provider).brand} ${o.level.cefr_code}`;

const sortedOptions = computed(() =>
  [...options.value].sort(
    (a, b) =>
      orderOf(a.exam.provider) - orderOf(b.exam.provider) ||
      a.level.cefr_code.localeCompare(b.level.cefr_code),
  ),
);

async function choose(levelId: string) {
  if (levelId === activeOption.value?.level.id) return popover.value?.hide();
  switching.value = levelId;
  const result = await setActiveLevel(levelId);
  switching.value = null;
  if (!result.success) {
    toast.add({
      severity: "error",
      summary: result.error || t("onboarding.error"),
      life: 4000,
    });
    return;
  }
  const picked = options.value.find((o) => o.level.id === levelId);
  if (picked)
    notify.success(t("toast.level_changed", { level: label(picked) }));
  popover.value?.hide();
}

onMounted(ensureCatalog);
</script>
