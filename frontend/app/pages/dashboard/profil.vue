<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Mon profil</h1>
      <p class="text-gray-600">Gérez vos informations personnelles</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Profile Card -->
      <Card class="lg:col-span-1">
        <template #content>
          <div class="text-center">
            <Avatar 
              :label="authStore.userName[0]?.toUpperCase()" 
              shape="circle"
              size="xlarge"
              class="bg-linear-to-br from-teal-600 to-blue-600 text-white mx-auto mb-4"
              style="width: 120px; height: 120px; font-size: 48px;"
            />
            
            <h2 class="text-xl font-bold text-gray-900 mb-1">
              {{ authStore.userName }}
            </h2>
            <p class="text-gray-600 mb-4">{{ authStore.userEmail }}</p>
            
            <div class="flex items-center justify-center gap-2 mb-4">
              <Tag 
                v-if="authStore.isVerified" 
                value="Email vérifié" 
                severity="success"
                icon="pi pi-check-circle"
              />
              <Tag 
                v-else 
                value="Email non vérifié" 
                severity="warning"
                icon="pi pi-exclamation-triangle"
              />
            </div>

            <Divider />

            <div class="space-y-3 text-left">
              <div class="flex items-center gap-3 text-sm">
                <i class="pi pi-calendar text-gray-400"></i>
                <div>
                  <p class="text-gray-500">Membre depuis</p>
                  <p class="font-semibold">{{ formatDate(userDetails?.full_name) }}</p>
                </div>
              </div>
              
              <div class="flex items-center gap-3 text-sm">
                <i class="pi pi-shield text-gray-400"></i>
                <div>
                  <p class="text-gray-500">Statut</p>
                  <p class="font-semibold">{{ authStore.isAdmin ? 'Administrateur' : 'Utilisateur' }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Edit Profile Form -->
      <Card class="lg:col-span-2">
        <template #title>Informations personnelles</template>
        <template #content>
          <Message v-if="successMessage" severity="success" :closable="true" @close="successMessage = ''">
            {{ successMessage }}
          </Message>
          
          <Message v-if="errorMessage" severity="error" :closable="true" @close="errorMessage = ''">
            {{ errorMessage }}
          </Message>

          <form @submit.prevent="updateProfile" class="space-y-6 mt-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Full Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Nom complet
                </label>
                <InputText 
                  v-model="profileForm.full_name" 
                  class="w-full"
                  placeholder="Jean Dupont"
                />
              </div>

              <!-- Email (readonly) -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <InputText 
                  :value="authStore.userEmail" 
                  class="w-full"
                  disabled
                />
                <small class="text-gray-500">L'email ne peut pas être modifié</small>
              </div>

              <!-- Phone -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone
                </label>
                <InputText 
                  v-model="profileForm.phone" 
                  class="w-full"
                  placeholder="+237 6XX XXX XXX"
                />
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-4">
              <Button 
                label="Annuler"
                severity="secondary"
                outlined
                @click="resetForm"
              />
              <Button 
                label="Enregistrer"
                icon="pi pi-save"
                :loading="loading"
                type="submit"
              />
            </div>
          </form>
        </template>
      </Card>
    </div>

    <!-- Change Password Section -->
    <Card class="mt-6">
      <template #title>Changer le mot de passe</template>
      <template #content>
        <Message v-if="passwordSuccess" severity="success" :closable="true" @close="passwordSuccess = ''">
          {{ passwordSuccess }}
        </Message>
        
        <Message v-if="passwordError" severity="error" :closable="true" @close="passwordError = ''">
          {{ passwordError }}
        </Message>

        <form @submit.prevent="changePassword" class="space-y-6 mt-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Current Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe actuel
              </label>
              <Password 
                v-model="passwordForm.current_password" 
                class="w-full"
                toggleMask
                :feedback="false"
              />
            </div>

            <!-- New Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Nouveau mot de passe
              </label>
              <Password 
                v-model="passwordForm.new_password" 
                class="w-full"
                toggleMask
              />
            </div>

            <!-- Confirm Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Confirmer le mot de passe
              </label>
              <Password 
                v-model="passwordForm.confirm_password" 
                class="w-full"
                toggleMask
                :feedback="false"
              />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <Button 
              label="Annuler"
              severity="secondary"
              outlined
              @click="resetPasswordForm"
            />
            <Button 
              label="Changer le mot de passe"
              icon="pi pi-lock"
              :loading="passwordLoading"
              type="submit"
            />
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
              <p class="text-sm text-gray-600">Examens complétés</p>
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
              <p class="text-sm text-gray-600">Score moyen</p>
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
              <p class="text-sm text-gray-600">Temps d'étude</p>
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
          <span>Zone dangereuse</span>
        </div>
      </template>
      <template #content>
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-gray-900 mb-1">Supprimer mon compte</h3>
            <p class="text-sm text-gray-600">
              Une fois votre compte supprimé, toutes vos données seront définitivement perdues.
            </p>
          </div>
          <Button 
            label="Supprimer le compte"
            severity="danger"
            outlined
            @click="confirmDelete"
          />
        </div>
      </template>
    </Card>

    <!-- Delete Confirmation Dialog -->
    <Dialog
      v-model:visible="deleteDialogVisible"
      header="Supprimer votre compte ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '450px' }"
    >
      <div class="flex flex-col gap-4">
        <Message severity="error" :closable="false">
          Cette action est irréversible !
        </Message>
        <p>
          Êtes-vous absolument sûr de vouloir supprimer votre compte ? 
          Toutes vos données, y compris vos résultats d'examens, seront définitivement supprimées.
        </p>
        <div>
          <label class="block text-sm font-medium mb-2">
            Tapez "<strong>SUPPRIMER</strong>" pour confirmer
          </label>
          <InputText 
            v-model="deleteConfirmText" 
            class="w-full"
            placeholder="SUPPRIMER"
          />
        </div>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="deleteDialogVisible = false" />
        <Button 
          label="Supprimer définitivement" 
          severity="danger"
          :disabled="deleteConfirmText !== 'SUPPRIMER'"
          @click="deleteAccount"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
});

const authStore = useAuthStore();

const loading = ref(false);
const passwordLoading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const passwordSuccess = ref('');
const passwordError = ref('');
const deleteDialogVisible = ref(false);
const deleteConfirmText = ref('');

const userDetails = computed(() => authStore.user);

const profileForm = ref({
  full_name: '',
  phone: '',
});

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

// Initialize form with current user data
const initForm = () => {
  profileForm.value = {
    full_name: authStore.userName || '',
    phone: (userDetails.value as any)?.phone || '',
  };
};

const formatDate = (dateString?: string) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const updateProfile = async () => {
  loading.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  const result = await authStore.updateProfile(
    profileForm.value.full_name,
    profileForm.value.phone
  );

  if (result.success) {
    successMessage.value = 'Profil mis à jour avec succès !';
  } else {
    errorMessage.value = result.error || 'Erreur lors de la mise à jour';
  }

  loading.value = false;
};

const resetForm = () => {
  initForm();
  successMessage.value = '';
  errorMessage.value = '';
};

const changePassword = async () => {
  passwordSuccess.value = '';
  passwordError.value = '';

  // Validation
  if (!passwordForm.value.current_password || !passwordForm.value.new_password) {
    passwordError.value = 'Veuillez remplir tous les champs';
    return;
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'Les mots de passe ne correspondent pas';
    return;
  }

  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = 'Le mot de passe doit contenir au moins 8 caractères';
    return;
  }

  passwordLoading.value = true;

  const result = await authStore.changePassword(
    passwordForm.value.current_password,
    passwordForm.value.new_password
  );

  if (result.success) {
    passwordSuccess.value = 'Mot de passe changé avec succès !';
    resetPasswordForm();
  } else {
    passwordError.value = result.error || 'Erreur lors du changement de mot de passe';
  }

  passwordLoading.value = false;
};

const resetPasswordForm = () => {
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: '',
  };
  passwordSuccess.value = '';
  passwordError.value = '';
};

const confirmDelete = () => {
  deleteDialogVisible.value = true;
  deleteConfirmText.value = '';
};

const deleteAccount = async () => {
  // TODO: Implémenter la suppression de compte via l'API
  console.log('Delete account');
  deleteDialogVisible.value = false;
  
  // Pour l'instant, déconnecter l'utilisateur
  authStore.logout();
};

// Initialize on mount
onMounted(() => {
  initForm();
});
</script>