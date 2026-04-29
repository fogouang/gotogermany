import { defineStore } from "pinia";
import { AuthService, UsersService, OpenAPI } from "#shared/api";
import type { AuthUserResponse, UserMeResponse } from "#shared/api";

interface AuthState {
  user: AuthUserResponse | UserMeResponse | null;
  token: string | null;
  loading: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    token: null,
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) =>
      state.user && "is_admin" in state.user ? state.user.is_admin : false,
    isVerified: (state) => state.user?.is_verified || false,
    userName: (state) => state.user?.full_name || "",
    userEmail: (state) => state.user?.email || "",
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      // Toujours setter le token depuis le cookie
      const tokenCookie = useCookie("access_token");
      if (tokenCookie.value) {
        OpenAPI.TOKEN = tokenCookie.value;
      }
    },

    async login(email: string, password: string) {
      this._ensureApiConfig();
      this.loading = true;

      try {
        const response = await AuthService.loginApiV1AuthLoginPost({
          email,
          password,
        });

        const tokenCookie = useCookie("access_token", {
          maxAge: 60 * 60 * 24 * 7,
          sameSite: "lax",
          secure: process.env.NODE_ENV === "production",
        });

        tokenCookie.value = response.access_token;
        OpenAPI.TOKEN = response.access_token;
        this.token = response.access_token;
        this.user = response.user;

        return { success: true, user: response.user };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Email ou mot de passe incorrect",
        };
      } finally {
        this.loading = false;
      }
    },

    async register(
      email: string,
      password: string,
      fullName: string,
      phone?: string,
    ) {
      this._ensureApiConfig();
      this.loading = true;

      try {
        const response = await AuthService.registerApiV1AuthRegisterPost({
          email,
          password,
          full_name: fullName,
          phone: phone || null,
        });

        const tokenCookie = useCookie("access_token", {
          maxAge: 60 * 60 * 24 * 7,
          sameSite: "lax",
          secure: process.env.NODE_ENV === "production",
        });

        tokenCookie.value = response.access_token;
        OpenAPI.TOKEN = response.access_token;
        this.token = response.access_token;
        this.user = response.user;

        return { success: true, user: response.user };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur lors de l'inscription",
        };
      } finally {
        this.loading = false;
      }
    },

    async fetchUser() {
      this._ensureApiConfig();

      const tokenCookie = useCookie("access_token");

      if (!tokenCookie.value) {
        this.user = null;
        this.token = null;
        return;
      }

      // S'assurer que le token est dans OpenAPI
      OpenAPI.TOKEN = tokenCookie.value;

      this.loading = true;
      try {
        const response = await UsersService.getMeApiV1UsersMeGet();
        this.user = response;
        this.token = tokenCookie.value;
      } catch (error) {
        console.error("Fetch user error:", error);
        this.logout();
      } finally {
        this.loading = false;
      }
    },

    async updateProfile(fullName?: string, phone?: string) {
      this._ensureApiConfig();
      this.loading = true;
      try {
        const response = await UsersService.updateMeApiV1UsersMePatch({
          full_name: fullName || null,
          phone: phone || null,
        });
        this.user = response;
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur lors de la mise à jour",
        };
      } finally {
        this.loading = false;
      }
    },

    async changePassword(currentPassword: string, newPassword: string) {
      this._ensureApiConfig();
      this.loading = true;
      try {
        await UsersService.changePasswordApiV1UsersMeChangePasswordPost({
          current_password: currentPassword,
          new_password: newPassword,
        });
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error:
            error.body?.detail || "Erreur lors du changement de mot de passe",
        };
      } finally {
        this.loading = false;
      }
    },

    logout() {
      // Vider le state
      this.user = null;
      this.token = null;
      OpenAPI.TOKEN = undefined;

      // Cookie côté client uniquement
      if (import.meta.client) {
        document.cookie =
          "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      }
    },
  },
});
