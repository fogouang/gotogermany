<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4">
    <div class="max-w-4xl mx-auto mb-16">

      <!-- En-tête -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center gap-2 bg-teal-50 text-teal-800 px-4 py-2 rounded-full text-sm font-semibold mb-4">
          <i class="pi pi-envelope"></i>
          <span>{{ t('contact.badge') }}</span>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">{{ t('contact.title') }}</h1>
        <p class="text-lg text-gray-600">{{ t('contact.subtitle') }}</p>
      </div>

      <div class="grid md:grid-cols-2 gap-8">

        <!-- Formulaire -->
        <Card class="shadow-xl border-2 border-gray-200">
          <template #content>
            <form @submit.prevent="handleSubmit" class="space-y-6">

              <!-- Nom -->
              <div>
                <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                  <i class="pi pi-user text-teal-600"></i> {{ t('contact.form.name') }}
                </label>
                <InputText
                  id="name" v-model="form.name"
                  :placeholder="t('contact.form.name_placeholder')"
                  class="w-full" :invalid="submitted && !form.name"
                />
                <small v-if="submitted && !form.name" class="text-red-500">
                  {{ t('contact.form.name_required') }}
                </small>
              </div>

              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                  <i class="pi pi-at text-teal-600"></i> Email
                </label>
                <InputText
                  id="email" v-model="form.email" type="email"
                  :placeholder="t('contact.form.email_placeholder')"
                  class="w-full" :invalid="submitted && !form.email"
                />
                <small v-if="submitted && !form.email" class="text-red-500">
                  {{ t('contact.form.email_required') }}
                </small>
              </div>

              <!-- Sujet -->
              <div>
                <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
                  <i class="pi pi-tag text-teal-600"></i> {{ t('contact.form.subject') }}
                </label>
                <Select
                  id="subject" v-model="form.subject"
                  :options="subjects" optionLabel="name"
                  :placeholder="t('contact.form.subject_placeholder')"
                  class="w-full" :invalid="submitted && !form.subject"
                />
                <small v-if="submitted && !form.subject" class="text-red-500">
                  {{ t('contact.form.subject_required') }}
                </small>
              </div>

              <!-- Message -->
              <div>
                <label for="message" class="block text-sm font-medium text-gray-700 mb-2">
                  <i class="pi pi-comment text-teal-600"></i> {{ t('contact.form.message') }}
                </label>
                <Textarea
                  id="message" v-model="form.message" rows="5"
                  :placeholder="t('contact.form.message_placeholder')"
                  class="w-full" :invalid="submitted && !form.message"
                />
                <small v-if="submitted && !form.message" class="text-red-500">
                  {{ t('contact.form.message_required') }}
                </small>
              </div>

              <Button
                type="submit" :label="t('contact.form.submit')"
                icon="pi pi-send"
                class="w-full bg-gradient-primary! border-0! text-white! hover:opacity-90"
                :loading="loading"
              />
            </form>
          </template>
        </Card>

        <!-- Informations -->
        <div class="space-y-6">

          <!-- Email -->
          <Card class="shadow-lg hover:shadow-xl transition-all border-2 border-gray-200 hover:border-teal-600 group">
            <template #content>
              <div class="flex items-start gap-4">
                <div class="bg-gradient-primary p-3 rounded-lg group-hover:scale-110 transition-transform">
                  <i class="pi pi-envelope text-2xl text-white"></i>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 mb-1">Email</h3>
                  <a href="mailto:lfogouang39@gmail.com" class="text-teal-700 hover:text-teal-800 font-medium">
                    lfogouang39@gmail.com
                  </a>
                  <p class="text-sm text-gray-500 mt-1">{{ t('contact.info.email_response') }}</p>
                </div>
              </div>
            </template>
          </Card>

          <!-- Téléphone -->
          <Card class="shadow-lg hover:shadow-xl transition-all border-2 border-gray-200 hover:border-teal-600 group">
            <template #content>
              <div class="flex items-start gap-4">
                <div class="bg-gradient-secondary p-3 rounded-lg group-hover:scale-110 transition-transform">
                  <i class="pi pi-phone text-2xl text-white"></i>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 mb-1">{{ t('contact.info.phone') }}</h3>
                  <div class="space-y-1">
                    <a href="tel:+237691850913" class="block text-teal-700 hover:text-teal-800 font-medium">+237 691 85 09 13</a>
                    <a href="tel:+237670886288" class="block text-teal-700 hover:text-teal-800 font-medium">+237 670 88 62 88</a>
                  </div>
                  <p class="text-sm text-gray-500 mt-1">{{ t('contact.info.phone_hours') }}</p>
                </div>
              </div>
            </template>
          </Card>

          <!-- WhatsApp -->
          <Card class="shadow-lg hover:shadow-xl transition-all border-2 border-gray-200 hover:border-green-600 group">
            <template #content>
              <div class="flex items-start gap-4">
                <div class="bg-green-500 p-3 rounded-lg group-hover:scale-110 transition-transform">
                  <i class="pi pi-whatsapp text-2xl text-white"></i>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 mb-1">WhatsApp</h3>
                  <a href="https://wa.me/237691850913" target="_blank" class="text-green-600 hover:text-green-700 font-medium">
                    +237 691 85 09 13
                  </a>
                  <p class="text-sm text-gray-500 mt-1">{{ t('contact.info.whatsapp') }}</p>
                </div>
              </div>
            </template>
          </Card>

          <!-- Bureau -->
          <Card class="shadow-lg hover:shadow-xl transition-all border-2 border-gray-200 hover:border-teal-600 group">
            <template #content>
              <div class="flex items-start gap-4">
                <div class="bg-gradient-primary p-3 rounded-lg group-hover:scale-110 transition-transform">
                  <i class="pi pi-map-marker text-2xl text-white"></i>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 mb-1">{{ t('contact.info.office') }}</h3>
                  <p class="text-gray-600">{{ t('contact.info.office_location') }}</p>
                  <p class="text-sm text-gray-500 mt-1">{{ t('contact.info.office_note') }}</p>
                </div>
              </div>
            </template>
          </Card>

          <!-- FAQ -->
          <Card class="shadow-lg bg-linear-to-br from-teal-50 to-teal-100 border-2 border-teal-200">
            <template #content>
              <div class="flex items-start gap-3">
                <i class="pi pi-info-circle text-xl text-teal-600 mt-1"></i>
                <div>
                  <h3 class="font-semibold text-gray-900 mb-2">{{ t('contact.info.faq_title') }}</h3>
                  <p class="text-sm text-gray-600 mb-3">{{ t('contact.info.faq_desc') }}</p>
                  <Button
                    :label="t('contact.info.faq_btn')"
                    icon="pi pi-arrow-right" iconPos="right"
                    text size="small"
                    class="text-teal-700! hover:bg-teal-200/50!"
                    @click="navigateTo('/faq')"
                  />
                </div>
              </div>
            </template>
          </Card>

        </div>
      </div>
    </div>

    <Toast position="top-right" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
const { t } = useI18n();

useHead({
  title: "Contact - GotoGermany",
  meta: [
    {
      name: "description",
      content:
        "Contactez l'équipe DeutschTest pour toute question sur nos examens d'allemand. Téléphone, email, WhatsApp disponibles.",
    },
  ],
});

const toast = useToast();

const form = ref({
  name: "",
  email: "",
  subject: null,
  message: "",
});

const subjects = computed(() => [
  { name: t("contact.subjects.inscription"), value: "inscription" },
  { name: t("contact.subjects.tarifs"), value: "tarifs" },
  { name: t("contact.subjects.technique"), value: "technique" },
  { name: t("contact.subjects.partenariat"), value: "partenariat" },
  { name: t("contact.subjects.renseignements"), value: "renseignements" },
  { name: t("contact.subjects.autre"), value: "autre" },
]);

const submitted = ref(false);
const loading = ref(false);

const handleSubmit = async () => {
  submitted.value = true;
  if (
    !form.value.name ||
    !form.value.email ||
    !form.value.subject ||
    !form.value.message
  ) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: t("contact.form.error_fill"),
      life: 3000,
    });
    return;
  }
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
    toast.add({
      severity: "success",
      summary: t("contact.form.success_summary"),
      detail: t("contact.form.success_detail"),
      life: 5000,
    });
    form.value = { name: "", email: "", subject: null, message: "" };
    submitted.value = false;
  }, 2000);
};

const goToFAQ = () => {
  // Navigation vers FAQ (à implémenter)
  navigateTo("/faq");
};
</script>

<style scoped>
/* Animations d'entrée */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in-left {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out;
  animation-fill-mode: both;
}

.animate-slide-in-left {
  animation: slide-in-left 0.6s ease-out;
}

.animate-slide-in-right {
  animation: slide-in-right 0.6s ease-out;
}

/* Animations PrimeVue Dialog */
:deep(.p-dialog-enter-active) {
  animation: demo-dialog-in 500ms ease-out;
}

:deep(.p-dialog-leave-active) {
  animation: demo-dialog-out 500ms ease-in;
}

@keyframes demo-dialog-in {
  from {
    opacity: 0;
    transform: translateY(-10%) scale(1.1);
    filter: blur(10px);
  }
}

@keyframes demo-dialog-out {
  to {
    opacity: 0;
    transform: translateY(200%) rotate(-90deg);
  }
}

/* Animations Collapse */
:deep(.p-collapsible-enter-active) {
  animation: demo-collapsible-expand 500ms cubic-bezier(0.65, 0, 0.35, 1);
}

:deep(.p-collapsible-leave-active) {
  animation: demo-collapsible-collapse 500ms cubic-bezier(0.65, 0, 0.35, 1);
}

@keyframes demo-collapsible-expand {
  from {
    opacity: 0;
    grid-template-rows: 0fr;
    transform: scale(0.93);
  }
  to {
    opacity: 1;
    grid-template-rows: 1fr;
  }
}

@keyframes demo-collapsible-collapse {
  from {
    opacity: 1;
    grid-template-rows: 1fr;
  }
  to {
    opacity: 0;
    grid-template-rows: 0fr;
    transform: scale(0.93);
  }
}

/* Gradients */
.bg-gradient-primary {
  background: linear-gradient(
    135deg,
    hsl(145 63% 32%) 0%,
    hsl(145 50% 22%) 100%
  );
}

.bg-gradient-secondary {
  background: linear-gradient(135deg, hsl(45 92% 55%) 0%, hsl(35 90% 50%) 100%);
}
</style>
