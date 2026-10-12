<template>
  <div class="flex min-h-screen flex-col bg-canvas text-ink">
    <LandingNavbar />
    <main class="flex-1">
      <slot />
    </main>
    <LandingFooter />
  </div>
</template>