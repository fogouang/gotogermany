/**
 * stores/correction.store.ts
 */
import { defineStore } from 'pinia'
import { CorrectionsService, OpenAPI } from '#shared/api'
import type { CorrectionResponse } from '#shared/api'

interface CorrectionState {
  // Correction courante (résultat affiché)
  current: CorrectionResponse | null
  // Cache : sessionId → CorrectionResponse (évite de rappeler l'IA)
  cache: Record<string, CorrectionResponse>
  loading: boolean
  error: string | null
}

export const useCorrectionStore = defineStore('correction', {
  state: (): CorrectionState => ({
    current: null,
    cache: {},
    loading: false,
    error: null,
  }),

  getters: {
    // Score en pourcentage arrondi
    scorePercentage: (state): number => {
      if (!state.current) return 0
      return Math.round(state.current.score_percentage)
    },

    // Niveau CECRL calculé depuis le pourcentage
    cecrlLevel: (state): string => {
      if (!state.current) return ''
      const pct = state.current.score_percentage
      if (pct >= 87) return 'C1'
      if (pct >= 70) return state.current.level.toUpperCase() + '+'
      if (pct >= 60) return state.current.level.toUpperCase()
      if (pct >= 45) return state.current.level.toUpperCase() + '-'
      return state.current.level === 'b2' ? 'B1' : 'A2'
    },

    // Feedbacks par critère sous forme de tableau pour l'affichage
    criteriaList: (state): Array<{ key: string; label: string; score: number; maxScore: number; feedback: string }> => {
      if (!state.current) return []
      const c = state.current
      const f = c.criteria_feedbacks as Record<string, string>

      // Calcul des max par critère selon l'examen
      const maxMap = _getCriteriaMax(c.provider, c.level)

      return [
        { key: 'aufgabe',    label: 'Aufgabenerfüllung', score: c.aufgabe_score,    maxScore: maxMap.aufgabe,    feedback: f.aufgabe_feedback    || '' },
        { key: 'kohaesion',  label: 'Kohäsion',          score: c.kohaesion_score,  maxScore: maxMap.kohaesion,  feedback: f.kohaesion_feedback  || '' },
        { key: 'wortschatz', label: 'Wortschatz',         score: c.wortschatz_score, maxScore: maxMap.wortschatz, feedback: f.wortschatz_feedback || '' },
        { key: 'grammatik',  label: 'Grammatik',          score: c.grammatik_score,  maxScore: maxMap.grammatik,  feedback: f.grammatik_feedback  || '' },
      ]
    },

    // Feedbacks par tâche sous forme de tableau
    taskList: (state): Array<{ key: string; label: string; correctedText: string; strengths: string[]; weaknesses: string[] }> => {
      if (!state.current) return []
      const tf = state.current.task_feedbacks as Record<string, any>
      return Object.entries(tf).map(([key, val]) => ({
        key,
        label: _taskLabel(key),
        correctedText: val.corrected_text || '',
        strengths: val.main_strengths || [],
        weaknesses: val.main_weaknesses || [],
      }))
    },

    isCached: (state) => (sessionId: string): boolean => {
      return !!state.cache[sessionId]
    },
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig()
      OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001'
      const tokenCookie = useCookie('access_token')
      OpenAPI.TOKEN = tokenCookie.value ?? undefined
    },

    /**
     * Lancer ou récupérer la correction d'une session Schreiben.
     * Si déjà en cache local → pas d'appel réseau.
     */
    async correct(sessionId: string) {
      // Cache local d'abord
      if (this.cache[sessionId]) {
        this.current = this.cache[sessionId]
        return { success: true, data: this.current }
      }

      this._ensureApiConfig()
      this.loading = true
      this.error = null

      try {
        const result = await CorrectionsService.createCorrectionApiV1CorrectionsPost({
          exam_session_id: sessionId,
        })

        this.current = result
        this.cache[sessionId] = result
        return { success: true, data: result }

      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur lors de la correction IA'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    /**
     * Récupérer une correction existante par session (sans relancer l'IA).
     * Utile au chargement de la page résultats.
     */
    async fetchBySession(sessionId: string) {
      if (this.cache[sessionId]) {
        this.current = this.cache[sessionId]
        return { success: true, data: this.current }
      }

      this._ensureApiConfig()
      this.loading = true
      this.error = null

      try {
        const result = await CorrectionsService.getCorrectionBySessionApiV1CorrectionsSessionSessionIdGet(sessionId)

        if (result) {
          this.current = result
          this.cache[sessionId] = result
        }
        return { success: true, data: result }

      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur lors du chargement'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    clearCurrent() {
      this.current = null
      this.error = null
    },
  },
})


// ─────────────────────────────────────────────────────────
// Helpers internes
// ─────────────────────────────────────────────────────────

interface CriteriaMax {
  aufgabe: number
  kohaesion: number
  wortschatz: number
  grammatik: number
}

/** Calcule le max par critère selon (provider, level) */
function _getCriteriaMax(provider: string, level: string): CriteriaMax {
  if (provider === 'telc') {
    return { aufgabe: 15, kohaesion: 10, wortschatz: 10, grammatik: 10 }
  }
  if (provider === 'osd' && level === 'b2') {
    return { aufgabe: 28, kohaesion: 22, wortschatz: 22, grammatik: 18 }
  }
  return { aufgabe: 30, kohaesion: 25, wortschatz: 25, grammatik: 20 }
}

/** Label lisible pour chaque tâche */
function _taskLabel(key: string): string {
  const labels: Record<string, string> = {
    task1: 'Teil 1',
    task2: 'Teil 2',
    task3: 'Teil 3',
  }
  return labels[key] || key
}