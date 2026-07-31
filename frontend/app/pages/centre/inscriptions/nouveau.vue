<!-- pages/centre/inscriptions/nouveau.vue -->
<template>
  <div class="max-w-lg">
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block">Type</label>
        <SelectButton
          v-model="mode"
          :options="modeOptions"
          optionLabel="label"
          optionValue="value"
        />
      </div>

      <!-- Élève existant -->
      <div v-if="mode === 'existing'">
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Élève</label
        >
        <Select
          v-model="form.student_id"
          :options="studentOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Sélectionner un élève"
          class="w-full"
          filter
        />
      </div>

      <!-- Nouvel élève -->
      <template v-else>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nom complet</label
          >
          <InputText
            v-model="newStudent.full_name"
            class="w-full"
            placeholder="ex: Paul Nguemo"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Téléphone (optionnel)</label
          >
          <InputText
            v-model="newStudent.phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
        </div>
        <div v-if="authStore.isDirector">
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Succursale</label
          >
          <Select
            v-model="newStudent.branch_id"
            :options="branchOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Sélectionner une succursale"
            class="w-full"
          />
        </div>
      </template>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Niveau de départ</label
        >
        <Select
          v-model="form.start_level"
          :options="levelOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="ex: A1"
          class="w-full"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 mb-1 block"
          >Niveau visé</label
        >
        <Select
          v-model="form.target_level"
          :options="levelOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="ex: B2"
          class="w-full"
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
          @click="navigateTo('/centre/inscriptions')"
        />
        <Button
          label="Créer le cursus"
          icon="pi pi-plus"
          class="flex-1"
          :loading="creating"
          @click="handleCreate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CursusLevel } from "#shared/api";

definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

const centerStaffStore = useCenterStaffStore();
const enrollmentsStore = useEnrollmentsStore();
const authStore = useAuthStore();
const toast = useToast();

const creating = ref(false);
const createError = ref<string | null>(null);

const mode = ref<"existing" | "new">("existing");
const modeOptions = [
  { label: "Élève existant", value: "existing" },
  { label: "Nouvel élève", value: "new" },
];

const form = ref({
  student_id: "",
  start_level: "" as CursusLevel | "",
  target_level: "" as CursusLevel | "",
});

const newStudent = ref({
  full_name: "",
  phone: "",
  branch_id: "",
});

const branchOptions = ref<{ label: string; value: string }[]>([]);

const levelOptions = [
  { label: "A1", value: "A1" },
  { label: "A2", value: "A2" },
  { label: "B1", value: "B1" },
  { label: "B2", value: "B2" },
];

const studentOptions = computed(() =>
  centerStaffStore.students.map((s) => ({
    label: s.full_name,
    value: s.id,
  })),
);

async function handleCreate() {
  if (!form.value.start_level || !form.value.target_level) {
    createError.value = "Les niveaux de départ et visé sont obligatoires.";
    return;
  }

  creating.value = true;
  createError.value = null;

  let studentId = form.value.student_id;
  let branchId: string | undefined;

  if (mode.value === "new") {
    if (!newStudent.value.full_name.trim()) {
      createError.value = "Le nom de l'élève est obligatoire.";
      creating.value = false;
      return;
    }
    if (authStore.isDirector && !newStudent.value.branch_id) {
      createError.value = "Veuillez sélectionner une succursale.";
      creating.value = false;
      return;
    }

    const createResult = await centerStaffStore.createStudentQuick({
      full_name: newStudent.value.full_name.trim(),
      phone: newStudent.value.phone.trim() || null,
      branch_id: authStore.isDirector ? newStudent.value.branch_id : null,
    });

    if (!createResult.success || !createResult.student) {
      createError.value =
        createResult.error || "Erreur lors de la création de l'élève.";
      creating.value = false;
      return;
    }

    studentId = createResult.student.id;
    branchId = createResult.student.branch_id ?? undefined;
  } else {
    if (!studentId) {
      createError.value = "Veuillez sélectionner un élève.";
      creating.value = false;
      return;
    }
    const student = centerStaffStore.students.find((s) => s.id === studentId);
    branchId = student?.branch_id ?? undefined;
  }

  if (!branchId) {
    createError.value = "Impossible de déterminer la succursale de cet élève.";
    creating.value = false;
    return;
  }

  const result = await enrollmentsStore.createCursus({
    student_id: studentId,
    branch_id: branchId,
    start_level: form.value.start_level as CursusLevel,
    target_level: form.value.target_level as CursusLevel,
  });

  creating.value = false;

  if (result.success) {
    toast.add({
      severity: "success",
      summary: "Cursus créé",
      detail: `Le parcours ${form.value.start_level} → ${form.value.target_level} a été créé.`,
      life: 3000,
    });
    navigateTo("/centre/inscriptions");
  } else {
    createError.value = result.error || "Erreur lors de la création.";
  }
}

onMounted(async () => {
  if (centerStaffStore.students.length === 0) {
    if (authStore.isDirector) {
      await centerStaffStore.fetchStudentsByCenter();
    } else {
      await centerStaffStore.fetchStudentsByBranch();
    }
  }

  if (authStore.isDirector) {
    const result = await centerStaffStore.fetchMyBranches();
    if (result.success && result.branches) {
      branchOptions.value = result.branches.map((b) => ({
        label: b.name,
        value: b.id,
      }));
    }
  }
});
</script>
