<template>
  <div class="max-w-3xl mx-auto px-4 py-8 space-y-6">

    <!-- En-tête -->
    <div class="flex items-center gap-3">
      <Button icon="pi pi-arrow-left" text rounded @click="router.back()" />
      <h1 class="text-xl font-bold text-gray-900">
        {{ isNew ? 'Nouveau sujet' : 'Modifier le sujet' }}
      </h1>
    </div>

    <!-- Chargement (mode édition) -->
    <div v-if="loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 40px; height: 40px" />
    </div>

    <div v-else class="space-y-6">

      <!-- ── Infos générales ──────────────────────────── -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <h2 class="font-semibold text-gray-700 text-sm uppercase tracking-wide">Informations générales</h2>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-600">Provider *</label>
            <Select
              v-model="form.provider"
              :options="providerOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Sélectionner"
              class="w-full"
              :disabled="!isNew"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-600">Niveau *</label>
            <Select
              v-model="form.level"
              :options="levelOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Sélectionner"
              class="w-full"
              :disabled="!isNew"
            />
          </div>
        </div>

        <div class="space-y-1">
          <label class="text-xs font-medium text-gray-600">Titre *</label>
          <InputText v-model="form.title" class="w-full" placeholder="ex: Fahrradtour mit Trainer" />
        </div>

        <div class="space-y-1">
          <label class="text-xs font-medium text-gray-600">Description (optionnelle)</label>
          <Textarea v-model="form.description" class="w-full" :rows="2" placeholder="Courte description admin" />
        </div>

        <div class="flex items-center gap-4">
          <div class="space-y-1 flex-1">
            <label class="text-xs font-medium text-gray-600">Ordre d'affichage</label>
            <InputNumber v-model="form.display_order" class="w-full" :min="0" />
          </div>
          <div class="space-y-1 flex items-center gap-2 pt-5">
            <InputSwitch v-model="form.is_active" />
            <label class="text-sm text-gray-600">Actif</label>
          </div>
        </div>
      </div>

      <!-- ── Tâches ────────────────────────────────────── -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="font-semibold text-gray-700 text-sm uppercase tracking-wide">
            Tâches
            <span class="ml-1 text-gray-400 font-normal normal-case">({{ form.tasks.length }} / {{ expectedTaskCount }})</span>
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

        <Message v-if="form.provider && form.level && form.tasks.length !== expectedTaskCount" severity="warn" :closable="false">
          {{ form.provider.toUpperCase() }} {{ form.level.toUpperCase() }} attend {{ expectedTaskCount }} tâche(s).
        </Message>

        <div
          v-for="(task, i) in form.tasks"
          :key="i"
          class="bg-white border border-gray-200 rounded-2xl p-6 space-y-4"
        >
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-800">Teil {{ task.teil }}</h3>
            <Button
              v-if="form.tasks.length > 1"
              icon="pi pi-trash"
              text
              rounded
              size="small"
              severity="danger"
              @click="removeTask(i)"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-600">Scénario / Consigne *</label>
            <Textarea v-model="task.scenario" class="w-full" :rows="3" placeholder="Sie haben an einer Fahrradtour teilgenommen…" />
          </div>

          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-600">Points à traiter (un par ligne)</label>
            <Textarea
              :modelValue="task.prompts.join('\n')"
              class="w-full"
              :rows="3"
              placeholder="Warum Sie unzufrieden waren&#10;Was Sie sich wünschen"
              @update:modelValue="(v: string) => task.prompts = v.split('\n').map(s => s.trim()).filter(Boolean)"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs font-medium text-gray-600">Thème (Goethe/ÖSD B2 Teil 1)</label>
              <InputText v-model="task.topic" class="w-full" placeholder="Klimawandel" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-medium text-gray-600">Annonce / context_ad</label>
              <InputText v-model="task.context_ad" class="w-full" placeholder="Texte de l'annonce…" />
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-600">Citation forum (Goethe B1 Teil 2)</label>
            <InputText v-model="task.opinion_quote" class="w-full" placeholder="« Ich denke, dass… »" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs font-medium text-gray-600">Mots min</label>
              <InputNumber v-model="task.word_count_min" class="w-full" :min="50" :max="500" />
            </div>
            <div class="space-y-1">
              <label class="text-xs font-medium text-gray-600">Mots max</label>
              <InputNumber v-model="task.word_count_max" class="w-full" :min="50" :max="500" />
            </div>
          </div>
        </div>
      </div>

      <!-- ── Erreur / Actions ─────────────────────────── -->
      <Message v-if="saveError" severity="error" :closable="false">{{ saveError }}</Message>

      <div class="flex gap-3 pb-8">
        <Button label="Annuler" outlined class="flex-1" @click="router.back()" />
        <Button
          :label="isNew ? 'Créer le sujet' : 'Enregistrer'"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!isFormValid"
          class="flex-1"
          @click="save"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SchreibenSimulatorService, OpenAPI } from '#shared/api'
import type { SchreibenSubjectResponse } from '#shared/api'

definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

const route  = useRouter()
const router = useRouter()
const r      = useRoute()
const config = useRuntimeConfig()

const id    = r.params.id as string
const isNew = id === 'nouveau'

const loading  = ref(!isNew)
const saving   = ref(false)
const saveError = ref<string | null>(null)

// ── Formulaire ───────────────────────────────────────

interface TaskForm {
  teil: number
  scenario: string
  prompts: string[]
  topic: string
  context_ad: string
  opinion_quote: string
  word_count_min: number
  word_count_max: number
}

const blankTask = (teil: number): TaskForm => ({
  teil,
  scenario: '',
  prompts: [],
  topic: '',
  context_ad: '',
  opinion_quote: '',
  word_count_min: 100,
  word_count_max: 200,
})

const form = reactive({
  provider: '' as string,
  level: '' as string,
  title: '',
  description: '' as string | null,
  display_order: 0,
  is_active: true,
  tasks: [blankTask(1)] as TaskForm[],
})

const providerOptions = [
  { label: 'Goethe', value: 'goethe' },
  { label: 'TELC',   value: 'telc'   },
  { label: 'ÖSD',    value: 'osd'    },
]
const levelOptions = [
  { label: 'B1', value: 'b1' },
  { label: 'B2', value: 'b2' },
]

// ── Nombre de tâches attendu ─────────────────────────

const expectedTaskCount = computed(() => {
  const map: Record<string, number> = {
    'telc-b1': 1, 'telc-b2': 1,
    'goethe-b1': 3, 'goethe-b2': 2,
    'osd-b1': 3, 'osd-b2': 2,
  }
  return map[`${form.provider}-${form.level}`] ?? 1
})

const isFormValid = computed(() =>
  form.provider && form.level && form.title.trim() &&
  form.tasks.length === expectedTaskCount.value &&
  form.tasks.every(t => t.scenario.trim())
)

// Sync du nombre de tâches quand provider/level changent
watch([() => form.provider, () => form.level], () => {
  const n = expectedTaskCount.value
  while (form.tasks.length < n) form.tasks.push(blankTask(form.tasks.length + 1))
  while (form.tasks.length > n) form.tasks.pop()
})

// ── Helpers tâches ───────────────────────────────────

const addTask = () => form.tasks.push(blankTask(form.tasks.length + 1))
const removeTask = (i: number) => form.tasks.splice(i, 1)

// ── Chargement (édition) ─────────────────────────────

const ensureApi = () => { OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001' }

const hydrateForm = (s: SchreibenSubjectResponse) => {
  form.provider      = s.provider
  form.level         = s.level
  form.title         = s.title
  form.description   = s.description
  form.display_order = s.display_order
  form.is_active     = s.is_active
  form.tasks         = s.tasks.map((t: any) => ({
    teil:           t.teil          ?? 1,
    scenario:       t.scenario      ?? '',
    prompts:        t.prompts       ?? [],
    topic:          t.topic         ?? '',
    context_ad:     t.context_ad    ?? '',
    opinion_quote:  t.opinion_quote ?? '',
    word_count_min: t.word_count_min ?? 100,
    word_count_max: t.word_count_max ?? 200,
  }))
}

onMounted(async () => {
  ensureApi()
  if (!isNew) {
    try {
      const s = await SchreibenSimulatorService.getSubjectApiV1SchreibenSimulatorSubjectIdGet(id)
      hydrateForm(s)
    } catch {
      saveError.value = 'Sujet introuvable'
    } finally {
      loading.value = false
    }
  }
})

// ── Sauvegarde ───────────────────────────────────────

const save = async () => {
  ensureApi()
  saving.value    = true
  saveError.value = null
  const payload = {
    provider:      form.provider as any,
    level:         form.level as any,
    title:         form.title,
    description:   form.description || null,
    display_order: form.display_order,
    is_active:     form.is_active,
    tasks:         form.tasks,
  }
  try {
    if (isNew) {
      await SchreibenSimulatorService.createSubjectApiV1SchreibenSimulatorPost(payload)
    } else {
      await SchreibenSimulatorService.updateSubjectApiV1SchreibenSimulatorSubjectIdPatch(id, payload)
    }
    router.push('/admin/simulateur')
  } catch (e: any) {
    saveError.value = e.body?.detail || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

useHead({ title: isNew ? 'Nouveau sujet — Admin' : 'Modifier sujet — Admin' })
</script>