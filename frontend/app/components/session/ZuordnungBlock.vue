<template>
  <div class="space-y-4">
    <!-- ── Options réutilisables (Lesen 5, Hören 4) : grille comme à l'examen ── -->
    <div
      v-if="reusable"
      class="overflow-x-auto rounded-card border border-line bg-card"
    >
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-card-2">
            <th class="px-3 py-2.5 text-left font-semibold text-muted w-1/2"></th>
            <th
              v-for="(label, key) in options"
              :key="key"
              class="px-2 py-2.5 text-center text-xs font-semibold text-ink"
            >
              {{ label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="q in questions"
            :id="`question-${q.id}`"
            :key="q.id"
            :class="[
              'border-t border-line transition-colors',
              valueOf(q) ? 'bg-primary/5' : '',
            ]"
          >
            <td class="px-3 py-3 align-middle text-ink">
              <span
                class="mr-2 inline-flex h-6 min-w-6 items-center justify-center rounded-full border border-line bg-card-2 px-1.5 text-[11px] font-bold tabular-nums text-ink"
                >{{ numberOf(q) }}</span
              >
              {{ q.content?.item }}
            </td>
            <td
              v-for="(label, key) in options"
              :key="key"
              class="px-2 py-3 text-center align-middle"
            >
              <button
                type="button"
                :aria-label="String(label)"
                :aria-pressed="isSel(q, key)"
                :class="[
                  'inline-flex h-6 w-6 items-center justify-center rounded-full border-2 transition-colors',
                  isSel(q, key)
                    ? 'border-primary bg-primary'
                    : 'border-line bg-card hover:border-primary/50',
                ]"
                @click="choose(q, key)"
              >
                <span
                  v-if="isSel(q, key)"
                  class="h-2 w-2 rounded-full bg-white"
                ></span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Options uniques (Lesen 4, Lesen 6) : liste une seule fois, puis une ligne par case ── -->
    <template v-else>
      <div class="rounded-card border border-line bg-card-2 p-4">
        <ul class="space-y-1.5">
          <li
            v-for="(label, key) in options"
            :key="key"
            :class="[
              'flex items-start gap-2 text-sm transition-opacity',
              assigned[norm(key)] ? 'opacity-50' : '',
            ]"
          >
            <span class="w-5 shrink-0 font-bold text-primary">{{
              String(key).toUpperCase()
            }}</span>
            <span
              :class="[
                'flex-1',
                assigned[norm(key)] ? 'text-faint line-through' : 'text-ink',
              ]"
              >{{ label }}</span
            >
            <span
              v-if="assigned[norm(key)]"
              class="shrink-0 rounded-full bg-primary/10 px-1.5 text-[10px] font-bold text-primary"
            >
              {{ assigned[norm(key)] }}
            </span>
          </li>
        </ul>
      </div>

      <!-- Lesen 6 : cases regroupées sous les deux notions (Ursachen / Folgen…) -->
      <div v-for="group in groups" :key="group.key" class="space-y-2">
        <p
          v-if="group.title"
          class="text-xs font-semibold uppercase tracking-wide text-faint"
        >
          {{ group.title }}
        </p>
        <div
          v-for="q in group.questions"
          :id="`question-${q.id}`"
          :key="q.id"
          :class="[
            'rounded-card border p-3 sm:p-4 transition-colors',
            valueOf(q) ? 'border-primary/30 bg-primary/5' : 'border-line bg-card',
          ]"
        >
          <div class="flex items-start gap-2 mb-2.5">
            <span
              class="inline-flex h-6 min-w-6 shrink-0 items-center justify-center rounded-full border border-line bg-card-2 px-1.5 text-[11px] font-bold tabular-nums text-ink"
              >{{ numberOf(q) }}</span
            >
            <p class="text-sm text-ink leading-relaxed pt-0.5">
              {{ itemLabel(q) }}
            </p>
          </div>

          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="(label, key) in options"
              :key="key"
              type="button"
              :title="String(label)"
              :aria-pressed="isSel(q, key)"
              :class="[
                'relative h-9 w-9 rounded-leaf border-2 text-sm font-bold transition-colors',
                chipClass(q, key),
              ]"
              @click="choose(q, key)"
            >
              {{ String(key).toUpperCase() }}
              <span
                v-if="!isSel(q, key) && takenBy(q, key)"
                class="absolute -right-1.5 -top-1.5 rounded-full border border-line bg-card-2 px-1 text-[9px] font-semibold leading-4 text-muted"
              >
                {{ takenBy(q, key) }}
              </span>
            </button>
          </div>

          <!-- Choix en clair -->
          <p v-if="valueOf(q)" class="mt-2 text-sm text-ink">
            <span class="font-bold text-primary"
              >{{ valueOf(q).toUpperCase() }})</span
            >
            {{ options[valueOf(q)] ?? options[valueOf(q).toUpperCase()] }}
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  teil: any;
  questions: any[];
  answers: Record<string, any>;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const cfg = computed<Record<string, any>>(() => props.teil.config || {});

const options = computed<Record<string, string>>(
  () => cfg.value.options || props.questions[0]?.content?.options || {},
);

const reusable = computed(
  () =>
    !!(
      cfg.value.options_reusable ??
      props.questions[0]?.content?.options_reusable
    ),
);

const norm = (v: unknown) => String(v ?? "").trim().toLowerCase();

const valueOf = (q: any): string =>
  String(props.answers[q.id]?.user_answer?.answer ?? "").trim();

const isSel = (q: any, key: string | number) =>
  valueOf(q) !== "" && norm(valueOf(q)) === norm(key);

const choose = (q: any, key: string | number) =>
  emit("answer", q.id, { answer: String(key) });

const numberOf = (q: any) => q.content?.display_number ?? q.question_number;

// « Ursachen (1) » → « (1) » quand le titre du groupe est déjà affiché
const itemLabel = (q: any) => {
  const item = String(q.content?.item ?? "");
  const group = groups.value.find((g) => g.questions.includes(q));
  return group?.title && item.startsWith(group.title)
    ? item.slice(group.title.length).trim() || item
    : item;
};

// Options déjà attribuées { lettre: numéro de la question }
const assigned = computed<Record<string, number>>(() => {
  const out: Record<string, number> = {};
  for (const q of props.questions) {
    const v = norm(valueOf(q));
    if (v) out[v] = numberOf(q);
  }
  return out;
});

const takenBy = (q: any, key: string | number) => {
  const owner = assigned.value[norm(key)];
  return owner && owner !== numberOf(q) ? owner : null;
};

const chipClass = (q: any, key: string | number) => {
  if (isSel(q, key)) return "border-primary bg-primary text-white";
  if (takenBy(q, key))
    return "border-dashed border-line bg-card-2 text-faint hover:border-primary/40";
  return "border-line bg-card text-ink hover:border-primary/40";
};

// Lesen 6 : groupes dans l'ordre des questions (slot_group), titre tiré de begriffspaar
const groups = computed(() => {
  const begriffe: string[] = cfg.value.begriffspaar || [];
  const out: { key: string; title: string; questions: any[] }[] = [];
  for (const q of props.questions) {
    const key = String(q.content?.slot_group ?? "");
    let g = out.find((x) => x.key === key);
    if (!g) {
      const title = key
        ? begriffe.find((b) => norm(String(q.content?.item ?? "")).startsWith(norm(b))) ?? ""
        : "";
      g = { key, title, questions: [] };
      out.push(g);
    }
    g.questions.push(q);
  }
  return out;
});
</script>