// composables/useSchreibenPdf.ts
//
// Génère un PDF récapitulatif du devoir Schreiben (consignes + réponses
// de l'étudiant), 100% côté client — aucun appel backend. L'étudiant
// télécharge et envoie lui-même le fichier à son formateur.

import jsPDF from "jspdf";

interface SchreibenTeil {
  id: string;
  teil_number: number;
  format_type: string;
  instructions?: string | null;
  questions?: Array<{
    id: string;
    content: {
      prompt?: string;
      content_points?: string[];
      prompt_text?: string;
      fields?: Array<{ number: number | string; label: string }>;
    };
  }>;
}

interface DownloadParams {
  subjectTitle: string;
  level: string;
  studentName: string;
  teile: SchreibenTeil[];
  /** answers[questionId].user_answer — { text: "..." } pour free_text, { "1": "...", "2": "..." } pour form_fill */
  answers: Record<string, any>;
}

export function useSchreibenPdf() {
  function download({ subjectTitle, level, studentName, teile, answers }: DownloadParams) {
    const doc = new jsPDF({ unit: "mm", format: "a4" });
    const marginX = 15;
    const maxWidth = doc.internal.pageSize.getWidth() - marginX * 2;
    const pageHeight = doc.internal.pageSize.getHeight();
    let y = 20;

    function addText(text: string, opts: { size?: number; bold?: boolean; italic?: boolean; spacingAfter?: number } = {}) {
      const { size = 11, bold = false, italic = false, spacingAfter = 6 } = opts;
      doc.setFont("helvetica", bold ? "bold" : italic ? "italic" : "normal");
      doc.setFontSize(size);
      const lines = doc.splitTextToSize(text, maxWidth);
      for (const line of lines) {
        if (y > pageHeight - 20) {
          doc.addPage();
          y = 20;
        }
        doc.text(line, marginX, y);
        y += size * 0.5;
      }
      y += spacingAfter;
    }

    function addRule() {
      if (y > pageHeight - 20) {
        doc.addPage();
        y = 20;
      }
      doc.setDrawColor(200);
      doc.line(marginX, y, marginX + maxWidth, y);
      y += 6;
    }

    // ── En-tête ──────────────────────────────────────────────
    addText("Start Deutsch — Schreiben", { size: 16, bold: true, spacingAfter: 2 });
    addText(`${subjectTitle} · ${level}`, { size: 11, spacingAfter: 2 });
    addText(`Kandidat/-in: ${studentName}`, { size: 10, italic: true, spacingAfter: 2 });
    addText(`Datum: ${new Date().toLocaleDateString("de-DE")}`, { size: 10, italic: true, spacingAfter: 4 });
    addRule();

    // ── Un bloc par Teil ─────────────────────────────────────
    const sortedTeile = [...teile].sort((a, b) => a.teil_number - b.teil_number);

    for (const teil of sortedTeile) {
      const question = teil.questions?.[0];
      if (!question) continue;

      addText(`Teil ${teil.teil_number}`, { size: 13, bold: true, spacingAfter: 2 });
      if (teil.instructions) {
        addText(teil.instructions, { size: 10, italic: true, spacingAfter: 4 });
      }

      const userAnswer = answers[question.id]?.user_answer;

      if (teil.format_type === "free_text") {
        if (question.content.prompt) {
          addText(question.content.prompt, { size: 11, spacingAfter: 2 });
        }
        if (question.content.content_points?.length) {
          for (const point of question.content.content_points) {
            addText(`• ${point}`, { size: 10, spacingAfter: 1 });
          }
          y += 3;
        }
        addText("Antwort:", { size: 11, bold: true, spacingAfter: 2 });
        addText(userAnswer?.text || "(keine Antwort)", { size: 11, spacingAfter: 6 });
      } else if (teil.format_type === "form_fill") {
        if (question.content.prompt_text) {
          addText(question.content.prompt_text, { size: 11, spacingAfter: 4 });
        }
        for (const field of question.content.fields ?? []) {
          const value = userAnswer?.[String(field.number)] || "—";
          addText(`${field.label}: ${value}`, { size: 11, spacingAfter: 2 });
        }
        y += 2;
      }

      addRule();
    }

    const safeTitle = subjectTitle.replace(/[^\w\-]+/g, "_");
    doc.save(`Schreiben_${safeTitle}_${level}.pdf`);
  }

  return { download };
}