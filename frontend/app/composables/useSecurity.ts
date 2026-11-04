// composables/useSecurity.ts
// Accès admin au module de protection du contenu, via le client OpenAPI généré.

import { SecurityService } from "#shared/api";
import type {
  SecurityBlockResponse,
  SecurityIncidentResponse,
  SecuritySummaryResponse,
  SecurityUserInfo,
} from "#shared/api";

// Noms utilisés par pages/admin/securite.vue
export type SecurityUser = SecurityUserInfo;
export type SecurityIncident = SecurityIncidentResponse;
export type SecurityBlock = SecurityBlockResponse;
export type SecuritySummary = SecuritySummaryResponse;

export function useSecurity() {
  const apiError = (e: any, fallback: string) =>
    typeof e?.body?.detail === "string" ? e.body.detail : fallback;

  return {
    apiError,
    getSummary: () => SecurityService.summaryApiV1SecuritySummaryGet(),
    listIncidents: (status: "open" | "resolved" | "" = "open", limit = 200) =>
      SecurityService.listIncidentsApiV1SecurityIncidentsGet(status, limit),
    getIncident: (id: string) =>
      SecurityService.getIncidentApiV1SecurityIncidentsIncidentIdGet(id),
    resolveIncident: (id: string, note: string | null) =>
      SecurityService.resolveIncidentApiV1SecurityIncidentsIncidentIdResolvePost(id, { note }),
    listBlocks: () => SecurityService.listBlocksApiV1SecurityBlocksGet(),
    unblockUser: (userId: string) =>
      SecurityService.unblockUserApiV1SecurityUsersUserIdUnblockPost(userId),
    banUser: (userId: string, note: string | null) =>
      SecurityService.banUserApiV1SecurityUsersUserIdBanPost(userId, { note }),

    /** Télécharge le dossier de preuves d'un élève (JSON). */
    async downloadEvidence(userId: string, name: string) {
      const data = await SecurityService.evidenceApiV1SecurityUsersUserIdEvidenceGet(userId);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const safe = name.normalize("NFD").replace(/[^\w-]+/g, "_").slice(0, 40);
      a.href = url;
      a.download = `preuves_${safe}_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
  };
}