<template>
  <div class="flex-1 overflow-y-auto">
    <div class="max-w-2xl mx-auto px-4 py-8 sm:py-12">
      <div class="bg-card border border-line rounded-card shadow-soft overflow-hidden">
        <!-- En-tête -->
        <div class="px-5 sm:px-6 py-5 border-b border-line">
          <p class="text-xs font-semibold uppercase tracking-wider text-primary">
            {{ t("session.player.intro_title") }}
          </p>
          <h1 class="text-xl font-bold text-ink mt-1">{{ examName }}</h1>
          <p class="text-sm text-muted">{{ t("session.subject") }} {{ subjectNumber }}</p>
        </div>

        <div class="px-5 sm:px-6 py-5 space-y-6">
          <!-- Déroulé -->
          <section>
            <h2 class="text-sm font-semibold text-ink mb-3">
              {{ t("session.player.intro_modules") }}
            </h2>
            <ol class="space-y-2">
              <li
                v-for="(b, i) in blocks"
                :key="`b-${i}`"
                class="flex items-center gap-3 rounded-leaf border border-line bg-card-2 px-3 py-2.5"
              >
                <span class="w-7 h-7 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center shrink-0">
                  {{ i + 1 }}
                </span>
                <span class="flex-1 min-w-0 text-sm font-medium text-ink">{{ b.label }}</span>
                <span class="text-xs text-muted whitespace-nowrap">
                  <i class="pi pi-clock text-[10px] mr-1"></i>
                  {{ t("session.player.intro_minutes", { n: b.minutes }) }}
                </span>
              </li>

              <li
                v-for="name in oralModules"
                :key="`o-${name}`"
                class="flex items-center gap-3 rounded-leaf border border-dashed border-line px-3 py-2.5"
              >
                <span class="w-7 h-7 rounded-full bg-card-2 text-muted flex items-center justify-center shrink-0">
                  <i class="pi pi-microphone text-xs"></i>
                </span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-ink">{{ name }}</p>
                  <p class="text-xs text-muted">{{ t("session.player.intro_oral") }}</p>
                </div>
                <NuxtLink
                  v-if="oralLink"
                  :to="oralLink"
                  class="text-xs font-semibold text-primary whitespace-nowrap hover:underline"
                >
                  {{ t("session.player.intro_oral_link") }}
                </NuxtLink>
              </li>
            </ol>
          </section>

          <!-- Règles -->
          <section>
            <h2 class="text-sm font-semibold text-ink mb-3">
              {{ t("session.player.intro_rules_title") }}
            </h2>
            <ul class="space-y-2.5">
              <li
                v-for="rule in rules"
                :key="rule.key"
                class="flex items-start gap-3 text-sm text-ink"
              >
                <i :class="['pi text-primary mt-0.5 shrink-0', rule.icon]"></i>
                <span>{{ rule.text }}</span>
              </li>
            </ul>
          </section>

          <!-- Test du son -->
          <section
            v-if="hasAudio"
            class="rounded-leaf border border-line bg-card-2 p-4 flex flex-col sm:flex-row sm:items-center gap-3"
          >
            <Button
              :label="t('session.player.audio_test')"
              icon="pi pi-volume-up"
              outlined
              size="small"
              @click="playBeep"
            />
            <p class="text-xs text-muted">{{ t("session.player.audio_test_hint") }}</p>
          </section>

          <!-- Plein écran -->
          <div v-if="fullscreenSupported" class="flex items-center gap-3">
            <Checkbox v-model="fullscreen" binary input-id="exam-fullscreen" />
            <label for="exam-fullscreen" class="text-sm text-ink cursor-pointer">
              {{ t("session.player.fullscreen") }}
            </label>
          </div>

          <Message v-if="resumedCount > 0" severity="info" :closable="false">
            {{ t("session.player.resume_info", { n: resumedCount }, resumedCount) }}
          </Message>
        </div>

        <!-- Actions -->
        <div class="px-5 sm:px-6 py-4 border-t border-line flex flex-col-reverse sm:flex-row gap-2 sm:justify-between">
          <Button
            :label="t('session.quit')"
            text
            severity="secondary"
            @click="emit('exit')"
          />
          <Button
            :label="resumedCount > 0 ? t('session.player.resume') : t('session.player.begin')"
            icon="pi pi-play"
            @click="emit('begin', fullscreen)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n();

const emit = defineEmits<{ begin: [fullscreen: boolean]; exit: [] }>();

const props = defineProps<{
  examName: string;
  subjectNumber: number;
  blocks: { label: string; minutes: number }[];
  oralModules: string[];
  oralLink: string | null;
  hasAudio: boolean;
  resumedCount: number;
}>();

const fullscreen = ref(true);
const fullscreenSupported = ref(false);

const rules = computed(() => {
  const list = [{ key: "timer", icon: "pi-clock", text: t("session.player.rule_timer") }];
  if (props.blocks.length > 1) {
    list.push({ key: "modules", icon: "pi-list", text: t("session.player.rule_modules") });
  }
  if (props.hasAudio) {
    list.push({ key: "audio", icon: "pi-volume-up", text: t("session.player.rule_audio") });
  }
  list.push(
    { key: "saved", icon: "pi-save", text: t("session.player.rule_saved") },
    { key: "focus", icon: "pi-eye", text: t("session.player.rule_focus") },
  );
  return list;
});

// Bip de test généré par le navigateur (aucun fichier audio nécessaire)
let audioCtx: AudioContext | null = null;

function playBeep() {
  try {
    const Ctx = window.AudioContext || (window as any).webkitAudioContext;
    audioCtx ??= new Ctx();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.frequency.value = 660;
    gain.gain.value = 0.15;
    osc.connect(gain).connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.6);
  } catch {
    /* audio indisponible */
  }
}

onMounted(() => {
  fullscreenSupported.value = !!document.fullscreenEnabled;
  if (!fullscreenSupported.value) fullscreen.value = false;
});

onBeforeUnmount(() => {
  audioCtx?.close().catch(() => {});
});
</script>