<!-- pages/centre/enseignants.vue -->
<template>
  <div class="space-y-5">
    <!-- ── En-tête ── -->
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <p class="text-sm text-muted">
        {{ t("centre.teachers.count", teachers.length) }}
      </p>
      <Button
        :label="t('centre.teachers.new')"
        icon="pi pi-user-plus"
        class="w-full sm:w-auto"
        @click="openCreateDialog"
      />
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="n in 3"
        :key="n"
        class="h-16 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="teachers.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-user-edit" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{ t("centre.teachers.empty_title") }}
      </p>
      <p class="max-w-sm text-xs text-muted">
        {{ t("centre.teachers.empty_text") }}
      </p>
    </div>

    <!-- ── Liste ── -->
    <ul
      v-else
      class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
    >
      <li
        v-for="teacher in teachers"
        :key="teacher.id"
        class="flex cursor-pointer flex-wrap items-center gap-x-4 gap-y-2 px-5 py-4 transition-colors hover:bg-card-2/60"
        @click="openDetail(teacher)"
      >
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-full text-sm font-bold"
          :class="
            teacher.is_active
              ? 'bg-primary/10 text-primary'
              : 'bg-card-2 text-muted'
          "
        >
          {{ initials(teacher.full_name) }}
        </span>
        <div
          class="min-w-0 flex-1"
          :class="{ 'opacity-60': !teacher.is_active }"
        >
          <p class="truncate font-medium text-ink">{{ teacher.full_name }}</p>
          <p class="truncate text-xs text-muted">{{ teacher.email }}</p>
        </div>

        <!-- Classes en cours -->
        <div class="flex flex-wrap items-center gap-1.5">
          <template v-if="currentClassesOf(teacher.id).length">
            <span
              v-for="c in currentClassesOf(teacher.id).slice(0, 2)"
              :key="c.id"
              class="rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-medium text-muted"
            >
              {{ c.label || c.level_name }}
            </span>
            <span
              v-if="currentClassesOf(teacher.id).length > 2"
              class="rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-medium text-muted"
            >
              +{{ currentClassesOf(teacher.id).length - 2 }}
            </span>
          </template>
          <span
            v-else-if="teacher.is_active"
            class="rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
          >
            {{ t("centre.teachers.no_class") }}
          </span>
        </div>

        <span
          v-if="authStore.isDirector"
          class="inline-flex items-center gap-1.5 text-xs text-muted"
        >
          <i class="pi pi-map-marker text-[11px]" />
          {{ branchName(teacher.branch_id) }}
        </span>
        <span
          class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
          :class="
            teacher.is_active
              ? 'bg-emerald-500/10 text-emerald-600'
              : 'bg-red-500/10 text-red-600'
          "
        >
          {{
            teacher.is_active
              ? t("centre.account.active")
              : t("centre.account.disabled")
          }}
        </span>
        <i class="pi pi-chevron-right text-xs text-muted" />
      </li>
    </ul>

    <!-- ══ Détail enseignant ══ -->
    <Drawer
      v-model:visible="showDetail"
      position="right"
      :style="{ width: '30rem', maxWidth: '100vw' }"
      :header="selectedTeacher?.full_name ?? ''"
    >
      <div v-if="selectedTeacher" class="space-y-6">
        <!-- Identité -->
        <div class="flex items-center gap-3">
          <span
            class="flex size-12 shrink-0 items-center justify-center rounded-full text-base font-bold"
            :class="
              selectedTeacher.is_active
                ? 'bg-primary/10 text-primary'
                : 'bg-card-2 text-muted'
            "
          >
            {{ initials(selectedTeacher.full_name) }}
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm text-muted">
              {{ selectedTeacher.email }}
            </p>
            <div
              class="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted"
            >
              <span
                v-if="authStore.isDirector"
                class="inline-flex items-center gap-1"
              >
                <i class="pi pi-map-marker text-[11px]" />
                {{ branchName(selectedTeacher.branch_id) }}
              </span>
              <span
                class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="
                  selectedTeacher.is_active
                    ? 'bg-emerald-500/10 text-emerald-600'
                    : 'bg-red-500/10 text-red-600'
                "
              >
                {{
                  selectedTeacher.is_active
                    ? t("centre.account.active")
                    : t("centre.account.disabled")
                }}
              </span>
            </div>
          </div>
        </div>

        <!-- Chiffres -->
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-leaf bg-card-2 px-4 py-3">
            <p class="text-xl font-bold text-ink">
              {{ currentClassesOf(selectedTeacher.id).length }}
            </p>
            <p class="text-xs text-muted">
              {{ t("centre.teachers.detail.current_classes") }}
            </p>
          </div>
          <div class="rounded-leaf bg-card-2 px-4 py-3">
            <p class="text-xl font-bold text-ink">
              {{ activeStudentsOf(selectedTeacher.id) }}
            </p>
            <p class="text-xs text-muted">
              {{ t("centre.teachers.detail.active_students") }}
            </p>
          </div>
        </div>

        <!-- Classes -->
        <section>
          <h3 class="mb-2 text-sm font-semibold text-ink">
            {{ t("centre.teachers.detail.classes_title") }}
          </h3>

          <p
            v-if="classesOf(selectedTeacher.id).length === 0"
            class="text-sm text-muted"
          >
            {{ t("centre.teachers.no_class") }}
          </p>

          <ul v-else class="space-y-2">
            <li
              v-for="c in classesOf(selectedTeacher.id)"
              :key="c.id"
              class="flex items-center gap-3 rounded-leaf border border-line px-3 py-2.5"
              :class="{ 'opacity-60': statusOf(c) === 'finished' }"
            >
              <NuxtLink
                :to="localePath(`/centre/sessions/${c.id}`)"
                class="min-w-0 flex-1"
              >
                <p
                  class="truncate text-sm font-medium text-ink hover:text-primary"
                >
                  {{ c.label || c.level_name }}
                </p>
                <p class="truncate text-xs text-muted">
                  {{
                    t(
                      "centre.classes.active_label",
                      { total: c.students.length },
                      activeCount(c),
                    )
                  }}
                </p>
              </NuxtLink>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="statusBadge(c).class"
              >
                {{ statusBadge(c).label }}
              </span>
              <Button
                v-if="statusOf(c) !== 'finished'"
                icon="pi pi-times"
                text
                rounded
                size="small"
                severity="danger"
                v-tooltip.top="t('centre.teachers.detail.unassign')"
                :aria-label="t('centre.teachers.detail.unassign')"
                @click="confirmUnassign(c)"
              />
            </li>
          </ul>
        </section>

        <!-- Attribuer une classe -->
        <section v-if="selectedTeacher.is_active">
          <h3 class="mb-2 text-sm font-semibold text-ink">
            {{ t("centre.teachers.detail.assign_title") }}
          </h3>
          <div v-if="eligibleClasses.length" class="flex gap-2">
            <Select
              v-model="classToAssign"
              :options="eligibleClasses"
              optionLabel="name"
              optionValue="id"
              :placeholder="t('centre.teachers.detail.assign_placeholder')"
              class="min-w-0 flex-1"
              filter
            />
            <Button
              icon="pi pi-plus"
              :aria-label="t('common.add')"
              :disabled="!classToAssign"
              :loading="busy"
              @click="handleAssign"
            />
          </div>
          <p v-else class="text-sm text-muted">
            {{ t("centre.teachers.detail.no_eligible") }}
          </p>
        </section>

        <Message v-if="detailError" severity="error" :closable="false">{{
          detailError
        }}</Message>

        <!-- Compte -->
        <div class="border-t border-line pt-4">
          <Button
            :label="
              selectedTeacher.is_active
                ? t('centre.teachers.deactivate')
                : t('centre.teachers.reactivate')
            "
            :icon="
              selectedTeacher.is_active ? 'pi pi-ban' : 'pi pi-check-circle'
            "
            text
            size="small"
            :severity="selectedTeacher.is_active ? 'danger' : 'success'"
            @click="confirmToggleActive(selectedTeacher)"
          />
        </div>
      </div>
    </Drawer>

    <!-- ── Création ── -->
    <Dialog
      v-model:visible="showCreateDialog"
      :header="t('centre.teachers.new')"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleCreate">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("auth.full_name") }} <span class="text-red-600">*</span>
          </label>
          <InputText
            v-model="form.full_name"
            class="w-full"
            :placeholder="t('centre.form.name_placeholder')"
          />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("auth.email") }} <span class="text-red-600">*</span>
            </label>
            <InputText
              v-model="form.email"
              type="email"
              class="w-full"
              :placeholder="t('centre.form.email_placeholder')"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">{{
              t("profile.phone")
            }}</label>
            <InputText
              v-model="form.phone"
              class="w-full"
              placeholder="+237 6XX XXX XXX"
            />
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.form.temp_password") }}
            <span class="text-red-600">*</span>
          </label>
          <div class="flex gap-2">
            <Password
              v-model="form.password"
              class="flex-1"
              inputClass="w-full"
              :feedback="false"
              toggleMask
              :placeholder="t('centre.form.password_placeholder')"
            />
            <Button
              type="button"
              icon="pi pi-refresh"
              outlined
              v-tooltip.top="t('centre.form.generate_password')"
              :aria-label="t('centre.form.generate_password')"
              @click="form.password = genererMotDePasse()"
            />
          </div>
        </div>
        <!-- Succursale : directeur uniquement. La secrétaire crée toujours
             dans sa propre succursale (géré côté backend). -->
        <div v-if="authStore.isDirector">
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.form.branch") }} <span class="text-red-600">*</span>
          </label>
          <Select
            v-model="form.branch_id"
            :options="branches"
            optionLabel="name"
            optionValue="id"
            :placeholder="t('centre.form.branch_placeholder')"
            class="w-full"
          />
        </div>
        <Message v-if="createError" severity="error" :closable="false">{{
          createError
        }}</Message>
      </form>
      <template #footer>
        <Button
          :label="t('common.cancel')"
          text
          @click="showCreateDialog = false"
        />
        <Button
          :label="t('common.create')"
          icon="pi pi-check"
          :loading="creating"
          @click="handleCreate"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { UserAdminResponse, BranchResponse } from "#shared/api";
import type { NormalizedTrainingSession } from "~/stores/trainingSessions";

definePageMeta({ layout: "centre", watermark: "Lehrkräfte" });

const { t } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const trainingSessionsStore = useTrainingSessionsStore();
const confirm = useConfirm();
const toast = useToast();

const loading = ref(true);
const teachers = ref<UserAdminResponse[]>([]);
const branches = ref<BranchResponse[]>([]);
const sessions = ref<NormalizedTrainingSession[]>([]);
const errorMessage = ref<string | null>(null);

const showCreateDialog = ref(false);
const creating = ref(false);
const createError = ref<string | null>(null);
const formVide = () => ({
  full_name: "",
  email: "",
  phone: "",
  password: "",
  branch_id: "",
});
const form = ref(formVide());

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function branchName(branchId: string | null) {
  if (!branchId) return "-";
  return branches.value.find((b) => b.id === branchId)?.name ?? "-";
}

// ── Classes ──
type Statut = "upcoming" | "ongoing" | "finished";

function statusOf(session: NormalizedTrainingSession): Statut {
  const now = Date.now();
  if (session.end_date && new Date(session.end_date).getTime() < now)
    return "finished";
  if (new Date(session.start_date).getTime() > now) return "upcoming";
  return "ongoing";
}

function statusBadge(session: NormalizedTrainingSession) {
  const s = statusOf(session);
  if (s === "finished")
    return {
      label: t("centre.classes.status.finished"),
      class: "bg-card-2 text-muted",
    };
  if (s === "upcoming")
    return {
      label: t("centre.classes.status.upcoming"),
      class: "bg-sky-500/10 text-sky-600",
    };
  return {
    label: t("centre.classes.status.ongoing"),
    class: "bg-emerald-500/10 text-emerald-600",
  };
}

function activeCount(session: NormalizedTrainingSession) {
  return session.students.filter((s) => !s.ended_at).length;
}

const ORDRE: Record<Statut, number> = { ongoing: 0, upcoming: 1, finished: 2 };

// Toutes les classes de l'enseignant : en cours, à venir, puis terminées
function classesOf(teacherId: string) {
  return sessions.value
    .filter((s) => s.teachers.some((x) => x.teacher_id === teacherId))
    .sort(
      (a, b) =>
        ORDRE[statusOf(a)] - ORDRE[statusOf(b)] ||
        new Date(b.start_date).getTime() - new Date(a.start_date).getTime(),
    );
}

// Classes non terminées
function currentClassesOf(teacherId: string) {
  return classesOf(teacherId).filter((s) => statusOf(s) !== "finished");
}

function activeStudentsOf(teacherId: string) {
  return currentClassesOf(teacherId).reduce(
    (sum, s) => sum + activeCount(s),
    0,
  );
}

// ══ Détail ══
const showDetail = ref(false);
const selectedTeacher = ref<UserAdminResponse | null>(null);
const classToAssign = ref("");
const busy = ref(false);
const detailError = ref<string | null>(null);

function openDetail(teacher: UserAdminResponse) {
  selectedTeacher.value = teacher;
  classToAssign.value = "";
  detailError.value = null;
  showDetail.value = true;
}

// Classes non terminées, de la même succursale que l'enseignant, où il n'est pas déjà
const eligibleClasses = computed(() => {
  const tch = selectedTeacher.value;
  if (!tch) return [];
  return sessions.value
    .filter((s) => statusOf(s) !== "finished")
    .filter((s) => !tch.branch_id || s.branch_id === tch.branch_id)
    .filter((s) => !s.teachers.some((x) => x.teacher_id === tch.id))
    .map((s) => ({
      id: s.id,
      name: s.label ? `${s.label} · ${s.level_name}` : s.level_name,
    }));
});

async function refreshSessions() {
  const result = authStore.isDirector
    ? await trainingSessionsStore.fetchByCenter()
    : await trainingSessionsStore.fetchByBranch();
  if (result.success) sessions.value = trainingSessionsStore.sessions;
}

async function handleAssign() {
  if (!selectedTeacher.value || !classToAssign.value) return;
  busy.value = true;
  detailError.value = null;
  const result = await trainingSessionsStore.assignTeacher(
    classToAssign.value,
    {
      teacher_id: selectedTeacher.value.id,
    },
  );
  if (result.success) {
    classToAssign.value = "";
    await refreshSessions();
  } else {
    detailError.value = result.error || t("centre.classes.assign_error");
  }
  busy.value = false;
}

function confirmUnassign(session: NormalizedTrainingSession) {
  const tch = selectedTeacher.value;
  if (!tch) return;
  confirm.require({
    header: t("centre.teachers.detail.unassign"),
    message: t("centre.teachers.detail.unassign_confirm", {
      name: tch.full_name,
      className: session.label || session.level_name,
    }),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: t("centre.teachers.detail.unassign"),
    rejectLabel: t("common.cancel"),
    acceptClass: "p-button-danger",
    accept: async () => {
      busy.value = true;
      detailError.value = null;
      const result = await trainingSessionsStore.removeTeacher(
        session.id,
        tch.id,
      );
      if (result.success) {
        await refreshSessions();
      } else {
        detailError.value = result.error || t("centre.classes.remove_error");
      }
      busy.value = false;
    },
  });
}

// ── Activation / désactivation ──
function confirmToggleActive(teacher: UserAdminResponse) {
  const desactiver = teacher.is_active;
  confirm.require({
    header: desactiver
      ? t("centre.teachers.deactivate_title")
      : t("centre.teachers.reactivate_title"),
    message: desactiver
      ? t("centre.teachers.deactivate_message", { name: teacher.full_name })
      : t("centre.teachers.reactivate_message", { name: teacher.full_name }),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: desactiver
      ? t("centre.teachers.deactivate")
      : t("centre.teachers.reactivate"),
    rejectLabel: t("common.cancel"),
    acceptClass: desactiver ? "p-button-danger" : undefined,
    accept: async () => {
      const result = await centerStaffStore.toggleTeacherActive(teacher.id);
      if (result.success) {
        await loadData();
        // Garde le panneau à jour avec le nouvel état du compte
        if (selectedTeacher.value?.id === teacher.id) {
          selectedTeacher.value =
            teachers.value.find((x) => x.id === teacher.id) ?? null;
        }
      } else {
        toast.add({
          severity: "error",
          summary: result.error || t("centre.teachers.toggle_error"),
          life: 4000,
        });
      }
    },
  });
}

// ── Chargement ──
async function loadData() {
  loading.value = true;
  const [teacherResult, branchResult] = await Promise.all([
    centerStaffStore.fetchTeachers(),
    // Les succursales ne servent qu'au directeur (colonne + choix dans le formulaire)
    authStore.isDirector
      ? centerStaffStore.fetchMyBranches()
      : Promise.resolve(null),
    refreshSessions(),
  ]);

  if (teacherResult.success) {
    teachers.value = teacherResult.teachers ?? [];
    errorMessage.value = null;
  } else {
    errorMessage.value = teacherResult.error || t("common.load_error");
  }

  if (branchResult?.success) {
    branches.value = branchResult.branches ?? [];
  }

  loading.value = false;
}

// ── Création ──
function openCreateDialog() {
  form.value = formVide();
  // Une seule succursale : on la présélectionne
  if (branches.value.length === 1) form.value.branch_id = branches.value[0]!.id;
  createError.value = null;
  showCreateDialog.value = true;
}

async function handleCreate() {
  const f = form.value;
  if (
    !f.full_name.trim() ||
    !f.email.trim() ||
    !f.password ||
    (authStore.isDirector && !f.branch_id)
  ) {
    createError.value = t("centre.form.required_fields");
    return;
  }
  if (f.password.length < 8) {
    createError.value = t("centre.form.password_min");
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await centerStaffStore.createTeacher({
    email: f.email.trim(),
    password: f.password,
    full_name: f.full_name.trim(),
    phone: f.phone.trim() || null,
    branch_id: authStore.isDirector ? f.branch_id : null,
  });

  creating.value = false;

  if (result.success) {
    showCreateDialog.value = false;
    toast.add({
      severity: "success",
      summary: t("centre.form.account_created"),
      detail: t("centre.form.credentials", {
        email: f.email.trim(),
        password: f.password,
      }),
      life: 10000,
    });
    await loadData();
  } else {
    createError.value = result.error || t("centre.form.create_error");
  }
}

onMounted(loadData);
</script>
