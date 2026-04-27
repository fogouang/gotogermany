<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="mx-auto mb-4 w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
          <i class="pi pi-check text-4xl text-green-600"></i>
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Examen terminé !</h1>
        <p class="text-lg text-gray-600">Voici vos résultats</p>
      </div>

      <!-- Score global -->
      <Card class="shadow-xl mb-8">
        <template #content>
          <div class="text-center py-8">
            <div class="mb-6">
              <div class="text-6xl font-bold mb-2" :class="scoreColorClass">
                {{ Math.round(score.percentage) }}%
              </div>
              <p class="text-gray-600 text-lg">
                {{ score.totalScore }} / {{ score.maxScore }} points
              </p>
            </div>

            <div class="flex justify-center gap-8 mb-6">
              <div class="text-center">
                <Tag 
                  :value="isPassed ? 'RÉUSSI' : 'ÉCHOUÉ'" 
                  :severity="isPassed ? 'success' : 'danger'"
                  class="!text-lg !px-6 !py-2 !font-bold"
                />
                <p class="text-sm text-gray-500 mt-2">Seuil: 60%</p>
              </div>
            </div>

            <ProgressBar
              :value="score.percentage"
              :showValue="false"
              :pt="{
                root: { class: '!h-4 !rounded-full' },
                value: { class: isPassed ? '!bg-green-500' : '!bg-red-500' }
              }"
            />
          </div>
        </template>
      </Card>

      <!-- Résultats par module -->
      <div class="space-y-4 mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Détails par module</h2>

        <Card
          v-for="(detail, moduleSlug) in score.details"
          :key="moduleSlug"
          class="shadow-lg"
        >
          <template #content>
            <div class="flex items-center justify-between gap-4">
              <!-- Icône module -->
              <div class="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center shrink-0">
                <i :class="getModuleIcon(moduleSlug)" class="text-2xl text-indigo-600"></i>
              </div>

              <!-- Détails -->
              <div class="flex-1">
                <h3 class="text-xl font-bold text-gray-900 mb-2 capitalize">
                  {{ getModuleName(moduleSlug) }}
                </h3>
                <div class="flex items-center gap-4">
                  <span class="text-sm text-gray-600">
                    {{ detail.score }} / {{ detail.max }} points
                  </span>
                  <ProgressBar
                    :value="detail.percentage"
                    :showValue="false"
                    class="flex-1 max-w-xs !h-2 !rounded-full"
                    :pt="{
                      value: { class: getProgressColor(detail.percentage) }
                    }"
                  />
                </div>
              </div>

              <!-- Score & badge -->
              <div class="text-right shrink-0">
                <div class="text-3xl font-bold" :class="getScoreColor(detail.percentage)">
                  {{ Math.round(detail.percentage) }}%
                </div>
                <i
                  class="text-2xl mt-2"
                  :class="
                    detail.percentage >= 60
                      ? 'pi pi-check-circle text-green-500'
                      : 'pi pi-times-circle text-red-500'
                  "
                ></i>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Actions -->
      <div class="flex flex-wrap gap-4 justify-center mb-8">
        <Button
          label="Voir les réponses"
          icon="pi pi-eye"
          outlined
          @click="$emit('view-answers')"
        />
        <Button
          label="Refaire l'examen"
          icon="pi pi-refresh"
          outlined
          @click="$emit('retake-exam')"
        />
        <Button
          label="Retour à l'accueil"
          icon="pi pi-home"
          @click="$emit('go-home')"
        />
      </div>

      <!-- Conseils -->
      <Card v-if="!isPassed && weakModules.length > 0" class="shadow-lg bg-orange-50">
        <template #content>
          <div class="flex items-start gap-4">
            <i class="pi pi-info-circle text-orange-600 text-2xl mt-1 shrink-0"></i>
            <div class="flex-1">
              <h3 class="font-bold text-gray-900 mb-3">Conseils pour progresser</h3>
              <ul class="space-y-2 text-gray-700">
                <li
                  v-for="module in weakModules"
                  :key="module"
                  class="flex items-start gap-2"
                >
                  <i class="pi pi-arrow-right text-orange-600 mt-1 shrink-0"></i>
                  <span>
                    Travaillez davantage le module
                    <strong>{{ getModuleName(module) }}</strong>
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ModuleDetail {
  score: number;
  max: number;
  percentage: number;
}

interface ScoreResult {
  totalScore: number;
  maxScore: number;
  percentage: number;
  details: Record<string, ModuleDetail>;
}

const props = defineProps<{
  score: ScoreResult;
}>();

defineEmits(['view-answers', 'retake-exam', 'go-home']);

const isPassed = computed(() => props.score.percentage >= 60);

const scoreColorClass = computed(() => {
  if (props.score.percentage >= 80) return 'text-green-600';
  if (props.score.percentage >= 60) return 'text-yellow-600';
  return 'text-red-600';
});

const weakModules = computed(() => {
  return Object.entries(props.score.details)
    .filter(([_, detail]) => detail.percentage < 60)
    .map(([slug, _]) => slug);
});

const getModuleName = (slug: string) => {
  const names: Record<string, string> = {
    lesen: 'Lesen',
    horen: 'Hören',
    schreiben: 'Schreiben',
    sprechen: 'Sprechen',
  };
  return names[slug] || slug;
};

const getModuleIcon = (slug: string) => {
  const icons: Record<string, string> = {
    lesen: 'pi pi-book',
    horen: 'pi pi-volume-up',
    schreiben: 'pi pi-pencil',
    sprechen: 'pi pi-comments',
  };
  return icons[slug] || 'pi pi-circle';
};

const getScoreColor = (percentage: number) => {
  if (percentage >= 80) return 'text-green-600';
  if (percentage >= 60) return 'text-yellow-600';
  return 'text-red-600';
};

const getProgressColor = (percentage: number) => {
  if (percentage >= 80) return '!bg-green-500';
  if (percentage >= 60) return '!bg-yellow-500';
  return '!bg-red-500';
};
</script>