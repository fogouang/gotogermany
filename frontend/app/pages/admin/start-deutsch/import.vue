<!-- pages/admin/start-deutsch/import.vue -->
<template>
  <div class="space-y-5 pb-10">
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <NuxtLink
        to="/admin/start-deutsch"
        class="inline-flex items-center gap-2 text-sm text-muted hover:text-ink"
      >
        <i class="pi pi-arrow-left text-xs" />
        Retour aux sujets
      </NuxtLink>
      <p class="text-sm text-muted">
        Importe d'abord le sujet (JSON), puis ses fichiers audio et ses images.
      </p>
    </div>

    <div class="grid items-start gap-4 xl:grid-cols-3">
      <!-- ══════════ 1. JSON ══════════ -->
      <section
        class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <header class="flex items-center gap-3">
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary"
            >1</span
          >
          <div>
            <h2 class="font-semibold text-ink">Sujet (JSON)</h2>
            <p class="text-xs text-muted">Un sujet A1 ou A2 complet.</p>
          </div>
        </header>

        <FileDropZone
          v-model="jsonFiles"
          accept="application/json,.json"
          icon="pi pi-file"
          label="Dépose le fichier JSON"
          hint="Un seul fichier"
          :disabled="jsonLoading"
        />

        <label
          class="flex cursor-pointer items-center justify-between gap-3 rounded-leaf bg-card-2 px-3 py-2.5 text-sm text-ink"
        >
          <span>
            Remplacer les Teile existants
            <span class="block text-xs text-muted"
              >Écrase les Teile déjà importés pour ce sujet.</span
            >
          </span>
          <ToggleSwitch v-model="jsonReplace" />
        </label>

        <Button
          label="Importer le sujet"
          icon="pi pi-upload"
          class="w-full"
          :loading="jsonLoading"
          :disabled="!jsonFiles.length"
          @click="submitJson"
        />

        <ImportLogPanel
          :log="jsonResult?.log"
          :summary="jsonSummary"
          :error="jsonError"
        />
      </section>

      <!-- ══════════ 2. Audio ══════════ -->
      <section
        ref="audioSection"
        class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <header class="flex items-center gap-3">
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-sky-500/10 text-sm font-bold text-sky-600"
            >2</span
          >
          <div>
            <h2 class="font-semibold text-ink">Fichiers audio (Hören)</h2>
            <p class="text-xs text-muted">Un fichier par Teil.</p>
          </div>
        </header>

        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Sujet visé</label
          >
          <Select
            v-model="audioSubjectId"
            :options="subjectOptions"
            optionLabel="label"
            optionValue="id"
            filter
            placeholder="Choisir le sujet"
            class="w-full"
          />
        </div>

        <FileDropZone
          v-model="audioFiles"
          accept="audio/mpeg,.mp3"
          multiple
          icon="pi pi-volume-up"
          label="Dépose les fichiers MP3"
          :disabled="audioLoading"
        />

        <p class="rounded-leaf bg-card-2 px-3 py-2 text-xs text-muted">
          Nommage : <code class="text-ink">hoeren_teilN.mp3</code>. Les fichiers
          sont rangés par sujet, pas seulement par niveau : vérifie bien le
          sujet choisi.
        </p>

        <Button
          label="Importer l'audio"
          icon="pi pi-upload"
          class="w-full"
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

      <!-- ══════════ 3. Images ══════════ -->
      <section
        class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <header class="flex items-center gap-3">
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-violet-500/10 text-sm font-bold text-violet-600"
            >3</span
          >
          <div>
            <h2 class="font-semibold text-ink">Images</h2>
            <p class="text-xs text-muted">Hören mc_image et cartes Sprechen.</p>
          </div>
        </header>

        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Sujet visé</label
          >
          <Select
            v-model="imagesSubjectId"
            :options="subjectOptions"
            optionLabel="label"
            optionValue="id"
            filter
            placeholder="Choisir le sujet"
            class="w-full"
          />
        </div>

        <FileDropZone
          v-model="imagesFiles"
          accept="image/png,image/jpeg,image/webp"
          multiple
          icon="pi pi-image"
          label="Dépose les images"
          hint="PNG, JPEG ou WEBP"
          :disabled="imagesLoading"
        />

        <p class="rounded-leaf bg-card-2 px-3 py-2 text-xs text-muted">
          Les noms doivent correspondre exactement à
          <code class="text-ink">image_file</code> dans le JSON importé (ex.
          <code class="text-ink">hoeren_teil1_q1_a.png</code>,
          <code class="text-ink">sprechen_teil3_q1.png</code>).
        </p>

        <Button
          label="Importer les images"
          icon="pi pi-upload"
          class="w-full"
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
  </div>
</template>

<script setup lang="ts">
import ImportLogPanel from "~/components/admin/ImportLogPanel.vue";

definePageMeta({ layout: "admin", watermark: "Hochladen" });

const route = useRoute();
const toast = useToast();
const store = useStartDeutschSessionStore();

// ── Sujets (sélecteurs audio et images) ──
interface SubjectOption {
  id: string;
  label: string;
}

const subjects = ref<any[]>([]);
const subjectOptions = computed<SubjectOption[]>(() =>
  subjects.value.map((s) => ({
    id: s.id,
    label: `${s.level} · n°${s.subject_number} · ${s.title}`,
  })),
);

async function fetchSubjects() {
  const result = await store.adminListSubjects();
  if (result.success) {
    subjects.value = result.data;
  } else {
    toast.add({
      severity: "error",
      summary: "Impossible de charger les sujets",
      detail: result.error,
      life: 4000,
    });
  }
}

// Préselection depuis la liste (/admin/start-deutsch/import?subjectId=...)
const audioSection = ref<HTMLElement | null>(null);

onMounted(async () => {
  await fetchSubjects();
  const preset =
    typeof route.query.subjectId === "string" ? route.query.subjectId : null;
  if (preset && subjects.value.some((s) => s.id === preset)) {
    audioSubjectId.value = preset;
    imagesSubjectId.value = preset;
    await nextTick();
    audioSection.value?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

// ── 1. JSON ──
const jsonFiles = ref<File[]>([]);
const jsonReplace = ref(false);
const jsonLoading = ref(false);
const jsonResult = ref<{
  log?: string[];
  total_questions?: number;
  level?: string;
} | null>(null);
const jsonError = ref<string | null>(null);

const jsonSummary = computed(() =>
  jsonResult.value
    ? `Sujet ${jsonResult.value.level ?? ""} importé : ${jsonResult.value.total_questions ?? "?"} question(s)`
    : null,
);

async function submitJson() {
  const file = jsonFiles.value[0];
  if (!file) return;
  jsonLoading.value = true;
  jsonError.value = null;
  jsonResult.value = null;

  const result = await store.adminImportJson(file, jsonReplace.value);
  if (result.success) {
    jsonResult.value = result.data;
    jsonFiles.value = [];
    await fetchSubjects(); // le nouveau sujet apparaît dans les sélecteurs
  } else {
    jsonError.value = result.error || "Erreur lors de l'import.";
  }
  jsonLoading.value = false;
}

// ── 2. Audio ──
const audioFiles = ref<File[]>([]);
const audioSubjectId = ref<string | null>(null);
const audioLoading = ref(false);
const audioResult = ref<{
  log?: string[];
  teile_updated?: number;
  files_processed?: number;
} | null>(null);
const audioError = ref<string | null>(null);

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
    audioFiles.value = [];
  } else {
    audioError.value = result.error || "Erreur lors de l'import audio.";
  }
  audioLoading.value = false;
}

// ── 3. Images ──
const imagesFiles = ref<File[]>([]);
const imagesSubjectId = ref<string | null>(null);
const imagesLoading = ref(false);
const imagesResult = ref<{ log?: string[]; files_saved?: number } | null>(null);
const imagesError = ref<string | null>(null);

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
    imagesFiles.value = [];
  } else {
    imagesError.value = result.error || "Erreur lors de l'import images.";
  }
  imagesLoading.value = false;
}
</script>
