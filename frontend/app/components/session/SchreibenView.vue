<template>
  <div class="flex flex-col lg:flex-row h-full min-h-0">

    <!-- ── Colonne gauche : consignes ───────────────── -->
    <div class="lg:w-[45%] bg-white border-r border-gray-100 overflow-y-auto">
      <div class="p-6 space-y-4 max-w-xl mx-auto lg:mx-0">

        <!-- Instructions -->
        <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-blue-800 font-medium">{{ teil.instructions }}</p>
        </div>

        <div v-for="q in questions" :key="q.id" class="space-y-4">

          <!-- Stimulus e-mail (TELC) -->
          <div v-if="q.content.stimulus_email" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div class="bg-gray-50 border-b border-gray-200 px-5 py-3 space-y-1">
              <div class="flex items-center gap-2 text-sm">
                <span class="font-semibold text-gray-500 w-16">Von:</span>
                <span class="text-gray-900 font-medium">{{ q.content.stimulus_email.sender }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm">
                <span class="font-semibold text-gray-500 w-16">Betreff:</span>
                <span class="text-gray-900">{{ q.content.stimulus_email.subject }}</span>
              </div>
            </div>
            <div class="px-5 py-4">
              <p class="text-sm text-gray-800 whitespace-pre-line leading-relaxed">
                {{ q.content.stimulus_email.body }}
              </p>
            </div>
          </div>

          <!-- Stimulus forum (Goethe) -->
          <div v-else-if="q.content.stimulus" class="bg-gray-50 border border-gray-200 rounded-xl p-5">
            <div class="flex items-center gap-2 mb-3">
              <i class="pi pi-comment text-gray-500"></i>
              <span class="text-sm font-semibold text-gray-700">
                {{ q.content.stimulus_author || t('schreiben.comment') }}
              </span>
            </div>
            <p class="text-sm text-gray-800 italic">{{ q.content.stimulus }}</p>
          </div>

          <!-- Scénario -->
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
            <p class="text-sm font-semibold text-amber-800 mb-3">{{ t('schreiben.task') }} :</p>
            <p class="text-sm text-amber-900">{{ q.content.scenario }}</p>
            <ul v-if="q.content.prompts?.length" class="mt-3 space-y-1">
              <li v-for="(prompt, i) in q.content.prompts" :key="i" class="flex gap-2 text-sm text-amber-800">
                <span class="font-bold">–</span>
                <span>{{ prompt }}</span>
              </li>
            </ul>
            <p v-if="q.content.word_count_target" class="mt-3 text-xs text-amber-700 font-medium">
              {{ t('schreiben.approx') }} {{ q.content.word_count_target }} {{ t('schreiben.words') }}
              <span v-if="q.content.register === 'formell'"> • {{ t('schreiben.formal_required') }}</span>
            </p>
          </div>

        </div>
      </div>
    </div>

    <!-- ── Colonne droite : rédaction + correction ─── -->
    <div class="lg:w-[55%] overflow-y-auto bg-gray-50">
      <div class="p-6 space-y-4 max-w-2xl mx-auto">

        <div v-for="q in questions" :key="`input-${q.id}`" class="space-y-4">

          <!-- Zone de rédaction -->
          <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden focus-within:border-teal-400 transition-colors">
            <Textarea
              :modelValue="getTextAnswer(q)"
              :placeholder="t('schreiben.placeholder')"
              class="w-full border-0 resize-none p-5 text-sm focus:ring-0 focus:outline-none"
              :rows="12"
              @update:modelValue="(val) => onInput(q, val)"
            />
            <div class="border-t border-gray-100 px-5 py-2 flex items-center justify-between bg-gray-50">
              <span class="text-xs text-gray-400">{{ getWordCount(q) }} {{ t('schreiben.word_count') }}</span>
              <div class="flex items-center gap-3">
                <!-- Barre progression mots -->
                <div v-if="q.content.word_count_target" class="flex items-center gap-2">
                  <div class="w-24 bg-gray-200 rounded-full h-1">
                    <div
                      :class="['h-1 rounded-full transition-all', getWordCount(q) >= q.content.word_count_target ? 'bg-green-500' : 'bg-teal-400']"
                      :style="{ width: `${Math.min((getWordCount(q) / q.content.word_count_target) * 100, 100)}%` }"
                    />
                  </div>
                  <span :class="['text-xs font-medium', getWordCount(q) >= q.content.word_count_target ? 'text-green-600' : 'text-gray-400']">
                    / {{ q.content.word_count_target }}
                  </span>
                </div>
                <!-- Bouton PDF -->
                <Button
                  icon="pi pi-download"
                  label="PDF"
                  outlined
                  size="small"
                  :loading="downloading"
                  :disabled="!getTextAnswer(q)"
                  v-tooltip.top="t('schreiben.download_pdf')"
                  @click="downloadPDF(q)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- ─── Bouton correction IA ──────────────────────── -->
        <div class="pt-2">

          <!-- État : pas encore soumis -->
          <div v-if="!correctionStore.current && !correctionStore.loading">
            <Button
              :label="t('schreiben.correct_btn')"
              icon="pi pi-sparkles"
              :disabled="!canCorrect"
              class="w-full"
              size="large"
              @click="launchCorrection"
            />
            <p v-if="!canCorrect" class="text-center text-xs text-gray-400 mt-2">
              {{ t('schreiben.correct_hint') }}
            </p>
          </div>

          <!-- État : chargement IA -->
          <div
            v-else-if="correctionStore.loading"
            class="flex flex-col items-center gap-3 py-6 bg-teal-50 border border-teal-200 rounded-xl"
          >
            <i class="pi pi-spin pi-spinner text-teal-600 text-2xl"></i>
            <p class="text-sm font-medium text-teal-700">{{ t('schreiben.correcting') }}</p>
            <p class="text-xs text-teal-500">{{ t('schreiben.correcting_sub') }}</p>
          </div>

          <!-- État : erreur -->
          <div
            v-else-if="correctionStore.error"
            class="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3"
          >
            <i class="pi pi-exclamation-circle text-red-500 mt-0.5"></i>
            <div class="flex-1">
              <p class="text-sm font-medium text-red-700">{{ t('schreiben.error_title') }}</p>
              <p class="text-xs text-red-500 mt-1">{{ correctionStore.error }}</p>
            </div>
            <Button :label="t('schreiben.retry')" size="small" outlined severity="danger" @click="launchCorrection" />
          </div>

          <!-- État : correction disponible -->
          <div
            v-else-if="correctionStore.current"
            class="p-5 bg-white border-2 rounded-xl"
            :class="correctionStore.current.passed ? 'border-green-400' : 'border-orange-400'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm"
                  :class="correctionStore.current.passed ? 'bg-green-500' : 'bg-orange-500'"
                >
                  {{ correctionStore.scorePercentage }}%
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-800">
                    {{ correctionStore.current.passed ? 'Prüfung bestanden ✓' : 'Nicht bestanden' }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ correctionStore.current.overall_score }} / {{ correctionStore.current.max_score }} points
                  </p>
                </div>
              </div>
              <Button
                :label="t('schreiben.see_results')"
                icon="pi pi-arrow-right"
                iconPos="right"
                size="small"
                @click="goToResults"
              />
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCorrectionStore } from '~/stores/correction'

const props = defineProps<{
  teil: any
  questions: any[]
  answers: Record<string, any>
  sessionId: string
  examName?: string
}>()

const emit = defineEmits<{ answer: [questionId: string, value: any] }>()

const { t } = useI18n()
const router = useRouter()
const correctionStore = useCorrectionStore()
const downloading = ref(false)

const getTextAnswer = (q: any): string => props.answers[q.id]?.user_answer?.text || ''

const getWordCount = (q: any): number => {
  const text = getTextAnswer(q)
  return text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0
}

const onInput = (q: any, val: string) => {
  emit('answer', q.id, { text: val })
}

const canCorrect = computed(() => props.questions.some(q => getWordCount(q) > 0))

const launchCorrection = async () => {
  correctionStore.clearCurrent()
  await correctionStore.correct(props.sessionId)
}

const goToResults = () => {
  const route = useRoute()
  const slug = route.params.slug as string
  router.push({
    path: `/dashboard/examens/correction/${props.sessionId}`,
    query: { examId: route.query.examId as string, slug },
  })
}

const downloadPDF = async (q: any) => {
  downloading.value = true
  try {
    const { jsPDF } = await import('jspdf')
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pageW = doc.internal.pageSize.getWidth()
    const pageH = doc.internal.pageSize.getHeight()
    const margin = 20
    const maxW = pageW - margin * 2
    let y = margin

    doc.setFillColor(15, 118, 110)
    doc.rect(0, 0, pageW, 30, 'F')
    doc.setTextColor(255, 255, 255)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    doc.text('DeutschTest', margin, 13)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text(props.examName || 'Goethe-ÖSD Zertifikat B1', margin, 22)
    doc.text(
      new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' }),
      pageW - margin, 22, { align: 'right' },
    )
    y = 45

    doc.setTextColor(80, 80, 80)
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.text('SCHREIBEN', margin, y)
    y += 6
    doc.setDrawColor(15, 118, 110)
    doc.setLineWidth(0.5)
    doc.line(margin, y, pageW - margin, y)
    y += 8

    if (props.teil.instructions) {
      doc.setFillColor(239, 246, 255)
      doc.setDrawColor(147, 197, 253)
      doc.roundedRect(margin, y, maxW, 14, 2, 2, 'FD')
      doc.setTextColor(30, 64, 175)
      doc.setFontSize(9)
      doc.setFont('helvetica', 'italic')
      const instrLines = doc.splitTextToSize(props.teil.instructions, maxW - 6)
      doc.text(instrLines, margin + 3, y + 5)
      y += 18
    }

    doc.setFillColor(255, 251, 235)
    doc.setDrawColor(252, 211, 77)
    const scenarioText = q.content.scenario || ''
    const scenarioLines = doc.splitTextToSize(scenarioText, maxW - 6)
    const prompts = q.content.prompts || []
    const blockH = 10 + scenarioLines.length * 5 + prompts.length * 6 + 10
    doc.roundedRect(margin, y, maxW, blockH, 2, 2, 'FD')
    doc.setTextColor(146, 64, 14)
    doc.setFontSize(9)
    doc.setFont('helvetica', 'bold')
    doc.text('Aufgabe :', margin + 3, y + 7)
    doc.setFont('helvetica', 'normal')
    let textY = y + 13
    doc.text(scenarioLines, margin + 3, textY)
    textY += scenarioLines.length * 5 + 3
    prompts.forEach((p: string) => { doc.text(`– ${p}`, margin + 5, textY); textY += 6 })
    if (q.content.word_count_target) {
      doc.setFont('helvetica', 'bold')
      doc.text(`Environ ${q.content.word_count_target} mots`, margin + 3, textY)
    }
    y += blockH + 10

    doc.setTextColor(30, 30, 30)
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.text('Ma réponse :', margin, y)
    y += 4
    doc.setDrawColor(200, 200, 200)
    doc.line(margin, y, pageW - margin, y)
    y += 8
    const answerText = getTextAnswer(q)
    if (answerText) {
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(10)
      const answerLines = doc.splitTextToSize(answerText, maxW)
      answerLines.forEach((line: string) => {
        if (y > pageH - 25) { doc.addPage(); y = margin }
        doc.text(line, margin, y)
        y += 6
      })
    } else {
      doc.setFont('helvetica', 'italic')
      doc.setTextColor(150, 150, 150)
      doc.setFontSize(10)
      doc.text('(Aucune réponse)', margin, y)
      y += 8
    }
    y += 6

    doc.setDrawColor(200, 200, 200)
    doc.line(margin, y, pageW - margin, y)
    y += 5
    doc.setFont('helvetica', 'italic')
    doc.setFontSize(8)
    doc.setTextColor(120, 120, 120)
    doc.text(
      `${getWordCount(q)} mot(s)${q.content.word_count_target ? ` / ${q.content.word_count_target} recommandés` : ''}`,
      margin, y,
    )

    doc.setFillColor(245, 245, 245)
    doc.rect(0, pageH - 12, pageW, 12, 'F')
    doc.setTextColor(150, 150, 150)
    doc.setFontSize(7)
    doc.setFont('helvetica', 'normal')
    doc.text('Généré par DeutschTest — deutschtest.com', margin, pageH - 5)
    doc.text('Page 1', pageW - margin, pageH - 5, { align: 'right' })

    doc.save(`schreiben_teil${props.teil.teil_number}_${Date.now()}.pdf`)
  } catch (err) {
    console.error('Erreur génération PDF:', err)
  } finally {
    downloading.value = false
  }
}
</script>