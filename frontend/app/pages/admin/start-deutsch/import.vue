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
        Importe le sujet, puis l'audio du Hören et les images.
      </p>
    </div>

    <div class="grid items-start gap-4 xl:grid-cols-3">
      <!-- ══════════ 1. Sujet (JSON) ══════════ -->
      <section
        class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <header class="flex items-center gap-3">
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary"
            >1</span
          >
          <div>
            <h2 class="font-semibold text-ink">Sujet</h2>
            <p class="text-xs text-muted">
              Fichier JSON d'un sujet A1 ou A2. Chaque import crée un nouveau
              sujet.
            </p>
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

        <Button
          label="Importer le sujet"
          icon="pi pi-upload"
          class="w-full"
          :loading="jsonLoading"
          :disabled="!jsonFiles.length"
          @click="submitJson"
        />

        <!-- Résumé de l'import : un bloc par module -->
        <div
          v-if="jsonResult"
          class="space-y-3 rounded-leaf border border-emerald-500/30 bg-emerald-500/5 p-4"
        >
          <div class="flex items-start gap-2">
            <i class="pi pi-check-circle mt-0.5 text-emerald-600" />
            <div class="min-w-0">
              <p class="text-sm font-semibold text-ink">
                {{ jsonResult.title }}
              </p>
              <p class="text-xs text-muted">
                {{ jsonResult.level }} · sujet n°{{ jsonResult.subject_number }}
                · {{ jsonResult.total_questions }} questions
              </p>
            </div>
          </div>

          <div class="space-y-2">
            <div
              v-for="group in importedModules"
              :key="group.module"
              class="rounded-leaf bg-card px-3 py-2"
            >
              <p
                class="mb-1 text-xs font-semibold uppercase tracking-wide text-muted"
              >
                {{ moduleLabel(group.module) }}
              </p>
              <ul class="space-y-0.5 text-xs text-ink">
                <li
                  v-for="t in group.teile"
                  :key="t.teil_number"
                  class="flex items-center justify-between gap-2"
                >
                  <span
                    >Teil {{ t.teil_number }} ·
                    {{ formatLabel(t.format_type) }}</span
                  >
                  <span class="tabular-nums text-muted">{{ t.questions }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <Message v-if="jsonError" severity="error" :closable="false">
          {{ jsonError }}
        </Message>
      </section>

      <!-- ══════════ 2 et 3. Médias du sujet ══════════ -->
      <section
        ref="mediaSection"
        class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft xl:col-span-2"
      >
        <header
          class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between"
        >
          <div class="flex items-center gap-3">
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-sky-500/10 text-sm font-bold text-sky-600"
              >2</span
            >
            <div>
              <h2 class="font-semibold text-ink">Audio et images</h2>
              <p class="text-xs text-muted">
                La liste des fichiers attendus vient du sujet choisi.
              </p>
            </div>
          </div>

          <div class="w-full lg:w-96">
            <label class="mb-1.5 block text-xs font-medium text-muted"
              >Sujet</label
            >
            <Select
              v-model="subjectId"
              :options="subjectOptions"
              optionLabel="label"
              optionValue="id"
              filter
              placeholder="Choisir le sujet"
              class="w-full"
            />
          </div>
        </header>

        <!-- Aucun sujet choisi -->
        <div
          v-if="!subjectId"
          class="flex flex-col items-center gap-2 rounded-leaf border border-dashed border-line px-6 py-10 text-center"
        >
          <i class="pi pi-folder-open text-xl text-faint" />
          <p class="text-sm text-muted">
            Choisis un sujet, ou importe-en un : il sera sélectionné ici.
          </p>
        </div>

        <div v-else-if="mediaLoading && !media" class="grid gap-4 md:grid-cols-2">
          <div
            v-for="n in 2"
            :key="n"
            class="h-64 animate-pulse rounded-leaf bg-card-2"
          />
        </div>

        <div v-else-if="media" class="grid items-start gap-4 md:grid-cols-2">
          <!-- ── Audio ── -->
          <div class="space-y-3 rounded-leaf border border-line p-4">
            <div class="flex items-center justify-between gap-2">
              <h3 class="flex items-center gap-2 text-sm font-semibold text-ink">
                <i class="pi pi-volume-up text-sky-600" /> Audio du Hören
              </h3>
              <ProgressPill
                :done="audioDone"
                :total="media.audio.length"
              />
            </div>

            <p v-if="!media.audio.length" class="text-xs text-muted">
              Ce sujet n'a pas de module Hören.
            </p>

            <template v-else>
              <ul class="divide-y divide-line rounded-leaf bg-card-2">
                <li
                  v-for="item in media.audio"
                  :key="item.filename"
                  class="flex items-center justify-between gap-2 px-3 py-2 text-xs"
                >
                  <span class="min-w-0">
                    <span class="font-medium text-ink"
                      >Teil {{ item.teil_number }}</span
                    >
                    <code class="ml-2 text-muted">{{ item.filename }}</code>
                  </span>
                  <FileState :state="stateOf(item, audioSelected)" />
                </li>
              </ul>

              <FileDropZone
                v-model="audioFiles"
                accept="audio/mpeg,.mp3"
                multiple
                icon="pi pi-volume-up"
                label="Dépose les fichiers MP3"
                :disabled="audioLoading"
              />

              <Message
                v-if="audioUnknown.length"
                severity="warn"
                :closable="false"
              >
                Nom non reconnu, fichier ignoré :
                {{ audioUnknown.join(", ") }}
              </Message>

              <Button
                label="Importer l'audio"
                icon="pi pi-upload"
                class="w-full"
                :loading="audioLoading"
                :disabled="!audioFiles.length"
                @click="submitAudio"
              />

              <ImportLogPanel
                :log="audioResult?.log"
                :summary="audioSummary"
                :error="audioError"
              />
            </template>
          </div>

          <!-- ── Images ── -->
          <div class="space-y-3 rounded-leaf border border-line p-4">
            <div class="flex items-center justify-between gap-2">
              <h3 class="flex items-center gap-2 text-sm font-semibold text-ink">
                <i class="pi pi-image text-violet-600" /> Images
              </h3>
              <ProgressPill
                :done="imagesDone"
                :total="media.images.length"
              />
            </div>

            <p v-if="!media.images.length" class="text-xs text-muted">
              Ce sujet n'utilise pas d'images.
            </p>

            <template v-else>
              <div
                class="max-h-72 space-y-2 overflow-y-auto rounded-leaf bg-card-2 p-2"
              >
                <div v-for="group in imageGroups" :key="group.key">
                  <p
                    class="px-1 pb-1 text-[11px] font-semibold uppercase tracking-wide text-muted"
                  >
                    {{ group.label }}
                  </p>
                  <ul class="divide-y divide-line rounded-leaf bg-card">
                    <li
                      v-for="item in group.items"
                      :key="item.filename"
                      class="flex items-center justify-between gap-2 px-3 py-1.5 text-xs"
                    >
                      <code class="min-w-0 truncate text-muted">{{
                        item.filename
                      }}</code>
                      <FileState :state="stateOf(item, imagesSelected)" />
                    </li>
                  </ul>
                </div>
              </div>

              <FileDropZone
                v-model="imagesFiles"
                accept="image/png,image/jpeg,image/webp"
                multiple
                icon="pi pi-image"
                label="Dépose les images"
                hint="PNG, JPEG ou WEBP, avec les noms ci-dessus"
                :disabled="imagesLoading"
              />

              <Message
                v-if="imagesUnknown.length"
                severity="warn"
                :closable="false"
              >
                Aucun de ces noms n'est cité dans le sujet, ils seront ignorés :
                {{ imagesUnknown.join(", ") }}
              </Message>

              <Button
                label="Importer les images"
                icon="pi pi-upload"
                class="w-full"
                :loading="imagesLoading"
                :disabled="!imagesFiles.length"
                @click="submitImages"
              />

              <ImportLogPanel
                :log="imagesResult?.log"
                :summary="imagesSummary"
                :error="imagesError"
              />
            </template>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import ImportLogPanel from "~/components/admin/ImportLogPanel.vue";
import type {
  StartDeutschMediaFile,
  StartDeutschMediaStatus,
} from "~/stores/start-deutsch-session";

definePageMeta({ layout: "admin", watermark: "Hochladen" });

const route = useRoute();
const toast = useToast();
const store = useStartDeutschSessionStore();

const MODULE_LABELS: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
};

const FORMAT_LABELS: Record<string, string> = {
  mc_text: "QCM",
  mc_image: "QCM en images",
  true_false: "Richtig / Falsch",
  ja_nein: "Ja / Nein",
  matching_2options: "Choix entre deux annonces",
  matching_with_distractor: "Annonces à associer",
  image_day_matching: "Images et jours",
  form_fill: "Formulaire",
  free_text: "Texte libre",
  sprechen_group_intro: "Se présenter",
  sprechen_group_word_card: "Cartes mots",
  sprechen_group_image_card: "Cartes images",
  sprechen_duo_question_card: "Cartes questions",
  sprechen_duo_monologue_card: "Parler de soi",
  sprechen_duo_negotiation: "Trouver un rendez-vous",
};

const moduleLabel = (slug: string) => MODULE_LABELS[slug] ?? slug;
const formatLabel = (format: string) => FORMAT_LABELS[format] ?? format;

// ── Petits composants d'affichage ──

type FileStateValue = "done" | "ready" | "missing";

const FILE_STATES: Record<FileStateValue, { label: string; icon: string; cls: string }> = {
  done: { label: "Importé", icon: "pi-check-circle", cls: "text-emerald-600" },
  ready: { label: "Prêt", icon: "pi-arrow-circle-up", cls: "text-primary" },
  missing: { label: "Manquant", icon: "pi-circle", cls: "text-faint" },
};

const FileState = (props: { state: FileStateValue }) => {
  const s = FILE_STATES[props.state];
  return h(
    "span",
    { class: ["inline-flex shrink-0 items-center gap-1 font-medium", s.cls] },
    [h("i", { class: ["pi text-[11px]", s.icon] }), s.label],
  );
};
FileState.props = ["state"];

const ProgressPill = (props: { done: number; total: number }) =>
  h(
    "span",
    {
      class: [
        "rounded-full px-2 py-0.5 text-[11px] font-semibold tabular-nums",
        props.total > 0 && props.done === props.total
          ? "bg-emerald-500/10 text-emerald-600"
          : "bg-card-2 text-muted",
      ],
    },
    `${props.done} / ${props.total}`,
  );
ProgressPill.props = ["done", "total"];

// ── Sujets ──
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

// ── Sujet visé et fichiers attendus ──
const subjectId = ref<string | null>(null);
const media = ref<StartDeutschMediaStatus | null>(null);
const mediaLoading = ref(false);
const mediaSection = ref<HTMLElement | null>(null);

async function loadMedia() {
  if (!subjectId.value) {
    media.value = null;
    return;
  }
  mediaLoading.value = true;
  const result = await store.adminMediaStatus(subjectId.value);
  if (result.success && result.data) {
    media.value = result.data;
  } else {
    media.value = null;
    toast.add({
      severity: "error",
      summary: "Médias du sujet",
      detail: result.error,
      life: 4000,
    });
  }
  mediaLoading.value = false;
}

watch(subjectId, () => {
  audioFiles.value = [];
  imagesFiles.value = [];
  audioResult.value = imagesResult.value = null;
  audioError.value = imagesError.value = null;
  media.value = null;
  loadMedia();
});

const norm = (name: string) => name.trim().toLowerCase();

const stateOf = (
  item: StartDeutschMediaFile,
  selected: Set<string>,
): FileStateValue =>
  selected.has(norm(item.filename))
    ? "ready"
    : item.imported
      ? "done"
      : "missing";

const unknownNames = (files: File[], expected: StartDeutschMediaFile[]) => {
  const names = new Set(expected.map((f) => norm(f.filename)));
  return files.filter((f) => !names.has(norm(f.name))).map((f) => f.name);
};

// Lien depuis la liste des sujets : /admin/start-deutsch/import?subjectId=...
onMounted(async () => {
  await fetchSubjects();
  const preset =
    typeof route.query.subjectId === "string" ? route.query.subjectId : null;
  if (preset && subjects.value.some((s) => s.id === preset)) {
    subjectId.value = preset;
    await nextTick();
    mediaSection.value?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

// ── 1. JSON ──
interface JsonImportResult {
  subject_id: string;
  subject_number: number;
  title: string;
  level: string;
  total_questions: number;
  teile: {
    module: string;
    teil_number: number;
    format_type: string;
    questions: number;
  }[];
}

const jsonFiles = ref<File[]>([]);
const jsonLoading = ref(false);
const jsonResult = ref<JsonImportResult | null>(null);
const jsonError = ref<string | null>(null);

const importedModules = computed(() => {
  const groups: { module: string; teile: JsonImportResult["teile"] }[] = [];
  for (const t of jsonResult.value?.teile ?? []) {
    let g = groups.find((x) => x.module === t.module);
    if (!g) {
      g = { module: t.module, teile: [] };
      groups.push(g);
    }
    g.teile.push(t);
  }
  return groups;
});

async function submitJson() {
  const file = jsonFiles.value[0];
  if (!file) return;
  jsonLoading.value = true;
  jsonError.value = null;
  jsonResult.value = null;

  const result = await store.adminImportJson(file);
  if (result.success) {
    jsonResult.value = result.data;
    jsonFiles.value = [];
    await fetchSubjects();
    // Le nouveau sujet devient le sujet visé pour l'audio et les images
    subjectId.value = result.data.subject_id;
    toast.add({
      severity: "success",
      summary: "Sujet importé",
      detail: "Ajoute maintenant l'audio et les images.",
      life: 3000,
    });
  } else {
    jsonError.value = result.error || "Erreur lors de l'import.";
  }
  jsonLoading.value = false;
}

// ── 2. Audio ──
const audioFiles = ref<File[]>([]);
const audioLoading = ref(false);
const audioResult = ref<{
  log?: string[];
  teile_updated?: number;
  files_processed?: number;
} | null>(null);
const audioError = ref<string | null>(null);

const audioSelected = computed(
  () => new Set(audioFiles.value.map((f) => norm(f.name))),
);
const audioUnknown = computed(() =>
  unknownNames(audioFiles.value, media.value?.audio ?? []),
);
const audioDone = computed(
  () => media.value?.audio.filter((a) => a.imported).length ?? 0,
);

const audioSummary = computed(() =>
  audioResult.value
    ? `${audioResult.value.teile_updated ?? 0} Teil(e) mis à jour`
    : null,
);

async function submitAudio() {
  if (!audioFiles.value.length || !subjectId.value) return;
  audioLoading.value = true;
  audioError.value = null;
  audioResult.value = null;

  const result = await store.adminImportAudio(
    subjectId.value,
    audioFiles.value,
  );
  if (result.success) {
    audioResult.value = result.data;
    audioFiles.value = [];
    await loadMedia();
  } else {
    audioError.value = result.error || "Erreur lors de l'import audio.";
  }
  audioLoading.value = false;
}

// ── 3. Images ──
const imagesFiles = ref<File[]>([]);
const imagesLoading = ref(false);
const imagesResult = ref<{ log?: string[]; files_saved?: number } | null>(
  null,
);
const imagesError = ref<string | null>(null);

const imagesSelected = computed(
  () => new Set(imagesFiles.value.map((f) => norm(f.name))),
);
const imagesUnknown = computed(() =>
  unknownNames(imagesFiles.value, media.value?.images ?? []),
);
const imagesDone = computed(
  () => media.value?.images.filter((i) => i.imported).length ?? 0,
);

// Une liste par Teil : « Hören · Teil 1 », « Sprechen · Teil 3 »
const imageGroups = computed(() => {
  const groups: {
    key: string;
    label: string;
    items: StartDeutschMediaFile[];
  }[] = [];
  for (const item of media.value?.images ?? []) {
    const key = `${item.module}-${item.teil_number}`;
    let g = groups.find((x) => x.key === key);
    if (!g) {
      g = {
        key,
        label: `${moduleLabel(item.module ?? "")} · Teil ${item.teil_number}`,
        items: [],
      };
      groups.push(g);
    }
    g.items.push(item);
  }
  return groups;
});

const imagesSummary = computed(() =>
  imagesResult.value
    ? `${imagesResult.value.files_saved ?? 0} image(s) déposée(s)`
    : null,
);

async function submitImages() {
  if (!imagesFiles.value.length || !subjectId.value) return;
  imagesLoading.value = true;
  imagesError.value = null;
  imagesResult.value = null;

  const result = await store.adminImportImages(
    subjectId.value,
    imagesFiles.value,
  );
  if (result.success) {
    imagesResult.value = result.data;
    imagesFiles.value = [];
    await loadMedia();
  } else {
    imagesError.value = result.error || "Erreur lors de l'import images.";
  }
  imagesLoading.value = false;
}
</script>