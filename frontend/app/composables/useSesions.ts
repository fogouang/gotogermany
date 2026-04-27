/**
 * composables/useSession.ts
 *
 * Composable pour la gestion d'une session d'examen.
 * Encapsule la logique timer, navigation, soumission.
 */
export const useSession = () => {
  const sessionStore = useSessionStore();
  const router = useRouter();

  let timerInterval: ReturnType<typeof setInterval> | null = null;

  // ── Timer ────────────────────────────────────────────

  const startTimer = () => {
    stopTimer();
    timerInterval = setInterval(() => {
      sessionStore.decrementTimer();
      if (sessionStore.timeRemaining === 0) {
        stopTimer();
        handleTimeUp();
      }
    }, 1000);
  };

  const stopTimer = () => {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  };

  const handleTimeUp = async () => {
    await submitSession();
  };

  // ── Navigation ───────────────────────────────────────

  const nextQuestion = () => sessionStore.nextQuestion();

  const previousQuestion = () => sessionStore.previousQuestion();

  const goToQuestion = (index: number) => sessionStore.goToQuestion(index);

  // ── Réponses ─────────────────────────────────────────

  const saveAnswer = async (
    questionId: string,
    userAnswer: Record<string, any>,
  ) => {
    return await sessionStore.saveAnswer(questionId, userAnswer);
  };

  // ── Démarrage ────────────────────────────────────────

  const startSession = async (examId: string, subjectId?: string) => {
    const result = await sessionStore.startSession(examId, subjectId);
    if (result.success) startTimer();
    return result;
  };

  // ── Soumission ───────────────────────────────────────

  const submitSession = async () => {
    stopTimer();
    const result = await sessionStore.submitSession();
    if (result.success) {
      const slug = useRoute().params.slug as string;
      navigateTo({
        path: `/dashboard/examens/${slug}/result`,
        query: { sessionId: sessionStore.sessionId },
      });
    }
    return result;
  };

  // ── Exit ─────────────────────────────────────────────

  const exitSession = () => {
    stopTimer();
    sessionStore.resetSession();
    router.push("/dashboard/examens");
  };

  // ── Cleanup ──────────────────────────────────────────

  const cleanup = () => stopTimer();

  return {
    // State
    sessionStore,
    currentQuestion: computed(() => sessionStore.currentQuestion),
    currentAnswer: computed(() => sessionStore.currentAnswer),
    progress: computed(() => sessionStore.progress),
    timeRemainingFormatted: computed(() => sessionStore.timeRemainingFormatted),
    isLastQuestion: computed(() => sessionStore.isLastQuestion),
    isFirstQuestion: computed(() => sessionStore.isFirstQuestion),
    isAnswered: (questionId: string) => sessionStore.isAnswered(questionId),

    // Actions
    startSession,
    saveAnswer,
    submitSession,
    exitSession,
    nextQuestion,
    previousQuestion,
    goToQuestion,
    startTimer,
    stopTimer,
    cleanup,
  };
};
