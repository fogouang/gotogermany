<!-- components/admin/FreeAccessToggle.vue -->
<template>
  <div
    class="flex flex-col gap-4 rounded-card border bg-card p-5 shadow-soft transition-colors sm:flex-row sm:items-center sm:justify-between"
    :class="isFree ? 'border-emerald-500/40' : 'border-line'"
  >
    <div class="flex items-center gap-3">
      <span
        class="flex size-10 shrink-0 items-center justify-center rounded-leaf transition-colors"
        :class="
          isFree ? 'bg-emerald-500/10 text-emerald-600' : 'bg-card-2 text-muted'
        "
      >
        <i :class="isFree ? 'pi pi-lock-open' : 'pi pi-lock'" />
      </span>
      <div>
        <p class="text-sm font-semibold text-ink">Mode accès libre</p>
        <p class="mt-0.5 text-xs text-muted">
          {{
            isFree
              ? "Tous les sujets sont ouverts à tous"
              : "Accès normal, paiement requis"
          }}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <span
        class="rounded-full px-2.5 py-1 text-[11px] font-semibold"
        :class="
          isFree
            ? 'bg-emerald-500/10 text-emerald-600'
            : 'bg-card-2 text-muted'
        "
      >
        {{ isFree ? "Activé" : "Désactivé" }}
      </span>
      <Button
        :label="isFree ? 'Fermer' : 'Ouvrir'"
        :severity="isFree ? 'danger' : 'success'"
        :icon="isFree ? 'pi pi-lock' : 'pi pi-lock-open'"
        size="small"
        :outlined="isFree"
        :loading="toggling"
        @click="toggle"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { SettingsService } from "#shared/api";

const toggling = ref(false);
const toast = useToast();
const appStore = useAppStore();

// isFree lit directement le store
const isFree = computed(() => appStore.freeAccessMode);

// fetchStatus met à jour le store
const fetchStatus = async () => {
  try {
    const res =
      await SettingsService.getFreeAccessModeApiV1SettingsFreeAccessGet();
    appStore.freeAccessMode = res.free_access_mode;
  } catch {}
};

const toggle = async () => {
  toggling.value = true;
  try {
    await SettingsService.toggleFreeAccessModeApiV1SettingsFreeAccessTogglePost();
    appStore.freeAccessMode = !appStore.freeAccessMode;
    toast.add({
      severity: isFree.value ? "success" : "warn",
      summary: isFree.value ? "Accès libre activé" : "Accès libre désactivé",
      detail: isFree.value
        ? "Tous les utilisateurs ont accès à tous les sujets."
        : "Le paiement est à nouveau requis.",
      life: 4000,
    });
  } catch {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Impossible de changer le statut.",
      life: 3000,
    });
  } finally {
    toggling.value = false;
  }
};

onMounted(fetchStatus);
</script>