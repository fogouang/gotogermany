<template>
  <Button label="Click me" />
  <Dialog v-model:visible="visible" header="Test">
    <p>Contenu</p>
  </Dialog>
</template>

<script setup>
const visible = ref(false);
</script>