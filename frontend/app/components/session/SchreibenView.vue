<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">

    <!-- Instructions -->
    <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-sm text-blue-800 font-medium">{{ teil.instructions }}</p>
    </div>

    <div v-for="q in questions" :key="q.id" class="space-y-4">

      <!-- Stimulus (Aufgabe 2 — forum) -->
      <div
        v-if="q.content.stimulus"
        class="bg-gray-50 border border-gray-200 rounded-xl p-5"
      >
        <div class="flex items-center gap-2 mb-3">
          <i class="pi pi-comment text-gray-500"></i>
          <span class="text-sm font-semibold text-gray-700">
            {{ q.content.stimulus_author || 'Commentaire' }}
          </span>
        </div>
        <p class="text-sm text-gray-800 italic">{{ q.content.stimulus }}</p>
      </div>

      <!-- Scénario -->
      <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-amber-800 mb-3">Aufgabe :</p>
        <p class="text-sm text-amber-900">{{ q.content.scenario }}</p>

        <ul v-if="q.content.prompts?.length" class="mt-3 space-y-1">
          <li
            v-for="(prompt, i) in q.content.prompts"
            :key="i"
            class="flex gap-2 text-sm text-amber-800"
          >
            <span class="font-bold">–</span>
            <span>{{ prompt }}</span>
          </li>
        </ul>

        <p v-if="q.content.word_count_target" class="mt-3 text-xs text-amber-700 font-medium">
          Environ {{ q.content.word_count_target }} mots
          <span v-if="q.content.register === 'formell'"> • Ton formel requis</span>
        </p>
      </div>

      <!-- Zone de rédaction -->
      <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden focus-within:border-teal-400 transition-colors">
        <Textarea
          :modelValue="getTextAnswer(q)"
          placeholder="Schreiben Sie hier Ihren Text..."
          class="w-full border-0 resize-none p-5 text-sm focus:ring-0 focus:outline-none"
          :rows="12"
          @update:modelValue="(val) => onInput(q, val)"
        />

        <!-- Pied de zone -->
        <div class="border-t border-gray-100 px-5 py-2 flex items-center justify-between bg-gray-50">
          <span class="text-xs text-gray-400">
            {{ getWordCount(q) }} mot(s)
          </span>
          <div class="flex items-center gap-3">
            <!-- Barre progression mots -->
            <div v-if="q.content.word_count_target" class="flex items-center gap-2">
              <div class="w-24 bg-gray-200 rounded-full h-1">
                <div
                  :class="[
                    'h-1 rounded-full transition-all',
                    getWordCount(q) >= q.content.word_count_target
                      ? 'bg-green-500'
                      : 'bg-teal-400',
                  ]"
                  :style="{
                    width: `${Math.min((getWordCount(q) / q.content.word_count_target) * 100, 100)}%`
                  }"
                />
              </div>
              <span
                :class="[
                  'text-xs font-medium',
                  getWordCount(q) >= q.content.word_count_target
                    ? 'text-green-600'
                    : 'text-gray-400',
                ]"
              >
                / {{ q.content.word_count_target }}
              </span>
            </div>

            <!-- Bouton télécharger PDF -->
            <Button
              icon="pi pi-download"
              label="PDF"
              outlined
              size="small"
              :loading="downloading"
              :disabled="!getTextAnswer(q)"
              v-tooltip.top="'Télécharger mon devoir en PDF'"
              @click="downloadPDF(q)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  teil: any
  questions: any[]
  answers: Record<string, any>
  examName?: string
}>()

const emit = defineEmits<{ answer: [questionId: string, value: any] }>()

const downloading = ref(false)

const getTextAnswer = (q: any): string => {
  return props.answers[q.id]?.user_answer?.text || ''
}

const getWordCount = (q: any): number => {
  const text = getTextAnswer(q)
  return text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0
}

const onInput = (q: any, val: string) => {
  emit('answer', q.id, { text: val })
}

const downloadPDF = async (q: any) => {
  downloading.value = true
  try {
    // Import dynamique jsPDF
    const { jsPDF } = await import('jspdf')

    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

    const pageW = doc.internal.pageSize.getWidth()
    const pageH = doc.internal.pageSize.getHeight()
    const margin = 20
    const maxW = pageW - margin * 2
    let y = margin

    // ── En-tête ──────────────────────────────────────
    doc.setFillColor(15, 118, 110) // teal-600
    doc.rect(0, 0, pageW, 30, 'F')

    doc.setTextColor(255, 255, 255)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    doc.text('DeutschTest', margin, 13)

    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text(props.examName || 'Goethe-ÖSD Zertifikat B1', margin, 22)

    doc.setFontSize(10)
    doc.text(
      new Date().toLocaleDateString('fr-FR', {
        day: '2-digit', month: 'long', year: 'numeric',
      }),
      pageW - margin,
      22,
      { align: 'right' }
    )

    y = 45

    // ── Module ───────────────────────────────────────
    doc.setTextColor(80, 80, 80)
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.text('SCHREIBEN', margin, y)

    y += 6
    doc.setDrawColor(15, 118, 110)
    doc.setLineWidth(0.5)
    doc.line(margin, y, pageW - margin, y)
    y += 8

    // ── Instructions ─────────────────────────────────
    if (props.teil.instructions) {
      doc.setFillColor(239, 246, 255) // blue-50
      doc.setDrawColor(147, 197, 253) // blue-300
      doc.roundedRect(margin, y, maxW, 14, 2, 2, 'FD')

      doc.setTextColor(30, 64, 175) // blue-800
      doc.setFontSize(9)
      doc.setFont('helvetica', 'italic')
      const instrLines = doc.splitTextToSize(props.teil.instructions, maxW - 6)
      doc.text(instrLines, margin + 3, y + 5)
      y += 18
    }

    // ── Scénario ─────────────────────────────────────
    doc.setFillColor(255, 251, 235) // amber-50
    doc.setDrawColor(252, 211, 77)  // amber-300

    const scenarioText = q.content.scenario || ''
    const scenarioLines = doc.splitTextToSize(scenarioText, maxW - 6)
    const prompts = q.content.prompts || []
    const promptLines = prompts.map((p: string) => `– ${p}`)
    const blockH = 10 + (scenarioLines.length * 5) + (prompts.length * 6) + 10

    doc.roundedRect(margin, y, maxW, blockH, 2, 2, 'FD')

    doc.setTextColor(146, 64, 14) // amber-800
    doc.setFontSize(9)
    doc.setFont('helvetica', 'bold')
    doc.text('Aufgabe :', margin + 3, y + 7)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    let textY = y + 13
    doc.text(scenarioLines, margin + 3, textY)
    textY += scenarioLines.length * 5 + 3

    if (prompts.length) {
      promptLines.forEach((line: string) => {
        doc.text(line, margin + 5, textY)
        textY += 6
      })
    }

    if (q.content.word_count_target) {
      doc.setFont('helvetica', 'bold')
      doc.text(`Environ ${q.content.word_count_target} mots`, margin + 3, textY)
    }

    y += blockH + 10

    // ── Réponse de l'étudiant ─────────────────────────
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
      doc.setTextColor(30, 30, 30)
      const answerLines = doc.splitTextToSize(answerText, maxW)

      answerLines.forEach((line: string) => {
        if (y > pageH - 25) {
          doc.addPage()
          y = margin
        }
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

    // ── Compteur de mots ─────────────────────────────
    doc.setDrawColor(200, 200, 200)
    doc.line(margin, y, pageW - margin, y)
    y += 5

    doc.setFont('helvetica', 'italic')
    doc.setFontSize(8)
    doc.setTextColor(120, 120, 120)
    doc.text(
      `${getWordCount(q)} mot(s) rédigé(s)${q.content.word_count_target ? ` / ${q.content.word_count_target} recommandés` : ''}`,
      margin,
      y
    )

    // ── Pied de page ─────────────────────────────────
    doc.setFillColor(245, 245, 245)
    doc.rect(0, pageH - 12, pageW, 12, 'F')
    doc.setTextColor(150, 150, 150)
    doc.setFontSize(7)
    doc.setFont('helvetica', 'normal')
    doc.text('Généré par DeutschTest — deutschtest.com', margin, pageH - 5)
    doc.text(
      `Page 1`,
      pageW - margin,
      pageH - 5,
      { align: 'right' }
    )

    // ── Télécharger ───────────────────────────────────
    const filename = `schreiben_teil${props.teil.teil_number}_${Date.now()}.pdf`
    doc.save(filename)

  } catch (err) {
    console.error('Erreur génération PDF:', err)
  } finally {
    downloading.value = false
  }
}
</script>