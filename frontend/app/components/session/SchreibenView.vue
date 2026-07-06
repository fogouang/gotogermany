<template>
  <div class="flex flex-col lg:flex-row h-full min-h-0">
    <!-- ── Colonne gauche : consignes ───────────────── -->
    <div class="lg:w-[45%] bg-white border-r border-gray-100 overflow-y-auto">
      <div class="p-6 space-y-4 max-w-xl mx-auto lg:mx-0">
        <!-- Instructions -->
        <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-blue-800 font-medium">
            {{ teil.instructions }}
          </p>
        </div>

        <!-- ✅ Sprachliche Mittel — commun à toutes les questions de ce Teil -->
        <SprachlicheMittelPanel :mittel-key="mittelKey" />

        <div v-for="q in questions" :key="q.id" class="space-y-4">
          <!-- ══ CAS 1 : choix entre 2 thèmes de lettre (TELC/ÖSD B2) ══ -->
          <template v-if="q.content.themes">
            <div v-if="!selectedThemes[String(q.id)]" class="space-y-3">
              <p class="text-sm font-semibold text-gray-700">
                Choisissez un thème :
              </p>
              <div class="grid grid-cols-1 gap-3">
                <button
                  v-for="(theme, key) in q.content.themes"
                  :key="key"
                  class="p-4 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-teal-400 transition-colors"
                  @click="selectTheme(String(q.id), String(key))"
                >
                  <p class="font-semibold text-gray-900 mb-1">
                    Thema {{ key }} : {{ theme.titel }}
                  </p>
                  <p class="text-xs text-gray-500 line-clamp-2">
                    {{ theme.stimulus }}
                  </p>
                </button>
              </div>
            </div>

            <template v-else>
              <div class="flex items-center justify-between mb-2">
                <p class="text-sm font-semibold text-gray-700">
                  Thema {{ selectedThemes[String(q.id)] }} :
                  {{ q.content.themes[selectedThemes[String(q.id)]!]?.titel }}
                </p>
                <button
                  class="text-xs text-gray-400 hover:text-gray-600"
                  @click="selectedThemes[String(q.id)] = null"
                >
                  Changer de thème
                </button>
              </div>

              <div class="bg-gray-50 border border-gray-200 rounded-xl p-5">
                <p class="text-sm text-gray-800 italic mb-3">
                  {{
                    q.content.themes[selectedThemes[String(q.id)]!]?.stimulus
                  }}
                </p>
              </div>

              <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                <p class="text-sm font-semibold text-amber-800 mb-3">
                  {{ t("schreiben.task") }} :
                </p>
                <ul class="space-y-1">
                  <li
                    v-for="(prompt, i) in q.content.themes[
                      selectedThemes[String(q.id)]!
                    ]?.prompts"
                    :key="i"
                    class="flex gap-2 text-sm text-amber-800"
                  >
                    <span class="font-bold">–</span>
                    <span>{{ prompt }}</span>
                  </li>
                </ul>
                <p
                  v-if="q.content.word_count_target"
                  class="mt-3 text-xs text-amber-700 font-medium"
                >
                  {{ t("schreiben.approx") }} {{ q.content.word_count_target }}
                  {{ t("schreiben.words") }}
                </p>
              </div>
            </template>
          </template>

          <!-- ══ CAS 2 : choix entre 2 variantes d'opinion (ÖSD) ══ -->
          <template v-else-if="q.content.opinion_variants">
            <div v-if="!selectedVariants[String(q.id)]" class="space-y-3">
              <p class="text-sm font-semibold text-gray-700">
                Choisissez un thème :
              </p>
              <div class="grid grid-cols-1 gap-3">
                <button
                  v-for="(variant, key) in q.content.opinion_variants"
                  :key="key"
                  class="p-4 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-teal-400 transition-colors"
                  @click="selectVariant(String(q.id), String(key))"
                >
                  <p class="font-semibold text-gray-900">
                    {{ variant.thema }}
                  </p>
                </button>
              </div>
            </div>

            <template v-else>
              <div class="flex items-center justify-between mb-2">
                <p class="text-sm font-semibold text-gray-700">
                  {{
                    q.content.opinion_variants[selectedVariants[String(q.id)]!]
                      ?.thema
                  }}
                </p>
                <button
                  class="text-xs text-gray-400 hover:text-gray-600"
                  @click="selectedVariants[String(q.id)] = null"
                >
                  Changer de thème
                </button>
              </div>

              <div
                v-if="
                  q.content.opinion_variants[selectedVariants[String(q.id)]!]
                    ?.aussagen?.length
                "
                class="space-y-2"
              >
                <div
                  v-for="(aussage, i) in q.content.opinion_variants[
                    selectedVariants[String(q.id)]!
                  ].aussagen"
                  :key="i"
                  class="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-800 italic"
                >
                  « {{ aussage }} »
                </div>
              </div>

              <div
                v-if="q.content.leitpunkte?.length"
                class="bg-amber-50 border border-amber-200 rounded-xl p-5"
              >
                <p class="text-sm font-semibold text-amber-800 mb-3">
                  {{ t("schreiben.task") }} :
                </p>
                <ul class="space-y-1">
                  <li
                    v-for="(punkt, i) in q.content.leitpunkte"
                    :key="i"
                    class="flex gap-2 text-sm text-amber-800"
                  >
                    <span class="font-bold">–</span>
                    <span>{{ punkt }}</span>
                  </li>
                </ul>
                <p
                  v-if="q.content.word_count_target"
                  class="mt-3 text-xs text-amber-700 font-medium"
                >
                  {{ t("schreiben.approx") }} {{ q.content.word_count_target }}
                  {{ t("schreiben.words") }}
                </p>
              </div>
            </template>
          </template>

          <!-- ══ CAS 3 : formats simples (Goethe, TELC message unique) ══ -->
          <template v-else>
            <!-- Stimulus e-mail (TELC) -->
            <div
              v-if="
                q.content.stimulus_email?.sender ||
                q.content.stimulus_email?.subject ||
                q.content.stimulus_email?.body
              "
              class="bg-white border border-gray-200 rounded-xl overflow-hidden"
            >
              <div
                class="bg-gray-50 border-b border-gray-200 px-5 py-3 space-y-1"
              >
                <div class="flex items-center gap-2 text-sm">
                  <span class="font-semibold text-gray-500 w-16">Von:</span>
                  <span class="text-gray-900 font-medium">{{
                    q.content.stimulus_email.sender
                  }}</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <span class="font-semibold text-gray-500 w-16">Betreff:</span>
                  <span class="text-gray-900">{{
                    q.content.stimulus_email.subject
                  }}</span>
                </div>
              </div>
              <div class="px-5 py-4">
                <p
                  class="text-sm text-gray-800 whitespace-pre-line leading-relaxed"
                >
                  {{ q.content.stimulus_email.body }}
                </p>
              </div>
            </div>

            <!-- Stimulus forum (Goethe) -->
            <div
              v-else-if="q.content.stimulus"
              class="bg-gray-50 border border-gray-200 rounded-xl p-5"
            >
              <div class="flex items-center gap-2 mb-2">
                <i class="pi pi-comment text-gray-500"></i>
                <span class="text-sm font-semibold text-gray-700">
                  {{ getStimulusAuthor(q) || t("schreiben.comment") }}
                </span>
              </div>
              <p
                v-if="getStimulusTitle(q)"
                class="text-xs font-semibold text-gray-500 mb-2"
              >
                {{ getStimulusTitle(q) }}
              </p>
              <p class="text-sm text-gray-800 italic">
                {{ getStimulusText(q) }}
              </p>
            </div>

            <!-- Destinataire (si précisé, hors e-mail) -->
            <div
              v-if="q.content.recipient"
              class="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm"
            >
              <span class="font-semibold text-gray-500">An:</span>
              <span class="text-gray-900 ml-2">{{ q.content.recipient }}</span>
            </div>

            <!-- Info comparaison (ÖSD — promesses vs réalité) -->
            <div
              v-if="q.content.info_comparison"
              class="bg-white border border-gray-200 rounded-xl overflow-hidden"
            >
              <div class="bg-gray-50 border-b border-gray-200 px-5 py-3">
                <p class="text-sm font-semibold text-gray-800">
                  {{ q.content.info_comparison.anbieter }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ q.content.info_comparison.situation }}
                </p>
              </div>
              <div class="px-5 py-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <p class="text-xs font-bold text-green-700 uppercase mb-2">
                    Versprochen
                  </p>
                  <ul class="space-y-1">
                    <li
                      v-for="(v, i) in q.content.info_comparison.versprechen"
                      :key="i"
                      class="text-xs text-gray-700 flex gap-1.5"
                    >
                      <span class="text-green-600">✓</span>{{ v }}
                    </li>
                  </ul>
                </div>
                <div>
                  <p class="text-xs font-bold text-red-700 uppercase mb-2">
                    Problème
                  </p>
                  <ul class="space-y-1">
                    <li
                      v-for="(p, i) in q.content.info_comparison.probleme"
                      :key="i"
                      class="text-xs text-gray-700 flex gap-1.5"
                    >
                      <span class="text-red-600">✗</span>{{ p }}
                    </li>
                  </ul>
                </div>
              </div>
              <div
                v-if="q.content.info_comparison.kontakt"
                class="px-5 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500"
              >
                Kontakt: {{ q.content.info_comparison.kontakt }}
              </div>
            </div>

            <!-- Sujet simple (topic) -->
            <div
              v-if="q.content.topic"
              class="bg-amber-50 border border-amber-200 rounded-xl p-5"
            >
              <p class="text-sm font-semibold text-amber-800 mb-2">Thema :</p>
              <p class="text-base font-bold text-amber-900">
                {{ q.content.topic }}
              </p>
            </div>

            <!-- Scénario -->
            <div
              v-if="q.content.scenario"
              class="bg-amber-50 border border-amber-200 rounded-xl p-5"
            >
              <p class="text-sm font-semibold text-amber-800 mb-3">
                {{ t("schreiben.task") }} :
              </p>
              <p class="text-sm text-amber-900">{{ q.content.scenario }}</p>
            </div>

            <!-- Prompts / consignes (communs à topic et scenario) -->
            <div
              v-if="q.content.prompts?.length"
              :class="[
                'rounded-xl p-5',
                q.content.scenario
                  ? 'bg-amber-50 border border-amber-200 -mt-4'
                  : 'bg-amber-50 border border-amber-200',
              ]"
            >
              <p
                v-if="!q.content.scenario"
                class="text-sm font-semibold text-amber-800 mb-3"
              >
                {{ t("schreiben.task") }} :
              </p>
              <ul class="space-y-1">
                <li
                  v-for="(prompt, i) in q.content.prompts"
                  :key="i"
                  class="flex gap-2 text-sm text-amber-800"
                >
                  <span class="font-bold">–</span>
                  <span>{{ prompt }}</span>
                </li>
              </ul>
              <p
                v-if="q.content.word_count_target"
                class="mt-3 text-xs text-amber-700 font-medium"
              >
                {{ t("schreiben.approx") }} {{ q.content.word_count_target }}
                {{ t("schreiben.words") }}
                <span v-if="q.content.register === 'formell'">
                  • {{ t("schreiben.formal_required") }}</span
                >
              </p>
            </div>

            <!-- Cible mots seule (aucun prompt mais un objectif de mots) -->
            <div
              v-else-if="q.content.word_count_target"
              class="bg-amber-50 border border-amber-200 rounded-xl p-4"
            >
              <p class="text-xs text-amber-700 font-medium">
                {{ t("schreiben.approx") }} {{ q.content.word_count_target }}
                {{ t("schreiben.words") }}
              </p>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ── Colonne droite : rédaction ─── -->
    <div class="lg:w-[55%] overflow-y-auto bg-gray-50">
      <div class="p-6 space-y-4 max-w-2xl mx-auto">
        <div v-for="q in questions" :key="`input-${q.id}`" class="space-y-4">
          <!-- Zone de rédaction -->
          <div
            class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden focus-within:border-teal-400 transition-colors"
          >
            <Textarea
              v-if="isWritingUnlocked(q)"
              :modelValue="getTextAnswer(q)"
              :placeholder="t('schreiben.placeholder')"
              class="w-full border-0 resize-none p-5 text-sm focus:ring-0 focus:outline-none"
              :rows="12"
              @update:modelValue="(val) => onInput(q, val)"
            />
            <div v-else class="p-5 text-sm text-gray-400 italic">
              Choisissez d'abord un thème pour commencer à écrire.
            </div>
            <div
              class="border-t border-gray-100 px-5 py-2 flex items-center justify-between bg-gray-50"
            >
              <span class="text-xs text-gray-400"
                >{{ getWordCount(q) }} {{ t("schreiben.word_count") }}</span
              >
              <div class="flex items-center gap-3">
                <!-- Barre progression mots -->
                <div
                  v-if="q.content.word_count_target"
                  class="flex items-center gap-2"
                >
                  <div class="w-24 bg-gray-200 rounded-full h-1">
                    <div
                      :class="[
                        'h-1 rounded-full transition-all',
                        getWordCount(q) >= q.content.word_count_target
                          ? 'bg-green-500'
                          : 'bg-teal-400',
                      ]"
                      :style="{
                        width: `${Math.min((getWordCount(q) / q.content.word_count_target) * 100, 100)}%`,
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SprachlicheMittelPanel from "~/components/session/SprachlicheMittelPanel.vue";
import { resolveMittelKey } from "#shared/sprachlicheMittel";

const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
  sessionId: string;
  examName?: string;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const { t } = useI18n();
const downloading = ref(false);

// ── Sprachliche Mittel ─────────────────────────────────
function parseExamInfo(name?: string) {
  const n = (name || "").toLowerCase();
  let provider = "";
  if (n.includes("ösd") || n.includes("osd")) provider = "ÖSD";
  else if (n.includes("goethe")) provider = "Goethe";
  else if (n.includes("telc")) provider = "TELC";
  const cefrMatch = n.match(/b1|b2/);
  const cefrCode = cefrMatch ? cefrMatch[0].toUpperCase() : "";
  return { provider, cefrCode };
}

const examInfo = computed(() => parseExamInfo(props.examName));

const mittelKey = computed(() =>
  resolveMittelKey({
    provider: examInfo.value.provider,
    cefrCode: examInfo.value.cefrCode,
    moduleSlug: "schreiben",
    formatType: props.teil?.format_type,
    teilNumber: props.teil?.teil_number,
  }),
);

const getTextAnswer = (q: any): string =>
  props.answers[q.id]?.user_answer?.text || "";

const getWordCount = (q: any): number => {
  const text = getTextAnswer(q);
  return text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0;
};

const onInput = (q: any, val: string) => {
  emit("answer", q.id, { text: val });
};

// ── Choix de thème (TELC/ÖSD B2 — "themen") ───────────────────────
const selectedThemes = ref<Record<string, string | null>>({});
const selectTheme = (questionId: string, key: string) => {
  selectedThemes.value[questionId] = key;
};

// ── Choix de variante d'opinion (ÖSD — variante_a/variante_b) ─────
const selectedVariants = ref<Record<string, string | null>>({});
const selectVariant = (questionId: string, key: string) => {
  selectedVariants.value[questionId] = key;
};

// La zone de rédaction n'est débloquée que si le format ne demande
// pas de choix préalable, ou si ce choix a déjà été fait.
const isWritingUnlocked = (q: any): boolean => {
  const id = String(q.id);
  if (q.content.themes) return !!selectedThemes.value[id];
  if (q.content.opinion_variants) return !!selectedVariants.value[id];
  return true;
};

const downloadPDF = async (q: any) => {
  downloading.value = true;
  try {
    const { jsPDF } = await import("jspdf");
    const doc = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
    });
    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxW = pageW - margin * 2;
    let y = margin;

    doc.setFillColor(15, 118, 110);
    doc.rect(0, 0, pageW, 30, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("DeutschTest", margin, 13);
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text(props.examName || "Goethe-ÖSD Zertifikat B1", margin, 22);
    doc.text(
      new Date().toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      }),
      pageW - margin,
      22,
      { align: "right" },
    );
    y = 45;

    doc.setTextColor(80, 80, 80);
    doc.setFontSize(11);
    doc.setFont("helvetica", "bold");
    doc.text("SCHREIBEN", margin, y);
    y += 6;
    doc.setDrawColor(15, 118, 110);
    doc.setLineWidth(0.5);
    doc.line(margin, y, pageW - margin, y);
    y += 8;

    if (props.teil.instructions) {
      doc.setFillColor(239, 246, 255);
      doc.setDrawColor(147, 197, 253);
      doc.roundedRect(margin, y, maxW, 14, 2, 2, "FD");
      doc.setTextColor(30, 64, 175);
      doc.setFontSize(9);
      doc.setFont("helvetica", "italic");
      const instrLines = doc.splitTextToSize(props.teil.instructions, maxW - 6);
      doc.text(instrLines, margin + 3, y + 5);
      y += 18;
    }

    // ── Résout le contenu de l'aufgabe selon le format actif ────
    const qid = String(q.id);
    const activeTheme = q.content.themes
      ? q.content.themes[selectedThemes.value[qid] || ""]
      : null;
    const activeVariant = q.content.opinion_variants
      ? q.content.opinion_variants[selectedVariants.value[qid] || ""]
      : null;

    let scenarioText =
      activeTheme?.stimulus ||
      q.content.scenario ||
      q.content.topic ||
      (q.content.info_comparison
        ? `${q.content.info_comparison.anbieter} — ${q.content.info_comparison.situation}`
        : "") ||
      "";
    let prompts: string[] =
      activeTheme?.prompts ||
      activeVariant?.aussagen ||
      q.content.prompts ||
      q.content.leitpunkte ||
      [];

    doc.setFillColor(255, 251, 235);
    doc.setDrawColor(252, 211, 77);
    const scenarioLines = doc.splitTextToSize(scenarioText, maxW - 6);
    const blockH = 10 + scenarioLines.length * 5 + prompts.length * 6 + 10;
    doc.roundedRect(margin, y, maxW, blockH, 2, 2, "FD");
    doc.setTextColor(146, 64, 14);
    doc.setFontSize(9);
    doc.setFont("helvetica", "bold");
    doc.text("Aufgabe :", margin + 3, y + 7);
    doc.setFont("helvetica", "normal");
    let textY = y + 13;
    doc.text(scenarioLines, margin + 3, textY);
    textY += scenarioLines.length * 5 + 3;
    prompts.forEach((p: string) => {
      doc.text(`– ${p}`, margin + 5, textY);
      textY += 6;
    });
    if (q.content.word_count_target) {
      doc.setFont("helvetica", "bold");
      doc.text(
        `Environ ${q.content.word_count_target} mots`,
        margin + 3,
        textY,
      );
    }
    y += blockH + 10;

    doc.setTextColor(30, 30, 30);
    doc.setFontSize(11);
    doc.setFont("helvetica", "bold");
    doc.text("Ma réponse :", margin, y);
    y += 4;
    doc.setDrawColor(200, 200, 200);
    doc.line(margin, y, pageW - margin, y);
    y += 8;
    const answerText = getTextAnswer(q);
    if (answerText) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      const answerLines = doc.splitTextToSize(answerText, maxW);
      answerLines.forEach((line: string) => {
        if (y > pageH - 25) {
          doc.addPage();
          y = margin;
        }
        doc.text(line, margin, y);
        y += 6;
      });
    } else {
      doc.setFont("helvetica", "italic");
      doc.setTextColor(150, 150, 150);
      doc.setFontSize(10);
      doc.text("(Aucune réponse)", margin, y);
      y += 8;
    }
    y += 6;

    doc.setDrawColor(200, 200, 200);
    doc.line(margin, y, pageW - margin, y);
    y += 5;
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8);
    doc.setTextColor(120, 120, 120);
    doc.text(
      `${getWordCount(q)} mot(s)${q.content.word_count_target ? ` / ${q.content.word_count_target} recommandés` : ""}`,
      margin,
      y,
    );

    doc.setFillColor(245, 245, 245);
    doc.rect(0, pageH - 12, pageW, 12, "F");
    doc.setTextColor(150, 150, 150);
    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    doc.text("Généré par DeutschTest — deutschtest.com", margin, pageH - 5);
    doc.text("Page 1", pageW - margin, pageH - 5, { align: "right" });

    doc.save(`schreiben_teil${props.teil.teil_number}_${Date.now()}.pdf`);
  } catch (err) {
    console.error("Erreur génération PDF:", err);
  } finally {
    downloading.value = false;
  }
};

// ── Stimulus forum — gère le cas où le générateur a produit un objet
// {text, title, author} au lieu d'une simple string.
const parseStimulus = (
  raw: any,
): { text: string; title?: string; author?: string } => {
  if (!raw) return { text: "" };
  if (typeof raw === "object") {
    return { text: raw.text || "", title: raw.title, author: raw.author };
  }
  if (typeof raw === "string") {
    const trimmed = raw.trim();
    if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
      try {
        const parsed = JSON.parse(trimmed);
        return {
          text: parsed.text || raw,
          title: parsed.title,
          author: parsed.author,
        };
      } catch {
        return { text: raw };
      }
    }
    return { text: raw };
  }
  return { text: String(raw) };
};

const getStimulusText = (q: any): string =>
  parseStimulus(q.content.stimulus).text;
const getStimulusAuthor = (q: any): string =>
  parseStimulus(q.content.stimulus).author || q.content.stimulus_author || "";
const getStimulusTitle = (q: any): string =>
  parseStimulus(q.content.stimulus).title || "";
</script>