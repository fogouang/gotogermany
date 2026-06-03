<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Hero -->
    <section class="bg-gradient-primary text-white py-20 relative overflow-hidden">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;"></div>
      </div>
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
        <div class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-semibold mb-6 animate-fade-in-down">
          <i class="pi pi-question-circle"></i>
          <span>{{ t('faq.badge') }}</span>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold mb-6 animate-fade-in-up" style="animation-delay: 0.2s">
          {{ t('faq.title') }}
        </h1>
        <p class="text-xl text-teal-100 animate-fade-in-up" style="animation-delay: 0.3s">
          {{ t('faq.subtitle') }}
        </p>
      </div>
      <div class="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 80" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full">
          <path d="M0 0L60 8C120 16 240 32 360 37.3C480 43 600 37 720 32C840 27 960 21 1080 21.3C1200 21 1320 27 1380 29.3L1440 32V80H1380C1320 80 1200 80 1080 80C960 80 840 80 720 80C600 80 480 80 360 80C240 80 120 80 60 80H0V0Z" fill="rgb(249, 250, 251)" />
        </svg>
      </div>
    </section>

    <!-- FAQ Content -->
    <section class="py-16 -mt-8">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">

        <!-- Catégories -->
        <div class="grid sm:grid-cols-4 gap-4 mb-12">
          <button
            v-for="category in categories" :key="category.id"
            :class="['p-4 rounded-xl border-2 transition-all duration-300 text-left group',
              selectedCategory === category.id
                ? 'border-teal-600 bg-teal-50 shadow-lg'
                : 'border-gray-200 bg-white hover:border-teal-300 hover:shadow-md']"
            @click="selectedCategory = category.id"
          >
            <div class="flex items-center gap-3">
              <div :class="['w-12 h-12 rounded-lg flex items-center justify-center transition-all',
                selectedCategory === category.id ? 'bg-gradient-primary' : 'bg-gray-100 group-hover:bg-teal-100']">
                <i :class="[category.icon, 'text-xl', selectedCategory === category.id ? 'text-white' : 'text-gray-600']"></i>
              </div>
              <div>
                <h3 :class="['font-semibold', selectedCategory === category.id ? 'text-teal-900' : 'text-gray-900']">
                  {{ category.label }}
                </h3>
                <p class="text-sm text-gray-500">{{ category.count }} questions</p>
              </div>
            </div>
          </button>
        </div>

        <!-- Accordion -->
        <Accordion :value="activeIndex" @update:value="activeIndex = $event" class="space-y-4">
          <AccordionPanel
            v-for="(faq, index) in filteredFaqs" :key="index" :value="index"
            class="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-teal-600 transition-all duration-300 bg-white"
          >
            <AccordionHeader class="px-6 py-4 hover:bg-teal-50 transition-colors">
              <div class="flex items-start gap-4 w-full">
                <div class="w-10 h-10 bg-gradient-secondary rounded-lg flex items-center justify-center shrink-0 mt-1">
                  <i class="pi pi-question text-white"></i>
                </div>
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900 text-left">{{ faq.question }}</h3>
                </div>
              </div>
            </AccordionHeader>
            <AccordionContent class="px-6 py-4 bg-gray-50">
              <div class="ml-14 text-gray-700 leading-relaxed" v-html="faq.answer"></div>
            </AccordionContent>
          </AccordionPanel>
        </Accordion>

        <!-- CTA -->
        <Card class="mt-12 border-2 border-teal-200 bg-linear-to-br from-teal-50 to-white">
          <template #content>
            <div class="text-center py-6">
              <div class="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-headphones text-3xl text-white"></i>
              </div>
              <h3 class="text-2xl font-bold text-gray-900 mb-3">{{ t('faq.cta_title') }}</h3>
              <p class="text-gray-600 mb-6 max-w-2xl mx-auto">{{ t('faq.cta_desc') }}</p>
              <Button
                :label="t('faq.cta_btn')" icon="pi pi-envelope" iconPos="right"
                class="bg-gradient-primary! border-0! text-white! hover:opacity-90 transition-opacity"
                @click="navigateTo('/contact')"
              />
            </div>
          </template>
        </Card>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

useHead({
  title:  t('faq.page_title'),
  meta: [{ name: 'description', content: t('faq.page_desc') }],
})

const selectedCategory = ref('all')
const activeIndex      = ref()

const categories = computed(() => [
  { id: 'all',       label: t('faq.categories.all'),       icon: 'pi pi-list', count: 12 },
  { id: 'exams',     label: t('faq.categories.exams'),     icon: 'pi pi-book', count: 5  },
  { id: 'account',   label: t('faq.categories.account'),   icon: 'pi pi-user', count: 4  },
  { id: 'technical', label: t('faq.categories.technical'), icon: 'pi pi-cog',  count: 3  },
])

const faqs = computed(() => [
  { category: 'exams',     question: t('faq.questions.exams_1.q'),     answer: t('faq.questions.exams_1.a')     },
  { category: 'exams',     question: t('faq.questions.exams_2.q'),     answer: t('faq.questions.exams_2.a')     },
  { category: 'exams',     question: t('faq.questions.exams_3.q'),     answer: t('faq.questions.exams_3.a')     },
  { category: 'exams',     question: t('faq.questions.exams_4.q'),     answer: t('faq.questions.exams_4.a')     },
  { category: 'exams',     question: t('faq.questions.exams_5.q'),     answer: t('faq.questions.exams_5.a')     },
  { category: 'account',   question: t('faq.questions.account_1.q'),   answer: t('faq.questions.account_1.a')   },
  { category: 'account',   question: t('faq.questions.account_2.q'),   answer: t('faq.questions.account_2.a')   },
  { category: 'account',   question: t('faq.questions.account_3.q'),   answer: t('faq.questions.account_3.a')   },
  { category: 'account',   question: t('faq.questions.account_4.q'),   answer: t('faq.questions.account_4.a')   },
  { category: 'technical', question: t('faq.questions.technical_1.q'), answer: t('faq.questions.technical_1.a') },
  { category: 'technical', question: t('faq.questions.technical_2.q'), answer: t('faq.questions.technical_2.a') },
  { category: 'technical', question: t('faq.questions.technical_3.q'), answer: t('faq.questions.technical_3.a') },
])

const filteredFaqs = computed(() =>
  selectedCategory.value === 'all' ? faqs.value : faqs.value.filter(f => f.category === selectedCategory.value)
)
</script>

<style scoped>
@keyframes fade-in-down { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fade-in-up   { from { opacity: 0; transform: translateY(20px);  } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in-down { animation: fade-in-down 0.6s ease-out; animation-fill-mode: both; }
.animate-fade-in-up   { animation: fade-in-up   0.6s ease-out; animation-fill-mode: both; }
.bg-gradient-primary  { background: linear-gradient(135deg, hsl(145 63% 32%) 0%, hsl(145 50% 22%) 100%); }
.bg-gradient-secondary{ background: linear-gradient(135deg, hsl(45 92% 55%)  0%, hsl(35 90% 50%)  100%); }
:deep(.p-accordion-content-enter-active) { animation: accordion-expand  400ms cubic-bezier(0.65, 0, 0.35, 1); }
:deep(.p-accordion-content-leave-active) { animation: accordion-collapse 400ms cubic-bezier(0.65, 0, 0.35, 1); }
@keyframes accordion-expand   { from { opacity: 0; max-height: 0;   transform: scale(0.95); } to { opacity: 1; max-height: 500px; transform: scale(1); } }
@keyframes accordion-collapse { from { opacity: 1; max-height: 500px; transform: scale(1); } to { opacity: 0; max-height: 0;   transform: scale(0.95); } }
</style>