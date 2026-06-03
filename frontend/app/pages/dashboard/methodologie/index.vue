<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <p class="text-xs font-bold uppercase tracking-widest text-green-600 mb-1">
        Guide de rédaction
      </p>
      <h1 class="text-2xl font-bold text-gray-900">Méthodologie Schreiben</h1>
      <p class="text-sm text-gray-500 mt-1">
        Structures attendues, formules clés et conseils par examen et niveau.
      </p>
    </div>

    <!-- Tabs examen -->
    <TabView v-model:value="activeExam" class="methodologie-tabs">
      <!-- ═══════════════════════════════════════════════
           TELC
      ═══════════════════════════════════════════════ -->
      <TabPanel value="telc">
        <template #header>
          <span class="flex items-center gap-2 px-1">
            <span class="w-2 h-2 rounded-full bg-purple-500"></span>
            TELC
          </span>
        </template>

        <div class="space-y-4 pt-4">
          <!-- Sous-tabs niveau -->
          <TabView v-model:value="activeTelcLevel">
            <TabPanel header="B1" value="b1">
              <div class="space-y-4 pt-4">
                <MethodCard
                  icon="pi-envelope"
                  icon-color="text-green-600"
                  bg-color="bg-green-50"
                  border-color="border-green-200"
                  title="E-mail informelle"
                  badge="45 pts · min. 120 mots"
                  badge-color="bg-green-100 text-green-700"
                >
                  <StructureList :items="telcB1Structure" />
                  <ConnectorBlock :items="telcB1Connectors" />
                  <ExampleBlock :text="telcB1Example" />
                  <PenaltyBlock :items="telcB1Penalties" />
                </MethodCard>
              </div>
            </TabPanel>

            <TabPanel header="B2" value="b2">
              <div class="space-y-4 pt-4">
                <MethodCard
                  icon="pi-file-edit"
                  icon-color="text-purple-600"
                  bg-color="bg-purple-50"
                  border-color="border-purple-200"
                  title="Lettre de réclamation (Beschwerde)"
                  badge="45 pts · min. 150 mots"
                  badge-color="bg-purple-100 text-purple-700"
                >
                  <StructureList :items="telcB2Structure" />
                  <ConnectorBlock :items="telcB2Connectors" />
                  <ExampleBlock :text="telcB2Example" />
                  <PenaltyBlock :items="telcB2Penalties" />
                </MethodCard>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </TabPanel>

      <!-- ═══════════════════════════════════════════════
           GOETHE
      ═══════════════════════════════════════════════ -->
      <TabPanel value="goethe">
        <template #header>
          <span class="flex items-center gap-2 px-1">
            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
            Goethe
          </span>
        </template>

        <div class="space-y-4 pt-4">
          <TabView v-model:value="activeGoetheLevel">
            <TabPanel header="B1" value="b1">
              <div class="space-y-4 pt-4">
                <!-- Teil 1 -->
                <MethodCard
                  icon="pi-envelope"
                  icon-color="text-green-600"
                  bg-color="bg-green-50"
                  border-color="border-green-200"
                  title="Teil 1 - E-mail informelle"
                  badge="40 pts · min. 80 mots · 20 min"
                  badge-color="bg-green-100 text-green-700"
                >
                  <StructureList :items="goetheB1Teil1Structure" />
                  <ConnectorBlock :items="goetheB1Teil1Connectors" />
                  <ExampleBlock :text="goetheB1Teil1Example" />
                </MethodCard>

                <!-- Teil 2 -->
                <MethodCard
                  icon="pi-comment"
                  icon-color="text-blue-600"
                  bg-color="bg-blue-50"
                  border-color="border-blue-200"
                  title="Teil 2 - Opinion forum / blog"
                  badge="40 pts · min. 80 mots · 25 min"
                  badge-color="bg-blue-100 text-blue-700"
                >
                  <StructureList :items="goetheB1Teil2Structure" />
                  <ConnectorBlock :items="goetheB1Teil2Connectors" />
                  <ExampleBlock :text="goetheB1Teil2Example" />
                </MethodCard>

                <!-- Teil 3 -->
                <MethodCard
                  icon="pi-briefcase"
                  icon-color="text-orange-600"
                  bg-color="bg-orange-50"
                  border-color="border-orange-200"
                  title="Teil 3 - E-mail formelle courte"
                  badge="20 pts · ~40 mots · 15 min"
                  badge-color="bg-orange-100 text-orange-700"
                >
                  <StructureList :items="goetheB1Teil3Structure" />
                  <ExampleBlock :text="goetheB1Teil3Example" />
                </MethodCard>
              </div>
            </TabPanel>

            <TabPanel header="B2" value="b2">
              <div class="space-y-4 pt-4">
                <!-- Teil 1 -->
                <MethodCard
                  icon="pi-align-left"
                  icon-color="text-indigo-600"
                  bg-color="bg-indigo-50"
                  border-color="border-indigo-200"
                  title="Teil 1 - Texte d'opinion argumenté"
                  badge="70 pts · ~200 mots"
                  badge-color="bg-indigo-100 text-indigo-700"
                >
                  <StructureList :items="goetheB2Teil1Structure" />
                  <ConnectorBlock :items="goetheB2Teil1Connectors" />
                  <ExampleBlock :text="goetheB2Teil1Example" />
                  <PenaltyBlock :items="goetheB2Teil1Penalties" />
                </MethodCard>

                <!-- Teil 2 -->
                <MethodCard
                  icon="pi-briefcase"
                  icon-color="text-purple-600"
                  bg-color="bg-purple-50"
                  border-color="border-purple-200"
                  title="Teil 2 - E-mail professionnelle"
                  badge="30 pts · ~80 mots"
                  badge-color="bg-purple-100 text-purple-700"
                >
                  <StructureList :items="goetheB2Teil2Structure" />
                  <ExampleBlock :text="goetheB2Teil2Example" />
                </MethodCard>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </TabPanel>

      <!-- ═══════════════════════════════════════════════
           ÖSD
      ═══════════════════════════════════════════════ -->
      <TabPanel value="osd">
        <template #header>
          <span class="flex items-center gap-2 px-1">
            <span class="w-2 h-2 rounded-full bg-orange-500"></span>
            ÖSD
          </span>
        </template>

        <div class="space-y-4 pt-4">
          <TabView v-model:value="activeOsdLevel">
            <TabPanel header="B1" value="b1">
              <div class="pt-4">
                <Message severity="info" :closable="false" class="mb-4">
                  Le ÖSD B1 partage la même structure que le Goethe B1 (3
                  tâches). Référez-vous à l'onglet Goethe B1.
                </Message>
                <!-- Rappel compact -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div
                    v-for="t in osdB1Summary"
                    :key="t.title"
                    class="bg-white border border-gray-200 rounded-xl p-4 space-y-1"
                  >
                    <div class="flex items-center gap-2">
                      <i :class="['pi text-sm', t.icon, t.color]"></i>
                      <span class="text-xs font-semibold text-gray-700">{{
                        t.title
                      }}</span>
                    </div>
                    <p class="text-xs text-gray-500">{{ t.desc }}</p>
                    <span
                      :class="[
                        'text-xs font-bold px-2 py-0.5 rounded-full',
                        t.badge,
                      ]"
                      >{{ t.pts }}</span
                    >
                  </div>
                </div>
              </div>
            </TabPanel>

            <TabPanel header="B2" value="b2">
              <div class="space-y-4 pt-4">
                <!-- Teil 1 -->
                <MethodCard
                  icon="pi-align-left"
                  icon-color="text-orange-600"
                  bg-color="bg-orange-50"
                  border-color="border-orange-200"
                  title="Teil 1 - Texte argumentatif"
                  badge="45 pts · ~200 mots"
                  badge-color="bg-orange-100 text-orange-700"
                >
                  <StructureList :items="osdB2Teil1Structure" />
                  <ConnectorBlock :items="osdB2Teil1Connectors" />
                  <ExampleBlock :text="osdB2Teil1Example" />
                </MethodCard>

                <!-- Teil 2 -->
                <MethodCard
                  icon="pi-file-edit"
                  icon-color="text-red-600"
                  bg-color="bg-red-50"
                  border-color="border-red-200"
                  title="Teil 2 - Lettre officielle"
                  badge="45 pts · min. 150 mots"
                  badge-color="bg-red-100 text-red-700"
                >
                  <StructureList :items="osdB2Teil2Structure" />
                  <ConnectorBlock :items="osdB2Teil2Connectors" />
                  <ExampleBlock :text="osdB2Teil2Example" />
                  <PenaltyBlock :items="osdB2Penalties" />
                </MethodCard>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </TabPanel>
    </TabView>

    <!-- Barème CECRL global -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
        <i class="pi pi-chart-bar text-green-600"></i>
        <h2 class="font-semibold text-gray-800">
          Barème de réussite par examen
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th
                class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
              >
                Examen
              </th>
              <th
                class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
              >
                Niveau
              </th>
              <th
                class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
              >
                Total
              </th>
              <th
                class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
              >
                Seuil
              </th>
              <th
                class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell"
              >
                Tâches
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr
              v-for="row in scoreTable"
              :key="row.exam + row.level"
              class="hover:bg-gray-50"
            >
              <td class="px-5 py-3">
                <span
                  :class="[
                    'text-xs font-bold px-2 py-0.5 rounded-full',
                    row.badgeClass,
                  ]"
                >
                  {{ row.exam }}
                </span>
              </td>
              <td class="px-5 py-3 font-semibold text-gray-700">
                {{ row.level }}
              </td>
              <td class="px-5 py-3 text-gray-600">{{ row.total }} pts</td>
              <td class="px-5 py-3">
                <span class="font-semibold text-green-600"
                  >{{ row.seuil }} pts</span
                >
                <span class="text-xs text-gray-400 ml-1">(60%)</span>
              </td>
              <td class="px-5 py-3 text-xs text-gray-500 hidden sm:table-cell">
                {{ row.tasks }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });
useHead({ title: "Méthodologie Schreiben - DeutschTest" });

const activeExam = ref("telc");
const activeTelcLevel = ref("b1");
const activeGoetheLevel = ref("b1");
const activeOsdLevel = ref("b1");

// ─────────────────────────────────────────────────────────
// Composants internes légers
// ─────────────────────────────────────────────────────────

const MethodCard = defineComponent({
  props: {
    icon: String,
    iconColor: String,
    bgColor: String,
    borderColor: String,
    title: String,
    badge: String,
    badgeClass: String,
    badgeColor: String,
  },
  setup(props, { slots }) {
    return () =>
      h(
        "div",
        {
          class: `bg-white rounded-xl border ${props.borderColor} overflow-hidden`,
        },
        [
          h(
            "div",
            {
              class: `flex items-center gap-3 px-5 py-4 ${props.bgColor} border-b ${props.borderColor}`,
            },
            [
              h("i", { class: `pi ${props.icon} ${props.iconColor}` }),
              h(
                "h3",
                { class: "font-semibold text-gray-800 flex-1" },
                props.title,
              ),
              h(
                "span",
                {
                  class: `text-xs font-medium px-2.5 py-1 rounded-full ${props.badgeColor}`,
                },
                props.badge,
              ),
            ],
          ),
          h("div", { class: "px-5 py-4 space-y-4" }, slots.default?.()),
        ],
      );
  },
});

const StructureList = defineComponent({
  props: {
    items: Array as () => Array<{
      step: string;
      desc: string;
      examples?: string[];
    }>,
  },
  setup(props) {
    return () =>
      h("div", { class: "space-y-2" }, [
        h(
          "p",
          {
            class:
              "text-xs font-bold uppercase tracking-wide text-gray-500 mb-2",
          },
          "Structure obligatoire",
        ),
        ...(props.items ?? []).map((item, i) =>
          h("div", { class: "flex items-start gap-3", key: i }, [
            h(
              "span",
              {
                class:
                  "w-6 h-6 rounded-full bg-gray-100 text-gray-600 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5",
              },
              String(i + 1),
            ),
            h("div", { class: "flex-1" }, [
              h(
                "p",
                { class: "text-sm font-semibold text-gray-800" },
                item.step,
              ),
              h("p", { class: "text-xs text-gray-500 mt-0.5" }, item.desc),
              item.examples?.length
                ? h(
                    "div",
                    { class: "mt-1.5 space-y-0.5" },
                    item.examples.map((ex) =>
                      h(
                        "p",
                        {
                          class:
                            "text-xs text-green-700 italic bg-green-50 px-2 py-0.5 rounded",
                        },
                        `« ${ex} »`,
                      ),
                    ),
                  )
                : null,
            ]),
          ]),
        ),
      ]);
  },
});

const ConnectorBlock = defineComponent({
  props: { items: Array as () => string[] },
  setup(props) {
    return () =>
      h("div", {}, [
        h(
          "p",
          {
            class:
              "text-xs font-bold uppercase tracking-wide text-gray-500 mb-2",
          },
          "Connecteurs attendus",
        ),
        h(
          "div",
          { class: "flex flex-wrap gap-1.5" },
          (props.items ?? []).map((c) =>
            h(
              "span",
              {
                class:
                  "text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full font-medium",
              },
              c,
            ),
          ),
        ),
      ]);
  },
});

const ExampleBlock = defineComponent({
  props: { text: String },
  setup(props) {
    const open = ref(false);
    return () =>
      h("div", {}, [
        h(
          "button",
          {
            class:
              "flex items-center gap-1.5 text-xs font-semibold text-green-600 hover:text-green-700 transition-colors",
            onClick: () => (open.value = !open.value),
          },
          [
            h("i", {
              class: `pi ${open.value ? "pi-chevron-up" : "pi-chevron-down"} text-xs`,
            }),
            open.value ? "Masquer l'exemple" : "Voir un exemple type",
          ],
        ),
        open.value
          ? h(
              "div",
              {
                class: "mt-2 bg-gray-50 border border-gray-200 rounded-lg p-4",
              },
              h(
                "pre",
                {
                  class:
                    "text-xs text-gray-700 whitespace-pre-wrap leading-relaxed font-sans",
                },
                props.text,
              ),
            )
          : null,
      ]);
  },
});

const PenaltyBlock = defineComponent({
  props: { items: Array as () => string[] },
  setup(props) {
    return () =>
      h("div", { class: "bg-red-50 border border-red-200 rounded-lg p-3" }, [
        h(
          "p",
          {
            class:
              "text-xs font-bold text-red-700 uppercase tracking-wide mb-1.5",
          },
          "⚠ Pénalités automatiques",
        ),
        h(
          "ul",
          { class: "space-y-1" },
          (props.items ?? []).map((p) =>
            h("li", { class: "flex items-start gap-2 text-xs text-red-600" }, [
              h("i", { class: "pi pi-times-circle mt-0.5 flex-shrink-0" }),
              p,
            ]),
          ),
        ),
      ]);
  },
});

// ─────────────────────────────────────────────────────────
// Données TELC B1
// ─────────────────────────────────────────────────────────

const telcB1Structure = [
  {
    step: "Anrede",
    desc: "Formule d'ouverture informelle",
    examples: ["Liebe Maria,", "Lieber Markus,"],
  },
  {
    step: "Einleitungssatz",
    desc: "Phrase d'accroche",
    examples: [
      "Wie geht es dir? Ich freue mich über deinen Brief!",
      "Gestern habe ich deine E-Mail gelesen und mich sehr gefreut.",
    ],
  },
  {
    step: "Hauptteil",
    desc: "Traiter les 3-4 points demandés en paragraphes distincts",
    examples: [],
  },
  {
    step: "Abschlusssatz",
    desc: "Formule de clôture",
    examples: ["Ich freue mich auf deine Antwort!", "Schreib mir bald!"],
  },
  {
    step: "Grußformel + Unterschrift",
    desc: "Formule de salutation + prénom",
    examples: ["Liebe Grüße, Anna", "Herzliche Grüße, Marc"],
  },
];

const telcB1Connectors = [
  "Tatsächlich...",
  "Zusätzlich...",
  "Außerdem...",
  "Entweder...oder...",
  "Zwar...aber...",
  "Bezüglich [Thema],...",
  "Was [Thema] betrifft,...",
  "Es freut mich sehr, dass...",
  "Ich würde gerne wissen, ob...",
];

const telcB1Example = `Lieber Viktor,

wie geht es dir? Gestern habe ich deinen Brief gelesen und mich darüber sehr gefreut.
Vielen Dank für das Buch über Malta - ich habe bereits reingeschaut und es gefällt mir sehr!

Es freut mich sehr, dass du nach meinen Hobbys gefragt hast. Ich lese entweder Bücher
oder gehe wandern. Beim Wandern fotografiere ich häufig die Natur - ähnlich wie du!

Für meinen nächsten Urlaub werde ich eine Wanderung in den Bergen unternehmen,
um ein bisschen die Natur zu genießen.

Ein Treffen mit dir wäre großartig. Gib Bescheid, wann es dir passt!

Liebe Grüße,
Anna`;

const telcB1Penalties = [
  'Tutoiement absent (pas de "du") → -3 pts structure',
  "Pas de Grußformel → -2 pts structure",
  "Moins de 80 mots → -3 pts aufgabe",
  "Thème complètement hors sujet → max 20/45",
];

// ─────────────────────────────────────────────────────────
// Données TELC B2
// ─────────────────────────────────────────────────────────

const telcB2Structure = [
  {
    step: "Absender + Empfänger",
    desc: "Coordonnées expéditeur et destinataire",
    examples: [],
  },
  {
    step: "Datum + Betreff",
    desc: "Date et ligne d'objet obligatoire",
    examples: [
      "Betreff: Beschwerde über meinen Aufenthalt",
      "Betreff: Mängelrüge - SuperClean-Staubsauger",
    ],
  },
  {
    step: "Anrede formelle",
    desc: "Vouvoiement obligatoire",
    examples: ["Sehr geehrte Damen und Herren,"],
  },
  {
    step: "Einleitung",
    desc: "Annoncer clairement le motif du courrier",
    examples: ["ich schreibe Ihnen, weil ich mit... sehr unzufrieden war."],
  },
  {
    step: "Hauptteil",
    desc: "Traiter 3 points (option a) ou 2 + 1 libre (option b)",
    examples: ["Erstens...", "Zweitens...", "Darüber hinaus..."],
  },
  {
    step: "Forderung",
    desc: "Demande concrète sans menacer d'un avocat dès l'ouverture",
    examples: [
      "Ich fordere Sie daher auf, das Gerät zu ersetzen.",
      "Ich erwarte eine angemessene Entschädigung.",
    ],
  },
  {
    step: "Schlussformel + Unterschrift",
    desc: "Formule de politesse finale",
    examples: ["Mit freundlichen Grüßen,"],
  },
];

const telcB2Connectors = [
  "Erstens / Zweitens / Drittens",
  "Außerdem",
  "Darüber hinaus",
  "Leider",
  "Obwohl...",
  "Ich fordere Sie daher auf,...",
  "Ich erwarte von Ihnen, dass...",
  "Sollte ich keine Antwort erhalten,...",
];

const telcB2Example = `Yassine Choukri                    Autovermietung Neustadt
Musterstraße 1                     info@autovermietung-neustadt.de
12345 Berlin

Berlin, 17.02.2025

Betreff: Beschwerde über gemietetes Fahrzeug und mangelhaften Kundenservice

Sehr geehrte Damen und Herren,

ich habe am vergangenen Wochenende bei Ihrer Autovermietung ein Fahrzeug gemietet
und war mit dem Service sowie dem Fahrzeugzustand sehr unzufrieden.

Erstens war das Fahrzeug weder sauber noch in einwandfreiem Zustand.
Zweitens war Ihr Kundenservice trotz mehrfacher Versuche nicht erreichbar.

Ich fordere Sie daher auf, mir eine angemessene Entschädigung zu gewähren.
Sollte ich keine Antwort erhalten, behalte ich mir weitere Schritte vor.

Mit freundlichen Grüßen,
Yassine Choukri`;

const telcB2Penalties = [
  '"du" au lieu de "Sie" → -4 pts aufgabe',
  "Menace directe d'avocat dès l'intro → -3 pts aufgabe",
  "Pas de Betreffzeile → -1 pt aufgabe",
  "Pas de demande concrète → -2 pts aufgabe",
  "Moins de 100 mots → -4 pts aufgabe",
];

// ─────────────────────────────────────────────────────────
// Données Goethe B1
// ─────────────────────────────────────────────────────────

const goetheB1Teil1Structure = [
  {
    step: "Anrede",
    desc: "Informelle - prénom uniquement",
    examples: ["Liebe Maria,", "Lieber Karl,"],
  },
  {
    step: "Einleitungssatz",
    desc: "Référence au message reçu",
    examples: [
      "Wie geht es dir?",
      "Ich war sehr froh, deinen Brief zu bekommen.",
    ],
  },
  {
    step: "Hauptteil",
    desc: "Traiter les 3 points de la consigne",
    examples: [],
  },
  {
    step: "Abschlusssatz",
    desc: "Invitation à répondre ou à se retrouver",
    examples: [
      "Ich warte auf deine Antwort.",
      "Ich freue mich sehr darauf, dich bald zu sehen.",
    ],
  },
  {
    step: "Grüße + Unterschrift",
    desc: "",
    examples: ["Liebe Grüße,", "Herzliche Grüße,", "Viele Grüße,"],
  },
];

const goetheB1Teil1Connectors = [
  "Tatsächlich...",
  "Außerdem...",
  "Zusätzlich...",
  "Entweder...oder...",
  "Zwar...aber...",
  "Bezüglich [Thema],...",
  "Ich würde gerne wissen, ob...",
];

const goetheB1Teil1Example = `Lieber Viktor,

wie geht es dir? Ich war sehr froh, deinen Brief zu bekommen.

Es freut mich, dass du nach meinen Hobbys gefragt hast. Ich gehe entweder wandern
oder lese Bücher. Zusätzlich fotografiere ich gerne die Natur.

Für meinen Urlaub plane ich eine Wanderung in den Bergen.
Ein Treffen mit dir wäre großartig - sag Bescheid, wann es dir passt!

Liebe Grüße,
Anna`;

const goetheB1Teil2Structure = [
  {
    step: "Einleitung",
    desc: "Référence obligatoire au texte cité",
    examples: [
      'Vor kurzem habe ich im Internet eine Meinung zum Thema "..." gelesen, in der es darum geht, dass...',
    ],
  },
  {
    step: "Eigene Meinung",
    desc: "Position personnelle claire",
    examples: [
      "Ich bin der Meinung, dass...",
      "Meiner Auffassung nach...",
      "Ich stimme dieser Meinung (nicht) zu, weil...",
    ],
  },
  {
    step: "Argument + Beispiel",
    desc: "Au moins 1 argument avec exemple personnel",
    examples: [],
  },
  {
    step: "Fazit",
    desc: "Résumé obligatoire",
    examples: [
      "Zusammenfassend möchte ich sagen, dass...",
      "Alles in allem bin ich der Ansicht, dass...",
    ],
  },
];

const goetheB1Teil2Connectors = [
  "Ich bin der Meinung / Auffassung / Ansicht, dass...",
  "Meiner Meinung nach...",
  "Einerseits... andererseits...",
  "Ich bin davon überzeugt, dass...",
  "Zusammenfassend...",
  "Schließlich möchte ich sagen, dass...",
];

const goetheB1Teil2Example = `Vor kurzem habe ich in einem Internet-Blog eine Meinung zum Thema
"Gesunde Ernährung" gelesen, in der es darum geht, dass sie nur ein Modetrend sei.

Ich bin der Auffassung, dass es vielleicht teilweise richtig ist, weil gesunde
Ernährung überall beworben wird. Allerdings versteht man schnell, dass sie eine
wichtige Rolle in unserem Leben spielt.

Ich persönlich habe auf einige Lebensmittel verzichtet, weil sie meine Gesundheit
negativ beeinflussen.

Zusammenfassend möchte ich sagen, dass gesunde Ernährung wichtig und kein Trend ist.`;

const goetheB1Teil3Structure = [
  {
    step: "Anrede formelle",
    desc: "Vouvoiement obligatoire",
    examples: ["Sehr geehrte/r [Name],", "Sehr geehrte Damen und Herren,"],
  },
  {
    step: "Einstieg",
    desc: "Motif du contact en 1 phrase",
    examples: [
      "da Sie telefonisch nicht erreichbar waren, schreibe ich nun diese E-Mail.",
      "ich habe Ihre Anzeige gelesen und möchte mich erkundigen...",
    ],
  },
  {
    step: "Bitte / Information",
    desc: "1 à 2 phrases - rester concis (~40 mots total)",
    examples: [],
  },
  { step: "Schlussformel", desc: "", examples: ["Mit freundlichen Grüßen,"] },
];

const goetheB1Teil3Example = `Sehr geehrte Damen und Herren,

ich habe Ihre Anzeige gelesen und möchte mich erkundigen, wie viel der Sprachkurs
kostet und wie viele Stunden es wöchentlich gibt.

Ich wäre Ihnen sehr dankbar, wenn Sie mir diese Informationen schicken würden.

Mit freundlichen Grüßen,
Maria Schulz`;

// ─────────────────────────────────────────────────────────
// Données Goethe B2
// ─────────────────────────────────────────────────────────

const goetheB2Teil1Structure = [
  {
    step: "Einleitung + Position",
    desc: "Introduire le thème + prendre position",
    examples: [
      "Das Thema [X] ist heutzutage ein viel diskutiertes Anliegen...",
      "Ich bin der Ansicht, dass...",
    ],
  },
  {
    step: "Argument 1",
    desc: "Avec justification et exemple",
    examples: ["Einerseits...", "Zum einen..."],
  },
  {
    step: "Argument 2 (contra)",
    desc: "Nuance ou contre-argument",
    examples: ["Andererseits...", "Obwohl...", "Dennoch..."],
  },
  {
    step: "Alternativen",
    desc: "Proposer des alternatives concrètes",
    examples: ["Als Alternative könnte man...", "Eine mögliche Lösung wäre..."],
  },
  {
    step: "Fazit nuancé",
    desc: "Conclusion obligatoire",
    examples: [
      "Zusammenfassend kommt man zu dem Ergebnis, dass...",
      "Alles in allem lässt sich sagen, dass...",
    ],
  },
];

const goetheB2Teil1Connectors = [
  "Einerseits / Andererseits",
  "Obwohl / Dennoch / Trotzdem",
  "Außerdem / Darüber hinaus",
  "Meines Erachtens / Meiner Auffassung nach",
  "Beispielsweise / So zum Beispiel",
  "Deshalb / Daher / Aus diesem Grund",
  "Der Hauptvorteil besteht darin, dass...",
];

const goetheB2Teil1Example = `Das Thema Schönheitsoperationen ist heutzutage ein viel diskutiertes Anliegen.
Ich bin der Ansicht, dass viele Menschen operiert werden, weil sie mit ihrem Äußeren
unzufrieden sind.

Einerseits können medizinisch notwendige Eingriffe das Leben verbessern.
Andererseits bringen kosmetische Operationen erhebliche Risiken mit sich.

Als Alternative könnte man Sport treiben, sich gesund ernähren und Naturkosmetik
verwenden. Der Hauptvorteil besteht darin, dass diese Methoden langfristig gesünder sind.

Zusammenfassend kommt man zu dem Ergebnis, dass man sich über alle Risiken bewusst
sein sollte, bevor man eine solche Entscheidung trifft.`;

const goetheB2Teil1Penalties = [
  "Pas de Fazit → -2 pts aufgabe",
  "Pas d'Alternativen → -2 pts aufgabe",
  "Moins de 5 connecteurs différents → kohaesion max 12/25",
];

const goetheB2Teil2Structure = [
  { step: "Anrede formelle", desc: "", examples: ["Sehr geehrte/r [Name],"] },
  {
    step: "Einstieg",
    desc: "Motif du contact",
    examples: [
      "da Sie telefonisch nicht erreichbar waren, schreibe ich nun diese E-Mail.",
    ],
  },
  {
    step: "Demande concrète",
    desc: "Avec Konjunktiv II obligatoire",
    examples: [
      "Ich wäre Ihnen dankbar, wenn Sie...",
      "Könnten Sie mir bitte...",
    ],
  },
  {
    step: "Abschluss + Schlussformel",
    desc: "",
    examples: ["Ich danke Ihnen im Voraus.", "Mit freundlichen Grüßen,"],
  },
];

const goetheB2Teil2Example = `Sehr geehrte Frau Müller,

da Sie telefonisch nicht erreichbar waren, schreibe ich nun diese E-Mail.

Unsere Gruppe hat bei Ihnen ein Praktikum absolviert, das sehr nützlich, jedoch
zu kurz war. Ich möchte Sie daher bitten, das Praktikum um zwei Wochen zu verlängern.
Wir wären auch bereit, am Wochenende zu arbeiten.

Ich danke Ihnen im Voraus für Ihr Verständnis.

Mit freundlichen Grüßen,
Asal Ahmadi`;

// ─────────────────────────────────────────────────────────
// Données ÖSD B1 — résumé
// ─────────────────────────────────────────────────────────

const osdB1Summary = [
  {
    title: "Teil 1 - E-mail informelle",
    desc: "Même structure que Goethe B1 Teil 1",
    icon: "pi-envelope",
    color: "text-green-600",
    badge: "bg-green-100 text-green-700",
    pts: "40 pts · 80 mots",
  },
  {
    title: "Teil 2 - Opinion forum",
    desc: "Même structure que Goethe B1 Teil 2",
    icon: "pi-comment",
    color: "text-blue-600",
    badge: "bg-blue-100 text-blue-700",
    pts: "40 pts · 80 mots",
  },
  {
    title: "Teil 3 - E-mail formelle",
    desc: "Même structure que Goethe B1 Teil 3",
    icon: "pi-briefcase",
    color: "text-orange-600",
    badge: "bg-orange-100 text-orange-700",
    pts: "20 pts · 40 mots",
  },
];

// ─────────────────────────────────────────────────────────
// Données ÖSD B2
// ─────────────────────────────────────────────────────────

const osdB2Teil1Structure = [
  {
    step: "Einleitung + Position",
    desc: "Thème + prise de position",
    examples: [
      "Das Thema [X] ist heutzutage ein viel diskutiertes Anliegen, somit habe ich vor, eine persönliche Stellung zu nehmen...",
    ],
  },
  {
    step: "Argument 1 (Einerseits)",
    desc: "Avec justification + exemple",
    examples: ["Der Hauptvorteil besteht meines Erachtens darin, dass..."],
  },
  {
    step: "Argument 2 (Andererseits)",
    desc: "Nuance ou inconvénient",
    examples: ["Man darf jedoch nicht außer Acht lassen, dass..."],
  },
  {
    step: "Alternativen",
    desc: "Solutions concrètes",
    examples: [
      "Nun wird auf die Alternativen eingegangen:",
      "Als Alternative könnte man...",
    ],
  },
  {
    step: "Fazit",
    desc: "Conclusion nuancée obligatoire",
    examples: ["Zusammenfassend kommt man zu dem Ergebnis, dass..."],
  },
];

const osdB2Teil1Connectors = [
  "Einerseits / Andererseits",
  "Obwohl / Dennoch / Allerdings",
  "Außerdem / Darüber hinaus",
  "Man darf nicht außer Acht lassen, dass...",
  "Meines Erachtens / Meiner Meinung nach",
  "Beispielsweise",
];

const osdB2Teil1Example = `Das Thema fleischreiche Ernährung ist heutzutage ein viel diskutiertes Anliegen.
Meiner Auffassung nach ist eine fleischreiche Ernährung gesundheitsschädlich.

Einerseits enthält Fleisch viele Vitamine und Proteine. Andererseits belastet eine
übermäßige Fleischproduktion die Umwelt stark.

Als Alternative gibt es vegetarisches und veganes Essen. Der Hauptvorteil besteht
darin, dass unser Körper kein zusätzliches Fett speichert.

Zusammenfassend sollte jeder sein Konsumverhalten überdenken.`;

const osdB2Teil2Structure = [
  {
    step: "Absender + Empfänger + Datum",
    desc: "En-tête complet",
    examples: [],
  },
  {
    step: "Betreff",
    desc: "Ligne d'objet obligatoire",
    examples: ["Betreff: Beschwerde über meinen Aufenthalt"],
  },
  {
    step: "Anrede formelle",
    desc: "",
    examples: ["Sehr geehrte Damen und Herren,"],
  },
  {
    step: "Hauptteil",
    desc: "3 points (option a) ou 2 + 1 libre (option b)",
    examples: [
      "Erstens...",
      "Zweitens...",
      "Obwohl ich mehrmals nachgefragt habe,...",
    ],
  },
  {
    step: "Forderung + Schluss",
    desc: "Demande sans menace directe",
    examples: [
      "Ich erwarte eine angemessene Entschädigung.",
      "Sollte ich keine Rückmeldung erhalten, behalte ich mir weitere Schritte vor.",
    ],
  },
];

const osdB2Teil2Connectors = [
  "Erstens / Zweitens",
  "Obwohl... / Trotz + Genitiv",
  "Ich fordere Sie daher auf,...",
  "Ich erwarte von Ihnen, dass...",
  "Ich wäre Ihnen dankbar, wenn...",
  "Sollte... behalte ich mir... vor.",
];

const osdB2Teil2Example = `Yassine Choukri                    Apartmenthaus Oranienburg
Berlin, 17.02.2025

Betreff: Beschwerde über meinen Aufenthalt

Sehr geehrte Damen und Herren,

ich musste für drei Monate beruflich nach Oranienburg ziehen und habe mich
deshalb für Ihr Apartmenthaus entschieden. Leider entsprach der Aufenthalt
nicht meinen Erwartungen.

Erstens fehlten in der Küche grundlegende Utensilien. Zweitens wurde der
gebuchte Wäscheservice oft nicht erbracht. Obwohl ich per E-Mail nachgefragt
habe, erhielt ich keine zeitnahe Antwort.

Ich erwarte eine Entschädigung für die entstandenen Unannehmlichkeiten.

Mit freundlichen Grüßen,
Yassine Choukri`;

const osdB2Penalties = [
  '"du" au lieu de "Sie" → -5 pts aufgabe',
  "Menace d'avocat dès l'introduction → -3 pts aufgabe",
  "Pas de Betreff → -1 pt aufgabe",
  "Moins de 2 points traités → aufgabe max 6/14",
];

// ─────────────────────────────────────────────────────────
// Tableau barème
// ─────────────────────────────────────────────────────────

const scoreTable = [
  {
    exam: "TELC",
    level: "B1",
    total: 45,
    seuil: 27,
    tasks: "1 tâche - e-mail informelle",
    badgeClass: "bg-purple-100 text-purple-700",
  },
  {
    exam: "TELC",
    level: "B2",
    total: 45,
    seuil: 27,
    tasks: "1 tâche - lettre de réclamation",
    badgeClass: "bg-purple-100 text-purple-700",
  },
  {
    exam: "Goethe",
    level: "B1",
    total: 100,
    seuil: 60,
    tasks: "3 tâches - e-mail + opinion + e-mail formelle",
    badgeClass: "bg-blue-100 text-blue-700",
  },
  {
    exam: "Goethe",
    level: "B2",
    total: 100,
    seuil: 60,
    tasks: "2 tâches - opinion (70pts) + e-mail pro (30pts)",
    badgeClass: "bg-blue-100 text-blue-700",
  },
  {
    exam: "ÖSD",
    level: "B1",
    total: 100,
    seuil: 60,
    tasks: "3 tâches - identique Goethe B1",
    badgeClass: "bg-orange-100 text-orange-700",
  },
  {
    exam: "ÖSD",
    level: "B2",
    total: 90,
    seuil: 54,
    tasks: "2 tâches - argumentatif (45pts) + lettre (45pts)",
    badgeClass: "bg-orange-100 text-orange-700",
  },
];
</script>

<style scoped>
/* Harmoniser les TabView imbriqués */
:deep(.p-tabview-nav) {
  background: transparent;
  border-bottom: 1px solid #e5e7eb;
}
:deep(.p-tabview-panels) {
  background: transparent;
  padding: 0;
}
:deep(.p-tabview-nav-link) {
  background: transparent !important;
  border: none !important;
  padding: 0.6rem 0.25rem !important;
  font-size: 0.875rem;
}
:deep(.p-tabview-ink-bar) {
  background-color: #0d9488;
}
</style>
