<!-- pages/centre/reglages.vue -->
<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
    <!-- Colonne gauche : formulaires -->
    <div class="space-y-6">
      <!-- Adresse -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <h3 class="text-sm font-semibold text-gray-700">
          Coordonnées du centre
        </h3>
        <p class="text-xs text-gray-400">
          Affichées en en-tête des reçus de paiement PDF générés pour vos élèves.
        </p>

        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block">Adresse / B.P.</label>
          <InputText
            v-model="addressForm"
            class="w-full"
            placeholder="ex: B.P. 123, Dschang"
          />
        </div>

        <Message v-if="addressError" severity="error" :closable="false">
          {{ addressError }}
        </Message>
        <Message v-if="addressSuccess" severity="success" :closable="false">
          Adresse mise à jour.
        </Message>

        <Button
          label="Enregistrer l'adresse"
          icon="pi pi-check"
          :loading="savingAddress"
          @click="handleSaveAddress"
        />
      </div>

      <!-- Logo -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <h3 class="text-sm font-semibold text-gray-700">Logo du centre</h3>
        <p class="text-xs text-gray-400">
          PNG ou JPG, affiché en haut à gauche des reçus PDF.
        </p>

        <FileUpload
          mode="basic"
          accept="image/png,image/jpeg"
          :maxFileSize="2000000"
          chooseLabel="Choisir un fichier"
          customUpload
          @select="handleLogoSelect"
        />

        <Message v-if="logoError" severity="error" :closable="false">
          {{ logoError }}
        </Message>
        <Message v-if="logoSuccess" severity="success" :closable="false">
          Logo mis à jour.
        </Message>

        <Button
          v-if="selectedLogoFile"
          label="Envoyer le logo"
          icon="pi pi-upload"
          :loading="uploadingLogo"
          @click="handleUploadLogo"
        />
      </div>
    </div>

    <!-- Colonne droite : aperçu en direct, style en-tête du reçu -->
    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-4">
        Aperçu sur les reçus
      </h3>

      <div v-if="loadingPreview" class="flex justify-center py-8">
        <i class="pi pi-spin pi-spinner text-2xl text-emerald-600"></i>
      </div>

      <div v-else class="border border-gray-100 rounded-lg p-6 bg-gray-50">
        <img
          v-if="currentLogoUrl"
          :src="currentLogoUrl"
          alt="Logo du centre"
          class="h-14 object-contain mb-3"
        />
        <p v-else class="text-xs text-gray-400 italic mb-3">Aucun logo envoyé</p>

        <p class="text-lg font-bold text-emerald-700">{{ centerName }}</p>
        <p v-if="currentAddress" class="text-sm text-gray-500 mt-1">
          {{ currentAddress }}
        </p>
        <p v-else class="text-sm text-gray-300 italic mt-1">
          Aucune adresse renseignée
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "director",
});

const centerStaffStore = useCenterStaffStore();

const addressForm = ref("");
const savingAddress = ref(false);
const addressError = ref<string | null>(null);
const addressSuccess = ref(false);

const selectedLogoFile = ref<File | null>(null);
const uploadingLogo = ref(false);
const logoError = ref<string | null>(null);
const logoSuccess = ref(false);

const loadingPreview = ref(true);
const centerName = ref("");
const currentAddress = ref<string | null>(null);
const currentLogoUrl = ref<string | null>(null);

async function loadCurrentSettings() {
  loadingPreview.value = true;

  const result = await centerStaffStore.fetchMyCenterDetails();

  if (result.success && result.center) {
    centerName.value = result.center.name;
    currentAddress.value = result.center.address ?? null;
    addressForm.value = result.center.address ?? "";

    if (result.center.logo_path) {
      const config = useRuntimeConfig();
      const base = config.public.apiBaseUrl || "http://localhost:8001";
      // logo_path est un chemin disque local (storage/center_logos/xxx) —
      // exposé publiquement via le mount /center-logos, on ne garde
      // que le nom de fichier pour reconstruire l'URL publique.
      const filename = result.center.logo_path.split(/[\\/]/).pop();
      currentLogoUrl.value = `${base}/center-logos/${filename}`;
    }
  }

  loadingPreview.value = false;
}

async function handleSaveAddress() {
  savingAddress.value = true;
  addressError.value = null;
  addressSuccess.value = false;

  const result = await centerStaffStore.updateMyCenter({
    address: addressForm.value.trim() || null,
  });

  savingAddress.value = false;

  if (result.success) {
    addressSuccess.value = true;
    currentAddress.value = addressForm.value.trim() || null;
  } else {
    addressError.value = result.error || "Erreur lors de l'enregistrement.";
  }
}

function handleLogoSelect(event: any) {
  selectedLogoFile.value = event.files[0];
  logoError.value = null;
  logoSuccess.value = false;
}

async function handleUploadLogo() {
  if (!selectedLogoFile.value) return;

  uploadingLogo.value = true;
  logoError.value = null;

  const result = await centerStaffStore.uploadMyLogo(selectedLogoFile.value);

  uploadingLogo.value = false;

  if (result.success) {
    logoSuccess.value = true;
    selectedLogoFile.value = null;
    await loadCurrentSettings();
  } else {
    logoError.value = result.error || "Erreur lors de l'envoi.";
  }
}

onMounted(() => {
  loadCurrentSettings();
});
</script>