<template>
  <section class="relative transition-all pt-8 pb-10">
    <div
      class="relative transition-all max-w-7xl mx-auto w-full px-6 flex flex-col items-center justify-between gap-12 md:flex-row md:gap-3"
    >
      <div class="transition-all relative w-full md:max-w-120">
        <div class="transition-all relative z-10 mb-6">
          <h2
            class="outline-none text-3xl text-[#076152] leading-tight font-bold md:text-4xl lg:text-[42px] lg:leading-14"
          >
            {{ t('hero.title') }}
          </h2>
          <p class="outline-none mt-4 text-lg text-muted-foreground">
            {{ t('hero.subtitle') }}
          </p>
        </div>

        <button
          class="inline-flex items-center gap-3 text-white font-bold uppercase tracking-widest px-8 py-4 rounded-md mb-4 transition-all hover:opacity-90"
          style="background-color: #076152; font-size: 0.75rem; letter-spacing: 0.12em;"
          @click="openSignup"
        >
          {{ t('hero.cta') }}
          <svg width="16" height="14" viewBox="0 0 16 14" fill="none">
            <path
              d="M7.5264 0C7.5264 0.6962 8.21633 1.738 8.9138 2.61293C9.81193 3.7394 10.8838 4.72347 12.1137 5.4748C13.0351 6.0374 14.154 6.57747 15.0528 6.57747M7.5264 13.1712C7.5264 12.475 8.21633 11.4332 8.9138 10.5583C9.81193 9.43187 10.8838 8.44773 12.1137 7.6964C13.0351 7.1338 14.154 6.59373 15.0528 6.59373M15.0528 6.5856H0"
              stroke="currentColor"
              stroke-width="1.5"
            />
          </svg>
        </button>

        <div class="transition-all relative z-10 flex items-center gap-3">
          <div class="relative transition-all">
            <div class="relative transition-all flex items-center gap-2">
              <span v-for="i in 5" :key="i">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24" height="24" viewBox="0 0 24 24"
                  fill="none" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"
                  class="lucide -mb-0.5 h-4 w-4 p-0 text-yellow-500"
                >
                  <path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path>
                </svg>
              </span>
              <p class="outline-none font-medium">5.0</p>
            </div>
            <p class="outline-none text-sm text-muted-foreground">
              {{ t('hero.social_proof') }}
            </p>
          </div>
        </div>

        <div class="transition-all pointer-events-none absolute -top-120 -right-120 h-300 w-300 rounded-full bg-[radial-gradient(circle,rgba(97,95,255,0.45)_0%,transparent_70%)] opacity-22 content-['']"></div>
      </div>

      <div class="transition-all relative w-full max-w-160">
        <img
          :alt="t('hero.image_alt')"
          draggable="false"
          class="relative z-10 h-full w-full"
          src="/images/hero-image.png"
        />
        <div class="transition-all pointer-events-none absolute -right-120 -bottom-100 h-300 w-300 rounded-full bg-[radial-gradient(circle,rgba(0,167,111,0.45)_0%,transparent_70%)] opacity-25 content-['']"></div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAuthDialog } from '~/composables/useAuthDialog'

const { t } = useI18n()

const authStore = useAuthStore()
const { openSignup } = useAuthDialog()
</script>