<!-- pages/admin/simulateur/[id].vue -->
<template>
  <div class="space-y-5 pb-10">
    <NuxtLink to="/admin/simulateur" class="inline-flex items-center gap-2 text-sm text-muted hover:text-ink">
      <i class="pi pi-arrow-left text-xs" />
      Retour aux sujets
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="grid gap-5 lg:grid-cols-3">
      <div class="h-96 animate-pulse rounded-card bg-card-2 lg:col-span-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <div v-else class="grid items-start gap-5 lg:grid-cols-3">
      <!-- ══════════ Colonne droite : infos + actions ══════════ -->
      <aside class="space-y-4 lg:sticky lg:top-0 lg:order-last">
        <section class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft">
          <h2 class="font-semibold text-ink">{{ isNew ? "Nouveau sujet" : "Informations" }}</h2>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Provider *</label>
              <Select
                v-model="form.provider"
                :options="providerOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Choisir"
                class="w-full"
                :disabled="!isNew"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Niveau *</label>
              <Select
                v-model="form.level"
                :options="levelOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Choisir"
                class="w-full"
                :disabled="!isNew"
              />
            </div>
          </div>
          <p v-if="!isNew" class="-mt-2 text-[11px] text-faint">Provider et niveau ne sont plus modifiables après création.</p>

          <div>
            <label class="mb-1.5 block text-xs font-medium text-muted">Titre *</label>
            <InputText v-model="form.title" class="w-full" placeholder="ex. Fahrradtour mit Trainer" />
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-medium text-muted">Description (optionnelle)</label>
            <Textarea v-model="form.description" class="w-full" :rows="2" autoResize placeholder="Courte description admin" />
          </div>

          <div class="grid grid-cols-2 items-end gap-3">
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Ordre d'affichage</label>
              <InputNumber v-model="form.display_order" :min="0" class="w-full" inputClass="w-full" />
            </div>
            <label class="flex h-10 cursor-pointer items-center justify-between gap-2 rounded-leaf bg-card-2 px-3 text-sm text-ink">
              {{ form.is_active ? "Actif" : "Inactif" }}
              <ToggleSwitch v-model="form.is_active" />
            </label>
          </div>
        </section>

        <!-- Récap + actions -->
        <section class="space-y-3 rounded-card border border-line bg-card p-5 shadow-soft">
          <ul class="space-y-2 text-sm">
            <li v-for="check in checks" :key="check.label" class="flex items-center gap-2">
              <i
                class="pi text-xs"
                :class="check.ok ? 'pi-check-circle text-emerald-600' : 'pi-circle text-faint'"
              />
              <span :class="check.ok ? 'text-ink' : 'text-muted'">{{ check.label }}</span>
            </li>
          </ul>

          <Message v-if="saveError" severity="error" :closable="false">{{ saveError }}</Message>

          <div class="flex gap-2 pt-1">
            <Button label="Annuler" outlined severity="secondary" class="flex-1" @click="router.push('/admin/simulateur')" />
            <Button
              :label="isNew ? 'Créer le sujet' : 'Enregistrer'"
              icon="pi pi-check"
              class="flex-1"
              :loading="saving"
              :disabled="!isFormValid"
              @click="save"
            />
          </div>
        </section>
      </aside>

      <!-- ══════════ Colonne gauche : tâches ══════════ -->
      <div class="space-y-4 lg:col-span-2">
        <div class="flex items-center justify-between gap-3">
          <h2 class="font-semibold text-ink">
            Tâches
            <span class="font-normal text-muted">· {{ form.tasks.length }} / {{ expectedTaskCount }}</span>
          </h2>
          <Button
            v-if="form.tasks.length < expectedTaskCount"
            label="Ajouter une tâche"
            icon="pi pi-plus"
            size="small"
            outlined
            @click="addTask"
          />
        </div>

        <Message
          v-if="form.provider && form.level && form.tasks.length !== expectedTaskCount"
          severity="warn"
          :closable="false"
        >
          {{ providerLabel(form.provider) }} {{ form.level.toUpperCase() }} attend {{ expectedTaskCount }} tâche(s).
        </Message>

        <section
          v-for="(task, i) in form.tasks"
          :key="i"
          class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <header class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="flex size-9 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary">
                {{ task.teil }}
              </span>
              <div>
                <h3 class="font-semibold text-ink">Teil {{ task.teil }}</h3>
                <p class="text-xs text-muted">{{ task.word_count_min }} à {{ task.word_count_max }} mots</p>
              </div>
            </div>
            <Button
              v-if="form.tasks.length > 1"
              icon="pi pi-trash"
              text
              rounded
              size="small"
              severity="danger"
              v-tooltip.top="'Retirer cette tâche'"
              aria-label="Retirer cette tâche"
              @click="removeTask(i)"
            />
          </header>

          <div>
            <label class="mb-1.5 block text-xs font-medium text-muted">Scénario / consigne *</label>
            <Textarea
              v-model="task.scenario"
              class="w-full"
              :rows="3"
              autoResize
              placeholder="Sie haben an einer Fahrradtour teilgenommen…"
              :invalid="touched && !task.scenario.trim()"
            />
          </div>

          <div>
            <label class="mb-1.5 flex items-center justify-between text-xs font-medium text-muted">
              Points à traiter (un par ligne)
              <span class="text-faint">{{ splitPrompts(task.promptsText).length }} point(s)</span>
            </label>
            <Textarea
              v-model="task.promptsText"
              class="w-full"
              :rows="3"
              autoResize
              placeholder="Warum Sie unzufrieden waren&#10;Was Sie sich wünschen"
            />
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Thème <span class="text-faint">(Goethe / ÖSD B2 Teil 1)</span></label>
              <InputText v-model="task.topic" class="w-full" placeholder="Klimawandel" />
            </div>
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Annonce <span class="text-faint">(context_ad)</span></label>
              <InputText v-model="task.context_ad" class="w-full" placeholder="Texte de l'annonce…" />
            </div>
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-medium text-muted">Citation forum <span class="text-faint">(Goethe B1 Teil 2)</span></label>
            <InputText v-model="task.opinion_quote" class="w-full" placeholder="« Ich denke, dass… »" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Mots min</label>
              <InputNumber
                v-model="task.word_count_min"
                :min="50"
                :max="500"
                class="w-full"
                inputClass="w-full"
                :invalid="task.word_count_min > task.word_count_max"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">Mots max</label>
              <InputNumber
                v-model="task.word_count_max"
                :min="50"
                :max="500"
                class="w-full"
                inputClass="w-full"
                :invalid="task.word_count_min > task.word_count_max"
              />
            </div>
          </div>
          <p v-if="task.word_count_min > task.word_count_max" class="-mt-2 text-xs text-red-600">
            Le minimum dépasse le maximum.
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SchreibenSimulatorService, OpenAPI } from "#shared/api";
import type { SchreibenSubjectResponse } from "#shared/api";

definePageMeta({ layout: "admin", watermark: "Schreiben" });

const router = useRouter();
const r = useRoute();
const config = useRuntimeConfig();

const id = r.params.id as string;
const isNew = id === "nouveau";

const loading = ref(!isNew);
const saving = ref(false);
const saveError = ref<string | null>(null);
const touched = ref(false);

// ── Formulaire ──
interface TaskForm {
  teil: number;
  scenario: string;
  promptsText: string;
  topic: string;
  context_ad: string;
  opinion_quote: string;
  word_count_min: number;
  word_count_max: number;
}

const blankTask = (teil: number): TaskForm => ({
  teil,
  scenario: "",
  promptsText: "",
  topic: "",
  context_ad: "",
  opinion_quote: "",
  word_count_min: 100,
  word_count_max: 200,
});

const splitPrompts = (text: string) =>
  text
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);

const form = reactive({
  provider: "" as string,
  level: "" as string,
  title: "",
  description: "" as string | null,
  display_order: 0,
  is_active: true,
  tasks: [blankTask(1)] as TaskForm[],
});

const providerOptions = [
  { label: "Goethe", value: "goethe" },
  { label: "TELC", value: "telc" },
  { label: "ÖSD", value: "osd" },
];
const levelOptions = [
  { label: "B1", value: "b1" },
  { label: "B2", value: "b2" },
];

const providerLabel = (p: string) => ({ goethe: "Goethe", telc: "TELC", osd: "ÖSD" })[p] ?? p.toUpperCase();

// ── Nombre de tâches attendu ──
const expectedTaskCount = computed(() => {
  const map: Record<string, number> = {
    "telc-b1": 1,
    "telc-b2": 1,
    "goethe-b1": 3,
    "goethe-b2": 2,
    "osd-b1": 3,
    "osd-b2": 2,
  };
  return map[`${form.provider}-${form.level}`] ?? 1;
});

const wordCountsOk = computed(() => form.tasks.every((t) => t.word_count_min <= t.word_count_max));

const checks = computed(() => [
  { label: "Provider et niveau choisis", ok: !!form.provider && !!form.level },
  { label: "Titre renseigné", ok: !!form.title.trim() },
  {
    label: `${expectedTaskCount.value} tâche(s) attendue(s)`,
    ok: form.tasks.length === expectedTaskCount.value,
  },
  { label: "Chaque tâche a un scénario", ok: form.tasks.every((t) => t.scenario.trim()) },
  { label: "Nombres de mots cohérents", ok: wordCountsOk.value },
]);

const isFormValid = computed(() => checks.value.every((c) => c.ok));

// Ajuste le nombre de tâches en création uniquement
watch([() => form.provider, () => form.level], () => {
  if (!isNew) return;
  const n = expectedTaskCount.value;
  while (form.tasks.length < n) form.tasks.push(blankTask(form.tasks.length + 1));
  while (form.tasks.length > n) form.tasks.pop();
});

// ── Tâches ──
const renumber = () => form.tasks.forEach((t, i) => (t.teil = i + 1));
const addTask = () => form.tasks.push(blankTask(form.tasks.length + 1));
const removeTask = (i: number) => {
  form.tasks.splice(i, 1);
  renumber();
};

// ── Chargement (édition) ──
const ensureApi = () => {
  OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
};

const hydrateForm = (s: SchreibenSubjectResponse) => {
  form.provider = s.provider;
  form.level = s.level;
  form.title = s.title;
  form.description = s.description;
  form.display_order = s.display_order;
  form.is_active = s.is_active;
  form.tasks = s.tasks.map((t: any) => ({
    teil: t.teil ?? 1,
    scenario: t.scenario ?? "",
    promptsText: (t.prompts ?? []).join("\n"),
    topic: t.topic ?? "",
    context_ad: t.context_ad ?? "",
    opinion_quote: t.opinion_quote ?? "",
    word_count_min: t.word_count_min ?? 100,
    word_count_max: t.word_count_max ?? 200,
  }));
};

onMounted(async () => {
  ensureApi();
  if (!isNew) {
    try {
      const s = await SchreibenSimulatorService.getSubjectApiV1SchreibenSimulatorSubjectIdGet(id);
      hydrateForm(s);
    } catch {
      saveError.value = "Sujet introuvable";
    } finally {
      loading.value = false;
    }
  }
});

// ── Sauvegarde ──
const save = async () => {
  touched.value = true;
  if (!isFormValid.value) return;

  ensureApi();
  saving.value = true;
  saveError.value = null;

  const payload = {
    provider: form.provider as any,
    level: form.level as any,
    title: form.title,
    description: form.description || null,
    display_order: form.display_order,
    is_active: form.is_active,
    tasks: form.tasks.map(({ promptsText, ...t }) => ({ ...t, prompts: splitPrompts(promptsText) })),
  };

  try {
    if (isNew) {
      await SchreibenSimulatorService.createSubjectApiV1SchreibenSimulatorPost(payload);
    } else {
      await SchreibenSimulatorService.updateSubjectApiV1SchreibenSimulatorSubjectIdPatch(id, payload);
    }
    router.push("/admin/simulateur");
  } catch (e: any) {
    saveError.value = e.body?.detail || "Erreur lors de la sauvegarde";
  } finally {
    saving.value = false;
  }
};

useHead({ title: isNew ? "Nouveau sujet · Admin" : "Modifier le sujet · Admin" });
</script>