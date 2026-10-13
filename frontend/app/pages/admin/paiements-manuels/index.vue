<template>
  <div class="space-y-5">
    <!-- ── Tuiles ── -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <div
        v-for="tile in tiles"
        :key="tile.label"
        class="rounded-card border border-line bg-card p-4 shadow-soft"
      >
        <div
          class="mb-3 flex size-9 items-center justify-center rounded-leaf"
          :class="tile.iconClass"
        >
          <i :class="tile.icon" class="text-sm" />
        </div>
        <p class="text-xl font-bold leading-none text-ink">{{ tile.value }}</p>
        <p class="mt-1.5 text-xs text-muted">{{ tile.label }}</p>
      </div>
    </div>

    <!-- ── Actions ── -->
    <div class="grid gap-3 md:grid-cols-2">
      <button
        type="button"
        class="group flex items-center gap-4 rounded-card border border-line bg-card p-5 text-left shadow-soft transition-colors hover:border-primary/40"
        @click="openAccessDialog"
      >
        <span
          class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary"
        >
          <i class="pi pi-key" />
        </span>
        <span class="min-w-0 flex-1">
          <span class="block font-semibold text-ink"
            >Accorder un accès examen</span
          >
          <span class="block text-sm text-muted"
            >Paiement reçu hors plateforme, l'accès est activé tout de
            suite.</span
          >
        </span>
        <i
          class="pi pi-arrow-right text-sm text-muted transition-transform group-hover:translate-x-1"
        />
      </button>

      <button
        type="button"
        class="group flex items-center gap-4 rounded-card border border-line bg-card p-5 text-left shadow-soft transition-colors hover:border-primary/40"
        @click="openCreditsDialog"
      >
        <span
          class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-violet-500/10 text-violet-600"
        >
          <i class="pi pi-sparkles" />
        </span>
        <span class="min-w-0 flex-1">
          <span class="block font-semibold text-ink"
            >Accorder des crédits IA</span
          >
          <span class="block text-sm text-muted"
            >Crédits de correction IA ajoutés au compte de l'étudiant.</span
          >
        </span>
        <i
          class="pi pi-arrow-right text-sm text-muted transition-transform group-hover:translate-x-1"
        />
      </button>
    </div>

    <!-- ── Historique ── -->
    <section class="space-y-3">
      <div
        class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
      >
        <div
          class="flex gap-1 rounded-leaf border border-line bg-card p-1 sm:w-fit"
        >
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="flex flex-1 items-center justify-center gap-2 rounded-leaf px-4 py-2 text-sm font-medium transition-colors sm:flex-none"
            :class="
              activeTab === tab.key
                ? 'bg-primary/10 text-primary'
                : 'text-muted hover:text-ink'
            "
            @click="activeTab = tab.key"
          >
            <i :class="tab.icon" class="text-xs" />
            {{ tab.label }}
            <span class="text-xs opacity-70">· {{ tab.count }}</span>
          </button>
        </div>
        <IconField class="w-full lg:w-72">
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="search"
            class="w-full"
            placeholder="Rechercher un utilisateur"
          />
        </IconField>
      </div>

      <div v-if="loadingHistory" class="space-y-3">
        <div
          v-for="n in 4"
          :key="n"
          class="h-16 animate-pulse rounded-card bg-card-2"
        />
      </div>

      <div
        v-else-if="currentRows.length === 0"
        class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
      >
        <span
          class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
        >
          <i :class="activeTab === 'access' ? 'pi pi-key' : 'pi pi-sparkles'" />
        </span>
        <p class="text-sm font-medium text-ink">
          {{
            search
              ? "Aucun résultat pour cette recherche."
              : activeTab === "access"
                ? "Aucun accès accordé manuellement."
                : "Aucun crédit IA accordé."
          }}
        </p>
      </div>

      <!-- Accès examen -->
      <ul
        v-else-if="activeTab === 'access'"
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="row in pagedAccess"
          :key="row.id"
          class="flex flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3.5 sm:px-5"
        >
          <div class="flex min-w-52 flex-1 items-center gap-3">
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-full bg-card-2 text-sm font-semibold text-muted"
            >
              {{ initials(row.user_name || row.user_email) }}
            </span>
            <div class="min-w-0">
              <p class="truncate font-medium text-ink">
                {{ row.user_name || row.user_email }}
              </p>
              <p v-if="row.user_name" class="truncate text-xs text-muted">
                {{ row.user_email }}
              </p>
            </div>
          </div>

          <div
            class="grid w-full grid-cols-3 gap-4 text-xs sm:w-auto sm:grid-cols-[7rem_8rem_8rem]"
          >
            <div>
              <p class="text-muted">Niveau</p>
              <p class="font-semibold text-ink">{{ row.level_name || "–" }}</p>
            </div>
            <div>
              <p class="text-muted">Montant</p>
              <p class="font-semibold text-ink">
                {{ row.amount_paid != null ? fcfa(row.amount_paid) : "–" }}
              </p>
            </div>
            <div>
              <p class="text-muted">Expire le</p>
              <p class="font-semibold text-ink">
                {{ row.expires_at ? shortDate(row.expires_at) : "–" }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-1.5 sm:w-28 sm:justify-end">
            <span
              class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
              :class="accessBadge(row).class"
            >
              {{ accessBadge(row).label }}
            </span>
          </div>
        </li>
      </ul>

      <!-- Crédits IA -->
      <ul
        v-else
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="grant in pagedCredits"
          :key="grant.id"
          class="flex flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3.5 sm:px-5"
        >
          <div class="flex min-w-52 flex-1 items-center gap-3">
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-full bg-card-2 text-sm font-semibold text-muted"
            >
              {{ initials(grant.user_email) }}
            </span>
            <p class="min-w-0 truncate font-medium text-ink">
              {{ grant.user_email }}
            </p>
          </div>

          <div
            class="grid w-full grid-cols-2 gap-4 text-xs sm:w-auto sm:grid-cols-[7rem_8rem]"
          >
            <div>
              <p class="text-muted">Crédits</p>
              <p class="font-semibold text-ink">
                +{{ grant.credits_purchased }}
              </p>
            </div>
            <div>
              <p class="text-muted">Date</p>
              <p class="font-semibold text-ink">
                {{ formatDate(grant.created_at) }}
              </p>
            </div>
          </div>

          <div class="flex items-center sm:w-28 sm:justify-end">
            <Tag
              :value="statusLabel(grant.payment_status)"
              :severity="statusSeverity(grant.payment_status)"
            />
          </div>
        </li>
      </ul>

      <Paginator
        v-if="currentRows.length > rowsPerPage"
        v-model:first="first"
        :rows="rowsPerPage"
        :totalRecords="currentRows.length"
        class="rounded-card border border-line bg-card"
      />
    </section>

    <!-- ══════════ Dialogue accès examen ══════════ -->
    <Dialog
      v-model:visible="showAccessDialog"
      modal
      header="Accorder un accès examen"
      :style="{ width: '34rem', maxWidth: '95vw' }"
    >
      <div class="space-y-4">
        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Utilisateur</label
          >
          <Select
            v-model="accessForm.user_id"
            :options="userOptions"
            optionLabel="label"
            optionValue="value"
            filter
            filterPlaceholder="Nom ou email"
            placeholder="Choisir un utilisateur"
            class="w-full"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Niveau</label
          >
          <Select
            v-model="accessForm.level_id"
            :options="levelOptions"
            optionLabel="label"
            optionValue="value"
            filter
            placeholder="Choisir un niveau"
            class="w-full"
          />
        </div>

        <!-- Formule ou pass journalier -->
        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Type d'accès</label
          >
          <div
            class="grid grid-cols-2 gap-1 rounded-leaf border border-line bg-card-2 p-1"
          >
            <button
              v-for="m in accessModes"
              :key="m.value"
              type="button"
              class="flex items-center justify-center gap-2 rounded-leaf px-3 py-2 text-sm font-medium transition-colors"
              :class="
                accessForm.mode === m.value
                  ? 'bg-card text-primary shadow-soft'
                  : 'text-muted hover:text-ink'
              "
              @click="accessForm.mode = m.value"
            >
              <i :class="m.icon" class="text-xs" />
              {{ m.label }}
            </button>
          </div>
        </div>

        <!-- Formule -->
        <div v-if="accessForm.mode === 'plan'">
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Formule</label
          >
          <div
            v-if="activePlans.length === 0"
            class="rounded-leaf bg-card-2 p-3 text-sm text-muted"
          >
            Aucun plan actif.
          </div>
          <div v-else class="grid gap-2 sm:grid-cols-2">
            <button
              v-for="plan in activePlans"
              :key="plan.id"
              type="button"
              class="rounded-leaf border px-3 py-2.5 text-left transition-colors"
              :class="
                accessForm.plan_id === plan.id
                  ? 'border-primary bg-primary/10'
                  : 'border-line bg-card hover:border-primary/30'
              "
              @click="accessForm.plan_id = plan.id"
            >
              <span class="block text-sm font-medium text-ink">{{
                plan.name
              }}</span>
            </button>
          </div>
        </div>

        <!-- Pass journalier -->
        <div v-else>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Nombre de jours</label
          >
          <InputNumber
            v-model="accessForm.days"
            :min="1"
            :max="30"
            showButtons
            class="w-full"
            inputClass="w-full"
          />
          <div class="mt-2 flex flex-wrap gap-2">
            <button
              v-for="n in [1, 2, 3, 7]"
              :key="n"
              type="button"
              class="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
              :class="
                accessForm.days === n
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-line bg-card text-muted hover:border-primary/30'
              "
              @click="accessForm.days = n"
            >
              {{ n }} jour{{ n > 1 ? "s" : "" }}
            </button>
          </div>
          <p class="mt-2 text-xs text-muted">
            Montant calculé au tarif du pass journalier. Aucune commission
            partenaire.
          </p>
        </div>

        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Note (optionnelle)</label
          >
          <Textarea
            v-model="accessForm.note"
            rows="2"
            autoResize
            class="w-full"
            placeholder="Ex. Virement Orange Money reçu le 13/10/2026"
          />
        </div>
        <Message v-if="dialogError" severity="error" :closable="false">{{
          dialogError
        }}</Message>
      </div>
      <template #footer>
        <Button
          label="Annuler"
          text
          severity="secondary"
          @click="showAccessDialog = false"
        />
        <Button
          label="Accorder l'accès"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!accessValid"
          @click="submitAccess"
        />
      </template>
    </Dialog>

    <!-- ══════════ Dialogue crédits IA ══════════ -->
    <Dialog
      v-model:visible="showCreditsDialog"
      modal
      header="Accorder des crédits IA"
      :style="{ width: '30rem', maxWidth: '95vw' }"
    >
      <div class="space-y-4">
        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Utilisateur</label
          >
          <Select
            v-model="creditsForm.user_id"
            :options="userOptions"
            optionLabel="label"
            optionValue="value"
            filter
            filterPlaceholder="Nom ou email"
            placeholder="Choisir un utilisateur"
            class="w-full"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-medium text-muted"
            >Nombre de crédits</label
          >
          <InputNumber
            v-model="creditsForm.credits"
            :min="1"
            showButtons
            class="w-full"
            inputClass="w-full"
          />
          <div class="mt-2 flex flex-wrap gap-2">
            <button
              v-for="n in creditPresets"
              :key="n"
              type="button"
              class="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
              :class="
                creditsForm.credits === n
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-line bg-card text-muted hover:border-primary/30'
              "
              @click="creditsForm.credits = n"
            >
              {{ n }}
            </button>
          </div>
        </div>
        <div
          v-if="creditsForm.credits"
          class="flex items-center justify-between rounded-leaf bg-card-2 px-4 py-3 text-sm"
        >
          <span class="text-muted">Valeur indicative</span>
          <span class="font-semibold text-ink">{{
            fcfa(creditsForm.credits * pricePerCredit)
          }}</span>
        </div>
        <Message v-if="dialogError" severity="error" :closable="false">{{
          dialogError
        }}</Message>
      </div>
      <template #footer>
        <Button
          label="Annuler"
          text
          severity="secondary"
          @click="showCreditsDialog = false"
        />
        <Button
          label="Accorder les crédits"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!creditsValid"
          @click="submitCredits"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PaymentAdminResponse } from "#shared/api";
import { AiCreditsService, PaymentsService } from "#shared/api";

definePageMeta({ layout: "admin" });

const toast = useToast();
const { adminGrantExamAccess } = usePayments();
const {
  adminGrantCredits,
  pricePerCredit,
  statusLabel,
  statusSeverity,
  formatDate,
} = useAiCredits();
const { catalog, loadCatalog } = useExams();
const { activePlans, loadPlans } = usePlans();
const adminUsersStore = useAdminUsersStore();

// ── Helpers ──
const fcfa = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} FCFA`;
const shortDate = (d: string) =>
  new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
const initials = (s?: string | null) =>
  (s ?? "?")
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join("");

const isActive = (row: PaymentAdminResponse) =>
  row.payment_status === "completed" &&
  !!row.expires_at &&
  new Date(row.expires_at) > new Date();

const accessBadge = (row: PaymentAdminResponse) => {
  if (row.payment_status !== "completed")
    return {
      label: row.payment_status,
      class: "bg-amber-500/15 text-amber-600",
    };
  return isActive(row)
    ? { label: "Actif", class: "bg-emerald-500/10 text-emerald-600" }
    : { label: "Expiré", class: "bg-card-2 text-muted" };
};

// ── Historique ──
type CreditGrant = {
  id: string;
  user_email: string;
  credits_purchased: number;
  payment_status: string;
  created_at: string;
};

const accessHistory = ref<PaymentAdminResponse[]>([]);
const creditsHistory = ref<CreditGrant[]>([]);
const loadingHistory = ref(true);

async function loadHistory() {
  loadingHistory.value = true;
  try {
    const [payments, credits] = await Promise.all([
      PaymentsService.listManualPaymentsApiV1PaymentsAdminManualListGet(),
      AiCreditsService.adminHistoryApiV1AiCreditsAdminHistoryGet(),
    ]);
    accessHistory.value = payments as PaymentAdminResponse[];
    creditsHistory.value = ((credits as any)?.data ?? []) as CreditGrant[];
  } catch {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Impossible de charger l'historique.",
      life: 4000,
    });
  } finally {
    loadingHistory.value = false;
  }
}

// ── Tuiles ──
const tiles = computed(() => [
  {
    label: "Accès accordés",
    value: accessHistory.value.length,
    icon: "pi pi-key",
    iconClass: "bg-primary/10 text-primary",
  },
  {
    label: "Accès encore actifs",
    value: accessHistory.value.filter(isActive).length,
    icon: "pi pi-check-circle",
    iconClass: "bg-emerald-500/10 text-emerald-600",
  },
  {
    label: "Octrois de crédits IA",
    value: creditsHistory.value.length,
    icon: "pi pi-sparkles",
    iconClass: "bg-violet-500/10 text-violet-600",
  },
  {
    label: "Crédits IA accordés",
    value: creditsHistory.value
      .reduce((s, g) => s + (g.credits_purchased ?? 0), 0)
      .toLocaleString("fr-FR"),
    icon: "pi pi-bolt",
    iconClass: "bg-amber-500/15 text-amber-600",
  },
]);

// ── Onglets, recherche, pagination ──
const activeTab = ref<"access" | "credits">("access");
const search = ref("");
const first = ref(0);
const rowsPerPage = 15;

const needle = computed(() => search.value.trim().toLowerCase());

const filteredAccess = computed(() =>
  [...accessHistory.value]
    .filter(
      (r) =>
        !needle.value ||
        `${r.user_name ?? ""} ${r.user_email ?? ""}`
          .toLowerCase()
          .includes(needle.value),
    )
    .sort((a, b) => (b.expires_at ?? "").localeCompare(a.expires_at ?? "")),
);
const filteredCredits = computed(() =>
  [...creditsHistory.value]
    .filter(
      (g) =>
        !needle.value ||
        (g.user_email ?? "").toLowerCase().includes(needle.value),
    )
    .sort((a, b) => b.created_at.localeCompare(a.created_at)),
);

const tabs = computed(() => [
  {
    key: "access" as const,
    label: "Accès examen",
    icon: "pi pi-key",
    count: filteredAccess.value.length,
  },
  {
    key: "credits" as const,
    label: "Crédits IA",
    icon: "pi pi-sparkles",
    count: filteredCredits.value.length,
  },
]);

const currentRows = computed(() =>
  activeTab.value === "access" ? filteredAccess.value : filteredCredits.value,
);
const pagedAccess = computed(() =>
  filteredAccess.value.slice(first.value, first.value + rowsPerPage),
);
const pagedCredits = computed(() =>
  filteredCredits.value.slice(first.value, first.value + rowsPerPage),
);

watch([activeTab, search], () => (first.value = 0));

// ── Options des selects ──
const userOptions = computed(() =>
  adminUsersStore.users.map((u: any) => ({
    value: u.id,
    label: u.full_name ? `${u.full_name} · ${u.email}` : u.email,
  })),
);

// Un accès se donne par niveau : une option par niveau de chaque examen
const levelOptions = computed(() =>
  (catalog.value ?? []).flatMap((e: any) =>
    (e.levels ?? []).map((l: any) => ({
      value: l.id,
      label: `${e.name} · ${l.cefr_code}`,
    })),
  ),
);
// ── Dialogues ──
const showAccessDialog = ref(false);
const showCreditsDialog = ref(false);
const saving = ref(false);
const dialogError = ref("");

type AccessMode = "plan" | "pass";

const accessModes: { value: AccessMode; label: string; icon: string }[] = [
  { value: "plan", label: "Formule", icon: "pi pi-tag" },
  { value: "pass", label: "Pass journalier", icon: "pi pi-sun" },
];

const accessForm = ref({
  user_id: "",
  level_id: "",
  mode: "plan" as AccessMode,
  plan_id: "",
  days: 1 as number | null,
  note: "",
});

const creditsForm = ref<{ user_id: string; credits: number | null }>({
  user_id: "",
  credits: 10,
});
const creditPresets = [5, 10, 20, 50];

const accessValid = computed(() => {
  const f = accessForm.value;
  if (!f.user_id || !f.level_id) return false;
  if (f.mode === "plan") return !!f.plan_id;
  // Pass : le backend ignore le plan mais le schéma l'exige, il faut au moins un plan actif
  return (f.days ?? 0) >= 1 && activePlans.value.length > 0;
});

const creditsValid = computed(
  () => !!creditsForm.value.user_id && (creditsForm.value.credits ?? 0) > 0,
);

function openAccessDialog() {
  dialogError.value = "";
  accessForm.value = {
    user_id: "",
    level_id: "",
    mode: "plan",
    plan_id: activePlans.value.length === 1 ? activePlans.value[0]!.id : "",
    days: 1,
    note: "",
  };
  showAccessDialog.value = true;
}

function openCreditsDialog() {
  dialogError.value = "";
  creditsForm.value = { user_id: "", credits: 10 };
  showCreditsDialog.value = true;
}

async function submitAccess() {
  if (!accessValid.value) return;
  saving.value = true;
  dialogError.value = "";

  const f = accessForm.value;
  const isPass = f.mode === "pass";
  const result = await adminGrantExamAccess({
    user_id: f.user_id,
    level_id: f.level_id,
    // Pass journalier : plan exigé par le schéma mais ignoré par le backend (prix et durée viennent de "days")
    plan_id: isPass ? activePlans.value[0]!.id : f.plan_id,
    days: isPass ? f.days : null,
    note: f.note.trim() || null,
  });

  saving.value = false;
  if (!result?.success) {
    dialogError.value = result?.message || "L'accès n'a pas pu être accordé.";
    return;
  }
  showAccessDialog.value = false;
  toast.add({
    severity: "success",
    summary: isPass ? `Pass de ${f.days} jour(s) accordé` : "Accès accordé",
    life: 3000,
  });
  activeTab.value = "access";
  loadHistory();
}

async function submitCredits() {
  if (!creditsValid.value) return;
  saving.value = true;
  dialogError.value = "";
  const result = await adminGrantCredits({
    user_id: creditsForm.value.user_id,
    credits: creditsForm.value.credits!,
  });
  saving.value = false;
  if (!result?.success) {
    dialogError.value =
      result?.message || "Les crédits n'ont pas pu être accordés.";
    return;
  }
  showCreditsDialog.value = false;
  toast.add({
    severity: "success",
    summary: `${creditsForm.value.credits} crédits accordés`,
    life: 3000,
  });
  activeTab.value = "credits";
  loadHistory();
}

onMounted(() => {
  loadHistory();
  loadCatalog();
  loadPlans();
  if (adminUsersStore.users.length === 0) adminUsersStore.fetchUsers();
});
</script>
