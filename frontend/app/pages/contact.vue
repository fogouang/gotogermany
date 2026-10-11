<script setup lang="ts">
import { SITE } from "@/config/site";

const { t } = useI18n();
const localePath = useLocalePath();

useSeo({
  title: t("seo.contact.title"),
  description: t("seo.contact.description"),
});

const form = ref({
  name: "",
  email: "",
  subject: null as string | null,
  message: "",
});
const submitted = ref(false);

const subjects = computed(() => [
  { name: t("contact.subjects.inscription"), value: "inscription" },
  { name: t("contact.subjects.tarifs"), value: "tarifs" },
  { name: t("contact.subjects.technique"), value: "technique" },
  { name: t("contact.subjects.partenariat"), value: "partenariat" },
  { name: t("contact.subjects.renseignements"), value: "renseignements" },
  { name: t("contact.subjects.autre"), value: "autre" },
]);

const emailValide = computed(() =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email.trim()),
);

const formulaireValide = computed(
  () =>
    !!form.value.name.trim() &&
    emailValide.value &&
    !!form.value.subject &&
    !!form.value.message.trim(),
);

const sujetLabel = computed(
  () => subjects.value.find((s) => s.value === form.value.subject)?.name ?? "",
);

const texteMessage = computed(
  () =>
    `${t("contact.whatsapp_greeting")}\n\n` +
    `${t("contact.form.name")} : ${form.value.name.trim()}\n` +
    `${t("contact.form.email")} : ${form.value.email.trim()}\n` +
    `${t("contact.form.subject")} : ${sujetLabel.value}\n\n` +
    form.value.message.trim(),
);

function verifier() {
  submitted.value = true;
  return formulaireValide.value;
}

function envoyerWhatsApp() {
  if (!verifier()) return;
  window.open(
    `https://wa.me/${SITE.phone}?text=${encodeURIComponent(texteMessage.value)}`,
    "_blank",
    "noopener",
  );
}

function envoyerEmail() {
  if (!verifier()) return;
  const sujet = encodeURIComponent(`GoToGermany : ${sujetLabel.value}`);
  window.location.href = `mailto:${SITE.email}?subject=${sujet}&body=${encodeURIComponent(texteMessage.value)}`;
}
</script>

<template>
  <div class="bg-canvas">
    <!-- En-tête -->
    <AppPageHero
      center
      icon="pi pi-envelope"
      watermark="Kontakt"
      :eyebrow="t('contact.badge')"
      :title="t('contact.title')"
      :subtitle="t('contact.subtitle')"
    />

    <div
      class="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1.3fr_1fr]"
    >
      <!-- Formulaire -->
      <form
        class="space-y-5 rounded-card border border-line bg-card p-6 shadow-soft sm:p-8"
        novalidate
        @submit.prevent="envoyerWhatsApp"
      >
        <div class="grid gap-5 sm:grid-cols-2">
          <div>
            <label for="name" class="mb-2 block text-sm font-medium text-ink">
              {{ t("contact.form.name") }}
            </label>
            <InputText
              id="name"
              v-model="form.name"
              autocomplete="name"
              :placeholder="t('contact.form.name_placeholder')"
              class="w-full"
              :invalid="submitted && !form.name.trim()"
            />
            <small
              v-if="submitted && !form.name.trim()"
              class="mt-1 block text-red-500"
            >
              {{ t("contact.form.name_required") }}
            </small>
          </div>

          <div>
            <label for="email" class="mb-2 block text-sm font-medium text-ink">
              {{ t("contact.form.email") }}
            </label>
            <InputText
              id="email"
              v-model="form.email"
              type="email"
              autocomplete="email"
              :placeholder="t('contact.form.email_placeholder')"
              class="w-full"
              :invalid="submitted && !emailValide"
            />
            <small
              v-if="submitted && !form.email.trim()"
              class="mt-1 block text-red-500"
            >
              {{ t("contact.form.email_required") }}
            </small>
            <small
              v-else-if="submitted && !emailValide"
              class="mt-1 block text-red-500"
            >
              {{ t("contact.form.email_invalid") }}
            </small>
          </div>
        </div>

        <div>
          <label for="subject" class="mb-2 block text-sm font-medium text-ink">
            {{ t("contact.form.subject") }}
          </label>
          <Select
            input-id="subject"
            v-model="form.subject"
            :options="subjects"
            option-label="name"
            option-value="value"
            :placeholder="t('contact.form.subject_placeholder')"
            class="w-full"
            :invalid="submitted && !form.subject"
          />
          <small
            v-if="submitted && !form.subject"
            class="mt-1 block text-red-500"
          >
            {{ t("contact.form.subject_required") }}
          </small>
        </div>

        <div>
          <label for="message" class="mb-2 block text-sm font-medium text-ink">
            {{ t("contact.form.message") }}
          </label>
          <Textarea
            id="message"
            v-model="form.message"
            rows="6"
            auto-resize
            :placeholder="t('contact.form.message_placeholder')"
            class="w-full"
            :invalid="submitted && !form.message.trim()"
          />
          <small
            v-if="submitted && !form.message.trim()"
            class="mt-1 block text-red-500"
          >
            {{ t("contact.form.message_required") }}
          </small>
        </div>

        <div class="space-y-3 pt-1">
          <AppButton
            type="submit"
            variant="gradient"
            icon="pi pi-whatsapp"
            :label="t('contact.form.submit_whatsapp')"
            class="h-12! w-full"
          />
          <p class="text-center text-xs text-faint">
            {{ t("contact.form.note") }}
          </p>
          <button
            type="button"
            class="mx-auto flex items-center gap-2 text-sm font-semibold text-primary hover:underline"
            @click="envoyerEmail"
          >
            <i class="pi pi-envelope text-xs" />
            {{ t("contact.form.or_email") }}
          </button>
        </div>
      </form>

      <!-- Informations -->
      <div class="space-y-4">
        <!-- WhatsApp -->
        <a
          :href="`https://wa.me/${SITE.phone}`"
          target="_blank"
          rel="noopener"
          class="group flex items-start gap-4 rounded-card border border-line bg-card p-5 shadow-soft transition hover:-translate-y-0.5 hover:border-emerald-500/40 hover:shadow-lift"
        >
          <span
            class="grid size-12 shrink-0 place-items-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
          >
            <i class="pi pi-whatsapp text-xl" />
          </span>
          <span>
            <span class="block font-semibold text-ink">WhatsApp</span>
            <span
              class="block font-medium text-emerald-600 dark:text-emerald-400"
              >{{ SITE.phoneLabel }}</span
            >
            <span class="mt-1 block text-sm text-muted">{{
              t("contact.info.whatsapp")
            }}</span>
          </span>
        </a>

        <!-- Email -->
        <a
          :href="`mailto:${SITE.email}`"
          class="group flex items-start gap-4 rounded-card border border-line bg-card p-5 shadow-soft transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lift"
        >
          <span
            class="grid size-12 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary"
          >
            <i class="pi pi-envelope text-xl" />
          </span>
          <span class="min-w-0">
            <span class="block font-semibold text-ink">{{
              t("contact.info.email")
            }}</span>
            <span class="block truncate font-medium text-primary">{{
              SITE.email
            }}</span>
            <span class="mt-1 block text-sm text-muted">{{
              t("contact.info.email_response")
            }}</span>
          </span>
        </a>

        <!-- Téléphone -->
        <div
          class="flex items-start gap-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <span
            class="grid size-12 shrink-0 place-items-center rounded-xl bg-accent-500/10 text-accent-600 dark:text-accent-400"
          >
            <i class="pi pi-phone text-xl" />
          </span>
          <div>
            <p class="font-semibold text-ink">{{ t("contact.info.phone") }}</p>
            <a
              :href="`tel:+${SITE.phone}`"
              class="block font-medium text-primary hover:underline"
            >
              {{ SITE.phoneLabel }}
            </a>
            <a
              :href="`tel:${SITE.phone2Label.replace(/\s/g, '')}`"
              class="block font-medium text-primary hover:underline"
            >
              {{ SITE.phone2Label }}
            </a>
            <p class="mt-1 text-sm text-muted">
              {{ t("contact.info.phone_hours") }}
            </p>
          </div>
        </div>

        <!-- Bureau -->
        <div
          class="flex items-start gap-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <span
            class="grid size-12 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary"
          >
            <i class="pi pi-map-marker text-xl" />
          </span>
          <div>
            <p class="font-semibold text-ink">{{ t("contact.info.office") }}</p>
            <p class="text-muted">{{ t("contact.info.office_location") }}</p>
            <p class="mt-1 text-sm text-faint">
              {{ t("contact.info.office_note") }}
            </p>
          </div>
        </div>

        <!-- FAQ -->
        <div
          class="relative overflow-hidden rounded-card bg-zinc-950 p-6 text-white"
        >
          <div
            class="flag-stripe absolute inset-x-0 top-0 h-1"
            aria-hidden="true"
          />
          <div class="flex items-start gap-3">
            <i class="pi pi-question-circle mt-0.5 text-xl text-accent-400" />
            <div>
              <p class="font-heading font-bold">
                {{ t("contact.info.faq_title") }}
              </p>
              <p class="mt-1 text-sm text-zinc-400">
                {{ t("contact.info.faq_desc") }}
              </p>
              <NuxtLink
                :to="localePath('/faq')"
                class="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-accent-400 hover:text-accent-300"
              >
                {{ t("contact.info.faq_btn") }}
                <i class="pi pi-arrow-right text-xs" />
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
