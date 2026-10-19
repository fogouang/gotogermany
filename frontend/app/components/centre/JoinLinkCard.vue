<template>
  <div class="rounded-card border border-line bg-card p-5 shadow-soft">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="flex items-start gap-3">
        <span
          class="grid size-10 shrink-0 place-items-center rounded-leaf bg-primary/10 text-primary"
        >
          <i class="pi pi-link" />
        </span>
        <div>
          <p class="font-semibold text-ink">{{ t("centre_join.title") }}</p>
          <p class="mt-0.5 text-sm text-muted">
            {{ t("centre_join.subtitle") }}
          </p>
        </div>
      </div>
      <span
        v-if="link && !link.enabled"
        class="rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-semibold text-red-600"
      >
        {{ t("centre_join.disabled_badge") }}
      </span>
    </div>

    <div
      v-if="loading"
      class="mt-4 h-11 animate-pulse rounded-leaf bg-card-2"
    />

    <p v-else-if="loadError" class="mt-4 text-sm text-red-600">
      {{ t("centre_join.load_error") }}
    </p>

    <template v-else-if="link">
      <div class="mt-4 flex flex-col gap-2 sm:flex-row">
        <div
          class="min-w-0 flex-1 truncate rounded-leaf border border-line bg-card-2 px-3 py-2.5 font-mono text-xs text-ink"
          :class="{ 'opacity-50': !link.enabled }"
        >
          {{ url }}
        </div>
        <div class="flex gap-2">
          <Button
            :label="t('centre_join.copy')"
            icon="pi pi-copy"
            outlined
            :disabled="!link.enabled"
            @click="copy"
          />
          <a
            :href="whatsappHref"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-2 rounded-leaf bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
            :class="{ 'pointer-events-none opacity-50': !link.enabled }"
          >
            <i class="pi pi-whatsapp" />
            {{ t("centre_join.share_whatsapp") }}
          </a>
        </div>
      </div>

      <p v-if="!link.enabled" class="mt-2 text-xs text-muted">
        {{ t("centre_join.disabled_hint") }}
      </p>

      <!-- Gestion du lien : directeur uniquement -->
      <div
        v-if="authStore.isDirector"
        class="mt-4 flex flex-wrap gap-2 border-t border-line pt-4"
      >
        <Button
          :label="t('centre_join.regenerate')"
          icon="pi pi-refresh"
          text
          size="small"
          :loading="busy === 'regenerate'"
          @click="regenerate"
        />
        <Button
          :label="
            link.enabled ? t('centre_join.disable') : t('centre_join.enable')
          "
          :icon="link.enabled ? 'pi pi-ban' : 'pi pi-check'"
          text
          size="small"
          :severity="link.enabled ? 'danger' : 'success'"
          :loading="busy === 'toggle'"
          @click="toggle"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
interface JoinLink {
  token: string;
  enabled: boolean;
  center_name: string;
}

const { t } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const toast = useToast();
const runtimeConfig = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const base = runtimeConfig.public.apiBaseUrl || "http://localhost:8001";
const headers = (): Record<string, string> => {
  const h: Record<string, string> = {};
  if (tokenCookie.value) h.Authorization = `Bearer ${tokenCookie.value}`;
  return h;
};

const link = ref<JoinLink | null>(null);
const loading = ref(true);
const loadError = ref(false);
const busy = ref<"regenerate" | "toggle" | null>(null);
const origin = ref("");

const url = computed(() =>
  link.value
    ? `${origin.value}${localePath(`/rejoindre/${link.value.token}`)}`
    : "",
);

const whatsappHref = computed(
  () =>
    `https://wa.me/?text=${encodeURIComponent(
      t("centre_join.share_message", {
        center: link.value?.center_name ?? "",
        url: url.value,
      }),
    )}`,
);

async function load() {
  loading.value = true;
  loadError.value = false;
  try {
    link.value = await $fetch<JoinLink>(`${base}/api/v1/centers/me/join-link`, {
      headers: headers(),
    });
  } catch {
    loadError.value = true;
  } finally {
    loading.value = false;
  }
}

async function copy() {
  try {
    await navigator.clipboard.writeText(url.value);
    toast.add({
      severity: "success",
      summary: t("centre_join.copied"),
      life: 2500,
    });
  } catch {
    toast.add({
      severity: "error",
      summary: t("centre_join.error_generic"),
      life: 3000,
    });
  }
}

async function regenerate() {
  if (!window.confirm(t("centre_join.regenerate_confirm"))) return;
  busy.value = "regenerate";
  try {
    link.value = await $fetch<JoinLink>(
      `${base}/api/v1/centers/me/join-link/regenerate`,
      {
        method: "POST",
        headers: headers(),
      },
    );
    toast.add({
      severity: "success",
      summary: t("centre_join.regenerated"),
      life: 3000,
    });
  } catch {
    toast.add({
      severity: "error",
      summary: t("centre_join.error_generic"),
      life: 3000,
    });
  } finally {
    busy.value = null;
  }
}

async function toggle() {
  if (!link.value) return;
  busy.value = "toggle";
  try {
    link.value = await $fetch<JoinLink>(`${base}/api/v1/centers/me/join-link`, {
      method: "PATCH",
      headers: headers(),
      body: { enabled: !link.value.enabled },
    });
  } catch {
    toast.add({
      severity: "error",
      summary: t("centre_join.error_generic"),
      life: 3000,
    });
  } finally {
    busy.value = null;
  }
}

onMounted(() => {
  origin.value = window.location.origin;
  load();
});
</script>
