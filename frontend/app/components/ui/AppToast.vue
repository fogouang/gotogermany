<template>
  <Toast
    position="top-right"
    :pt="{
      message: { class: 'bg-transparent! border-0! shadow-none! p-0! mb-3!' },
    }"
    :breakpoints="{
      '640px': { width: 'calc(100vw - 2rem)', right: '1rem', left: '1rem' },
    }"
  >
    <template #container="{ message, closeCallback }">
      <div
        class="relative flex w-full items-start gap-3 overflow-hidden rounded-card border border-line bg-card p-4 shadow-soft sm:w-96"
        role="status"
      >
        <span
          class="flex size-9 shrink-0 items-center justify-center rounded-full"
          :class="tone(message.severity).bubble"
        >
          <i class="pi text-sm" :class="tone(message.severity).icon" />
        </span>

        <div class="min-w-0 flex-1 pt-0.5">
          <p class="text-sm font-semibold text-ink">{{ message.summary }}</p>
          <p
            v-if="message.detail"
            class="mt-0.5 text-sm leading-snug text-muted"
          >
            {{ message.detail }}
          </p>
        </div>

        <button
          type="button"
          class="flex size-7 shrink-0 items-center justify-center rounded-full text-faint transition-colors hover:bg-card-2 hover:text-ink"
          :aria-label="t('toast.close')"
          @click="closeCallback"
        >
          <i class="pi pi-times text-xs" />
        </button>

        <!-- Barre de temps restant -->
        <span
          v-if="message.life"
          class="toast-progress absolute inset-x-0 bottom-0 h-0.5"
          :class="tone(message.severity).bar"
          :style="{ animationDuration: `${message.life}ms` }"
        />
      </div>
    </template>
  </Toast>
</template>

<script setup lang="ts">
const { t } = useI18n();
const notify = useNotify();

const tone = (severity?: string) =>
  ({
    success: {
      bubble: "bg-emerald-500/10 text-emerald-600",
      icon: "pi-check",
      bar: "bg-emerald-500",
    },
    error: {
      bubble: "bg-red-500/10 text-red-600",
      icon: "pi-times-circle",
      bar: "bg-red-500",
    },
    warn: {
      bubble: "bg-amber-500/15 text-amber-600",
      icon: "pi-exclamation-triangle",
      bar: "bg-amber-500",
    },
    info: {
      bubble: "bg-sky-500/10 text-sky-600",
      icon: "pi-info-circle",
      bar: "bg-sky-500",
    },
  })[severity ?? "info"] ?? {
    bubble: "bg-primary/10 text-primary",
    icon: "pi-bell",
    bar: "bg-primary",
  };

// ── Connexion internet (toutes les pages) ──
const onOffline = () =>
  notify.warn(t("toast.offline"), t("toast.offline_detail"));
const onOnline = () => notify.success(t("toast.online"));

onMounted(() => {
  window.addEventListener("offline", onOffline);
  window.addEventListener("online", onOnline);
});
onBeforeUnmount(() => {
  window.removeEventListener("offline", onOffline);
  window.removeEventListener("online", onOnline);
});
</script>
<style scoped>
.toast-progress {
  transform-origin: left;
  animation-name: toast-shrink;
  animation-timing-function: linear;
  animation-fill-mode: forwards;
}

@keyframes toast-shrink {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .toast-progress {
    animation: none;
    opacity: 0.4;
  }
}
</style>
