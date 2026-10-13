<!-- pages/dashboard/sessions-live/index.vue -->
<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold text-ink">{{ t("live_session.title") }}</h1>
      <p class="mt-1 text-sm text-muted">{{ t("live_session.subtitle") }}</p>
    </header>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div v-for="i in 4" :key="i" class="h-36 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="!sessions.length"
      class="rounded-card border border-line bg-card py-16 text-center shadow-soft"
    >
      <i class="pi pi-microphone mb-3 block text-4xl text-faint" />
      <p class="font-medium text-ink">{{ t("live_session.no_sessions_title") }}</p>
      <p class="mt-1 text-sm text-muted">{{ t("live_session.no_sessions_subtitle") }}</p>
    </div>

    <!-- ── Sessions ── -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <NuxtLink
        v-for="session in sessions"
        :key="session.id"
        :to="localePath(`/dashboard/sessions-live/${session.id}`)"
        class="group flex flex-col gap-3 rounded-card border border-line bg-card p-5 shadow-soft transition-all hover:border-primary/40"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary">
              <i class="pi pi-microphone" />
            </div>
            <div>
              <p class="text-sm font-semibold text-ink">{{ t("live_session.session_label") }}</p>
              <p class="text-xs text-faint">{{ formatDate(session.created_at) }}</p>
            </div>
          </div>
          <Tag :value="statusLabel(session.status)" :severity="statusSeverity(session.status)" />
        </div>

        <p
          v-if="session.status === 'ended' && session.examiner_notes"
          class="line-clamp-2 rounded-leaf bg-card-2 px-3 py-2 text-xs leading-relaxed text-muted"
        >
          {{ session.examiner_notes }}
        </p>

        <div class="flex items-center justify-end pt-1">
          <span class="flex items-center gap-1 text-xs font-semibold text-primary transition-all group-hover:gap-2">
            {{ ctaLabel(session.status) }}
            <i class="pi pi-arrow-right text-xs" />
          </span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LiveSessionResponse } from "#shared/api";

definePageMeta({ layout: "dashboard" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
useHead({ title: t("live_session.page_title") });

const liveSessionStore = useLiveSessionStore();

const loading = ref(true);
const sessions = ref<LiveSessionResponse[]>([]);

function statusLabel(status: string) {
  return (
    {
      waiting: t("live_session.status_waiting"),
      preparing: t("live_session.status_preparing"),
      live: t("live_session.status_live"),
      ended: t("live_session.status_ended"),
      cancelled: t("live_session.status_cancelled"),
    } as Record<string, string>
  )[status] ?? status;
}

function statusSeverity(status: string) {
  return (
    {
      waiting: "secondary",
      preparing: "warn",
      live: "success",
      ended: "info",
      cancelled: "danger",
    } as Record<string, string>
  )[status] ?? "secondary";
}

function ctaLabel(status: string) {
  return status === "ended" ? t("live_session.see_notes") : t("live_session.join");
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(async () => {
  const result = await liveSessionStore.fetchMine();
  if (result.success) sessions.value = liveSessionStore.mine;
  loading.value = false;
});
</script>