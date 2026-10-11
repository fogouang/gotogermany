<!-- components/start-deutsch/SprechenDuoNegotiationQuestion.vue -->
<!--
  A2 Sprechen Teil 3 — négociation de rendez-vous à partir de deux
  agendas partiels croisés (ex. trouver un créneau libre commun pour
  acheter un cadeau à un ami). Purement présentationnel — pas de
  correction en V1.

  Choix de rendu : contrairement à l'examen réel (chaque candidat ne
  voit QUE son propre agenda, l'autre lui est caché), on affiche les
  deux côte à côte alignés sur le même axe horaire — un seul étudiant
  s'entraîne seul ici (pas de vrai binôme en face), donc voir les deux
  agendas aide à repérer le créneau commun et formuler la négociation
  à l'oral, plutôt que de bloquer l'exercice faute de partenaire réel.
  content = {
    scenario: string,
    schedule_a: Record<string, string>,  // "7:00" -> "lange schlafen"
    schedule_b: Record<string, string>,
  }
-->
<template>
  <div class="space-y-4">
    <div class="question-container">
      <p class="text-base font-semibold text-ink">{{ question.content.scenario }}</p>
    </div>

    <div class="question-container overflow-hidden p-0">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-line bg-hover/60 text-xs font-semibold uppercase tracking-wide text-ink-secondary">
            <th class="w-20 px-3 py-2 text-left">{{ t("start_deutsch.sprechen.time_label") }}</th>
            <th class="px-3 py-2 text-left">{{ t("start_deutsch.sprechen.participant_a_label") }}</th>
            <th class="px-3 py-2 text-left">{{ t("start_deutsch.sprechen.participant_b_label") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="time in timeSlots"
            :key="time"
            class="border-b border-line last:border-0 even:bg-hover/20"
          >
            <td class="px-3 py-2 font-mono text-xs text-ink-tertiary">{{ time }}</td>
            <td class="px-3 py-2 text-ink">
              <span v-if="scheduleA[time]" class="italic">{{ scheduleA[time] }}</span>
            </td>
            <td class="px-3 py-2 text-ink">
              <span v-if="scheduleB[time]" class="italic">{{ scheduleB[time] }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  question: {
    id: string;
    question_number: number;
    content: {
      scenario: string;
      schedule_a: Record<string, string>;
      schedule_b: Record<string, string>;
    };
  };
}

const props = defineProps<Props>();
const { t } = useI18n();

const scheduleA = computed(() => props.question.content.schedule_a ?? {});
const scheduleB = computed(() => props.question.content.schedule_b ?? {});

// Union des créneaux des deux agendas, triés chronologiquement — les
// clés peuvent être "7:00" ou "07:00" selon la génération, donc on
// normalise sur la valeur numérique pour trier plutôt que sur la string.
const timeSlots = computed(() => {
  const allTimes = new Set([...Object.keys(scheduleA.value), ...Object.keys(scheduleB.value)]);
  return [...allTimes].sort((a, b) => parseFloat(a.replace(":", ".")) - parseFloat(b.replace(":", ".")));
});
</script>