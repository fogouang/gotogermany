<!-- pages/dashboard/sessions-live/index.vue -->
<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t("live_session.title") }}
      </h1>
      <p class="text-sm text-gray-500">{{ t("live_session.subtitle") }}</p>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <div
      v-else-if="!sessions.length"
      class="text-center py-16 bg-white rounded-xl border border-gray-100"
    >
      <i class="pi pi-microphone text-4xl text-gray-300 mb-3 block" />
      <p class="font-medium text-gray-600">
        {{ t("live_session.no_sessions_title") }}
      </p>
      <p class="text-sm text-gray-400">
        {{ t("live_session.no_sessions_subtitle") }}
      </p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <NuxtLink
        v-for="session in sessions"
        :key="session.id"
        :to="`/dashboard/sessions-live/${session.id}`"
        class="group bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-primary-200 transition-all flex flex-col gap-3"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-white text-xs font-bold bg-orange-500"
            >
              <i class="pi pi-microphone" />
            </div>
            <div>
              <p class="font-semibold text-gray-900 text-sm">
                {{ t("live_session.session_label") }}
              </p>
              <p class="text-xs text-gray-400">{{ formatDate(session.created_at) }}</p>
            </div>
          </div>
          <Tag :value="statusLabel(session.status)" :severity="statusSeverity(session.status)" />
        </div>

        <p
          v-if="session.status === 'ended' && session.examiner_notes"
          class="text-xs text-gray-500 line-clamp-2 leading-relaxed bg-gray-50 rounded-lg px-3 py-2"
        >
          {{ session.examiner_notes }}
        </p>

        <div class="flex items-center justify-end pt-1">
          <span
            class="text-xs text-primary-600 font-semibold flex items-center gap-1 group-hover:gap-2 transition-all"
          >
            {{ ctaLabel(session.status) }}
            <i class="pi pi-arrow-right text-xs" />
          </span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

import type { LiveSessionResponse } from "#shared/api";

const { t } = useI18n();
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
      preparing: "warning",
      live: "success",
      ended: "info",
      cancelled: "danger",
    } as Record<string, string>
  )[status] ?? "secondary";
}

function ctaLabel(status: string) {
  return status === "ended"
    ? t("live_session.see_notes")
    : t("live_session.join");
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("fr-FR", {
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