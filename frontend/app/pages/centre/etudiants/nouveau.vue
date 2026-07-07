<!-- pages/centre/etudiants/nouveau.vue -->
<template>
  <div class="max-w-lg">
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Nom complet</label
        >
        <InputText
          v-model="form.full_name"
          class="w-full"
          placeholder="ex: Paul Nguemo"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Email</label
        >
        <InputText
          v-model="form.email"
          class="w-full"
          placeholder="paul@exemple.com"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Téléphone (optionnel)</label
        >
        <InputText
          v-model="form.phone"
          class="w-full"
          placeholder="+237 6XX XXX XXX"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Mot de passe provisoire</label
        >
        <Password
          v-model="form.password"
          class="w-full"
          inputClass="w-full"
          :feedback="false"
          toggleMask
          placeholder="Min. 8 caractères"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Examen visé</label
        >
        <Select
          v-model="form.target_level_id"
          :options="allLevels"
          optionLabel="label"
          optionValue="value"
          placeholder="Sélectionner un examen et niveau"
          class="w-full"
          filter
        />
      </div>

      <Message v-if="createError" severity="error" :closable="false">{{
        createError
      }}</Message>

      <div class="flex gap-2 pt-2">
        <Button
          label="Annuler"
          text
          class="flex-1"
          @click="navigateTo('/centre/etudiants')"
        />
        <Button
          label="Créer l'étudiant"
          icon="pi pi-user-plus"
          class="flex-1"
          :loading="creating"
          @click="handleCreate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "secretary",
});

const centerStaffStore = useCenterStaffStore();
const examsStore = useExamsStore();
const toast = useToast();

const creating = ref(false);
const createError = ref<string | null>(null);

const form = ref({
  full_name: "",
  email: "",
  phone: "",
  password: "",
  target_level_id: "",
});

const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

async function handleCreate() {
  if (
    !form.value.full_name.trim() ||
    !form.value.email.trim() ||
    !form.value.password ||
    !form.value.target_level_id
  ) {
    createError.value = "Tous les champs obligatoires doivent être remplis.";
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await centerStaffStore.createStudent({
    email: form.value.email.trim(),
    password: form.value.password,
    full_name: form.value.full_name.trim(),
    phone: form.value.phone.trim() || null,
    target_level_id: form.value.target_level_id,
  });

  creating.value = false;

  if (result.success) {
    toast.add({
      severity: "success",
      summary: "Étudiant créé",
      detail: `${form.value.full_name} a été ajouté avec succès.`,
      life: 3000,
    });
    navigateTo("/centre/etudiants");
  } else {
    createError.value = result.error || "Erreur lors de la création.";
  }
}

onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
});
</script>
