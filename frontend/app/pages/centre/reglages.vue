<!-- pages/centre/reglages.vue -->
<template>
  <div class="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
    <!-- ── Colonne gauche : formulaires ── -->
    <div class="space-y-6">
      <!-- Adresse -->
      <section class="space-y-4 rounded-card border border-line bg-card p-6 shadow-soft">
        <header class="flex items-start gap-3">
          <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary">
            <i class="pi pi-map-marker" />
          </span>
          <div>
            <h3 class="font-semibold text-ink">{{ t("centre.settings.address_title") }}</h3>
            <p class="text-xs text-muted">{{ t("centre.settings.address_text") }}</p>
          </div>
        </header>

        <form class="space-y-4" @submit.prevent="handleSaveAddress">
          <div>
            <label for="center-address" class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("centre.settings.address_label") }}
            </label>
            <InputText
              id="center-address"
              v-model="addressForm"
              class="w-full"
              :placeholder="t('centre.settings.address_placeholder')"
            />
          </div>

          <Message v-if="addressError" severity="error" :closable="false">{{ addressError }}</Message>

          <Button
            type="submit"
            :label="t('common.save')"
            icon="pi pi-check"
            :loading="savingAddress"
            :disabled="addressForm.trim() === (currentAddress ?? '')"
          />
        </form>
      </section>

      <!-- Logo -->
      <section class="space-y-4 rounded-card border border-line bg-card p-6 shadow-soft">
        <header class="flex items-start gap-3">
          <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary">
            <i class="pi pi-image" />
          </span>
          <div>
            <h3 class="font-semibold text-ink">{{ t("centre.settings.logo_title") }}</h3>
            <p class="text-xs text-muted">{{ t("centre.settings.logo_text") }}</p>
          </div>
        </header>

        <input
          ref="fileInput"
          type="file"
          accept="image/png,image/jpeg"
          class="hidden"
          @change="handleLogoSelect"
        />

        <div class="flex flex-wrap items-center gap-3">
          <Button
            :label="selectedLogoFile ? t('centre.settings.change_file') : t('centre.settings.choose_file')"
            icon="pi pi-folder-open"
            outlined
            @click="fileInput?.click()"
          />
          <span v-if="selectedLogoFile" class="min-w-0 truncate text-sm text-muted">
            {{ selectedLogoFile.name }}
          </span>
        </div>

        <Message v-if="logoError" severity="error" :closable="false">{{ logoError }}</Message>

        <Button
          v-if="selectedLogoFile"
          :label="t('centre.settings.upload_logo')"
          icon="pi pi-upload"
          :loading="uploadingLogo"
          @click="handleUploadLogo"
        />
      </section>
    </div>

    <!-- ── Colonne droite : aperçu de l'en-tête du reçu ── -->
    <section class="rounded-card border border-line bg-card p-6 shadow-soft lg:sticky lg:top-0">
      <div class="mb-4 flex items-center justify-between gap-3">
        <h3 class="font-semibold text-ink">{{ t("centre.settings.preview_title") }}</h3>
        <span
          v-if="hasPendingChanges"
          class="rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
        >
          {{ t("centre.settings.preview_pending") }}
        </span>
      </div>

      <div v-if="loadingPreview" class="h-40 animate-pulse rounded-leaf bg-card-2" />

      <!-- Un reçu est toujours imprimé sur fond blanc : l'aperçu reste clair en mode sombre -->
      <div v-else class="rounded-leaf border border-line bg-white p-6 text-gray-900 shadow-sm">
        <div class="flex items-start justify-between gap-4 border-b border-gray-200 pb-4">
          <div class="min-w-0">
            <img
              v-if="previewLogoUrl"
              :src="previewLogoUrl"
              :alt="t('centre.settings.logo_title')"
              class="mb-3 h-14 max-w-48 object-contain"
            />
            <p v-else class="mb-3 text-xs italic text-gray-400">
              {{ t("centre.settings.no_logo") }}
            </p>
            <p class="truncate text-lg font-bold">{{ centerName }}</p>
            <p v-if="previewAddress" class="mt-1 text-sm text-gray-500">{{ previewAddress }}</p>
            <p v-else class="mt-1 text-sm italic text-gray-300">
              {{ t("centre.settings.no_address") }}
            </p>
          </div>
          <i class="pi pi-receipt text-2xl text-gray-300" />
        </div>
        <div class="mt-4 space-y-2">
          <div class="h-2.5 w-2/3 rounded bg-gray-100" />
          <div class="h-2.5 w-1/2 rounded bg-gray-100" />
          <div class="h-2.5 w-3/4 rounded bg-gray-100" />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "centre", watermark: "Einstellungen" });

const { t } = useI18n();
const centerStaffStore = useCenterStaffStore();
const toast = useToast();

const TAILLE_MAX = 2 * 1024 * 1024; // 2 Mo
const TYPES_ACCEPTES = ["image/png", "image/jpeg"];

// ── État courant (enregistré) ──
const loadingPreview = ref(true);
const centerName = ref("");
const currentAddress = ref<string | null>(null);
const currentLogoUrl = ref<string | null>(null);

// ── Adresse ──
const addressForm = ref("");
const savingAddress = ref(false);
const addressError = ref<string | null>(null);

// ── Logo ──
const fileInput = ref<HTMLInputElement | null>(null);
const selectedLogoFile = ref<File | null>(null);
const localLogoUrl = ref<string | null>(null);
const uploadingLogo = ref(false);
const logoError = ref<string | null>(null);

// L'aperçu montre ce qui est en cours de saisie, avant enregistrement
const previewLogoUrl = computed(() => localLogoUrl.value ?? currentLogoUrl.value);
const previewAddress = computed(() => addressForm.value.trim() || null);
const hasPendingChanges = computed(
  () => !!selectedLogoFile.value || (previewAddress.value ?? "") !== (currentAddress.value ?? ""),
);

function libererApercuLocal() {
  if (localLogoUrl.value) URL.revokeObjectURL(localLogoUrl.value);
  localLogoUrl.value = null;
}

async function loadCurrentSettings(remplirFormulaire = true) {
  loadingPreview.value = true;

  const result = await centerStaffStore.fetchMyCenterDetails();

  if (result.success && result.center) {
    centerName.value = result.center.name;
    currentAddress.value = result.center.address ?? null;
    // Après l'envoi du logo, on ne touche pas à une adresse en cours de saisie
    if (remplirFormulaire) addressForm.value = result.center.address ?? "";

    if (result.center.logo_path) {
      const config = useRuntimeConfig();
      const base = config.public.apiBaseUrl || "http://localhost:8001";
      // logo_path est un chemin disque local (storage/center_logos/xxx),
      // exposé via le mount /center-logos : on ne garde que le nom de fichier.
      // Le paramètre ?v= évite l'ancienne image en cache après un nouvel envoi.
      const filename = result.center.logo_path.split(/[\\/]/).pop();
      currentLogoUrl.value = `${base}/center-logos/${filename}?v=${Date.now()}`;
    }
  }

  loadingPreview.value = false;
}

async function handleSaveAddress() {
  savingAddress.value = true;
  addressError.value = null;

  const address = addressForm.value.trim() || null;
  const result = await centerStaffStore.updateMyCenter({ address });

  savingAddress.value = false;

  if (result.success) {
    currentAddress.value = address;
    toast.add({ severity: "success", summary: t("centre.settings.address_saved"), life: 3000 });
  } else {
    addressError.value = result.error || t("centre.settings.save_error");
  }
}

function handleLogoSelect(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = ""; // permet de rechoisir le même fichier
  if (!file) return;

  logoError.value = null;

  if (!TYPES_ACCEPTES.includes(file.type)) {
    logoError.value = t("centre.settings.file_type_error");
    return;
  }
  if (file.size > TAILLE_MAX) {
    logoError.value = t("centre.settings.file_size_error");
    return;
  }

  libererApercuLocal();
  selectedLogoFile.value = file;
  localLogoUrl.value = URL.createObjectURL(file);
}

async function handleUploadLogo() {
  if (!selectedLogoFile.value) return;

  uploadingLogo.value = true;
  logoError.value = null;

  const result = await centerStaffStore.uploadMyLogo(selectedLogoFile.value);

  uploadingLogo.value = false;

  if (result.success) {
    selectedLogoFile.value = null;
    libererApercuLocal();
    toast.add({ severity: "success", summary: t("centre.settings.logo_saved"), life: 3000 });
    await loadCurrentSettings(false);
  } else {
    logoError.value = result.error || t("centre.settings.upload_error");
  }
}

onMounted(() => loadCurrentSettings());
onBeforeUnmount(libererApercuLocal);
</script>