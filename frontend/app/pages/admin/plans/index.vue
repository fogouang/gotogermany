<!-- pages/admin/plans/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Barre d'action ── -->
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <p class="text-sm text-muted">
        {{ plans.length }} plan{{ plans.length > 1 ? "s" : "" }} ·
        {{ activeCount }} actif{{ activeCount > 1 ? "s" : "" }}
      </p>
      <Button
        label="Nouveau plan"
        icon="pi pi-plus"
        class="w-full sm:w-auto"
        @click="openCreate"
      />
    </div>

    <!-- ── Chargement ── -->
    <div
      v-if="loading && plans.length === 0"
      class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
    >
      <div
        v-for="n in 3"
        :key="n"
        class="h-64 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="plans.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-tag" />
      </span>
      <p class="text-sm font-medium text-ink">Aucun plan pour l'instant</p>
      <p class="text-xs text-muted">
        Créez votre premier plan pour l'afficher sur la page tarifs.
      </p>
    </div>

    <!-- ── Plans ── -->
    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="plan in sortedPlans"
        :key="plan.id"
        class="flex flex-col rounded-card border bg-card p-5 shadow-soft transition-colors"
        :class="
          plan.is_active
            ? 'border-line'
            : 'border-dashed border-line opacity-70'
        "
      >
        <!-- En-tête -->
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-semibold text-ink">{{ plan.name }}</p>
            <span
              class="mt-1 inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary"
            >
              {{ formatDuration(plan.duration_days) }}
            </span>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <span
                class="inline-flex rounded-full bg-card-2 px-2.5 py-0.5 text-[11px] font-semibold text-muted"
              >
                {{ trackLabel(plan.track) }}
              </span>
              <span
                v-if="plan.is_popular"
                class="inline-flex items-center gap-1 rounded-full bg-accent-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-accent-700"
              >
                <i class="pi pi-star-fill text-[9px]" /> Populaire
              </span>
            </div>
          </div>
          <span
            class="shrink-0 rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted"
          >
            #{{ plan.display_order }}
          </span>
        </div>

        <!-- Prix -->
        <div class="mt-4">
          <p class="text-3xl font-bold leading-none text-ink">
            {{ formatPrice(plan.price) }}
          </p>
          <p
            v-if="plan.duration_days > 0 && plan.price > 0"
            class="mt-1 text-xs text-muted"
          >
            ≈
            {{
              Math.round(plan.price / plan.duration_days).toLocaleString(
                "fr-FR",
              )
            }}
            FCFA / jour
          </p>
          <p
            v-if="plan.price_eur"
            class="mt-1 text-xs font-semibold text-primary"
          >
            Carte : {{ formatEur(plan.price_eur) }}
          </p>
          <p v-else class="mt-1 text-xs text-faint">
            Pas de paiement par carte
          </p>
        </div>

        <p
          class="mt-3 inline-flex items-center gap-1.5 text-xs font-medium"
          :class="plan.ai_credits ? 'text-primary' : 'text-faint'"
        >
          <i class="pi pi-sparkles text-[11px]" />
          {{
            plan.ai_credits
              ? `${plan.ai_credits} crédit${plan.ai_credits > 1 ? "s" : ""} IA à l'activation`
              : "Aucun crédit IA"
          }}
        </p>

        <p v-if="plan.description" class="mt-3 line-clamp-2 text-sm text-muted">
          {{ plan.description }}
        </p>

        <!-- Fonctionnalités -->
        <ul v-if="plan.features?.length" class="mt-4 space-y-1.5">
          <li
            v-for="key in plan.features"
            :key="key"
            class="flex items-start gap-2 text-xs text-ink"
          >
            <i class="pi pi-check mt-0.5 text-[10px] text-emerald-600" />
            {{ featureLabel(key) }}
          </li>
        </ul>

        <!-- Pied -->
        <div
          class="mt-auto flex items-center justify-between gap-3 border-t border-line pt-4"
          :class="{ 'mt-5': true }"
        >
          <label
            class="flex cursor-pointer items-center gap-2 text-xs font-medium text-muted"
          >
            <ToggleSwitch
              :modelValue="plan.is_active"
              :disabled="togglingId === plan.id"
              @update:modelValue="toggleActive(plan, $event)"
            />
            {{ plan.is_active ? "Actif" : "Inactif" }}
          </label>
          <div class="flex items-center gap-1">
            <Button
              icon="pi pi-pencil"
              text
              rounded
              size="small"
              severity="secondary"
              v-tooltip.top="'Modifier'"
              aria-label="Modifier"
              @click="openEdit(plan)"
            />
            <Button
              icon="pi pi-trash"
              text
              rounded
              size="small"
              severity="danger"
              v-tooltip.top="'Supprimer'"
              aria-label="Supprimer"
              @click="openDelete(plan)"
            />
          </div>
        </div>
      </article>
    </div>

    <!-- ══ Créer / modifier ══ -->
    <Dialog
      v-model:visible="formDialog"
      :header="editingPlan ? 'Modifier le plan' : 'Nouveau plan'"
      modal
      :style="{ width: '95vw', maxWidth: '32rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleSave">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Parcours <span class="text-red-600">*</span></label
          >
          <SelectButton
            v-model="form.track"
            :options="trackOptions"
            optionLabel="label"
            optionValue="value"
            :allowEmpty="false"
            class="w-full"
          />
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Nom <span class="text-red-600">*</span></label
          >
          <InputText
            v-model="form.name"
            class="w-full"
            placeholder="ex. Sprint, Fokus, Prüfungsreif"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Durée (jours) <span class="text-red-600">*</span></label
            >
            <InputNumber
              v-model="form.duration_days"
              :min="1"
              class="w-full"
              inputClass="w-full"
              placeholder="30"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Prix (FCFA) <span class="text-red-600">*</span></label
            >
            <InputNumber
              v-model="form.price"
              :min="0"
              class="w-full"
              inputClass="w-full"
              placeholder="10350"
            />
          </div>
        </div>
        <p
          v-if="form.duration_days && form.price"
          class="-mt-2 text-xs text-muted"
        >
          ≈
          {{
            Math.round(form.price / form.duration_days).toLocaleString("fr-FR")
          }}
          FCFA / jour
        </p>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            Prix carte (€) <span class="font-normal text-muted">(optionnel)</span>
          </label>
          <InputNumber
            v-model="form.price_eur"
            mode="currency"
            currency="EUR"
            locale="fr-FR"
            :min="0"
            class="w-full"
            inputClass="w-full"
            placeholder="15,00 €"
          />
          <p class="mt-1 text-xs text-muted">
            Prix payé par carte (Visa, Mastercard). Vide : la formule n'est payable qu'en Mobile Money.
          </p>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Crédits IA offerts</label
          >
          <InputNumber
            v-model="form.ai_credits"
            :min="0"
            :max="1000"
            class="w-full"
            inputClass="w-full"
            placeholder="0"
          />
          <p class="mt-1 text-xs text-muted">
            Ajoutés au solde de l'élève à chaque activation de ce plan (un oral
            coûte 2 crédits).
          </p>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            Description <span class="font-normal text-muted">(optionnel)</span>
          </label>
          <Textarea
            v-model="form.description"
            class="w-full"
            rows="2"
            autoResize
            placeholder="Affichée sur la page tarifs"
          />
        </div>

        <!-- Fonctionnalités -->
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Fonctionnalités affichées</label
          >
          <div class="space-y-1.5">
            <label
              v-for="feat in visibleFeatureOptions"
              :key="feat.key"
              :for="`feat-${feat.key}`"
              class="flex cursor-pointer items-center gap-3 rounded-leaf border px-3 py-2 text-sm transition-colors"
              :class="
                form.features.includes(feat.key)
                  ? 'border-primary/40 bg-primary/5 text-ink'
                  : 'border-line text-muted hover:border-primary/30'
              "
            >
              <Checkbox
                v-model="form.features"
                :inputId="`feat-${feat.key}`"
                :value="feat.key"
              />
              {{ feat.label }}
            </label>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Ordre d'affichage</label
            >
            <InputNumber
              v-model="form.display_order"
              :min="0"
              class="w-full"
              inputClass="w-full"
              placeholder="0"
            />
          </div>
          <div class="flex flex-col justify-end gap-2 pb-2">
            <label
              class="flex cursor-pointer items-center gap-2 text-sm text-ink"
            >
              <ToggleSwitch v-model="form.is_active" />
              Plan actif
            </label>
            <label
              class="flex cursor-pointer items-center gap-2 text-sm text-ink"
            >
              <ToggleSwitch v-model="form.is_popular" />
              Badge « Populaire »
            </label>
          </div>
        </div>

        <Message v-if="formError || error" severity="error" :closable="false">{{
          formError || error
        }}</Message>
      </form>
      <template #footer>
        <Button label="Annuler" text @click="formDialog = false" />
        <Button
          :label="editingPlan ? 'Enregistrer' : 'Créer'"
          icon="pi pi-check"
          :loading="loading"
          @click="handleSave"
        />
      </template>
    </Dialog>

    <!-- ══ Supprimer ══ -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le plan ?"
      modal
      :style="{ width: '95vw', maxWidth: '26rem' }"
    >
      <div class="space-y-3">
        <div class="rounded-leaf bg-card-2 p-3">
          <p class="font-medium text-ink">{{ deletingPlan?.name }}</p>
          <p class="text-sm text-muted">
            {{ formatDuration(deletingPlan?.duration_days ?? 0) }} ·
            {{ formatPrice(deletingPlan?.price ?? 0) }}
          </p>
        </div>
        <p class="flex items-start gap-2 text-xs text-muted">
          <i class="pi pi-info-circle mt-0.5 text-[11px]" />
          Les paiements existants liés à ce plan ne seront pas affectés. Pour le
          retirer de la page tarifs sans le supprimer, désactivez-le plutôt.
        </p>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button
          label="Supprimer"
          severity="danger"
          icon="pi pi-trash"
          :loading="loading"
          @click="handleDelete"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PlanCreate, PlanResponse } from "#shared/api";

definePageMeta({ layout: "admin" });

const toast = useToast();
const {
  plans,
  loading,
  error,
  loadPlans,
  createPlan,
  updatePlan,
  deletePlan,
  formatDuration,
  formatPrice,
} = usePlans();

// ── Parcours ──
type Track = "standard" | "start_deutsch";

const trackOptions: { label: string; value: Track }[] = [
  { label: "B1 / B2 / TestDaF", value: "standard" },
  { label: "Start Deutsch (A1 / A2)", value: "start_deutsch" },
];

const trackLabel = (t?: string | null) =>
  trackOptions.find((o) => o.value === t)?.label ?? "B1 / B2 / TestDaF";

// Options de features, clés alignées avec pricing.features.* (i18n)
const featureOptions: { key: string; label: string; tracks: Track[] }[] = [
  { key: "full_access", label: "Accès complet à ton examen : Goethe, telc, ÖSD ou TestDaF", tracks: ["standard"] },
  { key: "sd_full_access", label: "Accès complet à Start Deutsch A1 ou Goethe-Zertifikat A2", tracks: ["start_deutsch"] },
  { key: "all_modules", label: "Sujets complets au format officiel : Lesen, Hören, Schreiben, Sprechen", tracks: ["standard", "start_deutsch"] },
  { key: "exam_conditions", label: "Déroulé et chronomètre comme le jour de l'examen", tracks: ["standard"] },
  { key: "sd_guided_writing", label: "Écrit guidé : formulaire et message (A1), SMS et e-mail (A2)", tracks: ["start_deutsch"] },
  { key: "sd_oral_cards", label: "Oral préparé avec les cartes et images du jour de l'examen", tracks: ["start_deutsch"] },
  { key: "corrections", label: "Correction IA de l'écrit et de l'oral", tracks: ["standard"] },
  { key: "sd_beginner_friendly", label: "Consignes simples, pensées pour les débutants", tracks: ["start_deutsch"] },
  { key: "pass_fail_result", label: "Résultat réussi / échoué après chaque sujet", tracks: ["standard", "start_deutsch"] },
  { key: "progress", label: "Suivi de ta progression", tracks: ["standard"] },
  { key: "sd_next_step_b1", label: "La bonne base pour enchaîner sur le B1", tracks: ["start_deutsch"] },
  { key: "mobile_access", label: "Sur mobile et ordinateur", tracks: ["standard", "start_deutsch"] },
];

function featureLabel(key: string) {
  return featureOptions.find((f) => f.key === key)?.label ?? key;
}

const sortedPlans = computed(() =>
  [...plans.value].sort(
    (a, b) =>
      (a.track ?? "").localeCompare(b.track ?? "") ||
      a.display_order - b.display_order ||
      a.duration_days - b.duration_days,
  ),
);

const activeCount = computed(
  () => plans.value.filter((p) => p.is_active).length,
);

const formatEur = (n: number) =>
  Number(n).toLocaleString("fr-FR", { style: "currency", currency: "EUR" });

// Payload complet attendu par updatePlan
function payloadOf(plan: PlanResponse, overrides: Partial<PlanResponse> = {}) {
  const p = { ...plan, ...overrides };
  return {
    name: p.name,
    duration_days: p.duration_days,
    price: p.price,
    description: p.description ?? null,
    features: p.features ?? [],
    ai_credits: p.ai_credits ?? 0,
    display_order: p.display_order,
    is_active: p.is_active,
    price_eur: p.price_eur ?? null,
    track: (p.track ?? "standard") as Track,
    is_popular: p.is_popular ?? false,
  };
}

// ── Activer / désactiver depuis la carte ──
const togglingId = ref<string | null>(null);

async function toggleActive(plan: PlanResponse, value: boolean) {
  togglingId.value = plan.id;
  const res = await updatePlan(plan.id, payloadOf(plan, { is_active: value }));
  togglingId.value = null;
  if (res.success) {
    toast.add({
      severity: "success",
      summary: value ? "Plan activé" : "Plan désactivé",
      life: 2500,
    });
  } else {
    toast.add({
      severity: "error",
      summary: res.error || "Erreur",
      life: 4000,
    });
  }
}

// ── Formulaire ──
const formDialog = ref(false);
const editingPlan = ref<PlanResponse | null>(null);
const formError = ref<string | null>(null);

const defaultForm = () => ({
  name: "",
  duration_days: null as number | null,
  price: null as number | null,
  description: "",
  features: [] as string[],
  ai_credits: 0 as number | null,
  display_order: plans.value.length,
  is_active: true,
  price_eur: null as number | null,
  track: "standard" as Track,
  is_popular: false,
});

const form = ref(defaultForm());

const visibleFeatureOptions = computed(() =>
  featureOptions.filter((f) => f.tracks.includes(form.value.track)),
);

// Changement de parcours : on retire les fonctionnalités de l'autre parcours
watch(
  () => form.value.track,
  () => {
    const allowed = new Set(visibleFeatureOptions.value.map((f) => f.key));
    form.value.features = form.value.features.filter((k) => allowed.has(k));
  },
);

function openCreate() {
  editingPlan.value = null;
  form.value = defaultForm();
  formError.value = null;
  formDialog.value = true;
}

function openEdit(plan: PlanResponse) {
  editingPlan.value = plan;
  form.value = {
    name: plan.name,
    duration_days: plan.duration_days,
    price: plan.price,
    description: plan.description ?? "",
    features: [...(plan.features ?? [])],
    ai_credits: plan.ai_credits ?? 0,
    display_order: plan.display_order,
    is_active: plan.is_active,
    price_eur: plan.price_eur ?? null,
    track: (plan.track ?? "standard") as Track,
    is_popular: plan.is_popular ?? false,
  };
  formError.value = null;
  formDialog.value = true;
}

async function handleSave() {
  const f = form.value;
  if (!f.name.trim() || !f.duration_days || f.price === null) {
    formError.value = "Le nom, la durée et le prix sont requis.";
    return;
  }
  formError.value = null;

  const payload = {
    name: f.name.trim(),
    duration_days: f.duration_days,
    price: f.price,
    description: f.description.trim() || null,
    features: f.features,
    ai_credits: f.ai_credits ?? 0,
    display_order: f.display_order,
    is_active: f.is_active,
    price_eur: f.price_eur ?? null,
    track: f.track,
    is_popular: f.is_popular,
  };

  const res = editingPlan.value
    ? await updatePlan(editingPlan.value.id, payload)
    : await createPlan({
        ...payload,
        track: payload.track as PlanCreate["track"],
      });

  if (res.success) {
    formDialog.value = false;
    toast.add({
      severity: "success",
      summary: editingPlan.value ? "Plan modifié" : "Plan créé",
      life: 3000,
    });
  }
}

// ── Supprimer ──
const deleteDialog = ref(false);
const deletingPlan = ref<PlanResponse | null>(null);

function openDelete(plan: PlanResponse) {
  deletingPlan.value = plan;
  deleteDialog.value = true;
}

async function handleDelete() {
  if (!deletingPlan.value) return;
  const res = await deletePlan(deletingPlan.value.id);
  if (res.success) {
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Plan supprimé", life: 3000 });
  } else {
    toast.add({
      severity: "error",
      summary: res.error || "Erreur",
      life: 4000,
    });
  }
}

onMounted(loadPlans);
</script>