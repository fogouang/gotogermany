<!-- pages/admin/securite.vue -->
<template>
  <div class="space-y-6">
    <!-- ── En-tête ── -->
    <header class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-ink">Sécurité du contenu</h1>
        <p class="mt-1 text-sm text-muted">
          Comptes détectés en train d'aspirer les sujets, les audios ou les corrigés.
          Les cas graves sont suspendus automatiquement, la décision finale vous revient.
        </p>
      </div>
      <Button
        icon="pi pi-refresh"
        label="Actualiser"
        outlined
        size="small"
        :loading="loading"
        @click="loadAll"
      />
    </header>

    <!-- ── Chiffres ── -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div
        v-for="s in stats"
        :key="s.label"
        class="flex items-center gap-4 rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <span
          class="flex size-11 shrink-0 items-center justify-center rounded-leaf"
          :class="s.iconClass"
        >
          <i :class="s.icon" />
        </span>
        <div>
          <p class="text-2xl font-bold" :class="s.tone">{{ s.value }}</p>
          <p class="text-xs text-muted">{{ s.label }}</p>
        </div>
      </div>
    </div>

    <!-- ── Onglets ── -->
    <div class="flex flex-wrap gap-2 border-b border-line">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="-mb-px inline-flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
        :class="
          activeTab === tab.key
            ? 'border-primary text-primary'
            : 'border-transparent text-muted hover:text-ink'
        "
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span
          v-if="tab.count"
          class="rounded-full px-1.5 text-xs"
          :class="tab.key === 'incidents' ? 'bg-red-500/10 text-red-600' : 'bg-card-2 text-muted'"
        >
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- ══ Incidents ══ -->
    <section v-if="activeTab === 'incidents'" class="space-y-4">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="f in statusFilters"
          :key="f.key"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            statusFilter === f.key
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30'
          "
          @click="setStatusFilter(f.key)"
        >
          {{ f.label }}
        </button>
      </div>

      <div v-if="loading && !incidents.length" class="space-y-2">
        <div v-for="n in 4" :key="n" class="h-16 animate-pulse rounded-card bg-card-2" />
      </div>

      <div
        v-else-if="!incidents.length"
        class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
      >
        <span class="flex size-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600">
          <i class="pi pi-shield" />
        </span>
        <p class="text-sm font-medium text-ink">Aucun incident</p>
        <p class="max-w-md text-xs text-muted">
          Rien de suspect dans cette catégorie. Les détections apparaîtront ici dès qu'elles se produisent.
        </p>
      </div>

      <ul
        v-else
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="inc in incidents"
          :key="inc.id"
          class="flex cursor-pointer flex-wrap items-center gap-x-4 gap-y-2 px-5 py-4 transition-colors hover:bg-card-2/60"
          @click="openIncident(inc)"
        >
          <span class="size-2.5 shrink-0 rounded-full" :class="severityDot(inc.severity)" />

          <div class="min-w-48 flex-1">
            <p class="truncate text-sm font-semibold text-ink">{{ inc.user.full_name }}</p>
            <p class="truncate text-xs text-muted">
              {{ inc.user.email || "-" }}<template v-if="inc.user.phone"> · {{ inc.user.phone }}</template>
            </p>
          </div>

          <div class="min-w-48 flex-1">
            <p class="truncate text-sm text-ink">{{ ruleLabel(inc.rule) }}</p>
            <p class="truncate text-xs text-muted">
              {{ formatDateTime(inc.created_at) }}<template v-if="inc.ip"> · IP {{ inc.ip }}</template>
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-1.5">
            <span
              class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
              :class="actionBadge(inc.action).class"
            >
              {{ actionBadge(inc.action).label }}
            </span>
            <span
              v-if="inc.status === 'resolved'"
              class="rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted"
            >
              Traité
            </span>
          </div>

          <i class="pi pi-chevron-right text-xs text-muted" />
        </li>
      </ul>
    </section>

    <!-- ══ Comptes suspendus ══ -->
    <section v-else class="space-y-4">
      <div
        v-if="!blocks.length"
        class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
      >
        <span class="flex size-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600">
          <i class="pi pi-lock-open" />
        </span>
        <p class="text-sm font-medium text-ink">Aucun compte suspendu</p>
      </div>

      <ul
        v-else
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="b in blocks"
          :key="b.user.id"
          class="flex flex-wrap items-center gap-x-4 gap-y-3 px-5 py-4"
        >
          <span
            class="flex size-10 shrink-0 items-center justify-center rounded-full bg-red-500/10 text-sm font-bold text-red-600"
          >
            {{ initials(b.user.full_name) }}
          </span>
          <div class="min-w-48 flex-1">
            <p class="truncate text-sm font-semibold text-ink">{{ b.user.full_name }}</p>
            <p class="truncate text-xs text-muted">
              {{ b.user.email || "-" }}<template v-if="b.user.phone"> · {{ b.user.phone }}</template>
            </p>
          </div>
          <div class="min-w-48 flex-1">
            <p class="truncate text-sm text-ink">{{ ruleLabel(b.reason) }}</p>
            <p class="text-xs text-muted">
              Suspendu le {{ formatDateTime(b.blocked_at) }}
              <span v-if="!b.user.is_active" class="font-semibold text-red-600"> · compte désactivé</span>
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <Button
              icon="pi pi-download"
              text
              rounded
              size="small"
              severity="secondary"
              v-tooltip.top="'Télécharger les preuves'"
              aria-label="Télécharger les preuves"
              :loading="busy === `evidence-${b.user.id}`"
              @click="downloadEvidence(b.user)"
            />
            <Button
              label="Rétablir"
              icon="pi pi-lock-open"
              outlined
              size="small"
              :loading="busy === `unblock-${b.user.id}`"
              @click="confirmUnblock(b.user)"
            />
            <Button
              v-if="b.user.is_active"
              label="Bannir"
              icon="pi pi-ban"
              severity="danger"
              size="small"
              @click="openNoteDialog('ban', b.user)"
            />
          </div>
        </li>
      </ul>
    </section>

    <!-- ══ Détail d'un incident ══ -->
    <Drawer
      v-model:visible="showDetail"
      position="right"
      :style="{ width: '36rem', maxWidth: '100vw' }"
      header="Détail de l'incident"
    >
      <div v-if="selected" class="space-y-6">
        <!-- Élève -->
        <div class="flex items-center gap-3">
          <span
            class="flex size-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-base font-bold text-primary"
          >
            {{ initials(selected.user.full_name) }}
          </span>
          <div class="min-w-0">
            <p class="truncate font-semibold text-ink">{{ selected.user.full_name }}</p>
            <p class="truncate text-sm text-muted">
              {{ selected.user.email || "-" }}<template v-if="selected.user.phone"> · {{ selected.user.phone }}</template>
            </p>
            <div class="mt-1 flex flex-wrap gap-1.5">
              <span
                v-if="selected.user.is_blocked"
                class="rounded-full bg-red-500/10 px-2 py-0.5 text-[11px] font-semibold text-red-600"
              >
                Accès aux sujets suspendu
              </span>
              <span
                v-if="!selected.user.is_active"
                class="rounded-full bg-red-500/10 px-2 py-0.5 text-[11px] font-semibold text-red-600"
              >
                Compte désactivé
              </span>
              <span
                v-if="selected.user.is_active && !selected.user.is_blocked"
                class="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600"
              >
                Accès normal
              </span>
            </div>
          </div>
        </div>

        <!-- Détection -->
        <section class="space-y-2 rounded-leaf border border-line p-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <p class="text-sm font-semibold text-ink">{{ ruleLabel(selected.rule) }}</p>
            <span
              class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
              :class="actionBadge(selected.action).class"
            >
              {{ actionBadge(selected.action).label }}
            </span>
          </div>
          <p class="text-xs text-muted">{{ ruleHint(selected.rule) }}</p>
          <dl class="grid grid-cols-1 gap-x-4 gap-y-1 pt-2 text-xs sm:grid-cols-[auto_1fr]">
            <dt class="text-muted">Détecté le</dt>
            <dd class="text-ink">{{ formatDateTime(selected.created_at) }}</dd>
            <dt class="text-muted">Adresse IP</dt>
            <dd class="font-mono text-ink">{{ selected.ip || "-" }}</dd>
            <dt class="text-muted">Navigateur</dt>
            <dd class="break-all font-mono text-ink">{{ selected.user_agent || "-" }}</dd>
          </dl>
        </section>

        <!-- Compteurs -->
        <section v-if="countEntries.length">
          <h3 class="mb-2 text-sm font-semibold text-ink">Au moment de la détection</h3>
          <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
            <div
              v-for="c in countEntries"
              :key="c.key"
              class="rounded-leaf bg-card-2 px-3 py-2"
            >
              <p class="truncate text-lg font-bold text-ink">{{ c.value }}</p>
              <p class="text-[11px] text-muted">{{ c.label }}</p>
            </div>
          </div>
        </section>

        <!-- Derniers accès -->
        <section v-if="recentEvents.length">
          <h3 class="mb-2 text-sm font-semibold text-ink">
            Derniers accès au contenu
            <span class="font-normal text-muted">· {{ recentEvents.length }}</span>
          </h3>
          <div class="max-h-72 overflow-y-auto rounded-leaf border border-line">
            <table class="w-full text-xs">
              <thead class="sticky top-0 bg-card-2">
                <tr class="text-left text-muted">
                  <th class="px-3 py-2 font-medium">Heure</th>
                  <th class="px-3 py-2 font-medium">Action</th>
                  <th class="px-3 py-2 font-medium">Ressource</th>
                  <th class="px-3 py-2 font-medium">IP</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-line">
                <tr v-for="(e, i) in recentEvents" :key="i">
                  <td class="whitespace-nowrap px-3 py-1.5 text-ink">{{ formatTime(e.at) }}</td>
                  <td class="whitespace-nowrap px-3 py-1.5 text-ink">{{ kindLabel(e.kind) }}</td>
                  <td class="px-3 py-1.5 font-mono text-muted">{{ shortId(e.resource_id) }}</td>
                  <td class="whitespace-nowrap px-3 py-1.5 font-mono text-muted">{{ e.ip || "-" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Traitement -->
        <section v-if="selected.status === 'resolved'" class="rounded-leaf bg-card-2 px-4 py-3 text-sm">
          <p class="font-medium text-ink">
            Traité le {{ selected.resolved_at ? formatDateTime(selected.resolved_at) : "-" }}
          </p>
          <p v-if="selected.resolution_note" class="mt-1 whitespace-pre-wrap text-muted">
            {{ selected.resolution_note }}
          </p>
        </section>

        <!-- Actions -->
        <div class="flex flex-wrap gap-2 border-t border-line pt-4">
          <Button
            label="Preuves"
            icon="pi pi-download"
            outlined
            size="small"
            :loading="busy === `evidence-${selected.user.id}`"
            @click="downloadEvidence(selected.user)"
          />
          <Button
            v-if="selected.status === 'open'"
            label="Marquer traité"
            icon="pi pi-check"
            outlined
            size="small"
            @click="openNoteDialog('resolve', selected.user)"
          />
          <Button
            v-if="selected.user.is_blocked || !selected.user.is_active"
            label="Rétablir l'accès"
            icon="pi pi-lock-open"
            outlined
            size="small"
            :loading="busy === `unblock-${selected.user.id}`"
            @click="confirmUnblock(selected.user)"
          />
          <Button
            v-if="selected.user.is_active"
            label="Bannir le compte"
            icon="pi pi-ban"
            severity="danger"
            size="small"
            @click="openNoteDialog('ban', selected.user)"
          />
        </div>
      </div>
    </Drawer>

    <!-- ══ Note : traiter / bannir ══ -->
    <Dialog
      v-model:visible="noteDialog.visible"
      :header="noteDialog.mode === 'ban' ? `Bannir ${noteDialog.user?.full_name ?? ''}` : 'Marquer l\'incident comme traité'"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <div class="space-y-3">
        <p v-if="noteDialog.mode === 'ban'" class="text-sm text-muted">
          Le compte sera désactivé : l'élève ne pourra plus se connecter. Les preuves restent
          disponibles au téléchargement.
        </p>
        <label class="block text-sm font-medium text-ink">
          Note
          <span class="font-normal text-muted">
            {{ noteDialog.mode === "ban" ? "(motif, obligatoire)" : "(facultatif)" }}
          </span>
        </label>
        <Textarea
          v-model="noteDialog.note"
          rows="3"
          auto-resize
          class="w-full"
          :placeholder="
            noteDialog.mode === 'ban'
              ? 'Ex. aspiration de 25 sujets en 20 minutes, partage constaté sur WhatsApp'
              : 'Ex. faux positif, élève en révision intensive'
          "
        />
      </div>
      <template #footer>
        <Button label="Annuler" text @click="noteDialog.visible = false" />
        <Button
          :label="noteDialog.mode === 'ban' ? 'Bannir' : 'Valider'"
          :icon="noteDialog.mode === 'ban' ? 'pi pi-ban' : 'pi pi-check'"
          :severity="noteDialog.mode === 'ban' ? 'danger' : undefined"
          :disabled="noteDialog.mode === 'ban' && !noteDialog.note.trim()"
          :loading="busy === 'note'"
          @click="submitNote"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type {
  SecurityBlock,
  SecurityIncident,
  SecuritySummary,
  SecurityUser,
} from "~/composables/useSecurity";

definePageMeta({ layout: "admin" });

const toast = useToast();
const confirm = useConfirm();
const security = useSecurity();

// ── Données ──
const loading = ref(true);
const summary = ref<SecuritySummary>({ open_incidents: 0, open_high: 0, blocked_users: 0 });
const incidents = ref<SecurityIncident[]>([]);
const blocks = ref<SecurityBlock[]>([]);
const busy = ref<string | null>(null);

type StatusFilter = "open" | "resolved" | "";
const statusFilter = ref<StatusFilter>("open");
const statusFilters: { key: StatusFilter; label: string }[] = [
  { key: "open", label: "À traiter" },
  { key: "resolved", label: "Traités" },
  { key: "", label: "Tous" },
];

type TabKey = "incidents" | "blocks";
const activeTab = ref<TabKey>("incidents");
const tabs = computed(() => [
  { key: "incidents" as const, label: "Incidents", count: summary.value.open_incidents },
  { key: "blocks" as const, label: "Comptes suspendus", count: summary.value.blocked_users },
]);

const stats = computed(() => [
  {
    label: "Incidents à traiter",
    value: summary.value.open_incidents,
    icon: "pi pi-exclamation-triangle",
    iconClass: "bg-amber-500/15 text-amber-600",
    tone: summary.value.open_incidents ? "text-amber-600" : "text-ink",
  },
  {
    label: "Dont critiques",
    value: summary.value.open_high,
    icon: "pi pi-bolt",
    iconClass: "bg-red-500/10 text-red-600",
    tone: summary.value.open_high ? "text-red-600" : "text-ink",
  },
  {
    label: "Comptes suspendus",
    value: summary.value.blocked_users,
    icon: "pi pi-lock",
    iconClass: "bg-primary/10 text-primary",
    tone: "text-ink",
  },
]);

async function loadAll() {
  loading.value = true;
  try {
    const [s, inc, bl] = await Promise.all([
      security.getSummary(),
      security.listIncidents(statusFilter.value),
      security.listBlocks(),
    ]);
    summary.value = s;
    incidents.value = inc;
    blocks.value = bl;
  } catch (e) {
    toast.add({
      severity: "error",
      summary: security.apiError(e, "Chargement impossible"),
      life: 4000,
    });
  } finally {
    loading.value = false;
  }
}

async function setStatusFilter(key: StatusFilter) {
  statusFilter.value = key;
  try {
    incidents.value = await security.listIncidents(key);
  } catch (e) {
    toast.add({ severity: "error", summary: security.apiError(e, "Chargement impossible"), life: 4000 });
  }
}

// ── Libellés ──
const RULES: Record<string, { label: string; hint: string }> = {
  scripted_client: {
    label: "Client automatisé",
    hint: "Les requêtes viennent d'un script ou d'un outil d'API (Python, curl, Postman, Selenium…), pas d'un navigateur.",
  },
  too_many_subjects_10min: {
    label: "Trop de sujets ouverts en 10 min",
    hint: "Plus de 8 sujets différents ouverts en 10 minutes. Un élève normal en ouvre un ou deux par heure.",
  },
  too_many_subjects_1h: {
    label: "Trop de sujets ouverts en 1 h",
    hint: "Plus de 20 sujets différents ouverts en une heure.",
  },
  too_many_sessions_1h: {
    label: "Trop de sessions démarrées en 1 h",
    hint: "Plus de 12 sessions démarrées en une heure, souvent pour récupérer les questions sans répondre.",
  },
  too_many_results_1h: {
    label: "Trop de corrigés consultés en 1 h",
    hint: "Plus de 15 corrigés différents consultés en une heure : récupération des bonnes réponses.",
  },
  request_burst: {
    label: "Rafale de requêtes",
    hint: "Plus de 40 appels au contenu en une minute. L'élève a été ralenti, pas suspendu.",
  },
  many_subjects_warning: {
    label: "Nombreux sujets ouverts",
    hint: "Signal faible : plus de 5 sujets en 10 minutes. Aucune mesure prise, à surveiller.",
  },
  manual_ban: { label: "Bannissement manuel", hint: "Compte désactivé par un administrateur." },
  banned: { label: "Banni", hint: "Compte désactivé par un administrateur." },
};
const ruleLabel = (r: string) => RULES[r]?.label ?? r;
const ruleHint = (r: string) => RULES[r]?.hint ?? "";

const COUNT_LABELS: Record<string, string> = {
  requests_1min: "Requêtes / min",
  subjects_10min: "Sujets / 10 min",
  subjects_1h: "Sujets / heure",
  sessions_1h: "Sessions / heure",
  results_1h: "Corrigés / heure",
  user_agent: "Client",
};

const KINDS: Record<string, string> = {
  subject_view: "Sujet ouvert",
  session_start: "Session démarrée",
  result_view: "Corrigé consulté",
};
const kindLabel = (k: string) => KINDS[k] ?? k;

function severityDot(s: string) {
  if (s === "high") return "bg-red-500";
  if (s === "medium") return "bg-amber-500";
  return "bg-sky-500";
}

function actionBadge(a: string) {
  const map: Record<string, { label: string; class: string }> = {
    blocked: { label: "Suspendu", class: "bg-red-500/10 text-red-600" },
    banned: { label: "Banni", class: "bg-red-500/10 text-red-600" },
    throttled: { label: "Ralenti", class: "bg-amber-500/15 text-amber-600" },
    logged: { label: "Surveillance", class: "bg-sky-500/10 text-sky-600" },
  };
  return map[a] ?? { label: a, class: "bg-card-2 text-muted" };
}

// ── Utilitaires ──
const formatDateTime = (d: string) =>
  new Date(d).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
const formatTime = (d: string) =>
  new Date(d).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
const shortId = (id: string | null) => (id ? `${id.slice(0, 8)}…` : "-");
const initials = (name: string) =>
  name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

// ── Détail ──
const showDetail = ref(false);
const selected = ref<SecurityIncident | null>(null);

const countEntries = computed(() =>
  Object.entries(selected.value?.details?.counts ?? {})
    // Le navigateur est déjà affiché en entier dans la carte de détection
    .filter(([key]) => key !== "user_agent")
    .map(([key, value]) => ({
      key,
      label: COUNT_LABELS[key] ?? key,
      value,
    })),
);

const recentEvents = computed(() => selected.value?.details?.recent_events ?? []);

function openIncident(inc: SecurityIncident) {
  selected.value = inc;
  showDetail.value = true;
}

/** Recharge tout et garde le détail ouvert à jour. */
async function refreshAfterAction() {
  await loadAll();
  if (selected.value) {
    try {
      selected.value = await security.getIncident(selected.value.id);
    } catch {
      /* incident introuvable : on garde l'ancien affichage */
    }
  }
}

// ── Actions ──
async function downloadEvidence(user: SecurityUser) {
  busy.value = `evidence-${user.id}`;
  try {
    await security.downloadEvidence(user.id, user.full_name);
  } catch (e) {
    toast.add({ severity: "error", summary: security.apiError(e, "Téléchargement impossible"), life: 4000 });
  } finally {
    busy.value = null;
  }
}

function confirmUnblock(user: SecurityUser) {
  confirm.require({
    header: "Rétablir l'accès",
    message: `${user.full_name} pourra de nouveau se connecter et ouvrir les sujets. Continuer ?`,
    icon: "pi pi-lock-open",
    acceptLabel: "Rétablir",
    rejectLabel: "Annuler",
    accept: async () => {
      busy.value = `unblock-${user.id}`;
      try {
        await security.unblockUser(user.id);
        toast.add({ severity: "success", summary: "Accès rétabli", life: 3000 });
        await refreshAfterAction();
      } catch (e) {
        toast.add({ severity: "error", summary: security.apiError(e, "Action impossible"), life: 4000 });
      } finally {
        busy.value = null;
      }
    },
  });
}

const noteDialog = reactive<{
  visible: boolean;
  mode: "resolve" | "ban";
  user: SecurityUser | null;
  note: string;
}>({ visible: false, mode: "resolve", user: null, note: "" });

function openNoteDialog(mode: "resolve" | "ban", user: SecurityUser) {
  noteDialog.mode = mode;
  noteDialog.user = user;
  noteDialog.note = "";
  noteDialog.visible = true;
}

async function submitNote() {
  const note = noteDialog.note.trim() || null;
  busy.value = "note";
  try {
    if (noteDialog.mode === "ban" && noteDialog.user) {
      await security.banUser(noteDialog.user.id, note);
      toast.add({ severity: "success", summary: "Compte désactivé", life: 3000 });
    } else if (selected.value) {
      await security.resolveIncident(selected.value.id, note);
      toast.add({ severity: "success", summary: "Incident traité", life: 3000 });
    }
    noteDialog.visible = false;
    await refreshAfterAction();
  } catch (e) {
    toast.add({ severity: "error", summary: security.apiError(e, "Action impossible"), life: 4000 });
  } finally {
    busy.value = null;
  }
}

// ── Chargement + actualisation automatique ──
let timer: ReturnType<typeof setInterval> | null = null;

onMounted(() => {
  loadAll();
  timer = setInterval(() => {
    if (!showDetail.value && !noteDialog.visible) loadAll();
  }, 60_000);
});

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>