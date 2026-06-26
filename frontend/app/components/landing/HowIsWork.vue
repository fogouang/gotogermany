<template>
  <section class="py-20 overflow-hidden">
    <div class="max-w-6xl mx-auto px-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <!-- ── Image + cercle rotatif ─────────────────── -->
        <div class=" hidden  relative md:flex justify-center items-center">
          <!-- Cercle qui tourne -->
          <div
            class="absolute w-80 h-80 rounded-full border-0 opacity-80 animate-spin-slow"
            style="
              background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 6px,
                #0d9488 6px,
                #0d9488 7px
              );
              border-radius: 50%;
              -webkit-mask: radial-gradient(
                farthest-side,
                transparent calc(100% - 2px),
                white calc(100% - 1px)
              );
              mask: radial-gradient(
                farthest-side,
                transparent calc(100% - 40px),
                white calc(100% - 39px)
              );
            "
          />

          <!-- Version simplifiée du cercle hachuré -->
          <div
            class=" absolute w-72 h-72 animate-spin-slow"
            style="animation-duration: 20s"
          >
            <svg viewBox="0 0 300 300" class="w-full h-full opacity-70">
              <defs>
                <pattern
                  id="hatch"
                  patternUnits="userSpaceOnUse"
                  width="8"
                  height="8"
                  patternTransform="rotate(45)"
                >
                  <line
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="8"
                    stroke="#0d9488"
                    stroke-width="1.5"
                  />
                </pattern>
                <clipPath id="circle-clip">
                  <circle cx="150" cy="150" r="140" />
                </clipPath>
              </defs>
              <!-- Anneau hachuré -->
              <circle
                cx="150"
                cy="150"
                r="140"
                fill="url(#hatch)"
                clip-path="url(#circle-clip)"
                opacity="0.6"
              />
              <circle cx="150" cy="150" r="100" fill="white" />
            </svg>
          </div>

          <!-- Image -->
          <img
            src="/images/works.png"
            alt="Comment ça marche"
            class=" relative z-10 w-170 object-contain drop-shadow-xl"
          />
        </div>

        <!-- ── Contenu droite ──────────────────────────── -->
        <div class="space-y-8">
          <!-- Titre -->
          <div class="space-y-2">
            <span class="text-sm font-semibold text-[#076152] tracking-wide">
              {{ t("how_it_works.title") }}
            </span>
            <h2 class="text-2xl md:text-4xl font-bold text-gray-900 leading-tight">
              {{ t("how_it_works.subtitle1") }} <span style="color: #f5a623">{{ t("how_it_works.subtitle2") }}</span>{{ t("how_it_works.subtitle3") }}
            </h2>
            <!-- Underline orange -->
            <div class="w-32 h-1 rounded-full bg-orange-400" />
          </div>

          <!-- Steps -->
          <div class="space-y-0 divide-y divide-gray-100">
            <!-- Step 1 -->
            <div class="flex items-center gap-5 py-6">
              <div
                class="w-14 h-14 rounded-full bg-[#F59E0B] flex items-center justify-center shrink-0 shadow-md"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M21.998 10.5C21.982 6.768 21.836 4.765 20.535 3.464C19.072 2 16.714 2 12 2C7.286 2 4.929 2 3.464 3.464C2 4.93 2 7.286 2 12C2 16.714 2 19.071 3.464 20.535C4.705 21.776 6.587 21.965 10 21.995"
                    stroke="white"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                  <path
                    opacity="0.5"
                    d="M21.5 8H2.5M7 8L10.5 2.5M13.5 8L17 2.5"
                    stroke="white"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                  <path
                    d="M18.562 13.935L18.979 13.518C19.356 13.143 19.865 12.932 20.395 12.932C20.925 12.932 21.434 13.143 21.811 13.518C22.188 13.893 22.4 14.401 22.4 14.93C22.4 15.459 22.188 15.968 21.811 16.343L21.065 17.088M18.562 13.935C18.562 13.935 18.614 14.822 19.396 15.604C20.178 16.386 21.065 16.438 21.065 16.438M18.562 13.935L14.727 17.77C14.467 18.03 14.337 18.16 14.227 18.303C14.095 18.472 13.982 18.655 13.889 18.848C13.811 19.012 13.753 19.186 13.637 19.534L13.265 20.65L13.145 21.01L13.99 21.855M21.065 16.438L17.23 20.273C16.97 20.533 16.84 20.663 16.697 20.773C16.528 20.905 16.345 21.018 16.152 21.111C15.988 21.189 15.814 21.247 15.466 21.363L14.35 21.735L13.99 21.855M13.99 21.855L13.628 21.975C13.371 22.059 13.091 21.988 12.904 21.801C12.717 21.614 12.646 21.334 12.73 21.077L12.85 20.717"
                    stroke="white"
                    stroke-width="1.5"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">
                  {{ t('how_it_works.steps.account.title') }}
                </h3>
                <p class="text-sm text-gray-500 mt-0.5">
                  {{ t('how_it_works.steps.account.description') }}
                </p>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="flex items-center gap-5 py-6">
              <div
                class="w-14 h-14 rounded-full bg-[#076152] flex items-center justify-center shrink-0 shadow-md"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M3.794 12.03C4.331 9.342 4.6 8 5.487 7.134C5.651 6.974 5.828 6.829 6.017 6.7C7.04 6 8.41 6 11.15 6H12.853C15.592 6 16.961 6 17.983 6.7C18.173 6.831 18.35 6.976 18.513 7.135C19.4 8 19.67 9.343 20.207 12.03C20.978 15.886 21.364 17.814 20.476 19.18C20.315 19.429 20.129 19.656 19.916 19.863C18.75 21 16.785 21 12.853 21H11.15C7.217 21 5.251 21 4.085 19.862C3.874 19.656 3.686 19.427 3.526 19.179C2.638 17.813 3.024 15.885 3.796 12.029L3.794 12.03Z"
                    stroke="white"
                    stroke-width="1.5"
                  />
                  <path
                    opacity="0.5"
                    d="M9 6V5C9 4.204 9.316 3.441 9.879 2.879C10.441 2.316 11.204 2 12 2C12.796 2 13.559 2.316 14.121 2.879C14.684 3.441 15 4.204 15 5V6M9.17 15C9.377 15.586 9.76 16.093 10.267 16.451C10.774 16.81 11.379 17.003 12 17.003C12.621 17.003 13.227 16.81 13.733 16.451C14.24 16.093 14.623 15.586 14.83 15"
                    stroke="white"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">
                 {{ t('how_it_works.steps.exam.title') }}
                </h3>
                <p class="text-sm text-gray-500 mt-0.5">
                 {{ t('how_it_works.steps.exam.description') }}
                </p>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="flex items-center gap-5 py-6">
              <div
                class="w-14 h-14 rounded-full bg-orange-500 flex items-center justify-center shrink-0 shadow-md"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    opacity="0.5"
                    d="M2 12C2 7.286 2 4.929 3.464 3.464C4.93 2 7.286 2 12 2C16.714 2 19.071 2 20.535 3.464C22 4.93 22 7.286 22 12C22 16.714 22 19.071 20.535 20.535C19.072 22 16.714 22 12 22C7.286 22 4.929 22 3.464 20.535C2 19.072 2 16.714 2 12Z"
                    stroke="white"
                    stroke-width="1.5"
                  />
                  <path
                    d="M7 14L9.293 11.707C9.481 11.52 9.735 11.414 10 11.414C10.265 11.414 10.52 11.52 10.707 11.707L12.293 13.293C12.481 13.481 12.735 13.586 13 13.586C13.265 13.586 13.52 13.481 13.707 13.293L17 10M17 10V12.5M17 10H14.5"
                    stroke="white"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">
                   {{ t('how_it_works.steps.progress.title') }}
                </h3>
                <p class="text-sm text-gray-500 mt-0.5">
                   {{ t('how_it_works.steps.progress.description') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const { t } = useI18n();
</script>

<style scoped>
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.animate-spin-slow {
  animation: spin-slow 20s linear infinite;
}
</style>
