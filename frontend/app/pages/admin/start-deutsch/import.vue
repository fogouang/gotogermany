<!-- pages/admin/start-deutsch/import.vue -->
<template>
  <div class="space-y-8 pb-10">
    <div>
      <h1 class="text-2xl font-bold text-ink">Import Start Deutsch</h1>
      <p class="text-ink-secondary mt-1 text-sm">
        Importer un sujet A1/A2 complet (JSON), puis les fichiers audio et
        images associés.
      </p>
    </div>

    <!-- ── 1. Import JSON ── -->
    <section class="bg-card border border-line rounded-xl p-5 space-y-4">
      <h2 class="font-semibold text-ink flex items-center gap-2">
        <i class="pi pi-file text-primary-600" /> 1. Sujet (JSON)
      </h2>

      <div class="flex items-center gap-3">
        <input
          ref="jsonInput"
          type="file"
          accept="application/json"
          class="text-sm text-ink-secondary file:mr-3 file:rounded-lg file:border-0 file:bg-hover file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-ink"
          @change="onJsonFileChange"
        />
      </div>

      <label class="flex items-center gap-2 text-sm text-ink-secondary">
        <input
          v-model="jsonReplace"
          type="checkbox"
          class="rounded border-line"
        />
        Remplacer les Teile déjà existants (replace=true)
      </label>

      <Button
        :label="t('admin.import.submit_json')"
        icon="pi pi-upload"
        :loading="jsonLoading"
        :disabled="!jsonFile"
        @click="submitJson"
      />

      <ImportLogPanel
        :log="jsonResult?.log"
        :summary="jsonSummary"
        :error="jsonError"
      />
    </section>

    <!-- ── 2. Import Audio ── -->
    <section class="bg-card border border-line rounded-xl p-5 space-y-4">
      <h2 class="font-semibold text-ink flex items-center gap-2">
        <i class="pi pi-volume-up text-secondary-600" /> 2. Fichiers audio
        (Hören)
      </h2>

      <div class="flex items-center gap-3">
        <Select
          v-model="audioSubjectId"
          :options="subjectOptions"
          option-label="label"
          option-value="id"
          placeholder="Sujet"
          class="w-64"
        />
        <input
          ref="audioInput"
          type="file"
          accept="audio/mpeg"
          multiple
          class="text-sm text-ink-secondary file:mr-3 file:rounded-lg file:border-0 file:bg-hover file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-ink"
          @change="onAudioFilesChange"
        />
      </div>
      <p class="text-xs text-ink-tertiary">
        Convention de nommage : <code>hoeren_teilN.mp3</code> (un seul fichier
        par Teil). Choisis bien le <strong>sujet exact</strong> visé — les
        fichiers sont stockés par sujet, pas seulement par niveau (plusieurs
        sujets par niveau sont possibles).
      </p>

      <Button
        :label="t('admin.import.submit_audio')"
        icon="pi pi-upload"
        :loading="audioLoading"
        :disabled="!audioFiles.length || !audioSubjectId"
        @click="submitAudio"
      />

      <ImportLogPanel
        :log="audioResult?.log"
        :summary="audioSummary"
        :error="audioError"
      />
    </section>

    <!-- ── 3. Import Images ── -->
    <section class="bg-card border border-line rounded-xl p-5 space-y-4">
      <h2 class="font-semibold text-ink flex items-center gap-2">
        <i class="pi pi-image text-secondary-600" /> 3. Images (Hören mc_image /
        Sprechen cartes-images)
      </h2>

      <div class="flex items-center gap-3">
        <Select
          v-model="imagesSubjectId"
          :options="subjectOptions"
          option-label="label"
          option-value="id"
          placeholder="Sujet"
          class="w-64"
        />
        <input
          ref="imagesInput"
          type="file"
          accept="image/png,image/jpeg,image/webp"
          multiple
          class="text-sm text-ink-secondary file:mr-3 file:rounded-lg file:border-0 file:bg-hover file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-ink"
          @change="onImagesFilesChange"
        />
      </div>
      <p class="text-xs text-ink-tertiary">
        Les noms de fichiers doivent correspondre exactement à
        <code>image_file</code> dans le JSON déjà importé (ex.
        <code>hoeren_teil1_q1_a.png</code>, <code>sprechen_teil3_q1.png</code>).
        Choisis bien le <strong>sujet exact</strong> visé.
      </p>

      <Button
        :label="t('admin.import.submit_images')"
        icon="pi pi-upload"
        :loading="imagesLoading"
        :disabled="!imagesFiles.length || !imagesSubjectId"
        @click="submitImages"
      />

      <ImportLogPanel
        :log="imagesResult?.log"
        :summary="imagesSummary"
        :error="imagesError"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import ImportLogPanel from "~/components/admin/ImportLogPanel.vue";

definePageMeta({ layout: "admin", middleware: "admin" });

const { t } = useI18n();
const store = useStartDeutschSessionStore();

// ── Liste des sujets (pour les sélecteurs audio/images) ─────
// Depuis qu'un niveau peut avoir plusieurs sujets, l'audio et les images
// doivent cibler un sujet précis (subject_id), pas juste "A1"/"A2".
interface SubjectOption {
  id: string;
  label: string;
}

const subjects = ref<any[]>([]);
const subjectOptions = computed<SubjectOption[]>(() =>
  subjects.value.map((s) => ({ id: s.id, label: `${s.level} — ${s.title}` })),
);

async function fetchSubjects() {
  const result = await store.adminListSubjects();
  if (result.success) {
    subjects.value = result.data;
  } else {
    console.error("Impossible de charger la liste des sujets", result.error);
  }
}

onMounted(fetchSubjects);

// ── 1. JSON ──────────────────────────────────────────────

const jsonInput = ref<HTMLInputElement | null>(null);
const jsonFile = ref<File | null>(null);
const jsonReplace = ref(false);
const jsonLoading = ref(false);
const jsonResult = ref<{
  log?: string[];
  total_questions?: number;
  level?: string;
} | null>(null);
const jsonError = ref<string | null>(null);

function onJsonFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files;
  jsonFile.value = files?.[0] ?? null;
}

const jsonSummary = computed(() =>
  jsonResult.value
    ? `Sujet ${jsonResult.value.level} importé — ${jsonResult.value.total_questions ?? "?"} question(s)`
    : null,
);

async function submitJson() {
  if (!jsonFile.value) return;
  jsonLoading.value = true;
  jsonError.value = null;
  jsonResult.value = null;

  const result = await store.adminImportJson(jsonFile.value, jsonReplace.value);
  if (result.success) {
    jsonResult.value = result.data;
    await fetchSubjects(); // le nouveau sujet doit apparaître dans les sélecteurs audio/images
  } else {
    jsonError.value = result.error || "Erreur lors de l'import.";
  }
  jsonLoading.value = false;
}

// ── 2. Audio ─────────────────────────────────────────────

const audioInput = ref<HTMLInputElement | null>(null);
const audioFiles = ref<File[]>([]);
const audioSubjectId = ref<string | null>(null);
const audioLoading = ref(false);
const audioResult = ref<{
  log?: string[];
  teile_updated?: number;
  files_processed?: number;
} | null>(null);
const audioError = ref<string | null>(null);

function onAudioFilesChange(e: Event) {
  audioFiles.value = Array.from((e.target as HTMLInputElement).files ?? []);
}

const audioSummary = computed(() =>
  audioResult.value
    ? `${audioResult.value.teile_updated ?? 0} Teil(e) mis à jour sur ${audioResult.value.files_processed ?? 0} fichier(s)`
    : null,
);

async function submitAudio() {
  if (!audioFiles.value.length || !audioSubjectId.value) return;
  audioLoading.value = true;
  audioError.value = null;
  audioResult.value = null;

  const result = await store.adminImportAudio(
    audioSubjectId.value,
    audioFiles.value,
  );
  if (result.success) {
    audioResult.value = result.data;
  } else {
    audioError.value = result.error || "Erreur lors de l'import audio.";
  }
  audioLoading.value = false;
}

// ── 3. Images ────────────────────────────────────────────

const imagesInput = ref<HTMLInputElement | null>(null);
const imagesFiles = ref<File[]>([]);
const imagesSubjectId = ref<string | null>(null);
const imagesLoading = ref(false);
const imagesResult = ref<{ log?: string[]; files_saved?: number } | null>(null);
const imagesError = ref<string | null>(null);

function onImagesFilesChange(e: Event) {
  imagesFiles.value = Array.from((e.target as HTMLInputElement).files ?? []);
}

const imagesSummary = computed(() =>
  imagesResult.value
    ? `${imagesResult.value.files_saved ?? 0} image(s) déposée(s)`
    : null,
);

async function submitImages() {
  if (!imagesFiles.value.length || !imagesSubjectId.value) return;
  imagesLoading.value = true;
  imagesError.value = null;
  imagesResult.value = null;

  const result = await store.adminImportImages(
    imagesSubjectId.value,
    imagesFiles.value,
  );
  if (result.success) {
    imagesResult.value = result.data;
  } else {
    imagesError.value = result.error || "Erreur lors de l'import images.";
  }
  imagesLoading.value = false;
}
</script>
