<script setup lang="ts">
const visible = defineModel<boolean>("visible", { default: false });

const props = withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    icon?: string;
    tone?: "brand" | "danger";
    confirmLabel?: string;
    cancelLabel?: string;
    loading?: boolean;
    width?: string;
    hideFooter?: boolean;
  }>(),
  {
    tone: "brand",
    confirmLabel: "Confirmer",
    cancelLabel: "Annuler",
    loading: false,
    width: "32rem",
    hideFooter: false,
  },
);

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();

// L'échelle primary s'inverse déjà en sombre (fond doré sombre, or lisible) :
// pas de variantes dark: pour la marque.
const iconClass = computed(() =>
  props.tone === "danger"
    ? "bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-300"
    : "bg-primary-50 text-primary-700",
);

function cancel() {
  emit("cancel");
  visible.value = false;
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    dismissable-mask
    :draggable="false"
    :style="{ width }"
    :breakpoints="{ '640px': '92vw' }"
    :pt="{ mask: { class: 'backdrop-blur-sm' } }"
  >
    <template #header>
      <div class="flex items-start gap-3">
        <span
          v-if="icon"
          class="flex size-10 shrink-0 items-center justify-center rounded-leaf"
          :class="iconClass"
        >
          <i :class="[icon, 'text-lg']" />
        </span>
        <div>
          <h3 class="font-heading text-lg font-semibold text-ink">{{ title }}</h3>
          <p v-if="subtitle" class="mt-0.5 text-sm text-faint">{{ subtitle }}</p>
        </div>
      </div>
    </template>

    <div class="text-muted">
      <slot />
    </div>

    <template v-if="!hideFooter" #footer>
      <slot name="footer">
        <AppButton variant="ghost" :label="cancelLabel" @click="cancel" />
        <AppButton
          :variant="tone === 'danger' ? 'danger' : 'primary'"
          :label="confirmLabel"
          :loading="loading"
          @click="emit('confirm')"
        />
      </slot>
    </template>
  </Dialog>
</template>