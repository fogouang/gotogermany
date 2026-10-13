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

onMounted(() => {
  if (!props.modelValue) countryIso.value = detectCountry();
});

/** Numéro national saisi -> format international */
function toInternational(): string {
  const country = countryByIso(countryIso.value);
  let digits = localNumber.value.replace(/\D/g, "");
  if (!digits || !country) return "";
  if (country.trunkZero) digits = digits.replace(/^0+/, "");
  return `+${country.dial}${digits}`;
}

function emitValue() {
  emit("update:modelValue", toInternational());
}

// Remise à zéro par le parent (ex. après une inscription réussie)
watch(
  () => props.modelValue,
  (value) => {
    if (!value) localNumber.value = "";
  },
);
</script>