import { defineStore } from "pinia";
import { UsersService, ExamAccessService, ReferralsService, OpenAPI } from "#shared/api";
import type { UserAdminResponse, DirectorCreateRequest } from "#shared/api";

interface AdminUsersState {
  users: UserAdminResponse[];
  loading: boolean;
  error: string | null;
}

export const useAdminUsersStore = defineStore("adminUsers", {
  state: (): AdminUsersState => ({
    users: [],
    loading: false,
    error: null,
  }),
  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },
    async fetchUsers() {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const data = await UsersService.listUsersApiV1UsersGet();
        this.users = data;
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement users";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },
    async toggleActive(userId: string) {
      this._ensureApiConfig();
      try {
        const updated =
          await UsersService.toggleActiveApiV1UsersUserIdToggleActivePatch(
            userId,
          );
        const index = this.users.findIndex((u) => u.id === userId);
        if (index !== -1) this.users[index] = updated;
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },
    async toggleAmbassador(userId: string, currentStatus: boolean) {
      this._ensureApiConfig();
      try {
        await ReferralsService.setAmbassadorStatusApiV1ReferralsAdminSetAmbassadorPost(
          { user_id: userId, is_ambassador: !currentStatus },
        );
        // NOTE: UserAdminResponse doit exposer is_ambassador pour que
        // cette mise à jour locale ait un effet visible — si le champ
        // n'existe pas encore dans le schéma users/admin, l'ajouter
        // côté backend (UserAdminResponse) puis régénérer le client.
        const index = this.users.findIndex((u) => u.id === userId);
        if (index !== -1) {
          (this.users[index] as any).is_ambassador = !currentStatus;
        }
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur mise à jour statut ambassadeur",
        };
      }
    },
    async deleteUser(userId: string) {
      this._ensureApiConfig();
      try {
        await UsersService.deleteUserApiV1UsersUserIdDelete(userId);
        this.users = this.users.filter((u) => u.id !== userId);
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },
    async grantAccess(userId: string, levelId: string) {
      this._ensureApiConfig();
      try {
        await ExamAccessService.adminGrantAccessApiV1AccessAdminGrantPost(
          userId,
          levelId,
        );
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },
    async grantAllAccess(userId: string) {
      this._ensureApiConfig();
      try {
        await ExamAccessService.adminGrantAllLevelsApiV1AccessAdminGrantAllUserIdPost(
          userId,
        );
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },
    async createDirector(data: DirectorCreateRequest) {
      this._ensureApiConfig();
      try {
        const director =
          await UsersService.createDirectorApiV1UsersDirectorsPost(data);
        this.users.push(director);
        return { success: true, director };
      } catch (error: any) {
        console.error("ERREUR CREATE DIRECTOR:", error);
        return {
          success: false,
          error: error.body?.detail || "Erreur création directeur",
        };
      }
    },
  },
});