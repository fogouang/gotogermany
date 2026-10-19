<!-- pages/admin/exams/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Chiffres ── -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <div
        v-for="s in stats"
        :key="s.label"
        class="rounded-card border border-line bg-card p-4 shadow-soft"
      >
        <div
          class="mb-3 flex size-9 items-center justify-center rounded-leaf"
          :class="s.iconClass"
        >
          <i :class="s.icon" class="text-sm" />
        </div>
        <p
          class="text-2xl font-bold leading-none"
          :class="s.tone ?? 'text-ink'"
        >
          {{ s.value }}
        </p>
        <p class="mt-1.5 text-xs text-muted">{{ s.label }}</p>
      </div>
    </div>

    <!-- ── Filtres ── -->
    <div
      class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
    >
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="p in providerFilters"
          :key="p.key"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            providerFilter === p.key
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30'
          "
          @click="providerFilter = p.key"
        >
          {{ p.label }} · {{ p.count }}
        </button>
        <span class="mx-1 hidden h-7 w-px bg-line sm:block" />
        <button
          type="button"
          class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            onlyMissingAudio
              ? 'border-amber-500/40 bg-amber-500/15 text-amber-600'
              : 'border-line bg-card text-muted hover:border-amber-500/30'
          "
          @click="onlyMissingAudio = !onlyMissingAudio"
        >
          <i class="pi pi-volume-off text-[11px]" />
          Audios manquants · {{ missingAudioCount }}
        </button>
      </div>
      <div class="flex gap-2">
        <Button
          label="Importer des sujets"
          icon="pi pi-upload"
          class="shrink-0"
          @click="openImportJson()"
        />
        <IconField class="w-full lg:w-72">
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="search"
            class="w-full"
            placeholder="Examen ou sujet"
          />
        </IconField>
        <Button
          :icon="allOpen ? 'pi pi-angle-double-up' : 'pi pi-angle-double-down'"
          outlined
          v-tooltip.top="allOpen ? 'Tout replier' : 'Tout déplier'"
          :aria-label="allOpen ? 'Tout replier' : 'Tout déplier'"
          @click="toggleAll"
        />
      </div>
    </div>

    <!-- ── Chargement ── -->
    <div
      v-if="examsStore.loading && examsStore.catalog.length === 0"
      class="space-y-3"
    >
      <div
        v-for="n in 3"
        :key="n"
        class="h-20 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Aucun examen ── -->
    <div
      v-else-if="examsStore.catalog.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-book" />
      </span>
      <p class="text-sm font-medium text-ink">Aucun examen disponible</p>
      <p class="max-w-sm text-xs text-muted">
        Importez vos fichiers sujetN.json : l'examen et le niveau sont créés
        automatiquement.
      </p>
      <Button
        label="Importer des sujets"
        icon="pi pi-upload"
        size="small"
        class="mt-2"
        @click="openImportJson()"
      />
    </div>

    <p
      v-else-if="visibleExams.length === 0"
      class="rounded-card border border-dashed border-line bg-card p-8 text-center text-sm text-muted"
    >
      Aucun examen ou sujet ne correspond.
    </p>

    <!-- ── Examens ── -->
    <div v-else class="space-y-3">
      <article
        v-for="exam in visibleExams"
        :key="exam.id"
        class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <!-- En-tête de l'examen -->
        <div class="flex flex-wrap items-center gap-3 px-4 py-4 sm:px-5">
          <button
            type="button"
            class="flex min-w-0 flex-1 items-center gap-3 text-left"
            :aria-expanded="isOpen(exam.id)"
            @click="toggleExam(exam.id)"
          >
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary"
            >
              <i class="pi pi-book text-sm" />
            </span>
            <div class="min-w-0">
              <p class="truncate font-semibold text-ink">{{ exam.name }}</p>
              <p class="truncate text-xs text-muted">
                {{ exam.provider.toUpperCase() }} · {{ exam.slug }}
              </p>
            </div>
          </button>

          <div class="flex flex-wrap items-center gap-1.5">
            <span
              class="rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted"
            >
              {{ (subjects[exam.id] ?? []).length }} sujet{{
                (subjects[exam.id] ?? []).length > 1 ? "s" : ""
              }}
            </span>
            <span
              v-if="missingAudioOf(exam.id) > 0"
              class="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
            >
              {{ missingAudioOf(exam.id) }} sans audio
            </span>
          </div>

          <div class="flex items-center gap-1">
            <Button
              label="Importer un sujet"
              icon="pi pi-upload"
              size="small"
              @click="openImportJson()"
            />
            <Button
              :icon="
                isOpen(exam.id) ? 'pi pi-chevron-up' : 'pi pi-chevron-down'
              "
              text
              rounded
              size="small"
              severity="secondary"
              :aria-label="isOpen(exam.id) ? 'Replier' : 'Déplier'"
              @click="toggleExam(exam.id)"
            />
          </div>
        </div>

        <!-- Sujets, groupés par niveau -->
        <div v-if="isOpen(exam.id)" class="border-t border-line">
          <div v-if="loadingSubjects[exam.id]" class="space-y-2 p-4">
            <div
              v-for="n in 2"
              :key="n"
              class="h-14 animate-pulse rounded-leaf bg-card-2"
            />
          </div>

          <div
            v-else-if="!(subjects[exam.id] ?? []).length"
            class="flex flex-col items-center gap-2 px-5 py-8 text-center"
          >
            <i class="pi pi-inbox text-2xl text-faint" />
            <p class="text-sm text-muted">
              Aucun sujet. Importez votre premier sujet JSON.
            </p>
          </div>

          <template v-else>
            <section v-for="group in groupedSubjects(exam)" :key="group.level">
              <p
                class="bg-card-2/60 px-5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted"
              >
                Niveau {{ group.level }} · {{ group.items.length }}
              </p>
              <ul class="divide-y divide-line">
                <li
                  v-for="subject in group.items"
                  :key="subject.id"
                  class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 transition-colors hover:bg-card-2/40 sm:px-5"
                >
                  <button
                    type="button"
                    class="flex min-w-0 flex-1 items-center gap-3 text-left"
                    @click="openPreview(exam, subject)"
                  >
                    <span
                      class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-ink text-sm font-bold text-card"
                    >
                      {{ subject.subject_number }}
                    </span>
                    <div class="min-w-0">
                      <p
                        class="flex items-center gap-2 truncate text-sm font-medium text-ink"
                      >
                        <span class="truncate">{{
                          subject.name || `Sujet ${subject.subject_number}`
                        }}</span>
                        <span
                          v-if="subject.is_private"
                          class="inline-flex shrink-0 items-center gap-1 rounded-full bg-ink/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-ink"
                        >
                          <i class="pi pi-lock text-[9px]" />
                          Privé
                        </span>
                      </p>
                      <p
                        class="mt-0.5 flex items-center gap-1 text-xs"
                        :class="
                          subject.has_audio
                            ? 'text-emerald-600'
                            : 'text-amber-600'
                        "
                      >
                        <i
                          :class="
                            subject.has_audio
                              ? 'pi pi-check-circle'
                              : 'pi pi-exclamation-circle'
                          "
                          class="text-[11px]"
                        />
                        {{
                          subject.has_audio
                            ? "Audios associés"
                            : "Audios manquants"
                        }}
                      </p>
                    </div>
                  </button>

                  <div class="flex items-center gap-1">
                    <Button
                      icon="pi pi-eye"
                      text
                      rounded
                      size="small"
                      severity="secondary"
                      v-tooltip.top="'Ouvrir le sujet'"
                      aria-label="Ouvrir le sujet"
                      @click="openPreview(exam, subject)"
                    />
                    <Button
                      icon="pi pi-pencil"
                      text
                      rounded
                      size="small"
                      severity="secondary"
                      v-tooltip.top="'Renommer'"
                      aria-label="Renommer"
                      @click="openEdit(exam, subject)"
                    />
                    <Button
                      :icon="
                        subject.is_private ? 'pi pi-lock' : 'pi pi-lock-open'
                      "
                      text
                      rounded
                      size="small"
                      :severity="subject.is_private ? 'contrast' : 'secondary'"
                      :loading="togglingPrivate === subject.id"
                      v-tooltip.top="
                        subject.is_private
                          ? 'Privé : visible seulement par l\'admin. Cliquer pour le rendre public'
                          : 'Public : visible par les élèves. Cliquer pour le rendre privé'
                      "
                      :aria-label="
                        subject.is_private ? 'Rendre public' : 'Rendre privé'
                      "
                      @click="togglePrivate(subject)"
                    />
                    <Button
                      icon="pi pi-volume-up"
                      text
                      rounded
                      size="small"
                      :severity="subject.has_audio ? 'secondary' : 'warn'"
                      v-tooltip.top="'Supprimer'"
                      aria-label="Supprimer"
                      @click="openDelete(exam, subject)"
                    />
                  </div>
                </li>
              </ul>
            </section>
          </template>
        </div>
      </article>
    </div>

    <!-- ══ Renommer ══ -->
    <Dialog
      v-model:visible="editDialog"
      :header="`Renommer le sujet ${selectedSubject?.subject_number ?? ''}`"
      modal
      :style="{ width: '95vw', maxWidth: '26rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleEdit">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Nom du sujet</label
          >
          <InputText
            v-model="editName"
            class="w-full"
            placeholder="ex. Sujet 1, série A"
            autofocus
          />
        </div>
        <Message v-if="editError" severity="error" :closable="false">{{
          editError
        }}</Message>
      </form>
      <template #footer>
        <Button label="Annuler" text @click="editDialog = false" />
        <Button
          label="Enregistrer"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!editName.trim()"
          @click="handleEdit"
        />
      </template>
    </Dialog>

    <!-- ══ Supprimer ══ -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le sujet ?"
      modal
      :style="{ width: '95vw', maxWidth: '26rem' }"
    >
      <div class="space-y-3">
        <div class="flex items-center gap-3 rounded-leaf bg-card-2 p-3">
          <span
            class="flex size-9 items-center justify-center rounded-leaf bg-ink text-sm font-bold text-card"
          >
            {{ selectedSubject?.subject_number }}
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-ink">
              {{
                selectedSubject?.name ||
                `Sujet ${selectedSubject?.subject_number}`
              }}
            </p>
            <p class="truncate text-xs text-muted">{{ selectedExam?.name }}</p>
          </div>
        </div>
        <p
          class="flex items-start gap-2 rounded-leaf border border-red-500/30 bg-red-500/5 px-3 py-2.5 text-xs text-red-600"
        >
          <i class="pi pi-exclamation-triangle mt-0.5 text-[11px]" />
          Action irréversible : toutes les questions du sujet seront supprimées.
        </p>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button
          label="Supprimer"
          severity="danger"
          icon="pi pi-trash"
          :loading="deleting"
          @click="handleDelete"
        />
      </template>
    </Dialog>

    <!-- ══ Import JSON (plusieurs fichiers, vérification à blanc puis import) ══ -->
    <Dialog
      v-model:visible="importJsonDialog"
      header="Importer des sujets"
      modal
      :style="{ width: '95vw', maxWidth: '40rem' }"
    >
      <div class="space-y-4">
        <p class="text-sm text-muted">
          Ajoutez un ou plusieurs fichiers
          <span class="font-mono text-ink">sujetN.json</span>. L'examen et le
          niveau sont créés s'ils n'existent pas, et le numéro du sujet est lu
          dans le fichier.
        </p>

        <div
          role="button"
          tabindex="0"
          class="cursor-pointer rounded-card border-2 border-dashed p-6 text-center transition-colors"
          :class="
            dragging === 'json'
              ? 'border-primary bg-primary/5'
              : 'border-line hover:border-primary/40'
          "
          @click="jsonInput?.click()"
          @keydown.enter="jsonInput?.click()"
          @dragover.prevent="dragging = 'json'"
          @dragleave="dragging = null"
          @drop.prevent="onJsonDrop"
        >
          <input
            ref="jsonInput"
            type="file"
            accept=".json"
            multiple
            class="hidden"
            @change="onJsonSelect"
          />
          <i class="pi pi-file-import mb-2 block text-3xl text-faint" />
          <p class="text-sm text-muted">
            Glissez les fichiers JSON ici ou
            <span class="font-medium text-primary">parcourez</span>
          </p>
        </div>

        <!-- Fichiers et rapport de chacun -->
        <ul v-if="importRows.length" class="max-h-80 space-y-2 overflow-y-auto">
          <li
            v-for="(row, i) in importRows"
            :key="row.file.name"
            class="rounded-leaf border border-line bg-card-2/40"
          >
            <div class="flex items-center gap-2 px-3 py-2">
              <i :class="rowIcon(row.status)" class="text-sm" />
              <span
                class="min-w-0 flex-1 truncate font-mono text-xs text-ink"
                >{{ row.file.name }}</span
              >
              <span v-if="row.report" class="shrink-0 text-xs text-muted">
                {{ row.report.exam_name }} {{ row.report.cefr_code }} · sujet
                {{ row.report.subject_number }} ·
                {{ row.report.total_questions }} q.
                <span
                  v-if="row.report.action === 'replaced'"
                  class="font-semibold text-amber-600"
                  >· remplacé</span
                >
              </span>
              <button
                v-if="!importBusy"
                type="button"
                class="shrink-0 text-muted hover:text-red-600"
                aria-label="Retirer"
                @click="importRows.splice(i, 1)"
              >
                <i class="pi pi-times text-[11px]" />
              </button>
            </div>
            <p
              v-if="row.error"
              class="whitespace-pre-line border-t border-line px-3 py-2 text-xs text-red-600"
            >
              {{ row.error }}
            </p>
            <details
              v-else-if="row.report?.log?.length"
              class="border-t border-line px-3 py-1.5"
            >
              <summary class="cursor-pointer text-xs text-muted">
                Détail
              </summary>
              <p
                v-for="(line, j) in row.report.log"
                :key="j"
                class="font-mono text-[11px] leading-5 text-ink"
              >
                {{ line }}
              </p>
            </details>
          </li>
        </ul>

        <label class="flex cursor-pointer items-center gap-2 text-sm text-ink">
          <Checkbox
            v-model="importReplace"
            :binary="true"
            input-id="replace"
            @change="resetChecks"
          />
          Remplacer les sujets qui existent déjà (refusé s'ils ont été utilisés
          par des élèves)
        </label>
      </div>
      <template #footer>
        <Button
          label="Fermer"
          text
          :disabled="importBusy"
          @click="closeImportJson"
        />
        <Button
          label="Vérifier"
          icon="pi pi-search"
          outlined
          :loading="importBusy && importPhase === 'check'"
          :disabled="!importRows.length || importBusy"
          @click="runImport(true)"
        />
        <Button
          :label="`Importer ${readyCount} sujet${readyCount > 1 ? 's' : ''}`"
          icon="pi pi-check"
          :loading="importBusy && importPhase === 'import'"
          :disabled="!readyCount || importBusy"
          @click="runImport(false)"
        />
      </template>
    </Dialog>

    <!-- ══ Import audios ══ -->
    <Dialog
      v-model:visible="importAudioDialog"
      :header="`Audios · ${selectedExam?.name ?? ''} · Sujet ${selectedSubject?.subject_number ?? ''}`"
      modal
      :style="{ width: '95vw', maxWidth: '34rem' }"
    >
      <div class="space-y-4">
        <p class="text-sm text-muted">
          Sélectionnez <strong class="text-ink">tous les MP3</strong> du dossier
          audio du
          <strong class="text-ink"
            >sujet {{ selectedSubject?.subject_number }}</strong
          >.
        </p>

        <div
          class="space-y-1 rounded-leaf bg-card-2 p-3 font-mono text-xs text-muted"
        >
          <p class="mb-1.5 font-sans text-xs font-semibold text-ink">
            Noms attendus
          </p>
          <p>
            <span class="text-ink">horen_teil1_audio1.mp3</span> → Teil 1, audio
            1
          </p>
          <p>
            <span class="text-ink">horen_teil2.mp3</span> → Teil 2 (audio long)
          </p>
          <p>
            <span class="text-ink">horen_teil3_audio1.mp3</span> → Teil 3, audio
            1
          </p>
        </div>

        <div
          role="button"
          tabindex="0"
          class="cursor-pointer rounded-card border-2 border-dashed p-6 text-center transition-colors"
          :class="
            audioFiles.length
              ? 'border-emerald-500/50 bg-emerald-500/5'
              : dragging === 'audio'
                ? 'border-primary bg-primary/5'
                : 'border-line hover:border-primary/40'
          "
          @click="audioInput?.click()"
          @keydown.enter="audioInput?.click()"
          @dragover.prevent="dragging = 'audio'"
          @dragleave="dragging = null"
          @drop.prevent="onAudioDrop"
        >
          <input
            ref="audioInput"
            type="file"
            accept=".mp3"
            multiple
            class="hidden"
            @change="onAudioSelect"
          />
          <template v-if="!audioFiles.length">
            <i class="pi pi-volume-up mb-3 block text-3xl text-faint" />
            <p class="text-sm text-muted">
              Glissez les MP3 ici ou
              <span class="font-medium text-primary">parcourez</span>
            </p>
          </template>
          <p v-else class="text-sm font-medium text-emerald-600">
            <i class="pi pi-check-circle mr-1" />
            {{ audioFiles.length }} fichier{{
              audioFiles.length > 1 ? "s" : ""
            }}
            prêt{{ audioFiles.length > 1 ? "s" : "" }}
            <span class="ml-1 font-normal text-muted"
              >· cliquez pour en ajouter</span
            >
          </p>
        </div>

        <!-- Fichiers retenus, avec retrait individuel -->
        <ul v-if="audioFiles.length" class="max-h-40 space-y-1 overflow-y-auto">
          <li
            v-for="(f, i) in audioFiles"
            :key="f.name"
            class="flex items-center gap-2 rounded-leaf bg-card-2 px-3 py-1.5 text-xs"
          >
            <i class="pi pi-volume-up text-[11px] text-muted" />
            <span class="min-w-0 flex-1 truncate font-mono text-ink">{{
              f.name
            }}</span>
            <span class="text-muted"
              >{{ (f.size / 1024 / 1024).toFixed(1) }} Mo</span
            >
            <button
              type="button"
              class="text-muted hover:text-red-600"
              aria-label="Retirer"
              @click.stop="audioFiles.splice(i, 1)"
            >
              <i class="pi pi-times text-[11px]" />
            </button>
          </li>
        </ul>

        <Message v-if="audioError" severity="error" :closable="false">{{
          audioError
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="closeImportAudio" />
        <Button
          label="Associer les audios"
          icon="pi pi-link"
          :loading="importingAudio"
          :disabled="audioFiles.length === 0"
          @click="handleImportAudio"
        />
      </template>
    </Dialog>

    <!-- ══ Résultat ══ -->
    <Dialog
      v-model:visible="resultDialog"
      header="Résultat de l'opération"
      modal
      :style="{ width: '95vw', maxWidth: '34rem' }"
    >
      <div v-if="importResult" class="space-y-4">
        <p
          class="flex items-center gap-2 rounded-leaf px-3 py-2.5 text-sm font-medium"
          :class="
            importResult.success !== false
              ? 'bg-emerald-500/10 text-emerald-600'
              : 'bg-red-500/10 text-red-600'
          "
        >
          <i
            :class="
              importResult.success !== false
                ? 'pi pi-check-circle'
                : 'pi pi-times-circle'
            "
          />
          {{
            importResult.success !== false
              ? "Opération réussie"
              : "Erreur lors de l'opération"
          }}
        </p>

        <div v-if="resultTiles.length" class="grid grid-cols-2 gap-3">
          <div
            v-for="tile in resultTiles"
            :key="tile.label"
            class="rounded-leaf bg-card-2 p-3 text-center"
          >
            <p class="text-2xl font-bold text-ink">{{ tile.value }}</p>
            <p class="text-xs text-muted">{{ tile.label }}</p>
          </div>
        </div>

        <div
          v-if="importResult.log?.length"
          class="max-h-52 overflow-y-auto rounded-leaf bg-card-2 p-3"
        >
          <p
            v-for="(line, i) in importResult.log"
            :key="i"
            class="font-mono text-xs leading-6 text-ink"
          >
            {{ line }}
          </p>
        </div>
      </div>
      <template #footer>
        <Button label="Fermer" @click="resultDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { ExamCatalogResponse } from "#shared/api";

definePageMeta({ layout: "admin" });

const examsStore = useExamsStore();
const toast = useToast();

// ── API config ──
const setupApi = async () => {
  const { OpenAPI } = await import("#shared/api");
  const config = useRuntimeConfig();
  OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
  const tokenCookie = useCookie("access_token");
  OpenAPI.TOKEN = tokenCookie.value ?? undefined;
  return OpenAPI;
};

// ── Sujets par examen ──
const subjects = ref<Record<string, any[]>>({});
const loadingSubjects = ref<Record<string, boolean>>({});

const loadSubjects = async (exam: ExamCatalogResponse) => {
  if (subjects.value[exam.id]) return;
  loadingSubjects.value[exam.id] = true;
  try {
    const { ExamsService } = await import("#shared/api");
    await setupApi();
    const detail = await ExamsService.getExamDetailApiV1ExamsExamIdGet(exam.id);
    const allSubjects: any[] = [];
    for (const level of detail.levels ?? []) {
      // L'endpoint subjects renvoie has_audio
      const levelSubjects =
        await ExamsService.getSubjectsApiV1ExamsLevelsLevelIdSubjectsGet(
          level.id,
        );
      for (const subject of levelSubjects) {
        allSubjects.push({ ...subject, level_cefr: level.cefr_code });
      }
    }
    subjects.value[exam.id] = allSubjects.sort(
      (a, b) => a.subject_number - b.subject_number,
    );
  } catch {
    subjects.value[exam.id] = [];
  } finally {
    loadingSubjects.value[exam.id] = false;
  }
};

const reloadSubjects = async (exam: ExamCatalogResponse) => {
  delete subjects.value[exam.id];
  await loadSubjects(exam);
};

// ── Chiffres ──
const allSubjects = computed(() => Object.values(subjects.value).flat());
const missingAudioCount = computed(
  () => allSubjects.value.filter((s) => !s.has_audio).length,
);
const missingAudioOf = (examId: string) =>
  (subjects.value[examId] ?? []).filter((s) => !s.has_audio).length;

const stats = computed(() => [
  {
    label: "Examens",
    value: examsStore.catalog.length,
    icon: "pi pi-book",
    iconClass: "bg-primary/10 text-primary",
  },
  {
    label: "Sujets",
    value: allSubjects.value.length,
    icon: "pi pi-file",
    iconClass: "bg-sky-500/10 text-sky-600",
  },
  {
    label: "Sujets complets",
    value: allSubjects.value.length - missingAudioCount.value,
    icon: "pi pi-check-circle",
    iconClass: "bg-emerald-500/10 text-emerald-600",
  },
  {
    label: "Sans audio",
    value: missingAudioCount.value,
    tone: missingAudioCount.value ? "text-amber-600" : undefined,
    icon: "pi pi-volume-off",
    iconClass: "bg-amber-500/15 text-amber-600",
  },
]);

// ── Filtres ──
const search = ref("");
const providerFilter = ref("all");
const onlyMissingAudio = ref(false);

const providerFilters = computed(() => {
  const providers = [
    ...new Set(examsStore.catalog.map((e) => e.provider)),
  ].sort();
  return [
    { key: "all", label: "Tous", count: examsStore.catalog.length },
    ...providers.map((p) => ({
      key: p,
      label: p.toUpperCase(),
      count: examsStore.catalog.filter((e) => e.provider === p).length,
    })),
  ];
});

function subjectMatches(subject: any, q: string) {
  if (onlyMissingAudio.value && subject.has_audio) return false;
  if (!q) return true;
  return (subject.name ?? `sujet ${subject.subject_number}`)
    .toLowerCase()
    .includes(q);
}

const visibleExams = computed(() => {
  const q = search.value.trim().toLowerCase();
  return examsStore.catalog.filter((exam) => {
    if (
      providerFilter.value !== "all" &&
      exam.provider !== providerFilter.value
    )
      return false;
    const list = subjects.value[exam.id] ?? [];
    const examNameMatch = !q || exam.name.toLowerCase().includes(q);
    if (onlyMissingAudio.value)
      return list.some((s) => subjectMatches(s, examNameMatch ? "" : q));
    return examNameMatch || list.some((s) => subjectMatches(s, q));
  });
});

// Sujets d'un examen après filtres, groupés par niveau
function groupedSubjects(exam: ExamCatalogResponse) {
  const q = search.value.trim().toLowerCase();
  const examNameMatch = !q || exam.name.toLowerCase().includes(q);
  const list = (subjects.value[exam.id] ?? []).filter((s) =>
    subjectMatches(s, examNameMatch ? "" : q),
  );
  const groups = new Map<string, any[]>();
  for (const s of list) {
    const key = (s.level_cefr ?? "-").toUpperCase();
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(s);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([level, items]) => ({ level, items }));
}

// ── Dépliage ──
const openExams = ref<Set<string>>(new Set());
const isOpen = (id: string) =>
  openExams.value.has(id) || !!search.value.trim() || onlyMissingAudio.value;
const allOpen = computed(
  () =>
    examsStore.catalog.length > 0 &&
    examsStore.catalog.every((e) => openExams.value.has(e.id)),
);

function toggleExam(id: string) {
  const next = new Set(openExams.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  openExams.value = next;
}

function toggleAll() {
  openExams.value = allOpen.value
    ? new Set()
    : new Set(examsStore.catalog.map((e) => e.id));
}

// ── État commun ──
const selectedExam = ref<ExamCatalogResponse | null>(null);
const selectedSubject = ref<any>(null);
const resultDialog = ref(false);
const importResult = ref<any>(null);
const dragging = ref<"json" | "audio" | null>(null);

const resultTiles = computed(() => {
  const r = importResult.value;
  if (!r) return [];
  const tiles: { label: string; value: number | string }[] = [];
  if (r.total_questions)
    tiles.push({ label: "Questions importées", value: r.total_questions });
  if (r.subject_number)
    tiles.push({ label: "Numéro du sujet", value: r.subject_number });
  if (r.questions_updated)
    tiles.push({ label: "Questions mises à jour", value: r.questions_updated });
  if (r.files_processed)
    tiles.push({ label: "Fichiers traités", value: r.files_processed });
  return tiles;
});

const openPreview = (exam: ExamCatalogResponse, subject: any) => {
  navigateTo({
    path: `/admin/exams/${subject.id}`,
    query: { examId: exam.id },
  });
};

// ── Renommer ──
const editDialog = ref(false);
const editName = ref("");
const editError = ref("");
const saving = ref(false);

const openEdit = (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  editName.value = subject.name || `Sujet ${subject.subject_number}`;
  editError.value = "";
  editDialog.value = true;
};

const handleEdit = async () => {
  if (!selectedSubject.value || !editName.value.trim()) return;
  saving.value = true;
  editError.value = "";
  try {
    const { ExamsService } = await import("#shared/api");
    await setupApi();
    await (ExamsService as any).updateSubjectApiV1ExamsSubjectsSubjectIdPatch(
      selectedSubject.value.id,
      {
        name: editName.value.trim(),
      },
    );
    if (selectedExam.value) {
      const subj = (subjects.value[selectedExam.value.id] ?? []).find(
        (s) => s.id === selectedSubject.value.id,
      );
      if (subj) subj.name = editName.value.trim();
    }
    editDialog.value = false;
    toast.add({ severity: "success", summary: "Sujet renommé", life: 3000 });
  } catch (e: any) {
    editError.value = e.body?.detail || "Erreur lors de la sauvegarde";
  } finally {
    saving.value = false;
  }
};

// ── Privé / public ──
// Privé : retiré du catalogue des élèves (seul l'admin le voit).
const togglingPrivate = ref<string | null>(null);

const togglePrivate = async (subject: any) => {
  const next = !subject.is_private;
  togglingPrivate.value = subject.id;
  try {
    const { ExamsService } = await import("#shared/api");
    await setupApi();
    await (ExamsService as any).updateSubjectApiV1ExamsSubjectsSubjectIdPatch(
      subject.id,
      { is_private: next },
    );
    subject.is_private = next;
    toast.add({
      severity: "success",
      summary: next ? "Sujet rendu privé" : "Sujet rendu public",
      detail: next
        ? "Les élèves ne le voient plus."
        : "Il est de nouveau visible par les élèves.",
      life: 3000,
    });
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary:
        typeof e?.body?.detail === "string"
          ? e.body.detail
          : "Erreur lors du changement",
      life: 4000,
    });
  } finally {
    togglingPrivate.value = null;
  }
};

// ── Supprimer ──
const deleteDialog = ref(false);

const deleting = ref(false);

const openDelete = (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!selectedSubject.value) return;
  deleting.value = true;
  try {
    const { ExamsService } = await import("#shared/api");
    await setupApi();
    await ExamsService.deleteSubjectApiV1ExamsSubjectsSubjectIdDelete(
      selectedSubject.value.id,
    );
    if (selectedExam.value) {
      subjects.value[selectedExam.value.id] = (
        subjects.value[selectedExam.value.id] ?? []
      ).filter((s) => s.id !== selectedSubject.value.id);
    }
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Sujet supprimé", life: 3000 });
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary: e.body?.detail || "Erreur",
      life: 4000,
    });
  } finally {
    deleting.value = false;
  }
};

// ── Import JSON : plusieurs fichiers, vérification à blanc puis import ──
type ImportStatus =
  | "pending"
  | "checking"
  | "ready"
  | "error"
  | "importing"
  | "done";
interface ImportRow {
  file: File;
  status: ImportStatus;
  report?: any;
  error?: string;
}

const importJsonDialog = ref(false);
const jsonInput = ref<HTMLInputElement | null>(null);
const importRows = ref<ImportRow[]>([]);
const importReplace = ref(false);
const importBusy = ref(false);
const importPhase = ref<"check" | "import">("check");

const runtimeConfig = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const readyCount = computed(
  () => importRows.value.filter((r) => r.status === "ready").length,
);

function rowIcon(status: ImportStatus) {
  return {
    pending: "pi pi-file text-muted",
    checking: "pi pi-spin pi-spinner text-primary",
    importing: "pi pi-spin pi-spinner text-primary",
    ready: "pi pi-check text-sky-600",
    done: "pi pi-check-circle text-emerald-600",
    error: "pi pi-times-circle text-red-600",
  }[status];
}

const openImportJson = () => {
  importRows.value = [];
  importReplace.value = false;
  importJsonDialog.value = true;
};

const closeImportJson = () => {
  importJsonDialog.value = false;
  importRows.value = [];
};

// Ajoute sans doublon (même nom = remplacé), toujours à revérifier
function addJsonFiles(files: File[]) {
  const json = files.filter((f) => f.name.toLowerCase().endsWith(".json"));
  const byName = new Map(importRows.value.map((r) => [r.file.name, r]));
  json.forEach((f) => byName.set(f.name, { file: f, status: "pending" }));
  importRows.value = [...byName.values()].sort((a, b) =>
    a.file.name.localeCompare(b.file.name),
  );
  if (json.length < files.length) {
    toast.add({
      severity: "warn",
      summary: "Seuls les fichiers .json ont été retenus",
      life: 3000,
    });
  }
}

const onJsonSelect = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files) addJsonFiles(Array.from(input.files));
  input.value = "";
};

const onJsonDrop = (e: DragEvent) => {
  dragging.value = null;
  if (e.dataTransfer?.files) addJsonFiles(Array.from(e.dataTransfer.files));
};

// Changer l'option « Remplacer » invalide les vérifications déjà faites
function resetChecks() {
  importRows.value = importRows.value.map((r) =>
    r.status === "done" ? r : { file: r.file, status: "pending" as const },
  );
}

async function postImport(
  file: File,
  dryRun: boolean,
): Promise<{ ok: true; data: any } | { ok: false; error: string }> {
  const form = new FormData();
  form.append("file", file);
  form.append("replace", String(importReplace.value));
  form.append("dry_run", String(dryRun));
  try {
    const base = runtimeConfig.public.apiBaseUrl || "http://localhost:8001";
    const res = await fetch(`${base}/api/v1/exams/admin/import`, {
      method: "POST",
      headers: tokenCookie.value
        ? { Authorization: `Bearer ${tokenCookie.value}` }
        : {},
      body: form,
    });
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      return {
        ok: false,
        error:
          typeof body?.detail === "string"
            ? body.detail
            : `Erreur ${res.status}`,
      };
    }
    return { ok: true, data: body };
  } catch {
    return { ok: false, error: "Serveur injoignable." };
  }
}

/**
 * dryRun=true : vérifie tous les fichiers en attente, sans rien écrire.
 * dryRun=false : importe pour de bon les fichiers vérifiés, un par un.
 */
async function runImport(dryRun: boolean) {
  importBusy.value = true;
  importPhase.value = dryRun ? "check" : "import";
  const targets = importRows.value.filter((r) =>
    dryRun
      ? r.status === "pending" || r.status === "error"
      : r.status === "ready",
  );

  for (const row of targets) {
    row.status = dryRun ? "checking" : "importing";
    row.error = undefined;
    const res = await postImport(row.file, dryRun);
    if (res.ok) {
      row.report = res.data;
      row.status = dryRun ? "ready" : "done";
    } else {
      row.error = res.error;
      row.status = "error";
    }
  }
  importBusy.value = false;

  if (!dryRun) {
    const done = targets.filter((r) => r.status === "done").length;
    if (done) {
      // Nouveaux examens possibles : on recharge tout
      await examsStore.fetchCatalog();
      subjects.value = {};
      for (const exam of examsStore.catalog) loadSubjects(exam);
      toast.add({
        severity: "success",
        summary: `${done} sujet${done > 1 ? "s" : ""} importé${done > 1 ? "s" : ""}`,
        life: 3000,
      });
    }
  }
}

// ── Import audios ──
const importAudioDialog = ref(false);
const audioFiles = ref<File[]>([]);
const audioInput = ref<HTMLInputElement | null>(null);
const importingAudio = ref(false);
const audioError = ref("");

// Ajoute sans doublon (même nom = remplacé)
function addAudioFiles(files: File[]) {
  const mp3 = files.filter((f) => f.name.toLowerCase().endsWith(".mp3"));
  const byName = new Map(audioFiles.value.map((f) => [f.name, f]));
  mp3.forEach((f) => byName.set(f.name, f));
  audioFiles.value = [...byName.values()].sort((a, b) =>
    a.name.localeCompare(b.name),
  );
  if (mp3.length < files.length)
    audioError.value = "Seuls les fichiers .mp3 ont été retenus.";
}

const openImportAudio = (exam: ExamCatalogResponse, subject: any) => {
  selectedExam.value = exam;
  selectedSubject.value = subject;
  audioFiles.value = [];
  audioError.value = "";
  importAudioDialog.value = true;
};

const closeImportAudio = () => {
  importAudioDialog.value = false;
  audioFiles.value = [];
};

const onAudioSelect = (e: Event) => {
  const i = e.target as HTMLInputElement;
  if (i.files) addAudioFiles(Array.from(i.files));
  i.value = "";
};

const onAudioDrop = (e: DragEvent) => {
  dragging.value = null;
  if (e.dataTransfer?.files) addAudioFiles(Array.from(e.dataTransfer.files));
};

const handleImportAudio = async () => {
  if (!selectedExam.value || !selectedSubject.value || !audioFiles.value.length)
    return;
  importingAudio.value = true;
  audioError.value = "";
  const res = await examsStore.importAudio(
    selectedExam.value.id,
    audioFiles.value,
    selectedSubject.value.subject_number,
  );
  importingAudio.value = false;
  if (res.success) {
    importResult.value = res.data;
    importAudioDialog.value = false;
    resultDialog.value = true;
    const s = (subjects.value[selectedExam.value.id] ?? []).find(
      (x) => x.subject_number === selectedSubject.value.subject_number,
    );
    if (s) s.has_audio = true;
    toast.add({ severity: "success", summary: "Audios associés", life: 3000 });
  } else {
    audioError.value = res.error || "Erreur inconnue";
  }
};

// ── Init ──
onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
  for (const exam of examsStore.catalog) loadSubjects(exam);
});
</script>
