<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-lg font-semibold text-gray-900">Gestion des examens</h2>
      <p class="text-sm text-gray-500">
        Importez des sujets et associez leurs audios
      </p>
    </div>

    <!-- Loading -->
    <div v-if="examsStore.loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Liste examens -->
    <div v-else class="space-y-4">
      <div
        v-for="exam in examsStore.catalog"
        :key="exam.id"
        class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <!-- Header exam -->
        <div
          class="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-9 h-9 bg-teal-100 rounded-lg flex items-center justify-center"
            >
              <i class="pi pi-book text-teal-600 text-sm"></i>
            </div>
            <div>
              <p class="font-semibold text-gray-900">{{ exam.name }}</p>
              <p class="text-xs text-gray-400">
                {{ exam.slug }} · {{ exam.provider }}
              </p>
            </div>
          </div>
          <Button
            label="Importer un sujet"
            icon="pi pi-upload"
            size="small"
            @click="openImportJson(exam)"
          />
        </div>

        <!-- Sujets -->
        <div class="divide-y divide-gray-50">
          <div v-if="loadingSubjects[exam.id]" class="px-5 py-4 text-center">
            <ProgressSpinner style="width: 30px; height: 30px" />
          </div>

          <div
            v-else-if="!(subjects[exam.id] ?? []).length"
            class="px-5 py-6 text-center text-gray-400 text-sm"
          >
            <i class="pi pi-inbox text-2xl mb-2 block"></i>
            Aucun sujet — importez votre premier sujet JSON
          </div>

          <div
            v-else
            v-for="subject in subjects[exam.id] ?? []"
            :key="subject.subject_number"
            class="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors"
          >
            <!-- Info sujet -->
            <div class="flex items-center gap-4">
              <div
                class="w-10 h-10 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0"
              >
                {{ subject.subject_number }}
              </div>
              <div>
                <p class="font-medium text-gray-900 text-sm">
                  {{ subject.name || `Sujet ${subject.subject_number}` }}
                </p>
                <div class="flex items-center gap-3 mt-1">
                  <span
                    v-if="subject.has_audio"
                    class="flex items-center gap-1 text-xs text-green-600"
                  >
                    <i class="pi pi-check-circle"></i> Audios associés
                  </span>
                  <span
                    v-else
                    class="flex items-center gap-1 text-xs text-amber-500"
                  >
                    <i class="pi pi-exclamation-circle"></i> Audios manquants
                  </span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-1">
              <Button
                icon="pi pi-eye"
                text
                rounded
                size="small"
                severity="secondary"
                v-tooltip.top="'Aperçu du sujet'"
                @click="openPreview(exam, subject)"
              />
              <Button
                icon="pi pi-pencil"
                text
                rounded
                size="small"
                severity="secondary"
                v-tooltip.top="'Renommer'"
                @click="openEdit(exam, subject)"
              />
              <Button
                icon="pi pi-volume-up"
                text
                rounded
                size="small"
                severity="secondary"
                v-tooltip.top="'Associer audios'"
                @click="openImportAudio(exam, subject)"
              />
              <Button
                icon="pi pi-trash"
                text
                rounded
                size="small"
                severity="danger"
                v-tooltip.top="'Supprimer'"
                @click="openDelete(exam, subject)"
              />
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="examsStore.catalog.length === 0"
        class="text-center py-16 text-gray-400"
      >
        <i class="pi pi-book text-4xl mb-3 block"></i>
        Aucun examen disponible
      </div>
    </div>

    <!-- ─── Dialog Aperçu ─────────────────────────────── -->
    <Dialog
      v-model:visible="previewDialog"
      :header="`Aperçu — ${selectedExam?.name} · Sujet ${selectedSubject?.subject_number}`"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '640px' }"
    >
      <div v-if="loadingPreview" class="flex justify-center py-8">
        <ProgressSpinner style="width: 40px; height: 40px" />
      </div>
      <div v-else-if="previewData" class="space-y-4 mt-2">
        <!-- Stats -->
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-teal-50 rounded-lg p-3 text-center">
            <p class="text-xl font-bold text-teal-700">
              {{ previewData.modules?.length ?? 0 }}
            </p>
            <p class="text-xs text-teal-600">Modules</p>
          </div>
          <div class="bg-blue-50 rounded-lg p-3 text-center">
            <p class="text-xl font-bold text-blue-700">{{ totalTeile }}</p>
            <p class="text-xs text-blue-600">Teile</p>
          </div>
          <div class="bg-purple-50 rounded-lg p-3 text-center">
            <p class="text-xl font-bold text-purple-700">
              {{ totalQuestions }}
            </p>
            <p class="text-xs text-purple-600">Questions</p>
          </div>
        </div>

        <!-- Modules liste -->
        <div class="space-y-2">
          <div
            v-for="mod in previewData.modules"
            :key="mod.id"
            class="border border-gray-100 rounded-lg overflow-hidden"
          >
            <div
              class="flex items-center justify-between px-4 py-2.5 bg-gray-50"
            >
              <div class="flex items-center gap-2">
                <div
                  :class="[
                    'w-7 h-7 rounded-md flex items-center justify-center',
                    getModuleColor(mod.slug),
                  ]"
                >
                  <i :class="['pi text-xs', getModuleIcon(mod.slug)]"></i>
                </div>
                <span class="font-medium text-sm text-gray-900">{{
                  mod.name
                }}</span>
              </div>
              <div class="flex items-center gap-3 text-xs text-gray-400">
                <span
                  ><i class="pi pi-clock mr-1"></i
                  >{{ mod.time_limit_minutes }}min</span
                >
                <span
                  ><i class="pi pi-star mr-1"></i>{{ mod.max_score }}pts</span
                >
              </div>
            </div>
            <div class="px-4 py-2 flex flex-wrap gap-2">
              <div
                v-for="teil in mod.teile"
                :key="teil.id"
                class="flex items-center gap-1.5 text-xs text-gray-500"
              >
                <span class="bg-gray-100 px-2 py-0.5 rounded font-mono"
                  >Teil {{ teil.teil_number }}</span
                >
                <span class="text-gray-400">{{ teil.format_type }}</span>
                <span class="text-gray-300">·</span>
                <span>{{ teil.questions?.length ?? 0 }} questions</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Fermer" text @click="previewDialog = false" />
      </template>
    </Dialog>

    <!-- ─── Dialog Éditer ─────────────────────────────── -->
    <Dialog
      v-model:visible="editDialog"
      :header="`Renommer — Sujet ${selectedSubject?.subject_number}`"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <div class="space-y-4 mt-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Nom du sujet</label
          >
          <InputText
            v-model="editName"
            class="w-full"
            placeholder="Ex: Sujet 1 — Série A"
          />
        </div>
        <Message v-if="editError" severity="error" :closable="false">{{
          editError
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="editDialog = false" />
        <Button
          label="Enregistrer"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!editName.trim()"
          @click="handleEdit"
        />
      </template>
    </Dialog>

    <!-- ─── Dialog Supprimer ──────────────────────────── -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le sujet ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <div class="space-y-3 mt-2">
        <Message severity="error" :closable="false">
          Cette action est <strong>irréversible</strong>. Toutes les questions
          du sujet seront supprimées.
        </Message>
        <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
          <div
            class="w-9 h-9 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold text-sm"
          >
            {{ selectedSubject?.subject_number }}
          </div>
          <div>
            <p class="font-medium text-sm text-gray-900">
              {{ selectedSubject?.name }}
            </p>
            <p class="text-xs text-gray-400">{{ selectedExam?.name }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button
          label="Supprimer"
          severity="danger"
          icon="pi pi-trash"
          :loading="deleting"
          @click="handleDelete"
        />
      </template>
    </Dialog>

    <!-- ─── Dialog Import JSON ────────────────────────── -->
    <Dialog
      v-model:visible="importJsonDialog"
      :header="`Importer un sujet — ${selectedExam?.name}`"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '520px' }"
    >
      <div class="space-y-4 mt-2">
        <Message severity="info" :closable="false">
          Sélectionnez le fichier JSON généré. Un nouveau sujet sera créé pour
          <strong>{{ selectedExam?.name }}</strong
          >.
        </Message>
        <div
          class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-teal-400 transition-colors"
          :class="{ 'border-teal-500 bg-teal-50': jsonFile }"
          @click="jsonInput?.click()"
          @dragover.prevent
          @drop.prevent="onJsonDrop"
        >
          <input
            ref="jsonInput"
            type="file"
            accept=".json"
            class="hidden"
            @change="onJsonSelect"
          />
          <i class="pi pi-file-import text-4xl text-gray-300 mb-3 block"></i>
          <p v-if="!jsonFile" class="text-sm text-gray-500">
            Glissez le fichier JSON ici ou
            <span class="text-teal-600 font-medium"
              >cliquez pour parcourir</span
            >
          </p>
          <div
            v-else
            class="flex items-center justify-center gap-2 text-teal-700"
          >
            <i class="pi pi-check-circle text-xl"></i>
            <span class="font-medium text-sm">{{ jsonFile.name }}</span>
            <span class="text-xs text-gray-400"
              >({{ (jsonFile.size / 1024).toFixed(0) }} KB)</span
            >
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Checkbox v-model="importReplace" :binary="true" inputId="replace" />
          <label for="replace" class="text-sm text-gray-700 cursor-pointer"
            >Remplacer les questions existantes</label
          >
        </div>
        <Message v-if="importError" severity="error" :closable="false">{{
          importError
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="closeImportJson" />
        <Button
          label="Importer le sujet"
          icon="pi pi-check"
          :loading="importing"
          :disabled="!jsonFile"
          @click="handleImportJson"
        />
      </template>
    </Dialog>

    <!-- ─── Dialog Import Audio ───────────────────────── -->
    <Dialog
      v-model:visible="importAudioDialog"
      :header="`Audios — ${selectedExam?.name} · Sujet ${selectedSubject?.subject_number}`"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '520px' }"
    >
      <div class="space-y-4 mt-2">
        <Message severity="info" :closable="false">
          Sélectionnez <strong>tous les fichiers MP3</strong> du dossier audio
          correspondant au
          <strong>Sujet {{ selectedSubject?.subject_number }}</strong
          >.
        </Message>
        <div
          class="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 space-y-1 font-mono"
        >
          <p class="font-semibold text-gray-700 mb-2 font-sans text-sm">
            Fichiers attendus :
          </p>
          <p>horen_teil1_audio1.mp3 → Teil 1, audio 1</p>
          <p>horen_teil2.mp3 → Teil 2 (audio long)</p>
          <p>horen_teil3_audio1.mp3 → Teil 3, audio 1</p>
        </div>
        <div
          class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-teal-400 transition-colors"
          :class="{ 'border-teal-500 bg-teal-50': audioFiles.length > 0 }"
          @click="audioInput?.click()"
          @dragover.prevent
          @drop.prevent="onAudioDrop"
        >
          <input
            ref="audioInput"
            type="file"
            accept=".mp3"
            multiple
            class="hidden"
            @change="onAudioSelect"
          />
          <i class="pi pi-volume-up text-4xl text-gray-300 mb-3 block"></i>
          <p v-if="audioFiles.length === 0" class="text-sm text-gray-500">
            Sélectionnez plusieurs MP3 ou
            <span class="text-teal-600 font-medium"
              >cliquez pour parcourir</span
            >
          </p>
          <div v-else>
            <p class="text-teal-700 font-medium text-sm mb-3">
              <i class="pi pi-check-circle mr-1"></i
              >{{ audioFiles.length }} fichier(s)
            </p>
            <div
              class="flex flex-wrap gap-1 justify-center max-h-24 overflow-y-auto"
            >
              <span
                v-for="f in audioFiles"
                :key="f.name"
                class="bg-teal-100 text-teal-700 text-xs px-2 py-0.5 rounded"
              >
                {{ f.name }}
              </span>
            </div>
          </div>
        </div>
        <Message v-if="audioError" severity="error" :closable="false">{{
          audioError
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="closeImportAudio" />
        <Button
          label="Associer les audios"
          icon="pi pi-link"
          :loading="importingAudio"
          :disabled="audioFiles.length === 0"
          @click="handleImportAudio"
        />
      </template>
    </Dialog>

    <!-- ─── Dialog résultat ───────────────────────────── -->
    <Dialog
      v-model:visible="resultDialog"
      header="Résultat de l'opération"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '560px' }"
    >
      <div v-if="importResult" class="space-y-3 mt-2">
        <Message
          :severity="importResult.success ? 'success' : 'error'"
          :closable="false"
        >
          {{
            importResult.success
              ? "✅ Opération réussie"
              : "❌ Erreur lors de l'opération"
          }}
        </Message>
        <div v-if="importResult.total_questions" class="grid grid-cols-2 gap-3">
          <div class="bg-teal-50 rounded-lg p-3 text-center">
            <p class="text-2xl font-bold text-teal-700">
              {{ importResult.total_questions }}
            </p>
            <p class="text-xs text-teal-600">Questions importées</p>
          </div>
          <div class="bg-blue-50 rounded-lg p-3 text-center">
            <p class="text-2xl font-bold text-blue-700">
              {{ importResult.subject_number }}
            </p>
            <p class="text-xs text-blue-600">Numéro du sujet</p>
          </div>
        </div>
        <div
          v-if="importResult.questions_updated"
          class="grid grid-cols-2 gap-3"
        >
          <div class="bg-teal-50 rounded-lg p-3 text-center">
            <p class="text-2xl font-bold text-teal-700">
              {{ importResult.questions_updated }}
            </p>
            <p class="text-xs text-teal-600">Questions mises à jour</p>
          </div>
          <div class="bg-purple-50 rounded-lg p-3 text-center">
            <p class="text-2xl font-bold text-purple-700">
              {{ importResult.files_processed }}
            </p>
            <p class="text-xs text-purple-600">Fichiers traités</p>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4 max-h-52 overflow-y-auto">
          <p
            v-for="(line, i) in importResult.log"
            :key="i"
            class="text-xs text-gray-700 font-mono leading-6"
          >
            {{ line }}
          </p>
        </div>
      </div>
      <template #footer>
        <Button label="Fermer" @click="resultDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { ExamCatalogResponse } from "#shared/api";

definePageMeta({ layout: "admin", middleware: "admin" });

const examsStore = useExamsStore();
const toast = useToast();

// ── Helpers ───────────────────────────────────────────
const getModuleIcon = (slug: string) => {
  if (slug.includes("lesen")) return "pi-book";
  if (slug.includes("horen") || slug.includes("hören")) return "pi-volume-up";
  if (slug.includes("schreiben")) return "pi-pencil";
  if (slug.includes("sprechen")) return "pi-microphone";
  return "pi-file";
};
const getModuleColor = (slug: string) => {
  if (slug.includes("lesen")) return "bg-blue-100 text-blue-600";
  if (slug.includes("horen") || slug.includes("hören"))
    return "bg-purple-100 text-purple-600";
  if (slug.includes("schreiben")) return "bg-green-100 text-green-600";
  if (slug.includes("sprechen")) return "bg-orange-100 text-orange-600";
  return "bg-gray-100 text-gray-600";
};

// ── API config ────────────────────────────────────────
const setupApi = async () => {
  const { OpenAPI } = await import("#shared/api");
  const config = useRuntimeConfig();
  OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
  const tokenCookie = useCookie("access_token");
  OpenAPI.TOKEN = tokenCookie.value ?? undefined;
  return OpenAPI;
};

// ── Sujets par exam ───────────────────────────────────
const subjects = ref<Record<string, any[]>>({});
const loadingSubjects = ref<Record<string, boolean>>({});

const loadSubjects = async (exam: ExamCatalogResponse) => {
  if (subjects.value[exam.id]) return
  loadingSubjects.value[exam.id] = true
  try {
    const { ExamsService } = await import('#shared/api')
    await setupApi()
    const detail = await ExamsService.getExamDetailApiV1ExamsExamIdGet(exam.id)
    const allSubjects: any[] = []
    for (const level of detail.levels ?? []) {
      // ← Utiliser l'endpoint subjects qui retourne has_audio
      const levelSubjects = await ExamsService.getSubjectsApiV1ExamsLevelsLevelIdSubjectsGet(level.id)
      for (const subject of levelSubjects) {
        allSubjects.push({ ...subject, level_cefr: level.cefr_code })
      }
    }
    subjects.value[exam.id] = allSubjects.sort((a, b) => a.subject_number - b.subject_number)
  } catch {
    subjects.value[exam.id] = []
  } finally {
    loadingSubjects.value[exam.id] = false
  }
}

const reloadSubjects = async (exam: ExamCatalogResponse) => {
  delete subjects.value[exam.id];
  await loadSubjects(exam);
};

// ── State commun ──────────────────────────────────────
const selectedExam = ref<ExamCatalogResponse | null>(null);
const selectedSubject = ref<any>(null);
const resultDialog = ref(false);
const importResult = ref<any>(null);

// ── Aperçu ────────────────────────────────────────────
const previewDialog = ref(false);
const previewData = ref<any>(null);
const loadingPreview = ref(false);

const totalTeile = computed(() =>
  (previewData.value?.modules ?? []).reduce(
    (s: number, m: any) => s + (m.teile?.length ?? 0),
    0,
  ),
);
const totalQuestions = computed(() =>
  (previewData.value?.modules ?? []).reduce(
    (s: number, m: any) =>
      s +
      (m.teile ?? []).reduce(
        (st: number, t: any) => st + (t.questions?.length ?? 0),
        0,
      ),
    0,
  ),
);

const openPreview = async (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  previewData.value = null;
  loadingPreview.value = true;
  previewDialog.value = true;
  try {
    // Le subject vient du detail déjà chargé
    const subjectList = subjects.value[exam.id] ?? [];
    const full = subjectList.find((s) => s.id === subject.id);
    previewData.value = full ?? subject;
  } finally {
    loadingPreview.value = false;
  }
};

// ── Éditer ────────────────────────────────────────────
const editDialog = ref(false);
const editName = ref("");
const editError = ref("");
const saving = ref(false);

const openEdit = (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  editName.value = subject.name || `Sujet ${subject.subject_number}`;
  editError.value = "";
  editDialog.value = true;
};

const handleEdit = async () => {
  if (!selectedSubject.value || !editName.value.trim()) return;
  saving.value = true;
  editError.value = "";
  try {
    const { ExamsService } = await import("#shared/api");
    await setupApi();
    await (ExamsService as any).updateSubjectApiV1ExamsSubjectsSubjectIdPatch(
      selectedSubject.value.id,
      { name: editName.value.trim() },
    );
    // Mettre à jour localement
    if (selectedExam.value) {
      const list = subjects.value[selectedExam.value.id] ?? [];
      const subj = list.find((s) => s.id === selectedSubject.value.id);
      if (subj) subj.name = editName.value.trim();
    }
    editDialog.value = false;
    toast.add({ severity: "success", summary: "Sujet renommé", life: 3000 });
  } catch (e: any) {
    editError.value = e.body?.detail || "Erreur lors de la sauvegarde";
  } finally {
    saving.value = false;
  }
};

// ── Supprimer ─────────────────────────────────────────
const deleteDialog = ref(false);
const deleting = ref(false);

const openDelete = (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!selectedSubject.value) return;
  deleting.value = true;
  try {
    const { ExamsService } = await import("#shared/api");
    await setupApi();
    await ExamsService.deleteSubjectApiV1ExamsSubjectsSubjectIdDelete(
      selectedSubject.value.id,
    );
    // Retirer localement
    if (selectedExam.value) {
      subjects.value[selectedExam.value.id] = (
        subjects.value[selectedExam.value.id] ?? []
      ).filter((s) => s.id !== selectedSubject.value.id);
    }
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Sujet supprimé", life: 3000 });
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary: e.body?.detail || "Erreur",
      life: 4000,
    });
  } finally {
    deleting.value = false;
  }
};

// ── Import JSON ───────────────────────────────────────
const importJsonDialog = ref(false);
const jsonFile = ref<File | null>(null);
const jsonInput = ref<HTMLInputElement | null>(null);
const importReplace = ref(false);
const importing = ref(false);
const importError = ref("");

const openImportJson = (exam: ExamCatalogResponse) => {
  selectedExam.value = exam;
  jsonFile.value = null;
  importReplace.value = false;
  importError.value = "";
  importJsonDialog.value = true;
};

const closeImportJson = () => {
  importJsonDialog.value = false;
  jsonFile.value = null;
};
const onJsonSelect = (e: Event) => {
  const i = e.target as HTMLInputElement;
  if (i.files?.[0]) jsonFile.value = i.files[0];
};
const onJsonDrop = (e: DragEvent) => {
  const f = e.dataTransfer?.files?.[0];
  if (f?.name.endsWith(".json")) jsonFile.value = f;
};

const handleImportJson = async () => {
  if (!jsonFile.value) return;
  importing.value = true;
  importError.value = "";
  const res = await examsStore.importJson(jsonFile.value, importReplace.value);
  importing.value = false;
  if (res.success) {
    importResult.value = res.data;
    importJsonDialog.value = false;
    resultDialog.value = true;
    if (selectedExam.value) await reloadSubjects(selectedExam.value);
    toast.add({ severity: "success", summary: "Sujet importé", life: 3000 });
  } else {
    importError.value = res.error || "Erreur inconnue";
  }
};

// ── Import Audio ──────────────────────────────────────
const importAudioDialog = ref(false);
const audioFiles = ref<File[]>([]);
const audioInput = ref<HTMLInputElement | null>(null);
const importingAudio = ref(false);
const audioError = ref("");

const openImportAudio = (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  audioFiles.value = [];
  audioError.value = "";
  importAudioDialog.value = true;
};

const closeImportAudio = () => {
  importAudioDialog.value = false;
  audioFiles.value = [];
};
const onAudioSelect = (e: Event) => {
  const i = e.target as HTMLInputElement;
  if (i.files) audioFiles.value = Array.from(i.files);
};
const onAudioDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files)
    audioFiles.value = Array.from(e.dataTransfer.files).filter((f) =>
      f.name.endsWith(".mp3"),
    );
};

const handleImportAudio = async () => {
  if (!selectedExam.value || !selectedSubject.value || !audioFiles.value.length)
    return;
  importingAudio.value = true;
  audioError.value = "";
  const res = await examsStore.importAudio(
    selectedExam.value.id,
    audioFiles.value,
    selectedSubject.value.subject_number,
  );
  importingAudio.value = false;
  if (res.success) {
    importResult.value = res.data;
    importAudioDialog.value = false;
    resultDialog.value = true;
    const list = subjects.value[selectedExam.value.id];
    if (list) {
      const s = list.find(
        (s) => s.subject_number === selectedSubject.value.subject_number,
      );
      if (s) s.has_audio = true;
    }
    toast.add({ severity: "success", summary: "Audios associés", life: 3000 });
  } else {
    audioError.value = res.error || "Erreur inconnue";
  }
};

// ── Init ──────────────────────────────────────────────
onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
  for (const exam of examsStore.catalog) loadSubjects(exam);
});
</script>
