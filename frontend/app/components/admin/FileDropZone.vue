<template>
  <div class="space-y-2">
    <label
      class="flex cursor-pointer flex-col items-center justify-center gap-1.5 rounded-leaf border-2 border-dashed px-4 py-6 text-center transition-colors"
      :class="[
        dragging ? 'border-primary bg-primary/10' : 'border-line bg-card-2/50 hover:border-primary/40',
        disabled ? 'pointer-events-none opacity-60' : '',
      ]"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <i :class="icon" class="text-xl text-primary" />
      <span class="text-sm font-medium text-ink">{{ label }}</span>
      <span v-if="hint" class="text-xs text-muted">{{ hint }}</span>
      <input
        type="file"
        class="hidden"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        @change="onPick"
      />
    </label>

    <p v-if="ignored > 0" class="text-xs text-amber-600">
      {{ ignored }} fichier(s) ignoré(s) : format non accepté.
    </p>

    <ul v-if="modelValue.length" class="divide-y divide-line rounded-leaf border border-line bg-card">
      <li v-for="(file, i) in modelValue" :key="fileKey(file)" class="flex items-center gap-3 px-3 py-2">
        <i :class="icon" class="text-xs text-muted" />
        <span class="min-w-0 flex-1 truncate text-sm text-ink">{{ file.name }}</span>
        <span class="shrink-0 text-xs text-faint">{{ formatSize(file.size) }}</span>
        <Button
          icon="pi pi-times"
          text
          rounded
          size="small"
          severity="secondary"
          aria-label="Retirer"
          :disabled="disabled"
          @click="remove(i)"
        />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: File[];
    accept?: string;
    multiple?: boolean;
    label?: string;
    hint?: string;
    icon?: string;
    disabled?: boolean;
  }>(),
  {
    accept: "",
    multiple: false,
    label: "Glisse tes fichiers ici ou clique pour choisir",
    hint: "",
    icon: "pi pi-upload",
    disabled: false,
  },
);

const emit = defineEmits<{ "update:modelValue": [files: File[]] }>();

const dragging = ref(false);
const ignored = ref(0);

const fileKey = (f: File) => `${f.name}-${f.size}`;

const formatSize = (bytes: number) =>
  bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} Ko` : `${(bytes / 1024 / 1024).toFixed(1)} Mo`;

function matches(file: File) {
  if (!props.accept) return true;
  return props.accept.split(",").some((raw) => {
    const token = raw.trim().toLowerCase();
    if (token.startsWith(".")) return file.name.toLowerCase().endsWith(token);
    if (token.endsWith("/*")) return file.type.startsWith(token.slice(0, -1));
    return file.type === token;
  });
}

function add(list: File[]) {
  const accepted = list.filter(matches);
  ignored.value = list.length - accepted.length;
  if (!accepted.length) return;

  if (!props.multiple) {
    emit("update:modelValue", [accepted[0]!]);
    return;
  }
  const known = new Set(props.modelValue.map(fileKey));
  emit("update:modelValue", [...props.modelValue, ...accepted.filter((f) => !known.has(fileKey(f)))]);
}

function onPick(e: Event) {
  const input = e.target as HTMLInputElement;
  add(Array.from(input.files ?? []));
  input.value = "";
}

function onDrop(e: DragEvent) {
  dragging.value = false;
  if (props.disabled) return;
  add(Array.from(e.dataTransfer?.files ?? []));
}

function remove(index: number) {
  emit("update:modelValue", props.modelValue.filter((_, i) => i !== index));
}
</script>