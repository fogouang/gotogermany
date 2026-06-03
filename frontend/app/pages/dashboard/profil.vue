<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ t('profile.title') }}</h1>
      <p class="text-gray-600">{{ t('profile.subtitle') }}</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Profile Card -->
      <Card class="lg:col-span-1">
        <template #content>
          <div class="text-center">
            <Avatar
              :label="authStore.userName[0]?.toUpperCase()"
              shape="circle" size="xlarge"
              class="bg-linear-to-br from-teal-600 to-blue-600 text-white mx-auto mb-4"
              style="width: 120px; height: 120px; font-size: 48px;"
            />
            <h2 class="text-xl font-bold text-gray-900 mb-1">{{ authStore.userName }}</h2>
            <p class="text-gray-600 mb-4">{{ authStore.userEmail }}</p>
            <div class="flex items-center justify-center gap-2 mb-4">
              <Tag v-if="authStore.isVerified"  :value="t('profile.email_verified')"     severity="success" icon="pi pi-check-circle" />
              <Tag v-else                        :value="t('profile.email_not_verified')" severity="warning" icon="pi pi-exclamation-triangle" />
            </div>
            <Divider />
            <div class="space-y-3 text-left">
              <div class="flex items-center gap-3 text-sm">
                <i class="pi pi-calendar text-gray-400"></i>
                <div>
                  <p class="text-gray-500">{{ t('profile.member_since') }}</p>
                  <p class="font-semibold">{{ formatDate(userDetails?.full_name) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 text-sm">
                <i class="pi pi-shield text-gray-400"></i>
                <div>
                  <p class="text-gray-500">{{ t('profile.status') }}</p>
                  <p class="font-semibold">{{ authStore.isAdmin ? t('profile.admin') : t('profile.user') }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Edit Profile Form -->
      <Card class="lg:col-span-2">
        <template #title>{{ t('profile.personal_info') }}</template>
        <template #content>
          <Message v-if="successMessage" severity="success" :closable="true" @close="successMessage = ''">{{ successMessage }}</Message>
          <Message v-if="errorMessage"   severity="error"   :closable="true" @close="errorMessage = ''">{{ errorMessage }}</Message>

          <form @submit.prevent="updateProfile" class="space-y-6 mt-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('profile.full_name') }}</label>
                <InputText v-model="profileForm.full_name" class="w-full" placeholder="Jean Dupont" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('profile.email') }}</label>
                <InputText :value="authStore.userEmail" class="w-full" disabled />
                <small class="text-gray-500">{{ t('profile.email_readonly') }}</small>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('profile.phone') }}</label>
                <InputText v-model="profileForm.phone" class="w-full" placeholder="+237 6XX XXX XXX" />
              </div>
            </div>
            <div class="flex justify-end gap-3 pt-4">
              <Button :label="t('profile.cancel')" severity="secondary" outlined @click="resetForm" />
              <Button :label="t('profile.save')"   icon="pi pi-save" :loading="loading" type="submit" />
            </div>
          </form>
        </template>
      </Card>
    </div>

    <!-- Change Password -->
    <Card class="mt-6">
      <template #title>{{ t('profile.change_password') }}</template>
      <template #content>
        <Message v-if="passwordSuccess" severity="success" :closable="true" @close="passwordSuccess = ''">{{ passwordSuccess }}</Message>
        <Message v-if="passwordError"   severity="error"   :closable="true" @close="passwordError = ''">{{ passwordError }}</Message>

        <form @submit.prevent="changePassword" class="space-y-6 mt-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('profile.current_password') }}</label>
              <Password v-model="passwordForm.current_password" class="w-full" toggleMask :feedback="false" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('profile.new_password') }}</label>
              <Password v-model="passwordForm.new_password" class="w-full" toggleMask />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('profile.confirm_password') }}</label>
              <Password v-model="passwordForm.confirm_password" class="w-full" toggleMask :feedback="false" />
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <Button :label="t('profile.cancel')"          severity="secondary" outlined @click="resetPasswordForm" />
            <Button :label="t('profile.change_password_btn')" icon="pi pi-lock" :loading="passwordLoading" type="submit" />
          </div>
        </form>
      </template>
    </Card>

    <!-- Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
      <Card>
        <template #title>
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <i class="pi pi-check-circle text-2xl text-blue-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">12</p>
              <p class="text-sm text-gray-600">{{ t('profile.stats_exams') }}</p>
            </div>
          </div>
        </template>
      </Card>
      <Card>
        <template #title>
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <i class="pi pi-chart-line text-2xl text-green-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">85%</p>
              <p class="text-sm text-gray-600">{{ t('profile.stats_score') }}</p>
            </div>
          </div>
        </template>
      </Card>
      <Card>
        <template #title>
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <i class="pi pi-clock text-2xl text-purple-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">24h</p>
              <p class="text-sm text-gray-600">{{ t('profile.stats_time') }}</p>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Danger Zone -->
    <Card class="mt-6 border-2 border-red-200">
      <template #title>
        <div class="flex items-center gap-2 text-red-600">
          <i class="pi pi-exclamation-triangle"></i>
          <span>{{ t('profile.danger_zone') }}</span>
        </div>
      </template>
      <template #content>
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-gray-900 mb-1">{{ t('profile.delete_account') }}</h3>
            <p class="text-sm text-gray-600">{{ t('profile.delete_desc') }}</p>
          </div>
          <Button :label="t('profile.delete_btn')" severity="danger" outlined @click="confirmDelete" />
        </div>
      </template>
    </Card>

    <!-- Delete Dialog -->
    <Dialog
      v-model:visible="deleteDialogVisible"
      :header="t('profile.delete_dialog_title')"
      :modal="true" :style="{ width: '90vw', maxWidth: '450px' }"
    >
      <div class="flex flex-col gap-4">
        <Message severity="error" :closable="false">{{ t('profile.delete_warning') }}</Message>
        <p>{{ t('profile.delete_confirm_text') }}</p>
        <div>
          <label class="block text-sm font-medium mb-2" v-html="t('profile.delete_type')" />
          <InputText v-model="deleteConfirmText" class="w-full" :placeholder="t('profile.delete_placeholder')" />
        </div>
      </div>
      <template #footer>
        <Button :label="t('profile.cancel')" text @click="deleteDialogVisible = false" />
        <Button
          :label="t('profile.delete_confirm_btn')" severity="danger"
          :disabled="deleteConfirmText !== t('profile.delete_confirm_word')"
          @click="deleteAccount"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const { t }      = useI18n()
const authStore  = useAuthStore()

const loading         = ref(false)
const passwordLoading = ref(false)
const successMessage  = ref('')
const errorMessage    = ref('')
const passwordSuccess = ref('')
const passwordError   = ref('')
const deleteDialogVisible = ref(false)
const deleteConfirmText   = ref('')

const userDetails = computed(() => authStore.user)

const profileForm = ref({ full_name: '', phone: '' })
const passwordForm = ref({ current_password: '', new_password: '', confirm_password: '' })

const initForm = () => {
  profileForm.value = {
    full_name: authStore.userName || '',
    phone:     (userDetails.value as any)?.phone || '',
  }
}

const formatDate = (dateString?: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })
}

const updateProfile = async () => {
  loading.value        = true
  successMessage.value = ''
  errorMessage.value   = ''
  const result = await authStore.updateProfile(profileForm.value.full_name, profileForm.value.phone)
  successMessage.value = result.success ? t('profile.success_update') : ''
  errorMessage.value   = result.success ? '' : (result.error || t('profile.error_update'))
  loading.value        = false
}

const resetForm = () => {
  initForm()
  successMessage.value = ''
  errorMessage.value   = ''
}

const changePassword = async () => {
  passwordSuccess.value = ''
  passwordError.value   = ''
  if (!passwordForm.value.current_password || !passwordForm.value.new_password) {
    passwordError.value = t('profile.error_fields'); return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = t('profile.error_match'); return
  }
  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = t('profile.error_length'); return
  }
  passwordLoading.value = true
  const result = await authStore.changePassword(passwordForm.value.current_password, passwordForm.value.new_password)
  if (result.success) { passwordSuccess.value = t('profile.success_password'); resetPasswordForm() }
  else passwordError.value = result.error || t('profile.error_password')
  passwordLoading.value = false
}

const resetPasswordForm = () => {
  passwordForm.value    = { current_password: '', new_password: '', confirm_password: '' }
  passwordSuccess.value = ''
  passwordError.value   = ''
}

const confirmDelete = () => { deleteDialogVisible.value = true; deleteConfirmText.value = '' }
const deleteAccount = async () => { deleteDialogVisible.value = false; authStore.logout() }

onMounted(() => initForm())
</script>