<!-- components/start-deutsch/SprechenDuoNegotiationQuestion.vue -->
<!--
  A2 Sprechen Teil 3 : négociation de rendez-vous à partir de deux
  agendas partiels croisés (ex. trouver un créneau libre commun pour
  acheter un cadeau à un ami). Purement présentationnel, pas de
  correction en V1.

  Choix de rendu : à l'examen réel, chaque candidat ne voit que son
  propre agenda. Ici l'étudiant s'entraîne seul, sans binôme en face,
  donc on affiche les deux agendas côte à côte sur le même axe horaire
  pour l'aider à repérer le créneau commun et formuler la négociation.
  content = {
    scenario: string,
    schedule_a: Record<string, string>,  // "7:00" -> "lange schlafen"
    schedule_b: Record<string, string>,
  }
-->
<template>
  <div class="space-y-4">
    <div class="rounded-card border border-line bg-card p-4 shadow-soft">
      <p class="text-base font-semibold text-ink">{{ question.content.scenario }}</p>
    </div>

    <div class="overflow-x-auto rounded-card border border-line bg-card shadow-soft">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-line bg-card-2 text-xs font-semibold uppercase tracking-wide text-muted">
            <th class="w-20 px-3 py-2 text-left">{{ t("start_deutsch.sprechen.time_label") }}</th>
            <th class="px-3 py-2 text-left">{{ t("start_deutsch.sprechen.participant_a_label") }}</th>
            <th class="px-3 py-2 text-left">{{ t("start_deutsch.sprechen.participant_b_label") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="time in timeSlots"
            :key="time"
            class="border-b border-line last:border-0 even:bg-card-2/50"
          >
            <td class="px-3 py-2 font-mono text-xs text-faint">{{ time }}</td>
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

// Union des créneaux des deux agendas, triés chronologiquement : les clés
// peuvent être "7:00" ou "07:00", donc on trie sur la valeur numérique.
const timeSlots = computed(() => {
  const allTimes = new Set([...Object.keys(scheduleA.value), ...Object.keys(scheduleB.value)]);
  return [...allTimes].sort((a, b) => parseFloat(a.replace(":", ".")) - parseFloat(b.replace(":", ".")));
});
</script>