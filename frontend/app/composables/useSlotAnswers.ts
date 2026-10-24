/**
 * composables/useSlotAnswers.ts
 *
 * Formats TestDaF « à cases » : les N questions d'un Teil se remplissent par clics
 * (phrases fausses d'un résumé, mots du texte qui diffèrent de l'audio).
 * L'ordre des clics est libre : le backend accepte toute réponse du groupe.
 * Un 2e clic sur un élément marqué vide sa case (réponse "").
 */
import type { Ref } from "vue";

type EmitAnswer = (questionId: string, value: Record<string, any>) => void;

export function useSlotAnswers(
  questions: Ref<any[]>,
  answers: Ref<Record<string, any>>,
  emitAnswer: EmitAnswer,
  // Clé d'un élément marqué, à partir de la réponse enregistrée
  keyOf: (userAnswer: Record<string, any>) => string = (a) =>
    String(a?.answer ?? ""),
) {
  const userAnswer = (q: any): Record<string, any> =>
    answers.value[q.id]?.user_answer || {};

  const isFilled = (q: any) =>
    String(userAnswer(q).answer ?? "").trim() !== "";

  const selectedKeys = computed(() =>
    questions.value.filter(isFilled).map((q) => keyOf(userAnswer(q))),
  );

  const count = computed(() => selectedKeys.value.length);
  const max = computed(() => questions.value.length);
  const isFull = computed(() => count.value >= max.value);

  const isSelected = (key: string) => selectedKeys.value.includes(key);

  /** Retire la marque si l'élément est marqué, sinon le place dans la 1re case libre.
   *  Renvoie false si toutes les cases sont déjà prises. */
  function toggle(key: string, value: Record<string, any>): boolean {
    const holder = questions.value.find(
      (q) => isFilled(q) && keyOf(userAnswer(q)) === key,
    );
    if (holder) {
      emitAnswer(holder.id, { answer: "" });
      return true;
    }
    const free = questions.value.find((q) => !isFilled(q));
    if (!free) return false;
    emitAnswer(free.id, value);
    return true;
  }

  return { selectedKeys, count, max, isFull, isSelected, toggle };
}