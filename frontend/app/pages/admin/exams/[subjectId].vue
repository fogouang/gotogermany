<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <div
      v-else-if="!subject"
      class="text-center py-16 bg-white rounded-xl border border-gray-100"
    >
      <i
        class="pi pi-exclamation-triangle text-4xl text-red-400 mb-3 block"
      ></i>
      <p class="font-medium text-gray-700">Sujet introuvable</p>
      <Button label="Retour" outlined class="mt-4" @click="router.back()" />
    </div>

    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-3">
        <Button icon="pi pi-arrow-left" text rounded @click="router.back()" />
        <div class="flex-1">
          <p class="text-xs text-gray-400">{{ examName }}</p>
          <h1 class="text-xl font-bold text-gray-900">
            {{ subject.name || `Sujet ${subject.subject_number}` }}
          </h1>
        </div>
        <div class="hidden sm:flex items-center gap-4 text-sm text-gray-500">
          <span
            ><strong class="text-gray-900">{{ totalModules }}</strong>
            modules</span
          >
          <span
            ><strong class="text-gray-900">{{ totalTeile }}</strong> teile</span
          >
          <span
            ><strong class="text-gray-900">{{ totalQuestions }}</strong>
            questions</span
          >
        </div>
      </div>

      <!-- Modules -->
      <div class="space-y-6">
        <div
          v-for="mod in subject.modules"
          :key="mod.id"
          class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
        >
          <!-- Module header -->
          <div
            class="flex items-center gap-3 px-5 py-4 border-b border-gray-100 bg-gray-50"
          >
            <div
              :class="[
                'w-9 h-9 rounded-lg flex items-center justify-center shrink-0',
                getModuleColor(mod.slug),
              ]"
            >
              <i :class="['pi text-sm', getModuleIcon(mod.slug)]"></i>
            </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900">{{ mod.name }}</p>
              <p class="text-xs text-gray-400">
                {{ mod.time_limit_minutes }}min · {{ mod.max_score }}pts ·
                {{ mod.teile?.length }} teile
              </p>
            </div>
          </div>

          <!-- Teile -->
          <div class="divide-y divide-gray-50">
            <div v-for="teil in mod.teile" :key="teil.id">
              <!-- Teil header -->
              <div
                class="flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors"
              >
                <!-- Toggle -->
                <button
                  class="flex items-center gap-3 flex-1 text-left"
                  @click="toggleTeil(teil.id)"
                >
                  <span
                    class="text-xs font-bold bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono"
                  >
                    Teil {{ teil.teil_number }}
                  </span>
                  <span class="text-xs text-gray-400">{{
                    teil.format_type
                  }}</span>
                  <span class="text-xs text-gray-500 font-medium">
                    {{ (teil as any).questions?.length ?? 0 }} question(s)
                  </span>
                  <span
                    v-if="getTeilConfigImageCount(teil) > 0"
                    class="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-medium"
                  >
                    <i class="pi pi-image text-xs mr-1"></i
                    >{{ getTeilConfigImageCount(teil) }} image(s)
                  </span>
                </button>

                <!-- Upload image config -->
                <div class="flex items-center gap-2 shrink-0">
                  <label
                    :for="`teil-img-${teil.id}`"
                    class="inline-flex items-center gap-1.5 cursor-pointer text-xs font-medium px-3 py-1.5 rounded-lg border border-dashed transition-colors"
                    :class="
                      uploadingTeilImage === teil.id
                        ? 'border-teal-300 text-teal-500'
                        : 'border-gray-200 text-gray-400 hover:border-teal-300 hover:text-teal-600'
                    "
                    v-tooltip.top="
                      'Uploader une image config (person_a, speaker_b, article, topic, image)'
                    "
                  >
                    <i class="pi pi-upload text-xs"></i>
                    {{
                      uploadingTeilImage === teil.id
                        ? "Upload…"
                        : "Image config"
                    }}
                  </label>
                  <input
                    :id="`teil-img-${teil.id}`"
                    type="file"
                    accept=".png,.jpg,.jpeg,.webp"
                    multiple
                    class="hidden"
                    @change="(e) => handleUploadTeilImage(mod, teil, e)"
                  />
                  <i
                    :class="[
                      'pi text-gray-300 text-xs cursor-pointer',
                      expandedTeile.has(teil.id)
                        ? 'pi-chevron-up'
                        : 'pi-chevron-down',
                    ]"
                    @click="toggleTeil(teil.id)"
                  ></i>
                </div>
              </div>

              <!-- Contenu expandé -->
              <div
                v-if="expandedTeile.has(teil.id)"
                class="px-5 pb-5 space-y-4"
              >
                <!-- Instructions -->
                <div
                  v-if="teil.instructions"
                  class="bg-blue-50 rounded-lg px-4 py-2 text-xs text-blue-700"
                >
                  {{ teil.instructions }}
                </div>

                <!-- ── Images config ── -->
                <div
                  v-if="
                    getTeilConfigImageCount(teil) > 0 || hasConfigImages(teil)
                  "
                  class="space-y-3"
                >
                  <p
                    class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
                  >
                    Images associées au config
                  </p>

                  <!-- Persons -->
                  <div
                    v-if="teil.config?.persons"
                    class="grid grid-cols-2 sm:grid-cols-4 gap-3"
                  >
                    <div
                      v-for="(person, key) in teil.config.persons"
                      :key="key"
                      class="space-y-1"
                    >
                      <p
                        class="text-xs font-medium text-gray-500 flex items-center gap-1"
                      >
                        <span class="bg-gray-100 px-1.5 rounded font-mono">{{
                          key
                        }}</span>
                        {{ person?.name }}
                      </p>
                      <div v-if="person?.image">
                        <img
                          :src="`${apiBase}/images/${person.image}`"
                          :alt="`Personne ${key}`"
                          class="w-full h-28 object-cover rounded-lg border border-gray-200"
                        />
                        <button
                          class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                          @click="
                            removeConfigImage(teil, 'persons', String(key))
                          "
                        >
                          <i class="pi pi-trash text-xs"></i> Supprimer
                        </button>
                      </div>
                      <div
                        v-else
                        class="h-28 rounded-lg border-2 border-dashed border-gray-100 flex items-center justify-center"
                      >
                        <span class="text-xs text-gray-300">Aucune image</span>
                      </div>
                    </div>
                  </div>

                  <!-- Speakers -->
                  <div
                    v-if="teil.config?.speakers"
                    class="grid grid-cols-2 sm:grid-cols-3 gap-3"
                  >
                    <div
                      v-for="(speaker, key) in teil.config.speakers"
                      :key="key"
                      class="space-y-1"
                    >
                      <p
                        class="text-xs font-medium text-gray-500 flex items-center gap-1"
                      >
                        <span class="bg-gray-100 px-1.5 rounded font-mono">{{
                          key
                        }}</span>
                        {{ getSpeakerName(speaker) }}
                      </p>
                      <div v-if="getSpeakerImage(speaker)">
                        <img
                          :src="`${apiBase}/images/${getSpeakerImage(speaker)}`"
                          :alt="`Speaker ${key}`"
                          class="w-full h-28 object-cover rounded-lg border border-gray-200"
                        />
                        <button
                          class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                          @click="
                            removeConfigImage(teil, 'speakers', String(key))
                          "
                        >
                          <i class="pi pi-trash text-xs"></i> Supprimer
                        </button>
                      </div>
                      <div
                        v-else
                        class="h-28 rounded-lg border-2 border-dashed border-gray-100 flex items-center justify-center"
                      >
                        <span class="text-xs text-gray-300">Aucune image</span>
                      </div>
                    </div>
                  </div>
                  <!-- Audio images (Hören Teil 1/3 — une image par audio) -->
                  <div
                    v-if="teil.config?.audio_images"
                    class="grid grid-cols-2 sm:grid-cols-4 gap-3"
                  >
                    <div
                      v-for="(imgPath, num) in teil.config.audio_images"
                      :key="num"
                      class="space-y-1"
                    >
                      <p
                        class="text-xs font-medium text-gray-500 flex items-center gap-1"
                      >
                        <span class="bg-gray-100 px-1.5 rounded font-mono"
                          >Audio {{ num }}</span
                        >
                      </p>
                      <div v-if="imgPath">
                        <img
                          :src="`${apiBase}/images/${imgPath}`"
                          :alt="`Audio ${num}`"
                          class="w-full h-28 object-cover rounded-lg border border-gray-200"
                        />
                        <button
                          class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                          @click="
                            removeConfigImage(teil, 'audio_images', String(num))
                          "
                        >
                          <i class="pi pi-trash text-xs"></i> Supprimer
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Anzeigen (Lesen matching/selektives_matching — texte + image par annonce) -->
                  <div
                    v-if="teil.config?.anzeigen"
                    class="grid grid-cols-2 sm:grid-cols-3 gap-3"
                  >
                    <div
                      v-for="(anzeige, key) in teil.config.anzeigen"
                      :key="key"
                      class="space-y-1"
                    >
                      <p
                        class="text-xs font-medium text-gray-500 flex items-center gap-1"
                      >
                        <span class="bg-gray-100 px-1.5 rounded font-mono">{{
                          String(key).toUpperCase()
                        }}</span>
                        <span class="truncate">{{
                          getAnzeigeTitle(anzeige)
                        }}</span>
                      </p>
                      <div v-if="getAnzeigeImage(anzeige)">
                        <img
                          :src="`${apiBase}/images/${getAnzeigeImage(anzeige)}`"
                          :alt="`Annonce ${key}`"
                          class="w-full h-28 object-cover rounded-lg border border-gray-200"
                        />
                        <button
                          class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                          @click="
                            removeConfigImage(teil, 'anzeigen', String(key))
                          "
                        >
                          <i class="pi pi-trash text-xs"></i> Supprimer
                        </button>
                      </div>
                      <div
                        v-else
                        class="h-28 rounded-lg border-2 border-dashed border-gray-100 flex items-center justify-center"
                      >
                        <span class="text-xs text-gray-300">Aucune image</span>
                      </div>
                    </div>
                  </div>
                  <!-- Article image -->
                  <div
                    v-if="teil.config?.article_image !== undefined"
                    class="space-y-1"
                  >
                    <p class="text-xs font-medium text-gray-500">
                      Image article
                    </p>
                    <div v-if="teil.config.article_image">
                      <img
                        :src="`${apiBase}/images/${teil.config.article_image}`"
                        alt="Article"
                        class="h-36 w-auto object-contain rounded-lg border border-gray-200"
                      />
                      <button
                        class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                        @click="removeConfigImage(teil, 'article_image')"
                      >
                        <i class="pi pi-trash text-xs"></i> Supprimer
                      </button>
                    </div>
                    <div
                      v-else
                      class="h-28 rounded-lg border-2 border-dashed border-gray-100 flex items-center justify-center"
                    >
                      <span class="text-xs text-gray-300">Aucune image</span>
                    </div>
                  </div>

                  <!-- stimulus_image -->
                  <div
                    v-if="teil.config?.stimulus_image !== undefined"
                    class="space-y-1"
                  >
                    <p class="text-xs font-medium text-gray-500">
                      Image stimulus
                    </p>
                    <div v-if="teil.config.stimulus_image">
                      <img
                        :src="`${apiBase}/images/${teil.config.stimulus_image}`"
                        alt="Stimulus"
                        class="h-36 w-auto object-contain rounded-lg border border-gray-200"
                      />
                      <button
                        class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                        @click="removeConfigImage(teil, 'stimulus_image')"
                      >
                        <i class="pi pi-trash text-xs"></i> Supprimer
                      </button>
                    </div>
                  </div>

                  <!-- Topic image -->
                  <div
                    v-if="teil.config?.topic_image !== undefined"
                    class="space-y-1"
                  >
                    <p class="text-xs font-medium text-gray-500">Image topic</p>
                    <div v-if="teil.config.topic_image">
                      <img
                        :src="`${apiBase}/images/${teil.config.topic_image}`"
                        alt="Topic"
                        class="h-36 w-auto object-contain rounded-lg border border-gray-200"
                      />
                      <button
                        class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                        @click="removeConfigImage(teil, 'topic_image')"
                      >
                        <i class="pi pi-trash text-xs"></i> Supprimer
                      </button>
                    </div>
                    <div
                      v-else
                      class="h-28 rounded-lg border-2 border-dashed border-gray-100 flex items-center justify-center"
                    >
                      <span class="text-xs text-gray-300">Aucune image</span>
                    </div>
                  </div>

                  <!-- Image générique -->
                  <div
                    v-if="teil.config?.image !== undefined"
                    class="space-y-1"
                  >
                    <p class="text-xs font-medium text-gray-500">Image</p>
                    <div v-if="teil.config.image">
                      <img
                        :src="`${apiBase}/images/${teil.config.image}`"
                        alt="Image"
                        class="h-36 w-auto object-contain rounded-lg border border-gray-200"
                      />
                      <button
                        class="text-xs text-red-400 hover:text-red-600 mt-1 flex items-center gap-1"
                        @click="removeConfigImage(teil, 'image')"
                      >
                        <i class="pi pi-trash text-xs"></i> Supprimer
                      </button>
                    </div>
                    <div
                      v-else
                      class="h-28 rounded-lg border-2 border-dashed border-gray-100 flex items-center justify-center"
                    >
                      <span class="text-xs text-gray-300">Aucune image</span>
                    </div>
                  </div>
                </div>

                <!-- ── Questions (lecture seule) ── -->
                <div class="space-y-2">
                  <p
                    class="text-xs font-semibold text-gray-400 uppercase tracking-wide"
                  >
                    Questions
                  </p>
                  <div
                    v-for="q in (teil as any).questions ?? []"
                    :key="q.id"
                    class="border border-gray-100 rounded-lg px-4 py-3 flex items-center gap-3"
                  >
                    <span class="text-xs font-bold text-gray-400 shrink-0"
                      >Q{{ q.question_number }}</span
                    >
                    <span
                      class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded shrink-0"
                      >{{ q.question_type }}</span
                    >
                    <p
                      class="text-sm text-gray-600 line-clamp-1 flex-1 min-w-0"
                    >
                      {{
                        q.content?.statement ||
                        q.content?.stem ||
                        q.content?.scenario ||
                        q.content?.situation ||
                        "—"
                      }}
                    </p>
                    <span class="text-xs text-gray-400 shrink-0"
                      >{{ q.points }}pt</span
                    >
                    <span
                      v-if="q.audio_file"
                      class="text-xs text-purple-500 shrink-0 flex items-center gap-1"
                    >
                      <i class="pi pi-volume-up text-xs"></i>
                    </span>
                  </div>
                  <div
                    v-if="!(teil as any).questions?.length"
                    class="text-center py-3 text-gray-400 text-xs"
                  >
                    Aucune question
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "admin" });

const route = useRoute();
const router = useRouter();
const toast = useToast();
const config = useRuntimeConfig();

const subjectId = route.params.subjectId as string;
const examId = route.query.examId as string;
const apiBase = config.public.apiBaseUrl || "http://localhost:8001";

const loading = ref(true);
const subject = ref<any>(null);
const examName = ref("");
const expandedTeile = ref<Set<string>>(new Set());
const uploadingTeilImage = ref<string | null>(null);

// ── Setup API ────────────────────────────────────────────
const setupApi = async () => {
  const { OpenAPI } = await import("#shared/api");
  OpenAPI.BASE = apiBase;
  const token = useCookie("access_token");
  OpenAPI.TOKEN = token.value ?? undefined;
};

// ── Chargement ───────────────────────────────────────────
onMounted(async () => {
  await setupApi();
  const { ExamsService, QuestionsService } = await import("#shared/api");
  try {
    const detail = await ExamsService.getExamDetailApiV1ExamsExamIdGet(examId);
    examName.value = detail.name;
    for (const level of detail.levels ?? []) {
      const found = level.subjects?.find((s: any) => s.id === subjectId);
      if (found) {
        for (const mod of found.modules ?? []) {
          for (const teil of mod.teile ?? []) {
            try {
              (teil as any).questions =
                await QuestionsService.adminGetQuestionsApiV1AdminTeileTeilIdQuestionsGet(
                  teil.id,
                );
            } catch {
              (teil as any).questions = [];
            }
          }
        }
        subject.value = found;
        break;
      }
    }
  } finally {
    loading.value = false;
  }
});

// ── Computed ─────────────────────────────────────────────
const totalModules = computed(() => subject.value?.modules?.length ?? 0);
const totalTeile = computed(() =>
  (subject.value?.modules ?? []).reduce(
    (s: number, m: any) => s + (m.teile?.length ?? 0),
    0,
  ),
);
const totalQuestions = computed(() =>
  (subject.value?.modules ?? []).reduce(
    (s: number, m: any) =>
      s +
      (m.teile ?? []).reduce(
        (st: number, t: any) => st + (t.questions?.length ?? 0),
        0,
      ),
    0,
  ),
);

// ── Config helpers ───────────────────────────────────────
const getTeilConfigImageCount = (teil: any): number => {
  let count = 0;
  const c = teil.config ?? {};
  if (c.persons)
    count += Object.values(c.persons).filter((p: any) => p?.image).length;
  if (c.speakers)
    count += Object.values(c.speakers).filter(
      (s: any) => typeof s === "object" && s?.image,
    ).length;
  if (c.audio_images) count += Object.keys(c.audio_images).length;
  if (c.anzeigen)
    count += Object.values(c.anzeigen).filter(
      (a: any) => typeof a === "object" && a?.image,
    ).length; // ← ajouté
  if (c.article_image) count++;
  if (c.topic_image) count++;
  if (c.image) count++;
  if (c.stimulus_image) count++;
  return count;
};

const hasConfigImages = (teil: any): boolean => {
  const c = teil.config ?? {};
  return !!(
    c.persons ||
    c.speakers ||
    c.audio_images ||
    c.anzeigen || // ← ajouté
    c.article_image !== undefined ||
    c.topic_image !== undefined ||
    c.image !== undefined
  );
};

const getSpeakerImage = (speaker: any): string | null =>
  typeof speaker === "object" ? (speaker?.image ?? null) : null;

const getSpeakerName = (speaker: any): string =>
  typeof speaker === "object" ? (speaker?.name ?? "") : String(speaker);

// ── Toggle teil ──────────────────────────────────────────
const toggleTeil = (teilId: string) => {
  if (expandedTeile.value.has(teilId)) expandedTeile.value.delete(teilId);
  else expandedTeile.value.add(teilId);
};

const getAnzeigeImage = (anzeige: any): string | null =>
  typeof anzeige === "object" ? (anzeige?.image ?? null) : null;

const getAnzeigeTitle = (anzeige: any): string =>
  typeof anzeige === "object" ? (anzeige?.title ?? "") : "";

// ── Upload image config Teil ─────────────────────────────
const handleUploadTeilImage = async (mod: any, teil: any, e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (!files || files.length === 0) return;

  uploadingTeilImage.value = teil.id;
  try {
    await setupApi();
    const { OpenAPI, ExamsService } = await import("#shared/api");

    const formData = new FormData();
    for (const file of Array.from(files)) {
      formData.append("files", file); // même clé "files" pour chaque fichier sélectionné
    }
    formData.append("subject_number", String(subject.value.subject_number));
    formData.append("teil_id", teil.id); // ← le fix : on dit explicitement quel Teil cibler

    const response = await fetch(
      `${OpenAPI.BASE}/api/v1/exams/admin/${examId}/teil-images`,
      { method: "POST", credentials: "include", body: formData },
    );

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Erreur upload");
    }

    const result = await response.json();
    console.log("Result:", result);

    // Recharger le config du Teil pour le preview
    const detail = await ExamsService.getExamDetailApiV1ExamsExamIdGet(examId);
    for (const level of detail.levels ?? []) {
      const found = level.subjects?.find((s: any) => s.id === subjectId);
      if (found) {
        for (const m of found.modules ?? []) {
          if (m.id === mod.id) {
            const updatedTeil = m.teile?.find((t: any) => t.id === teil.id);
            if (updatedTeil) teil.config = updatedTeil.config;
          }
        }
      }
    }
    console.log(teil.config);

    toast.add({
      severity: "success",
      summary: `${result.updated ?? 0} image(s) associée(s)`,
      life: 3000,
    });

    if (result.not_found?.length) {
      toast.add({
        severity: "warn",
        summary: `${result.not_found.length} fichier(s) ignoré(s)`,
        detail: result.not_found.join(", "),
        life: 5000,
      });
    }
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: err.message || "Erreur upload",
      life: 3000,
    });
  } finally {
    uploadingTeilImage.value = null;
    (e.target as HTMLInputElement).value = "";
  }
};

// ── Supprimer image config ───────────────────────────────
const removeConfigImage = async (teil: any, type: string, key?: string) => {
  try {
    await setupApi();
    const { ExamsService } = await import("#shared/api");

    const config = { ...(teil.config ?? {}) };

    if (type === "persons" && key) {
      config.persons = { ...config.persons };
      delete config.persons[key].image;
    } else if (type === "speakers" && key) {
      config.speakers = { ...config.speakers };
      if (typeof config.speakers[key] === "object") {
        delete config.speakers[key].image;
      }
    } else if (type === "audio_images" && key) {
      // ← ajouté
      config.audio_images = { ...config.audio_images };
      delete config.audio_images[key];
      if (Object.keys(config.audio_images).length === 0) {
        delete config.audio_images;
      }
    } else if (type === "anzeigen" && key) {
      // ← ajouté
      config.anzeigen = { ...config.anzeigen };
      if (typeof config.anzeigen[key] === "object") {
        delete config.anzeigen[key].image;
      }
    } else {
      delete config[type];
    }

    await ExamsService.updateTeilApiV1ExamsTeileTeilIdPatch(teil.id, {
      config,
    });
    teil.config = config;
    toast.add({ severity: "success", summary: "Image supprimée", life: 3000 });
  } catch (err: any) {
    toast.add({ severity: "error", summary: "Erreur suppression", life: 3000 });
  }
};

// ── Style helpers ────────────────────────────────────────
const getModuleIcon = (s: string) => {
  if (s.includes("lesen")) return "pi-book";
  if (s.includes("horen") || s.includes("hören")) return "pi-volume-up";
  if (s.includes("schreiben")) return "pi-pencil";
  if (s.includes("sprechen")) return "pi-microphone";
  return "pi-file";
};
const getModuleColor = (s: string) => {
  if (s.includes("lesen")) return "bg-blue-100 text-blue-600";
  if (s.includes("horen") || s.includes("hören"))
    return "bg-purple-100 text-purple-600";
  if (s.includes("schreiben")) return "bg-green-100 text-green-600";
  if (s.includes("sprechen")) return "bg-orange-100 text-orange-600";
  return "bg-gray-100 text-gray-600";
};

watchEffect(() => {
  if (subject.value) {
    useHead({
      title: `${subject.value.name || "Sujet " + subject.value.subject_number} — Admin`,
    });
  }
});
</script>
