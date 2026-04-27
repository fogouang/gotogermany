import { defineStore } from "pinia";
import { UsersService, ExamAccessService, OpenAPI } from "#shared/api";
import type { UserAdminResponse } from "#shared/api";

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
        return { success: true }
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement users";
        return { success: false, error: this.error }
      } finally {
        this.loading = false;
      }
    },

    async toggleActive(userId: string) {
      this._ensureApiConfig();
      try {
        const updated = await UsersService.toggleActiveApiV1UsersUserIdToggleActivePatch(userId);
        const index = this.users.findIndex(u => u.id === userId);
        if (index !== -1) this.users[index] = updated;
        return { success: true }
      } catch (error: any) {
        return { success: false, error: error.body?.detail }
      }
    },

    async deleteUser(userId: string) {
      this._ensureApiConfig();
      try {
        await UsersService.deleteUserApiV1UsersUserIdDelete(userId);
        this.users = this.users.filter(u => u.id !== userId);
        return { success: true }
      } catch (error: any) {
        return { success: false, error: error.body?.detail }
      }
    },

    async grantAccess(userId: string, examId: string) {
      this._ensureApiConfig();
      try {
        await ExamAccessService.adminGrantAccessApiV1AccessAdminGrantPost(
          userId, examId
        );
        return { success: true }
      } catch (error: any) {
        return { success: false, error: error.body?.detail }
      }
    },
  },
});