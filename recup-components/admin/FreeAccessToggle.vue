<template>
  <div
    class="flex items-center justify-between bg-white rounded-2xl border border-gray-100 shadow-sm px-5 py-4"
  >
    <div class="flex items-center gap-3">
      <div
        :class="[
          'w-10 h-10 rounded-xl flex items-center justify-center',
          isFree ? 'bg-green-100' : 'bg-gray-100',
        ]"
      >
        <i
          :class="[
            'pi',
            isFree ? 'pi-lock-open text-green-600' : 'pi-lock text-gray-400',
          ]"
        ></i>
      </div>
      <div>
        <p class="font-semibold text-gray-900 text-sm">Mode accès libre</p>
        <p class="text-xs text-gray-400 mt-0.5">
          {{
            isFree
              ? "Tous les sujets sont ouverts à tous"
              : "Accès normal - paiement requis"
          }}
        </p>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <Tag
        :value="isFree ? 'Activé' : 'Désactivé'"
        :severity="isFree ? 'success' : 'secondary'"
      />
      <Button
        :label="isFree ? 'Fermer' : 'Ouvrir'"
        :severity="isFree ? 'danger' : 'success'"
        :icon="isFree ? 'pi pi-lock' : 'pi pi-lock-open'"
        size="small"
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

// isFree est un computed qui lit directement le store
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
        ? "Tous les users ont accès à tous les sujets."
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
