<!-- pages/admin/exams/[subjectId].vue -->
<template>
  <div class="space-y-5">
    <button
      type="button"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
      @click="router.back()"
    >
      <i class="pi pi-arrow-left text-xs" />
      Retour aux examens
    </button>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-4">
      <div class="h-28 animate-pulse rounded-card bg-card-2" />
      <div v-for="n in 3" :key="n" class="h-40 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Introuvable ── -->
    <div
      v-else-if="!subject"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-red-500/10 text-red-600">
        <i class="pi pi-exclamation-triangle" />
      </span>
      <p class="text-sm font-medium text-ink">Sujet introuvable</p>
      <Button label="Retour" outlined size="small" @click="router.back()" />
    </div>

    <template v-else>
      <!-- ══ En-tête ══ -->
      <section class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex min-w-0 items-center gap-4">
            <span class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-ink text-lg font-bold text-card">
              {{ subject.subject_number }}
            </span>
            <div class="min-w-0">
              <p class="truncate text-xs font-semibold uppercase tracking-wider text-muted">{{ examName }}</p>
              <h1 class="truncate text-xl font-bold text-ink">
                {{ subject.name || `Sujet ${subject.subject_number}` }}
              </h1>
            </div>
          </div>
          <Button
            :label="allExpanded ? 'Tout replier' : 'Tout déplier'"
            :icon="allExpanded ? 'pi pi-angle-double-up' : 'pi pi-angle-double-down'"
            outlined
            size="small"
            @click="toggleAllTeile"
          />
        </div>

        <div class="mt-5 grid grid-cols-2 gap-3 border-t border-line pt-5 sm:grid-cols-4">
          <div v-for="s in headerStats" :key="s.label">
            <p class="text-2xl font-bold" :class="s.tone ?? 'text-ink'">{{ s.value }}</p>
            <p class="text-xs text-muted">{{ s.label }}</p>
          </div>
        </div>
      </section>

      <!-- ══ Modules ══ -->
      <article
        v-for="mod in subject.modules"
        :key="mod.id"
        class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <header class="flex items-center gap-3 border-b border-line px-4 py-4 sm:px-5">
          <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf" :class="moduleStyle(mod.slug).box">
            <i :class="['pi text-sm', moduleStyle(mod.slug).icon]" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold text-ink">{{ mod.name }}</p>
            <p class="text-xs text-muted">
              {{ mod.time_limit_minutes }} min · {{ mod.max_score }} pts ·
              {{ mod.teile?.length ?? 0 }} Teil{{ (mod.teile?.length ?? 0) > 1 ? "e" : "" }}
            </p>
          </div>
        </header>

        <div class="divide-y divide-line">
          <div v-for="teil in mod.teile" :key="teil.id">
            <!-- En-tête du Teil -->
            <div class="flex flex-wrap items-center gap-x-3 gap-y-2 px-4 py-3 transition-colors hover:bg-card-2/40 sm:px-5">
              <button
                type="button"
                class="flex min-w-0 flex-1 flex-wrap items-center gap-2 text-left"
                :aria-expanded="expandedTeile.has(teil.id)"
                @click="toggleTeil(teil.id)"
              >
                <span class="rounded-full bg-ink px-2.5 py-0.5 font-mono text-[11px] font-bold text-card">
                  Teil {{ teil.teil_number }}
                </span>
                <span class="rounded-full bg-card-2 px-2 py-0.5 font-mono text-[11px] text-muted">{{ teil.format_type }}</span>
                <span class="text-xs text-muted">
                  {{ (teil as any).questions?.length ?? 0 }} question{{ ((teil as any).questions?.length ?? 0) > 1 ? "s" : "" }}
                </span>
                <span
                  v-if="imageSlots(teil).length"
                  class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="filledCount(teil) === imageSlots(teil).length ? 'bg-emerald-500/10 text-emerald-600' : 'bg-amber-500/15 text-amber-600'"
                >
                  <i class="pi pi-image text-[10px]" />
                  {{ filledCount(teil) }}/{{ imageSlots(teil).length }}
                </span>
              </button>

              <div class="flex items-center gap-1">
                <label
                  :for="`teil-img-${teil.id}`"
                  class="inline-flex cursor-pointer items-center gap-1.5 rounded-leaf border border-dashed px-3 py-1.5 text-xs font-medium transition-colors"
                  :class="
                    uploadingTeilImage === teil.id
                      ? 'border-primary/40 text-primary'
                      : 'border-line text-muted hover:border-primary/40 hover:text-primary'
                  "
                  v-tooltip.top="'Images du config : person_a, speaker_b, article, topic, image…'"
                >
                  <i :class="uploadingTeilImage === teil.id ? 'pi pi-spin pi-spinner' : 'pi pi-upload'" class="text-xs" />
                  {{ uploadingTeilImage === teil.id ? "Envoi…" : "Images" }}
                </label>
                <input
                  :id="`teil-img-${teil.id}`"
                  type="file"
                  accept=".png,.jpg,.jpeg,.webp"
                  multiple
                  class="hidden"
                  :disabled="uploadingTeilImage === teil.id"
                  @change="(e) => handleUploadTeilImage(mod, teil, e)"
                />
                <Button
                  :icon="expandedTeile.has(teil.id) ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  :aria-label="expandedTeile.has(teil.id) ? 'Replier' : 'Déplier'"
                  @click="toggleTeil(teil.id)"
                />
              </div>
            </div>

            <!-- Contenu du Teil -->
            <div v-if="expandedTeile.has(teil.id)" class="space-y-5 bg-card-2/30 px-4 pb-5 pt-1 sm:px-5">
              <p v-if="teil.instructions" class="rounded-leaf border border-sky-500/20 bg-sky-500/5 px-4 py-2.5 text-xs text-ink">
                {{ teil.instructions }}
              </p>

              <!-- Images du config -->
              <section v-if="imageSlots(teil).length" class="space-y-2">
                <p class="text-[11px] font-semibold uppercase tracking-wider text-muted">Images du config</p>
                <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-4">
                  <figure
                    v-for="slot in imageSlots(teil)"
                    :key="slot.id"
                    class="overflow-hidden rounded-leaf border border-line bg-card"
                    :class="{ 'sm:col-span-2': slot.wide }"
                  >
                    <div class="relative">
                      <Image
                        v-if="slot.path"
                        :src="`${apiBase}/images/${slot.path}`"
                        :alt="slot.label"
                        preview
                        class="block"
                        imageClass="h-32 w-full object-cover"
                      />
                      <div v-else class="flex h-32 flex-col items-center justify-center gap-1 bg-card-2/60 text-faint">
                        <i class="pi pi-image text-xl" />
                        <span class="text-[11px]">Aucune image</span>
                      </div>
                      <button
                        v-if="slot.path"
                        type="button"
                        class="absolute right-1.5 top-1.5 flex size-7 items-center justify-center rounded-full bg-black/60 text-white transition-colors hover:bg-red-600"
                        :aria-label="`Supprimer l'image ${slot.label}`"
                        v-tooltip.top="'Supprimer'"
                        @click="confirmRemove(teil, slot)"
                      >
                        <i class="pi pi-trash text-[11px]" />
                      </button>
                    </div>
                    <figcaption class="flex items-center gap-1.5 px-2.5 py-2 text-xs">
                      <span class="shrink-0 rounded bg-card-2 px-1.5 font-mono text-[11px] text-muted">{{ slot.badge }}</span>
                      <span class="truncate text-ink">{{ slot.label }}</span>
                    </figcaption>
                  </figure>
                </div>
              </section>

              <!-- Questions -->
              <section class="space-y-2">
                <p class="text-[11px] font-semibold uppercase tracking-wider text-muted">Questions</p>
                <ul v-if="(teil as any).questions?.length" class="space-y-1.5">
                  <li
                    v-for="q in (teil as any).questions"
                    :key="q.id"
                    class="flex items-center gap-3 rounded-leaf border border-line bg-card px-3 py-2.5"
                  >
                    <span class="w-8 shrink-0 text-xs font-bold text-muted">Q{{ q.question_number }}</span>
                    <span class="hidden shrink-0 rounded bg-card-2 px-1.5 py-0.5 font-mono text-[11px] text-muted sm:inline">
                      {{ q.question_type }}
                    </span>
                    <p class="min-w-0 flex-1 truncate text-sm text-ink">{{ questionText(q) }}</p>
                    <i
                      v-if="q.audio_file"
                      class="pi pi-volume-up shrink-0 text-xs text-violet-600"
                      v-tooltip.top="q.audio_file"
                    />
                    <span class="shrink-0 text-xs text-muted">{{ q.points }} pt{{ q.points > 1 ? "s" : "" }}</span>
                  </li>
                </ul>
                <p v-else class="rounded-leaf border border-dashed border-line py-3 text-center text-xs text-muted">Aucune question</p>
              </section>
            </div>
          </div>
        </div>
      </article>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin" });

const route = useRoute();
const router = useRouter();
const toast = useToast();
const confirm = useConfirm();
const config = useRuntimeConfig();

const subjectId = route.params.subjectId as string;
const examId = route.query.examId as string;
const apiBase = config.public.apiBaseUrl || "http://localhost:8001";

const loading = ref(true);
const subject = ref<any>(null);
const examName = ref("");
const expandedTeile = ref<Set<string>>(new Set());
const uploadingTeilImage = ref<string | null>(null);

// ── Setup API ──
const setupApi = async () => {
  const { OpenAPI } = await import("#shared/api");
  OpenAPI.BASE = apiBase;
  const token = useCookie("access_token");
  OpenAPI.TOKEN = token.value ?? undefined;
};

// ── Chargement ──
onMounted(async () => {
  await setupApi();
  const { ExamsService, QuestionsService } = await import("#shared/api");
  try {
    const detail = await ExamsService.getExamDetailApiV1ExamsExamIdGet(examId);
    examName.value = detail.name;
    for (const level of detail.levels ?? []) {
      const found = level.subjects?.find((s: any) => s.id === subjectId);
      if (found) {
        // Questions de tous les Teile en parallèle
        const teile = (found.modules ?? []).flatMap((m: any) => m.teile ?? []);
        await Promise.all(
          teile.map(async (teil: any) => {
            try {
              teil.questions = await QuestionsService.adminGetQuestionsApiV1AdminTeileTeilIdQuestionsGet(teil.id);
            } catch {
              teil.questions = [];
            }
          }),
        );
        subject.value = found;
        break;
      }
    }
  } finally {
    loading.value = false;
  }
});

// ── Chiffres ──
const allTeile = computed<any[]>(() => (subject.value?.modules ?? []).flatMap((m: any) => m.teile ?? []));

const headerStats = computed(() => {
  const teile = allTeile.value;
  const questions = teile.reduce((s, t) => s + (t.questions?.length ?? 0), 0);
  const slots = teile.reduce((s, t) => s + imageSlots(t).length, 0);
  const filled = teile.reduce((s, t) => s + filledCount(t), 0);
  return [
    { label: "Modules", value: subject.value?.modules?.length ?? 0 },
    { label: "Teile", value: teile.length },
    { label: "Questions", value: questions },
    {
      label: "Images du config",
      value: slots ? `${filled}/${slots}` : "-",
      tone: slots && filled < slots ? "text-amber-600" : undefined,
    },
  ];
});

// ── Dépliage ──
const toggleTeil = (teilId: string) => {
  const next = new Set(expandedTeile.value);
  if (next.has(teilId)) next.delete(teilId);
  else next.add(teilId);
  expandedTeile.value = next;
};

const allExpanded = computed(() => allTeile.value.length > 0 && allTeile.value.every((t) => expandedTeile.value.has(t.id)));

function toggleAllTeile() {
  expandedTeile.value = allExpanded.value ? new Set() : new Set(allTeile.value.map((t) => t.id));
}

// ── Emplacements d'images du config ──
// Une seule liste pour tous les types (persons, speakers, audio_images, anzeigen,
// article_image, stimulus_image, topic_image, image), affichée dans une même grille.
interface ImageSlot {
  id: string;
  type: string;
  key?: string;
  badge: string;
  label: string;
  path: string | null;
  wide?: boolean;
}

function imageSlots(teil: any): ImageSlot[] {
  const c = teil.config ?? {};
  const slots: ImageSlot[] = [];

  if (c.persons) {
    for (const [key, person] of Object.entries<any>(c.persons)) {
      slots.push({ id: `persons-${key}`, type: "persons", key, badge: key, label: person?.name || "Personne", path: person?.image ?? null });
    }
  }
  if (c.speakers) {
    for (const [key, speaker] of Object.entries<any>(c.speakers)) {
      const isObj = typeof speaker === "object";
      slots.push({
        id: `speakers-${key}`,
        type: "speakers",
        key,
        badge: key,
        label: isObj ? speaker?.name || "Speaker" : String(speaker),
        path: isObj ? (speaker?.image ?? null) : null,
      });
    }
  }
  if (c.audio_images) {
    for (const [num, path] of Object.entries<any>(c.audio_images)) {
      slots.push({ id: `audio-${num}`, type: "audio_images", key: num, badge: `Audio ${num}`, label: "Image d'audio", path: path || null });
    }
  }
  if (c.anzeigen) {
    for (const [key, anzeige] of Object.entries<any>(c.anzeigen)) {
      const isObj = typeof anzeige === "object";
      slots.push({
        id: `anzeigen-${key}`,
        type: "anzeigen",
        key,
        badge: String(key).toUpperCase(),
        label: (isObj && anzeige?.title) || "Annonce",
        path: isObj ? (anzeige?.image ?? null) : null,
      });
    }
  }
  const singles: Array<[string, string]> = [
    ["article_image", "Article"],
    ["stimulus_image", "Stimulus"],
    ["topic_image", "Topic"],
    ["image", "Image"],
  ];
  for (const [field, label] of singles) {
    if (c[field] !== undefined) {
      slots.push({ id: field, type: field, badge: label, label, path: c[field] || null, wide: true });
    }
  }
  return slots;
}

const filledCount = (teil: any) => imageSlots(teil).filter((s) => !!s.path).length;

// ── Texte d'une question (premier champ renseigné) ──
function questionText(q: any) {
  const c = q.content ?? {};
  return c.statement || c.stem || c.scenario || c.situation || c.prompt || "-";
}

// ── Envoi d'images ──
const handleUploadTeilImage = async (mod: any, teil: any, e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (!files || files.length === 0) return;

  uploadingTeilImage.value = teil.id;
  try {
    await setupApi();
    const { OpenAPI, ExamsService } = await import("#shared/api");

    const formData = new FormData();
    for (const file of Array.from(files)) formData.append("files", file);
    formData.append("subject_number", String(subject.value.subject_number));
    formData.append("teil_id", teil.id); // cible explicitement ce Teil

    const response = await fetch(`${OpenAPI.BASE}/api/v1/exams/admin/${examId}/teil-images`, {
      method: "POST",
      credentials: "include",
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || "Erreur lors de l'envoi");
    }

    const result = await response.json();

    // Recharge le config du Teil pour l'aperçu
    const detail = await ExamsService.getExamDetailApiV1ExamsExamIdGet(examId);
    for (const level of detail.levels ?? []) {
      const found = level.subjects?.find((s: any) => s.id === subjectId);
      const updatedTeil = found?.modules?.find((m: any) => m.id === mod.id)?.teile?.find((t: any) => t.id === teil.id);
      if (updatedTeil) teil.config = updatedTeil.config;
    }

    toast.add({ severity: "success", summary: `${result.updated ?? 0} image(s) associée(s)`, life: 3000 });
    if (result.not_found?.length) {
      toast.add({
        severity: "warn",
        summary: `${result.not_found.length} fichier(s) ignoré(s)`,
        detail: result.not_found.join(", "),
        life: 6000,
      });
    }
    // On déplie le Teil pour voir le résultat
    if (!expandedTeile.value.has(teil.id)) toggleTeil(teil.id);
  } catch (err: any) {
    toast.add({ severity: "error", summary: err.message || "Erreur lors de l'envoi", life: 4000 });
  } finally {
    uploadingTeilImage.value = null;
    (e.target as HTMLInputElement).value = "";
  }
};

// ── Suppression d'une image ──
function confirmRemove(teil: any, slot: ImageSlot) {
  confirm.require({
    header: "Supprimer l'image",
    message: `Retirer l'image « ${slot.label} » du Teil ${teil.teil_number} ? Le fichier reste sur le serveur, seul le lien est supprimé.`,
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "Supprimer",
    rejectLabel: "Annuler",
    acceptClass: "p-button-danger",
    accept: () => removeConfigImage(teil, slot.type, slot.key),
  });
}

const removeConfigImage = async (teil: any, type: string, key?: string) => {
  try {
    await setupApi();
    const { ExamsService } = await import("#shared/api");

    const cfg = { ...(teil.config ?? {}) };

    if (type === "persons" && key) {
      cfg.persons = { ...cfg.persons, [key]: { ...cfg.persons[key] } };
      delete cfg.persons[key].image;
    } else if (type === "speakers" && key) {
      cfg.speakers = { ...cfg.speakers };
      if (typeof cfg.speakers[key] === "object") {
        cfg.speakers[key] = { ...cfg.speakers[key] };
        delete cfg.speakers[key].image;
      }
    } else if (type === "audio_images" && key) {
      cfg.audio_images = { ...cfg.audio_images };
      delete cfg.audio_images[key];
      if (Object.keys(cfg.audio_images).length === 0) delete cfg.audio_images;
    } else if (type === "anzeigen" && key) {
      cfg.anzeigen = { ...cfg.anzeigen };
      if (typeof cfg.anzeigen[key] === "object") {
        cfg.anzeigen[key] = { ...cfg.anzeigen[key] };
        delete cfg.anzeigen[key].image;
      }
    } else {
      delete cfg[type];
    }

    await ExamsService.updateTeilApiV1ExamsTeileTeilIdPatch(teil.id, { config: cfg });
    teil.config = cfg;
    toast.add({ severity: "success", summary: "Image supprimée", life: 3000 });
  } catch {
    toast.add({ severity: "error", summary: "Erreur lors de la suppression", life: 3000 });
  }
};

// ── Style par module ──
function moduleStyle(slug: string) {
  if (slug.includes("lesen")) return { icon: "pi-book", box: "bg-sky-500/10 text-sky-600" };
  if (slug.includes("horen") || slug.includes("hören")) return { icon: "pi-volume-up", box: "bg-violet-500/10 text-violet-600" };
  if (slug.includes("schreiben")) return { icon: "pi-pencil", box: "bg-emerald-500/10 text-emerald-600" };
  if (slug.includes("sprechen")) return { icon: "pi-microphone", box: "bg-orange-500/10 text-orange-600" };
  return { icon: "pi-file", box: "bg-card-2 text-muted" };
}

watchEffect(() => {
  if (subject.value) {
    useHead({ title: `${subject.value.name || "Sujet " + subject.value.subject_number} | Admin` });
  }
});
</script>