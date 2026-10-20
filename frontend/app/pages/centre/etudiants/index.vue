<!-- pages/centre/etudiants/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Activations suspendues ── -->
    <div
      v-if="activationBlocked"
      class="flex items-start gap-3 rounded-card border border-red-500/30 bg-red-500/5 p-4"
    >
      <i class="pi pi-lock mt-0.5 text-red-600" />
      <div>
        <p class="text-sm font-semibold text-red-600">
          {{ t("centre.dashboard.blocked_title") }}
        </p>
        <p class="mt-0.5 text-sm text-muted">
          {{
            salesStore.mySummary?.block_reason ||
            t("centre.dashboard.blocked_default")
          }}
        </p>
      </div>
    </div>

    <!-- ── Filtres rapides (cliquables) ── -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-5">
      <button
        v-for="f in filters"
        :key="f.key"
        type="button"
        class="rounded-card border bg-card p-4 text-left shadow-soft transition-colors"
        :class="
          activeFilter === f.key
            ? 'border-primary ring-1 ring-primary/30'
            : 'border-line hover:border-primary/30'
        "
        @click="activeFilter = f.key"
      >
        <p class="text-xs font-medium text-muted">{{ f.label }}</p>
        <p class="mt-1 text-2xl font-bold" :class="f.tone">{{ f.count }}</p>
      </button>
    </div>

    <!-- ── Barre d'outils ── -->
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <IconField class="w-full sm:max-w-sm">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="search"
          class="w-full"
          :placeholder="t('centre.students.search_placeholder')"
        />
      </IconField>
      <Button
        v-if="authStore.isSecretary"
        :label="t('centre.nav.new_student')"
        icon="pi pi-user-plus"
        class="w-full sm:w-auto"
        @click="navigateTo(localePath('/centre/etudiants/nouveau'))"
      />
    </div>

    <!-- ── États ── -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="n in 5"
        :key="n"
        class="h-16 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <div
      v-else-if="filteredStudents.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-users" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{
          students.length === 0
            ? t("centre.students.empty_title")
            : t("centre.progress.no_results")
        }}
      </p>
      <p class="text-xs text-muted">
        {{
          students.length === 0
            ? t("centre.students.empty_text")
            : t("centre.students.no_results_hint")
        }}
      </p>
    </div>

    <template v-else>
      <!-- ── Tableau (écran large) ── -->
      <div
        class="hidden overflow-hidden rounded-card border border-line bg-card shadow-soft md:block"
      >
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-line text-left text-xs text-muted">
              <tr>
                <th class="px-5 py-3 font-medium">
                  {{ t("centre.dashboard.col_student") }}
                </th>
                <th class="px-5 py-3 font-medium">
                  {{ t("centre.students.col_target") }}
                </th>
                <th class="px-5 py-3 font-medium">
                  {{ t("centre.students.col_access") }}
                </th>
                <th class="px-5 py-3 font-medium">
                  {{ t("centre.students.col_class") }}
                </th>
                <th class="px-5 py-3 text-right font-medium">
                  {{ t("centre.students.col_actions") }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-line">
              <tr
                v-for="student in pagedStudents"
                :key="student.id"
                :class="{ 'opacity-60': !student.is_active }"
              >
                <td class="px-5 py-3">
                  <div class="flex items-center gap-3">
                    <span
                      class="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
                    >
                      {{ initials(student.full_name) }}
                    </span>
                    <div class="min-w-0">
                      <p class="truncate font-medium text-ink">
                        {{ student.full_name }}
                        <span
                          v-if="!student.is_active"
                          class="ml-1 rounded-full bg-red-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-red-600"
                        >
                          {{ t("centre.account.disabled") }}
                        </span>
                      </p>
                      <p
                        v-if="displayEmail(student.email)"
                        class="truncate text-xs text-muted"
                      >
                        {{ displayEmail(student.email) }}
                      </p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-3 text-muted">
                  {{ levelLabel(student.target_level_id) }}
                </td>
                <td class="px-5 py-3">
                  <span
                    class="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                    :class="accessBadge(student).class"
                  >
                    <i :class="accessBadge(student).icon" class="text-[10px]" />
                    {{ accessBadge(student).label }}
                  </span>
                </td>
                <td class="px-5 py-3">
                  <span
                    v-if="inActiveClass(student.id)"
                    class="text-xs text-muted"
                  >
                    {{ classOf(student.id) }}
                  </span>
                  <span
                    v-else
                    class="rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
                    v-tooltip.top="t('centre.students.no_class_hint')"
                  >
                    {{ t("centre.students.filter_noclass") }}
                  </span>
                </td>
                <td class="px-5 py-3">
                  <div class="flex items-center justify-end gap-1">
                    <Button
                      :label="
                        hasAccess(student)
                          ? t('centre.students.extend')
                          : t('centre.students.activate')
                      "
                      icon="pi pi-bolt"
                      size="small"
                      :outlined="accessState(student) === 'active'"
                      :disabled="!student.is_active || activationBlocked"
                      @click="openActivation(student)"
                    />
                    <Button
                      v-if="authStore.isDirector"
                      :icon="
                        student.is_active ? 'pi pi-ban' : 'pi pi-check-circle'
                      "
                      text
                      rounded
                      size="small"
                      :severity="student.is_active ? 'danger' : 'success'"
                      v-tooltip.top="
                        student.is_active
                          ? t('centre.students.deactivate_account')
                          : t('centre.students.reactivate_account')
                      "
                      @click="handleToggleActivation(student)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Cartes (mobile) ── -->
      <div class="space-y-3 md:hidden">
        <div
          v-for="student in pagedStudents"
          :key="student.id"
          class="rounded-card border border-line bg-card p-4 shadow-soft"
          :class="{ 'opacity-60': !student.is_active }"
        >
          <div class="flex items-start gap-3">
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
            >
              {{ initials(student.full_name) }}
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate font-medium text-ink">
                {{ student.full_name }}
              </p>
              <p class="truncate text-xs text-muted">
                {{ levelLabel(student.target_level_id) }}
              </p>
              <div class="mt-2 flex flex-wrap items-center gap-1.5">
                <span
                  class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="accessBadge(student).class"
                >
                  <i :class="accessBadge(student).icon" class="text-[10px]" />
                  {{ accessBadge(student).label }}
                </span>
                <span
                  v-if="!inActiveClass(student.id)"
                  class="rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
                >
                  {{ t("centre.students.filter_noclass") }}
                </span>
              </div>
            </div>
          </div>
          <div class="mt-3 flex items-center gap-2 border-t border-line pt-3">
            <Button
              :label="
                hasAccess(student)
                  ? t('centre.students.extend')
                  : t('centre.activation.title')
              "
              icon="pi pi-bolt"
              size="small"
              class="flex-1"
              :disabled="!student.is_active || activationBlocked"
              @click="openActivation(student)"
            />
            <Button
              v-if="authStore.isDirector"
              :icon="student.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
              text
              rounded
              size="small"
              :severity="student.is_active ? 'danger' : 'success'"
              :aria-label="
                student.is_active
                  ? t('centre.students.deactivate_account')
                  : t('centre.students.reactivate_account')
              "
              @click="handleToggleActivation(student)"
            />
          </div>
        </div>
      </div>

      <Paginator
        v-if="filteredStudents.length > rowsPerPage"
        :rows="rowsPerPage"
        :total-records="filteredStudents.length"
        :first="firstRecordIndex"
        :rows-per-page-options="[10, 20, 50]"
        class="rounded-card border border-line"
        @page="onPageChange"
      />
    </template>

    <!-- ══ Dialog : activer un accès ══ -->
    <Dialog
      v-model:visible="showActivation"
      modal
      :header="
        activationResult
          ? t('centre.activation.done_title')
          : t('centre.activation.title')
      "
      :style="{ width: '95vw', maxWidth: '34rem' }"
    >
      <div v-if="selectedStudent" class="space-y-5">
        <!-- Élève -->
        <div class="flex items-center gap-3 rounded-leaf bg-card-2 p-3">
          <span
            class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
          >
            {{ initials(selectedStudent.full_name) }}
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold text-ink">
              {{ selectedStudent.full_name }}
            </p>
            <p
              v-if="displayEmail(selectedStudent.email)"
              class="truncate text-xs text-muted"
            >
              {{ displayEmail(selectedStudent.email) }}
            </p>
          </div>
          <span
            class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="accessBadge(selectedStudent).class"
          >
            {{ accessBadge(selectedStudent).label }}
          </span>
        </div>

        <!-- ── Résultat après activation ── -->
        <template v-if="activationResult">
          <div class="flex flex-col items-center gap-2 py-2 text-center">
            <span
              class="flex size-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600"
            >
              <i class="pi pi-check text-lg" />
            </span>
            <p class="font-semibold text-ink">
              {{
                t("centre.activation.valid_until", {
                  date: formatDate(activationResult.access_expires_at),
                })
              }}
            </p>
          </div>
          <dl
            class="divide-y divide-line rounded-leaf border border-line text-sm"
          >
            <div class="flex justify-between px-4 py-2.5">
              <dt class="text-muted">
                {{ t("centre.activation.price_paid") }}
              </dt>
              <dd class="font-medium text-ink">
                {{ fcfa(activationResult.sale.price) }}
              </dd>
            </div>
            <div class="flex justify-between px-4 py-2.5">
              <dt class="text-muted">
                {{ t("centre.activation.centre_share") }}
              </dt>
              <dd class="font-medium text-emerald-600">
                {{ fcfa(activationResult.sale.partner_share) }}
              </dd>
            </div>
            <div class="flex justify-between px-4 py-2.5">
              <dt class="text-muted">{{ t("centre.activation.to_pay") }}</dt>
              <dd class="font-semibold text-ink">
                {{ fcfa(activationResult.sale.amount_due) }}
              </dd>
            </div>
            <div
              v-if="activationResult.sale.due_at"
              class="flex justify-between px-4 py-2.5"
            >
              <dt class="text-muted">{{ t("centre.activation.before") }}</dt>
              <dd class="font-medium text-amber-600">
                {{ formatDateTime(activationResult.sale.due_at) }}
              </dd>
            </div>
          </dl>
          <p
            v-if="!inActiveClass(selectedStudent.id)"
            class="flex items-start gap-2 rounded-leaf bg-amber-500/5 p-3 text-xs text-amber-600"
          >
            <i class="pi pi-info-circle mt-0.5" />
            {{ t("centre.activation.no_class_warning") }}
          </p>
        </template>

        <!-- ── Formulaire ── -->
        <template v-else>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">{{
              t("centre.form.level")
            }}</label>
            <Select
              v-model="activationForm.level_id"
              :options="allLevels"
              optionLabel="label"
              optionValue="value"
              :placeholder="t('centre.form.level_placeholder')"
              class="w-full"
              filter
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">{{
              t("centre.dashboard.col_plan")
            }}</label>
            <div
              v-if="activePlans.length === 0"
              class="rounded-leaf bg-card-2 p-3 text-sm text-muted"
            >
              {{ t("centre.activation.no_plans") }}
            </div>
            <div v-else class="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <button
                v-for="plan in activePlans"
                :key="plan.id"
                type="button"
                class="flex flex-col rounded-leaf border p-3 text-left transition-colors"
                :class="
                  activationForm.plan_id === plan.id
                    ? 'border-primary bg-primary/5 ring-1 ring-primary/30'
                    : 'border-line hover:border-primary/30'
                "
                @click="activationForm.plan_id = plan.id"
              >
                <span class="text-sm font-semibold text-ink">{{
                  plan.name
                }}</span>
                <span class="text-xs text-muted">{{
                  t("centre.activation.plan_days", plan.duration_days)
                }}</span>
                <span class="mt-2 text-base font-bold text-primary">{{
                  fcfa(plan.price)
                }}</span>
              </button>
            </div>
          </div>

          <!-- Récapitulatif -->
          <div v-if="selectedPlan" class="rounded-leaf border border-line p-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted">{{
                t("centre.activation.to_collect")
              }}</span>
              <span
                class="text-lg font-bold"
                :class="isTrial ? 'text-emerald-600' : 'text-ink'"
                >{{ isTrial ? fcfa(0) : fcfa(selectedPlan.price) }}</span
              >
            </div>
            <div class="mt-1 flex items-center justify-between">
              <span class="text-sm text-muted">{{
                t("centre.activation.estimated")
              }}</span>
              <span class="text-sm font-medium text-ink">{{
                formatDate(estimatedExpiry)
              }}</span>
            </div>
            <p
              v-if="isTrial"
              class="mt-4 flex items-start gap-2 rounded-leaf bg-emerald-500/10 px-3 py-2.5 text-sm text-emerald-700 dark:text-emerald-400"
            >
              <i class="pi pi-gift mt-0.5" />
              {{
                t("centre.activation.trial_free", {
                  n: salesStore.mySummary?.trial_activations_left ?? 0,
                  date: formatDate(salesStore.mySummary!.trial_ends_at!),
                })
              }}
            </p>
            <label
              v-else
              class="mt-4 flex cursor-pointer items-start gap-2 text-sm text-ink"
            >
              <Checkbox v-model="activationForm.paid" binary class="mt-0.5" />
              <span>
                {{
                  t("centre.activation.paid_confirm", {
                    amount: fcfa(selectedPlan.price),
                    name: selectedStudent.full_name,
                  })
                }}
              </span>
            </label>
          </div>

          <Message v-if="activationError" severity="error" :closable="false">
            {{ activationError }}
          </Message>
        </template>
      </div>

      <template #footer>
        <template v-if="activationResult">
          <Button
            :label="t('centre.activation.finish')"
            @click="showActivation = false"
          />
        </template>
        <template v-else>
          <Button
            :label="t('common.cancel')"
            text
            @click="showActivation = false"
          />
          <Button
            :label="t('centre.activation.submit')"
            icon="pi pi-bolt"
            :loading="activating"
            :disabled="!canActivate"
            @click="handleActivate"
          />
        </template>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { ActivationResponse, StudentResponse } from "#shared/api";
import CentreJoinLinkCard from "~/components/centre/JoinLinkCard.vue";
import CentreJoinRequestsPanel from "~/components/centre/JoinRequestsPanel.vue";

definePageMeta({ layout: "centre", watermark: "Lernende" });

interface PlanLite {
  id: string;
  name: string;
  duration_days: number;
  price: number;
  is_active?: boolean;
}

const { t, locale } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const examsStore = useExamsStore();
const plansStore = usePlansStore();
const salesStore = useSalesStore();
const trainingSessionsStore = useTrainingSessionsStore();
const toast = useToast();
const route = useRoute();
const router = useRouter();

const loading = ref(true);
const students = ref<StudentResponse[]>([]);
const errorMessage = ref<string | null>(null);

// ── Formatage ──
const fcfa = (n: number) =>
  `${new Intl.NumberFormat(locale.value).format(n)} FCFA`;
const formatDate = (d: string | Date) =>
  new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
const formatDateTime = (d: string) =>
  new Date(d).toLocaleString(locale.value, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

const PLACEHOLDER_EMAIL_DOMAIN = "@internal.gotogermany";

function displayEmail(email: string | null | undefined) {
  if (!email || email.endsWith(PLACEHOLDER_EMAIL_DOMAIN)) return "";
  return email;
}

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

// ── Niveaux ──
const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

function levelLabel(id: string | null) {
  if (!id) return "-";
  return allLevels.value.find((l) => l.value === id)?.label ?? "-";
}

// ── État de l'accès ──
type AccessState = "active" | "soon" | "expired" | "none";
const DAY = 24 * 60 * 60 * 1000;

function accessState(s: StudentResponse): AccessState {
  if (!s.access_expires_at) return "none";
  const left = new Date(s.access_expires_at).getTime() - Date.now();
  if (left < 0) return "expired";
  if (left <= 7 * DAY) return "soon";
  return "active";
}

function hasAccess(s: StudentResponse) {
  const st = accessState(s);
  return st === "active" || st === "soon";
}

function accessBadge(s: StudentResponse) {
  const state = accessState(s);
  if (state === "none")
    return {
      label: t("centre.students.access_none"),
      icon: "pi pi-minus-circle",
      class: "bg-card-2 text-muted",
    };
  if (state === "expired")
    return {
      label: t("centre.students.access_expired", {
        date: formatDate(s.access_expires_at!),
      }),
      icon: "pi pi-times-circle",
      class: "bg-red-500/10 text-red-600",
    };
  if (state === "soon") {
    const days = Math.max(
      1,
      Math.ceil((new Date(s.access_expires_at!).getTime() - Date.now()) / DAY),
    );
    return {
      label: t("centre.students.access_soon", days),
      icon: "pi pi-clock",
      class: "bg-amber-500/10 text-amber-600",
    };
  }
  return {
    label: t("centre.students.access_until", {
      date: formatDate(s.access_expires_at!),
    }),
    icon: "pi pi-check-circle",
    class: "bg-emerald-500/10 text-emerald-600",
  };
}

// ── Classes actives (règle : accès + classe active pour ouvrir les sujets) ──
const activeClassByStudent = ref<Record<string, string>>({});

function inActiveClass(studentId: string) {
  return studentId in activeClassByStudent.value;
}
function classOf(studentId: string) {
  return activeClassByStudent.value[studentId] ?? "";
}

function computeActiveClasses() {
  const now = Date.now();
  const map: Record<string, string> = {};
  for (const session of trainingSessionsStore.sessions) {
    if (session.end_date && new Date(session.end_date).getTime() < now)
      continue;
    for (const s of session.students) {
      if (!s.ended_at) map[s.student_id] = session.label || session.level_name;
    }
  }
  activeClassByStudent.value = map;
}

// ── Filtres + recherche ──
type FilterKey = "all" | "active" | "soon" | "none" | "noclass";
const activeFilter = ref<FilterKey>("all");
const search = ref("");

const filters = computed(() => {
  const list = students.value;
  const count = (fn: (s: StudentResponse) => boolean) => list.filter(fn).length;
  return [
    {
      key: "all" as const,
      label: t("centre.students.filter_all"),
      count: list.length,
      tone: "text-ink",
    },
    {
      key: "active" as const,
      label: t("centre.students.filter_active"),
      count: count((s) => ["active", "soon"].includes(accessState(s))),
      tone: "text-emerald-600",
    },
    {
      key: "soon" as const,
      label: t("centre.students.filter_soon"),
      count: count((s) => accessState(s) === "soon"),
      tone: "text-amber-600",
    },
    {
      key: "none" as const,
      label: t("centre.students.filter_none"),
      count: count((s) => ["none", "expired"].includes(accessState(s))),
      tone: "text-red-600",
    },
    {
      key: "noclass" as const,
      label: t("centre.students.filter_noclass"),
      count: count((s) => !inActiveClass(s.id)),
      tone: "text-amber-600",
    },
  ];
});

const filteredStudents = computed(() => {
  const q = search.value.trim().toLowerCase();
  return students.value.filter((s) => {
    if (
      q &&
      !s.full_name.toLowerCase().includes(q) &&
      !s.email.toLowerCase().includes(q)
    )
      return false;
    const st = accessState(s);
    switch (activeFilter.value) {
      case "active":
        return st === "active" || st === "soon";
      case "soon":
        return st === "soon";
      case "none":
        return st === "none" || st === "expired";
      case "noclass":
        return !inActiveClass(s.id);
      default:
        return true;
    }
  });
});

// ── Pagination ──
const rowsPerPage = ref(8);
const firstRecordIndex = ref(0);
const pagedStudents = computed(() =>
  filteredStudents.value.slice(
    firstRecordIndex.value,
    firstRecordIndex.value + rowsPerPage.value,
  ),
);
function onPageChange(event: { first: number; rows: number }) {
  firstRecordIndex.value = event.first;
  rowsPerPage.value = event.rows;
}
watch([search, activeFilter], () => {
  firstRecordIndex.value = 0;
});

// ── Chargement ──
async function loadStudents() {
  const result = authStore.isDirector
    ? await centerStaffStore.fetchStudentsByCenter()
    : await centerStaffStore.fetchStudentsByBranch();
  if (result.success) {
    students.value = result.students ?? [];
    errorMessage.value = null;
  } else {
    errorMessage.value = result.error || t("common.load_error");
  }
}

async function loadClasses() {
  const result = authStore.isDirector
    ? await trainingSessionsStore.fetchByCenter()
    : await trainingSessionsStore.fetchByBranch();
  if (result.success) computeActiveClasses();
}

async function loadAll() {
  loading.value = true;
  await Promise.all([
    loadStudents(),
    loadClasses(),
    examsStore.catalog.length === 0
      ? examsStore.fetchCatalog()
      : Promise.resolve(),
    plansStore.plans.length === 0 ? plansStore.fetchPlans() : Promise.resolve(),
    salesStore.fetchMySummary(),
  ]);
  loading.value = false;
}

// ══ Activation d'un accès ══
const activationBlocked = computed(() => {
  const s = salesStore.mySummary;
  return !!s && (s.is_blocked || !s.can_activate);
});

const activePlans = computed(() =>
  (plansStore.plans as unknown as PlanLite[])
    .filter((p) => p.is_active !== false)
    .sort((a, b) => a.duration_days - b.duration_days),
);

const showActivation = ref(false);
const selectedStudent = ref<StudentResponse | null>(null);
const activating = ref(false);
const activationError = ref<string | null>(null);
const activationResult = ref<ActivationResponse | null>(null);
const activationForm = ref({ level_id: "", plan_id: "", paid: false });

const selectedPlan = computed(
  () =>
    activePlans.value.find((p) => p.id === activationForm.value.plan_id) ??
    null,
);

// Estimation : le backend prolonge à partir de l'échéance en cours si elle n'est pas passée
const estimatedExpiry = computed(() => {
  const plan = selectedPlan.value;
  if (!plan || !selectedStudent.value) return new Date();
  const current = selectedStudent.value.access_expires_at
    ? new Date(selectedStudent.value.access_expires_at).getTime()
    : 0;
  const start = Math.max(Date.now(), current);
  return new Date(start + plan.duration_days * DAY);
});

// Essai en cours : activation offerte, rien à encaisser
const isTrial = computed(() => !!salesStore.mySummary?.trial_active);

const canActivate = computed(
  () =>
    !!activationForm.value.level_id &&
    !!activationForm.value.plan_id &&
    (activationForm.value.paid || isTrial.value) &&
    !activationBlocked.value,
);

function openActivation(student: StudentResponse) {
  selectedStudent.value = student;
  activationForm.value = {
    level_id: student.target_level_id ?? "",
    plan_id: activePlans.value.length === 1 ? activePlans.value[0]!.id : "",
    paid: false,
  };
  activationError.value = null;
  activationResult.value = null;
  showActivation.value = true;
}

// Réinitialise la case « encaissé » si on change de formule
watch(
  () => activationForm.value.plan_id,
  () => {
    activationForm.value.paid = false;
  },
);

async function handleActivate() {
  if (!selectedStudent.value || !canActivate.value) return;
  activating.value = true;
  activationError.value = null;

  const result = await salesStore.activateAccount({
    student_id: selectedStudent.value.id,
    level_id: activationForm.value.level_id,
    plan_id: activationForm.value.plan_id,
  });

  activating.value = false;

  if (result.success) {
    activationResult.value = result.data;
    toast.add({
      severity: "success",
      summary: t("centre.activation.done_title"),
      detail: t("centre.activation.toast_detail", {
        name: selectedStudent.value.full_name,
        date: formatDate(result.data.access_expires_at),
      }),
      life: 4000,
    });
    await Promise.all([loadStudents(), salesStore.fetchMySummary()]);
  } else {
    activationError.value = result.error;
  }
}

// ══ Activation / désactivation du compte (directeur) ══
async function handleToggleActivation(student: StudentResponse) {
  const result = await centerStaffStore.toggleStudentActivation(student.id);
  if (result.success) {
    await loadStudents();
  } else {
    toast.add({
      severity: "error",
      summary: result.error || t("centre.teachers.toggle_error"),
      life: 4000,
    });
  }
}

onMounted(async () => {
  await loadAll();

  // Arrivée depuis « Nouvel élève » : on ouvre directement l'activation
  const toActivate = route.query.activer as string | undefined;
  if (toActivate) {
    const student = students.value.find((s) => s.id === toActivate);
    if (student) openActivation(student);
    router.replace({ query: {} });
  }
});
</script>
