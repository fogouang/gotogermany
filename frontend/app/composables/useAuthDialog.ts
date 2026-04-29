/**
 * composables/useAuthDialog.ts
 * État partagé entre Navbar et Hero pour les dialogs login/signup
 */
const loginVisible = ref(false)
const signupVisible = ref(false)

export const useAuthDialog = () => {
  const openLogin = () => {
    signupVisible.value = false
    loginVisible.value = true
  }

  const openSignup = () => {
    loginVisible.value = false
    signupVisible.value = true
  }

  const closeAll = () => {
    loginVisible.value = false
    signupVisible.value = false
  }

  return {
    loginVisible,
    signupVisible,
    openLogin,
    openSignup,
    closeAll,
  }
}