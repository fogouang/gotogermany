<template>
  <AppShell role="admin">
    <template #header-actions>
      <NuxtLink
        to="/dashboard"
        class="hidden h-10 items-center gap-2 rounded-leaf border border-line bg-card px-3 text-sm font-medium text-muted shadow-soft transition-colors hover:border-primary/30 hover:text-primary sm:inline-flex"
      >
        <i class="pi pi-external-link text-xs" />
        Site
      </NuxtLink>
    </template>
    <slot />
  </AppShell>
</template>