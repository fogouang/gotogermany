<template>
  <div class="flex gap-2">
    <Select
      v-model="countryIso"
      :options="options"
      optionLabel="label"
      optionValue="iso"
      filter
      :filterFields="['label', 'dial']"
      class="w-32 shrink-0"
      :invalid="invalid"
      :aria-label="t('auth.country')"
      @update:modelValue="emitValue"
    >
      <template #value="{ value }">
        <span class="text-sm font-medium text-ink">
          {{ value }} <span class="text-muted">+{{ countryByIso(value)?.dial }}</span>
        </span>
      </template>
      <template #option="{ option }">
        <span class="flex w-full items-center justify-between gap-3 text-sm">
          <span class="truncate">{{ option.name }}</span>
          <span class="shrink-0 text-muted">+{{ option.dial }}</span>
        </span>
      </template>
    </Select>

    <InputText
      :id="inputId"
      v-model="localNumber"
      type="tel"
      inputmode="tel"
      autocomplete="tel-national"
      :placeholder="t('auth.phone_placeholder')"
      class="min-w-0 flex-1"
      :invalid="invalid"
      @update:modelValue="emitValue"
    />
  </div>
</template>

<script setup lang="ts">
import { DEFAULT_PHONE_COUNTRY, PHONE_COUNTRIES, type PhoneCountry } from "~/config/countries";

const props = defineProps<{
  /** Numéro au format international (+XXXXXXXX) ou "" */
  modelValue: string | null | undefined;
  inputId?: string;
  invalid?: boolean;
}>();

const emit = defineEmits<{ "update:modelValue": [value: string] }>();

const { t, locale } = useI18n();

const countryByIso = (iso: string): PhoneCountry | undefined => PHONE_COUNTRIES.find((c) => c.iso === iso);

// Noms de pays dans la langue de l'interface, sans clé de traduction
const options = computed(() => {
  let names: Intl.DisplayNames | null = null;
  try {
    names = new Intl.DisplayNames([locale.value], { type: "region" });
  } catch {
    names = null;
  }
  return PHONE_COUNTRIES.map((c) => {
    const name = names?.of(c.iso) ?? c.iso;
    return { ...c, name, label: `${name} +${c.dial}` };
  });
});

/** Pays par défaut : région de la langue du navigateur si on la propose, sinon Cameroun */
function detectCountry(): string {
  if (import.meta.client) {
    const region = navigator.language?.split("-")[1]?.toUpperCase();
    if (region && countryByIso(region)) return region;
  }
  return DEFAULT_PHONE_COUNTRY;
}

const countryIso = ref(DEFAULT_PHONE_COUNTRY);
const localNumber = ref("");

/** Numéro national saisi -> format international */
function toInternational(): string {
  const country = countryByIso(countryIso.value);
  let digits = localNumber.value.replace(/\D/g, "");
  if (!digits || !country) return "";
  if (country.trunkZero) digits = digits.replace(/^0+/, "");
  return `+${country.dial}${digits}`;
}

/** "+237690000000" -> pays CM + "690000000" (indicatif le plus long qui correspond) */
function fromInternational(value: string) {
  const digits = value.replace(/\D/g, "");
  const match = [...PHONE_COUNTRIES]
    .sort((a, b) => b.dial.length - a.dial.length)
    .find((c) => digits.startsWith(c.dial));
  if (match && value.trim().startsWith("+")) {
    countryIso.value = match.iso;
    localNumber.value = digits.slice(match.dial.length);
  } else {
    // Ancien numéro enregistré sans indicatif : on le garde tel quel
    localNumber.value = digits;
  }
}

function emitValue() {
  emit("update:modelValue", toInternational());
}

// Valeur fournie par le parent : numéro existant (profil), remise à zéro (après inscription)...
watch(
  () => props.modelValue,
  (value) => {
    if (!value) {
      localNumber.value = "";
      return;
    }
    // On ne relit que si la valeur ne vient pas de notre propre saisie
    if (value !== toInternational()) fromInternational(value);
  },
  { immediate: true },
);

onMounted(() => {
  if (!props.modelValue) countryIso.value = detectCountry();
});
</script>