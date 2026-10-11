<template>
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center gap-2">
          <i class="pi pi-flag text-2xl text-indigo-600"></i>
          <span class="text-xl font-bold text-gray-900 hidden sm:block"
            >DeutschTest</span
          >
          <span class="text-xl font-bold text-gray-900 sm:hidden">DT</span>
        </div>

        <!-- Desktop Menu -->
        <nav class="hidden md:flex items-center gap-6">
          <a
            href="#niveaux"
            class="text-gray-600 hover:text-indigo-600 transition"
            >Niveaux</a
          >
          <a
            href="#tarifs"
            class="text-gray-600 hover:text-indigo-600 transition"
            >Tarifs</a
          >
          <a
            href="/contact"
            class="text-gray-600 hover:text-indigo-600 transition"
            >Contact</a
          >
        </nav>

        <!-- Desktop Buttons -->
        <div class="hidden md:flex items-center gap-3">
          <Button label="Connexion" text />
          <Button label="Inscription" />
        </div>

        <!-- Mobile Menu Button -->
        <Button
          icon="pi pi-bars"
          text
          @click="menuVisible = true"
          class="md:hidden"
        />
      </div>
    </div>

    <!-- Mobile Sidebar -->
    <Drawer v-model:visible="menuVisible" position="right">
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-flag text-2xl text-indigo-600"></i>
          <span class="text-xl font-bold">DeutschTest</span>
        </div>
      </template>

      <div class="flex flex-col gap-4">
        <a
          href="#niveaux"
          class="p-3 hover:bg-gray-100 rounded-lg transition"
          @click="menuVisible = false"
        >
          Niveaux
        </a>
        <a
          href="#tarifs"
          class="p-3 hover:bg-gray-100 rounded-lg transition"
          @click="menuVisible = false"
        >
          Tarifs
        </a>
        <a
          href="#contact"
          class="p-3 hover:bg-gray-100 rounded-lg transition"
          @click="menuVisible = false"
        >
          Contact
        </a>

        <Divider />

        <Button label="Connexion" outlined class="w-full" />
        <Button label="Inscription" class="w-full" />
      </div>
    </Drawer>
  </header>
</template>

<script setup lang="ts">
const menuVisible = ref(false);
</script>
