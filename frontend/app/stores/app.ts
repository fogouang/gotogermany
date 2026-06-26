import { OpenAPI, SettingsService } from "~~/shared/api"

// stores/app.ts
export const useAppStore = defineStore('app', {
  state: () => ({
    freeAccessMode: false,
  }),
  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig()
      OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001'
      const tokenCookie = useCookie('access_token')
      OpenAPI.TOKEN = tokenCookie.value ?? undefined
    },
    async fetchFreeAccessMode() {
      this._ensureApiConfig()
      try {
        const res = await SettingsService.getFreeAccessModeApiV1SettingsFreeAccessGet()
        this.freeAccessMode = res.free_access_mode
      } catch {}
    },
  },
})