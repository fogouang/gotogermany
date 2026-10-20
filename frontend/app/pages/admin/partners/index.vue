<!-- pages/admin/partners/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Onglets ── -->
    <div
      class="flex gap-1 rounded-leaf border border-line bg-card p-1 sm:w-fit"
    >
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="flex flex-1 items-center justify-center gap-2 rounded-leaf px-4 py-2 text-sm font-medium transition-colors sm:flex-none"
        :class="
          activeTab === tab.key
            ? 'bg-primary/10 text-primary'
            : 'text-muted hover:text-ink'
        "
        @click="activeTab = tab.key"
      >
        <i :class="tab.icon" class="text-xs" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ══════════════════ PARTENAIRES ══════════════════ -->
    <template v-if="activeTab === 'partners'">
      <!-- Tuiles -->
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div
          v-for="tile in tiles"
          :key="tile.label"
          class="rounded-card border border-line bg-card p-4 shadow-soft"
        >
          <div
            class="mb-3 flex size-9 items-center justify-center rounded-leaf"
            :class="tile.iconClass"
          >
            <i :class="tile.icon" class="text-sm" />
          </div>
          <p class="text-xl font-bold leading-none" :class="tile.tone">
            {{ tile.value }}
          </p>
          <p class="mt-1.5 text-xs text-muted">{{ tile.label }}</p>
        </div>
      </div>

      <!-- Filtres -->
      <div
        class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
      >
        <div class="flex flex-wrap gap-2">
          <button
            v-for="f in typeFilters"
            :key="f.key"
            type="button"
            class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
            :class="
              typeFilter === f.key
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-line bg-card text-muted hover:border-primary/30'
            "
            @click="typeFilter = f.key"
          >
            {{ f.label }} · {{ f.count }}
          </button>
          <span class="mx-1 hidden h-7 w-px bg-line sm:block" />
          <button
            v-for="f in stateFilters"
            :key="f.key"
            type="button"
            class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
            :class="
              stateFilter === f.key
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-line bg-card text-muted hover:border-primary/30'
            "
            @click="stateFilter = stateFilter === f.key ? 'all' : f.key"
          >
            {{ f.label }} · {{ f.count }}
          </button>
        </div>
        <IconField class="w-full lg:w-72">
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="search"
            class="w-full"
            placeholder="Rechercher un partenaire"
          />
        </IconField>
      </div>

      <!-- Liste -->
      <div v-if="loadingPartners" class="space-y-3">
        <div
          v-for="n in 4"
          :key="n"
          class="h-16 animate-pulse rounded-card bg-card-2"
        />
      </div>

      <div
        v-else-if="filteredPartners.length === 0"
        class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
      >
        <span
          class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
        >
          <i class="pi pi-briefcase" />
        </span>
        <p class="text-sm font-medium text-ink">
          {{
            sales.partners.length === 0
              ? "Aucun partenaire pour l'instant."
              : "Aucun partenaire ne correspond."
          }}
        </p>
      </div>

      <ul
        v-else
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="p in filteredPartners"
          :key="`${p.partner_type}-${p.partner_id}`"
          class="flex cursor-pointer flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3.5 transition-colors hover:bg-card-2/60 sm:px-5"
          @click="openPartner(p)"
        >
          <!-- Identité -->
          <div class="flex min-w-52 flex-1 items-center gap-3">
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-leaf"
              :class="
                p.partner_type === 'center'
                  ? 'bg-primary/10 text-primary'
                  : 'bg-amber-500/15 text-amber-600'
              "
            >
              <i
                :class="
                  p.partner_type === 'center' ? 'pi pi-building' : 'pi pi-star'
                "
                class="text-sm"
              />
            </span>
            <div class="min-w-0">
              <p class="truncate font-medium text-ink">{{ p.name }}</p>
              <p class="text-xs text-muted">{{ typeLabel(p.partner_type) }}</p>
            </div>
          </div>

          <!-- Soldes -->
          <div
            class="grid w-full grid-cols-2 gap-4 text-xs sm:w-auto sm:grid-cols-[8rem_8rem]"
          >
            <div>
              <p class="text-muted">Doit à la plateforme</p>
              <p
                class="font-semibold"
                :class="p.owed_to_platform > 0 ? 'text-ink' : 'text-muted'"
              >
                {{ fcfa(p.owed_to_platform) }}
              </p>
            </div>
            <div>
              <p class="text-muted">À lui verser</p>
              <p
                class="font-semibold"
                :class="p.owed_to_partner > 0 ? 'text-ink' : 'text-muted'"
              >
                {{ fcfa(p.owed_to_partner) }}
              </p>
            </div>
          </div>

          <!-- État -->
          <div
            class="flex flex-wrap items-center gap-1.5 sm:w-48 sm:justify-end"
          >
            <span
              v-if="p.trial_active"
              class="rounded-full bg-violet-500/10 px-2 py-0.5 text-[11px] font-semibold text-violet-600"
            >
              Essai · {{ p.trial_activations_left }}
            </span>
            <span
              v-if="p.is_blocked"
              class="rounded-full bg-red-500/10 px-2 py-0.5 text-[11px] font-semibold text-red-600"
              >Bloqué</span
            >
            <span
              v-if="p.overdue_amount > 0"
              class="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
            >
              {{ p.overdue_count }} en retard · {{ fcfa(p.overdue_amount) }}
            </span>
            <span
              v-if="!p.can_activate"
              class="rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted"
              >Activation coupée</span
            >
            <span
              v-if="!p.is_blocked && p.overdue_amount === 0 && p.can_activate"
              class="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600"
            >
              À jour
            </span>
          </div>
          <i class="pi pi-chevron-right hidden text-xs text-muted sm:block" />
        </li>
      </ul>
    </template>

    <!-- ══════════════════ RÈGLES DE COMMISSION ══════════════════ -->
    <template v-else>
      <div
        class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <p class="max-w-2xl text-sm text-muted">
          Une règle sans partenaire ni plan s'applique par défaut à tous les
          partenaires du type. Une règle ciblée sur un partenaire ou un plan est
          prioritaire.
        </p>
        <Button
          label="Nouvelle règle"
          icon="pi pi-plus"
          class="w-full shrink-0 sm:w-auto"
          @click="openRuleCreate"
        />
      </div>

      <div v-if="loadingRules" class="space-y-3">
        <div
          v-for="n in 3"
          :key="n"
          class="h-14 animate-pulse rounded-card bg-card-2"
        />
      </div>

      <div
        v-else-if="sales.rules.length === 0"
        class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
      >
        <span
          class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
        >
          <i class="pi pi-percentage" />
        </span>
        <p class="text-sm font-medium text-ink">Aucune règle de commission</p>
      </div>

      <div v-else class="space-y-4">
        <section
          v-for="group in ruleGroups"
          :key="group.type"
          class="space-y-2"
        >
          <h3 class="text-sm font-semibold text-ink">{{ group.label }}</h3>
          <ul
            class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
          >
            <li
              v-for="rule in group.rules"
              :key="rule.id"
              class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-5"
              :class="{ 'opacity-60': !rule.is_active }"
            >
              <div class="min-w-52 flex-1">
                <p class="text-sm font-medium text-ink">
                  {{ ruleScope(rule) }}
                </p>
                <p v-if="rule.plan_id" class="text-xs text-muted">
                  Plan : {{ planName(rule.plan_id) }}
                </p>
              </div>
              <span
                class="rounded-full bg-primary/10 px-3 py-1 text-sm font-bold text-primary"
              >
                {{ ruleValue(rule) }}
              </span>
              <label
                class="flex cursor-pointer items-center gap-2 text-xs text-muted"
              >
                <ToggleSwitch
                  :modelValue="rule.is_active"
                  @update:modelValue="toggleRule(rule, $event)"
                />
                {{ rule.is_active ? "Active" : "Inactive" }}
              </label>
              <div class="flex items-center gap-1">
                <Button
                  icon="pi pi-pencil"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  v-tooltip.top="'Modifier'"
                  aria-label="Modifier"
                  @click="openRuleEdit(rule)"
                />
                <Button
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  aria-label="Supprimer"
                  @click="confirmDeleteRule(rule)"
                />
              </div>
            </li>
          </ul>
        </section>
      </div>
    </template>

    <!-- ══════════════════ PANNEAU PARTENAIRE ══════════════════ -->
    <Drawer
      v-model:visible="showDrawer"
      position="right"
      :style="{ width: '40rem', maxWidth: '100vw' }"
      :header="selected?.name ?? ''"
    >
      <div v-if="selected" class="space-y-6">
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <span
            class="rounded-full bg-card-2 px-2 py-0.5 font-semibold text-muted"
            >{{ typeLabel(selected.partner_type) }}</span
          >
          <span
            v-if="selected.trial_active"
            class="rounded-full bg-violet-500/10 px-2 py-0.5 font-semibold text-violet-600"
          >
            En essai
          </span>
          <span
            v-if="selected.is_blocked"
            class="rounded-full bg-red-500/10 px-2 py-0.5 font-semibold text-red-600"
          >
            Bloqué<span v-if="selected.block_reason">
              · {{ selected.block_reason }}</span
            >
          </span>
        </div>

        <!-- Soldes -->
        <div class="grid grid-cols-3 gap-3">
          <div class="rounded-leaf bg-card-2 px-3 py-3">
            <p class="text-lg font-bold text-ink">
              {{ fcfa(selected.owed_to_platform) }}
            </p>
            <p class="text-[11px] text-muted">Doit à la plateforme</p>
          </div>
          <div class="rounded-leaf bg-card-2 px-3 py-3">
            <p class="text-lg font-bold text-ink">
              {{ fcfa(selected.owed_to_partner) }}
            </p>
            <p class="text-[11px] text-muted">À lui verser</p>
          </div>
          <div class="rounded-leaf bg-card-2 px-3 py-3">
            <p
              class="text-lg font-bold"
              :class="
                selected.net_balance > 0
                  ? 'text-amber-600'
                  : selected.net_balance < 0
                    ? 'text-sky-600'
                    : 'text-ink'
              "
            >
              {{ fcfa(Math.abs(selected.net_balance)) }}
            </p>
            <p class="text-[11px] text-muted">
              {{
                selected.net_balance > 0
                  ? "Solde en notre faveur"
                  : selected.net_balance < 0
                    ? "Solde en sa faveur"
                    : "Solde net"
              }}
            </p>
          </div>
        </div>

        <Button
          label="Enregistrer un règlement"
          icon="pi pi-wallet"
          class="w-full"
          @click="openSettlement"
        />

        <!-- Réglages -->
        <section class="space-y-3 rounded-leaf border border-line p-4">
          <h3 class="text-sm font-semibold text-ink">Réglages</h3>
          <label
            class="flex cursor-pointer items-center justify-between gap-3 text-sm text-ink"
          >
            <span>
              Peut activer des accès
              <span class="block text-xs text-muted"
                >Couper empêche toute nouvelle vente.</span
              >
            </span>
            <ToggleSwitch v-model="settingsForm.can_activate" />
          </label>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted"
                >Plafond d'impayés (FCFA)</label
              >
              <InputNumber
                v-model="settingsForm.unpaid_limit"
                :min="0"
                class="w-full"
                inputClass="w-full"
                placeholder="Sans plafond"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted"
                >Délai de paiement (heures)</label
              >
              <InputNumber
                v-model="settingsForm.payment_delay_hours"
                :min="0"
                class="w-full"
                inputClass="w-full"
              />
            </div>
          </div>
          <div class="flex justify-end">
            <Button
              label="Enregistrer"
              icon="pi pi-check"
              size="small"
              :loading="savingSettings"
              :disabled="!settingsChanged"
              @click="saveSettings"
            />
          </div>
        </section>

        <!-- Période d'essai (centres) -->
        <section
          v-if="selected.partner_type === 'center'"
          class="space-y-3 rounded-leaf border p-4"
          :class="
            selected.trial_active
              ? 'border-violet-500/30 bg-violet-500/5'
              : 'border-line'
          "
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <h3 class="text-sm font-semibold text-ink">Période d'essai</h3>
              <p class="text-xs text-muted">
                Activations offertes : rien à encaisser ni à reverser. À la date
                de fin ou à 0 activation, les ventes redeviennent payantes.
              </p>
            </div>
            <span
              class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
              :class="
                selected.trial_active
                  ? 'bg-violet-500/10 text-violet-600'
                  : 'bg-card-2 text-muted'
              "
            >
              {{ selected.trial_active ? "Active" : "Aucune" }}
            </span>
          </div>

          <p
            v-if="selected.trial_active && selected.trial_ends_at"
            class="text-sm text-ink"
          >
            {{ selected.trial_activations_left }} activation(s) restante(s)
            jusqu'au
            <strong>{{ formatDate(selected.trial_ends_at) }}</strong>
          </p>

          <!-- Raccourcis -->
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="preset in TRIAL_PRESETS"
              :key="preset.label"
              type="button"
              class="rounded-full border border-line px-3 py-1 text-xs text-muted transition-colors hover:border-violet-500/40 hover:text-violet-600"
              @click="applyTrialPreset(preset.days, preset.activations)"
            >
              {{ preset.label }}
            </button>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted"
                >Fin de l'essai</label
              >
              <DatePicker
                v-model="trialForm.ends_at"
                :minDate="new Date()"
                dateFormat="dd/mm/yy"
                showIcon
                class="w-full"
                inputClass="w-full"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted"
                >Activations offertes</label
              >
              <InputNumber
                v-model="trialForm.activations"
                :min="0"
                :max="500"
                class="w-full"
                inputClass="w-full"
              />
            </div>
          </div>

          <div class="flex flex-wrap justify-end gap-2">
            <Button
              v-if="selected.trial_active || selected.trial_ends_at"
              label="Terminer l'essai"
              icon="pi pi-stop-circle"
              size="small"
              severity="danger"
              text
              :loading="savingTrial"
              @click="endTrial"
            />
            <Button
              :label="
                selected.trial_active ? 'Mettre à jour' : 'Ouvrir l\'essai'
              "
              icon="pi pi-gift"
              size="small"
              :loading="savingTrial"
              :disabled="!trialForm.ends_at || !trialForm.activations"
              @click="saveTrial"
            />
          </div>
        </section>

        <Message v-if="drawerError" severity="error" :closable="false">{{
          drawerError
        }}</Message>

        <!-- Ventes -->
        <section class="space-y-2">
          <h3 class="text-sm font-semibold text-ink">
            Ventes
            <span class="font-normal text-muted"
              >· {{ partnerSales.length }}</span
            >
          </h3>
          <div
            v-if="loadingDrawer"
            class="h-24 animate-pulse rounded-leaf bg-card-2"
          />
          <p v-else-if="partnerSales.length === 0" class="text-sm text-muted">
            Aucune vente.
          </p>
          <ul
            v-else
            class="divide-y divide-line rounded-leaf border border-line"
          >
            <li
              v-for="s in partnerSales"
              :key="s.id"
              class="flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2.5 text-sm"
            >
              <div class="min-w-40 flex-1">
                <p class="truncate font-medium text-ink">
                  {{ s.student_name }}
                </p>
                <p class="truncate text-xs text-muted">
                  {{ s.plan_name || "-" }} · {{ formatDate(s.created_at) }}
                </p>
              </div>
              <div class="text-right text-xs">
                <p class="font-semibold text-ink">{{ fcfa(s.price) }}</p>
                <p class="text-muted">
                  {{
                    s.direction === "partner_owes"
                      ? "Nous doit"
                      : "À lui verser"
                  }}
                  {{ fcfa(s.remaining) }}
                </p>
              </div>
              <span
                class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="saleBadge(s).class"
                >{{ saleBadge(s).label }}</span
              >
            </li>
          </ul>
        </section>

        <!-- Règlements -->
        <section class="space-y-2">
          <h3 class="text-sm font-semibold text-ink">
            Règlements
            <span class="font-normal text-muted"
              >· {{ partnerSettlements.length }}</span
            >
          </h3>
          <div
            v-if="loadingDrawer"
            class="h-16 animate-pulse rounded-leaf bg-card-2"
          />
          <p
            v-else-if="partnerSettlements.length === 0"
            class="text-sm text-muted"
          >
            Aucun règlement.
          </p>
          <ul
            v-else
            class="divide-y divide-line rounded-leaf border border-line"
          >
            <li
              v-for="st in partnerSettlements"
              :key="st.id"
              class="flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2.5 text-sm"
            >
              <i
                class="text-xs"
                :class="
                  st.direction === 'to_platform'
                    ? 'pi pi-arrow-down-left text-emerald-600'
                    : 'pi pi-arrow-up-right text-sky-600'
                "
              />
              <div class="min-w-40 flex-1">
                <p class="text-ink">
                  {{
                    st.direction === "to_platform"
                      ? "Reçu du partenaire"
                      : "Versé au partenaire"
                  }}
                </p>
                <p class="truncate text-xs text-muted">
                  {{ st.method
                  }}<span v-if="st.reference"> · {{ st.reference }}</span>
                  <span v-if="st.created_at">
                    · {{ formatDate(st.created_at) }}</span
                  >
                </p>
              </div>
              <span class="font-semibold text-ink">{{ fcfa(st.amount) }}</span>
            </li>
          </ul>
        </section>
      </div>
    </Drawer>

    <!-- ══ Règlement ══ -->
    <Dialog
      v-model:visible="showSettlement"
      header="Enregistrer un règlement"
      modal
      :style="{ width: '95vw', maxWidth: '28rem' }"
    >
      <form class="space-y-4" @submit.prevent="saveSettlement">
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="d in directions"
            :key="d.value"
            type="button"
            class="rounded-leaf border px-3 py-2.5 text-left text-sm transition-colors"
            :class="
              settlementForm.direction === d.value
                ? 'border-primary bg-primary/5 text-ink ring-1 ring-primary/30'
                : 'border-line text-muted hover:border-primary/30'
            "
            @click="setDirection(d.value)"
          >
            <p class="font-medium">{{ d.label }}</p>
            <p class="text-xs text-muted">Restant : {{ fcfa(d.remaining) }}</p>
          </button>
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Montant (FCFA) <span class="text-red-600">*</span></label
          >
          <InputNumber
            v-model="settlementForm.amount"
            :min="1"
            class="w-full"
            inputClass="w-full"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Moyen de paiement <span class="text-red-600">*</span></label
          >
          <div class="mb-2 flex flex-wrap gap-1.5">
            <button
              v-for="m in METHODS"
              :key="m"
              type="button"
              class="rounded-full border px-3 py-1 text-xs transition-colors"
              :class="
                settlementForm.method === m
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-line text-muted hover:border-primary/30'
              "
              @click="settlementForm.method = m"
            >
              {{ m }}
            </button>
          </div>
          <InputText
            v-model="settlementForm.method"
            class="w-full"
            placeholder="ou saisir un autre moyen"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Référence
            <span class="font-normal text-muted">(optionnel)</span></label
          >
          <InputText
            v-model="settlementForm.reference"
            class="w-full"
            placeholder="ex. ID de transaction Mobile Money"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink"
            >Note <span class="font-normal text-muted">(optionnel)</span></label
          >
          <Textarea
            v-model="settlementForm.note"
            rows="2"
            autoResize
            class="w-full"
          />
        </div>
        <Message v-if="settlementError" severity="error" :closable="false">{{
          settlementError
        }}</Message>
      </form>
      <template #footer>
        <Button label="Annuler" text @click="showSettlement = false" />
        <Button
          label="Enregistrer"
          icon="pi pi-check"
          :loading="savingSettlement"
          @click="saveSettlement"
        />
      </template>
    </Dialog>

    <!-- ══ Règle ══ -->
    <Dialog
      v-model:visible="showRuleDialog"
      :header="editingRule ? 'Modifier la règle' : 'Nouvelle règle'"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <form class="space-y-4" @submit.prevent="saveRule">
        <template v-if="!editingRule">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Type de partenaire <span class="text-red-600">*</span></label
            >
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="tp in PARTNER_TYPES"
                :key="tp.value"
                type="button"
                class="rounded-leaf border px-3 py-2 text-sm transition-colors"
                :class="
                  ruleForm.partner_type === tp.value
                    ? 'border-primary bg-primary/5 text-ink ring-1 ring-primary/30'
                    : 'border-line text-muted hover:border-primary/30'
                "
                @click="
                  ruleForm.partner_type = tp.value;
                  ruleForm.partner_id = null;
                "
              >
                {{ tp.label }}
              </button>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Partenaire
              <span class="font-normal text-muted">(vide = tous)</span></label
            >
            <Select
              v-model="ruleForm.partner_id"
              :options="partnerOptions"
              optionLabel="name"
              optionValue="partner_id"
              placeholder="Tous les partenaires du type"
              showClear
              filter
              class="w-full"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Plan
              <span class="font-normal text-muted">(vide = tous)</span></label
            >
            <Select
              v-model="ruleForm.plan_id"
              :options="plans"
              optionLabel="name"
              optionValue="id"
              placeholder="Tous les plans"
              showClear
              class="w-full"
            />
          </div>
        </template>
        <div v-else class="rounded-leaf bg-card-2 px-4 py-3 text-sm">
          <p class="font-medium text-ink">{{ ruleScope(editingRule) }}</p>
          <p v-if="editingRule.plan_id" class="text-xs text-muted">
            Plan : {{ planName(editingRule.plan_id) }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink"
              >Calcul</label
            >
            <SelectButton
              v-model="ruleForm.rule_type"
              :options="RULE_TYPES"
              optionLabel="label"
              optionValue="value"
              :allowEmpty="false"
              class="w-full"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              Valeur {{ ruleForm.rule_type === "percent" ? "(%)" : "(FCFA)" }}
              <span class="text-red-600">*</span>
            </label>
            <InputNumber
              v-model="ruleForm.value"
              :min="0"
              :max="ruleForm.rule_type === 'percent' ? 100 : undefined"
              :maxFractionDigits="2"
              class="w-full"
              inputClass="w-full"
            />
          </div>
        </div>
        <Message v-if="ruleError" severity="error" :closable="false">{{
          ruleError
        }}</Message>
      </form>
      <template #footer>
        <Button label="Annuler" text @click="showRuleDialog = false" />
        <Button
          :label="editingRule ? 'Enregistrer' : 'Créer'"
          icon="pi pi-check"
          :loading="savingRule"
          @click="saveRule"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type {
  CommissionRuleResponse,
  PartnerSaleResponse,
  PartnerSummaryResponse,
} from "#shared/api";
import { CommissionRuleCreate, SettlementCreate } from "#shared/api";
import type { PartnerType } from "~/stores/sales";

definePageMeta({ layout: "admin" });

const sales = useSalesStore();
const { plans, loadPlans } = usePlans();
const toast = useToast();
const confirm = useConfirm();

const fcfa = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} FCFA`;
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
const typeLabel = (t: string) => (t === "center" ? "Centre" : "Ambassadeur");

// ── Onglets ──
const tabs = [
  { key: "partners" as const, label: "Partenaires", icon: "pi pi-briefcase" },
  {
    key: "rules" as const,
    label: "Règles de commission",
    icon: "pi pi-percentage",
  },
];
const activeTab = ref<"partners" | "rules">("partners");

// ══════════ Partenaires ══════════
const loadingPartners = ref(true);

const tiles = computed(() => [
  {
    label: "Dû à la plateforme",
    value: fcfa(sales.totalOwedToPlatform),
    tone: "text-ink",
    icon: "pi pi-arrow-down-left",
    iconClass: "bg-emerald-500/10 text-emerald-600",
  },
  {
    label: "À verser aux partenaires",
    value: fcfa(sales.totalOwedToPartners),
    tone: "text-ink",
    icon: "pi pi-arrow-up-right",
    iconClass: "bg-sky-500/10 text-sky-600",
  },
  {
    label: "Partenaires en retard",
    value: String(sales.overduePartners.length),
    tone: sales.overduePartners.length ? "text-amber-600" : "text-ink",
    icon: "pi pi-clock",
    iconClass: "bg-amber-500/15 text-amber-600",
  },
  {
    label: "Partenaires bloqués",
    value: String(sales.blockedPartners.length),
    tone: sales.blockedPartners.length ? "text-red-600" : "text-ink",
    icon: "pi pi-lock",
    iconClass: "bg-red-500/10 text-red-600",
  },
]);

type TypeFilter = "all" | PartnerType;
type StateFilter = "all" | "overdue" | "blocked" | "trial";
const typeFilter = ref<TypeFilter>("all");
const stateFilter = ref<StateFilter>("all");
const search = ref("");

const typeFilters = computed(() => [
  { key: "all" as const, label: "Tous", count: sales.partners.length },
  {
    key: "center" as const,
    label: "Centres",
    count: sales.partners.filter((p) => p.partner_type === "center").length,
  },
  {
    key: "ambassador" as const,
    label: "Ambassadeurs",
    count: sales.partners.filter((p) => p.partner_type === "ambassador").length,
  },
]);

const stateFilters = computed(() => [
  {
    key: "overdue" as const,
    label: "En retard",
    count: sales.overduePartners.length,
  },
  {
    key: "blocked" as const,
    label: "Bloqués",
    count: sales.blockedPartners.length,
  },
  {
    key: "trial" as const,
    label: "En essai",
    count: sales.partners.filter((p) => p.trial_active).length,
  },
]);

// Les cas à traiter d'abord : bloqués, puis en retard, puis le plus gros solde dû
const filteredPartners = computed(() => {
  const q = search.value.trim().toLowerCase();
  return sales.partners
    .filter(
      (p) => typeFilter.value === "all" || p.partner_type === typeFilter.value,
    )
    .filter((p) => {
      if (stateFilter.value === "overdue") return p.overdue_amount > 0;
      if (stateFilter.value === "blocked") return p.is_blocked;
      if (stateFilter.value === "trial") return p.trial_active;
      return true;
    })
    .filter((p) => !q || p.name.toLowerCase().includes(q))
    .sort(
      (a, b) =>
        Number(b.is_blocked) - Number(a.is_blocked) ||
        b.overdue_amount - a.overdue_amount ||
        b.owed_to_platform - a.owed_to_platform,
    );
});

// ── Panneau partenaire ──
const showDrawer = ref(false);
const selectedKey = ref<{ type: string; id: string } | null>(null);
const selected = computed(
  () =>
    sales.partners.find(
      (p) =>
        p.partner_type === selectedKey.value?.type &&
        p.partner_id === selectedKey.value?.id,
    ) ?? null,
);

const loadingDrawer = ref(false);
const drawerError = ref<string | null>(null);
const partnerSales = ref<PartnerSaleResponse[]>([]);
const partnerSettlements = ref<any[]>([]);

const settingsForm = ref({
  can_activate: true,
  unpaid_limit: null as number | null,
  payment_delay_hours: 0,
});

function resetSettingsForm(p: PartnerSummaryResponse) {
  settingsForm.value = {
    can_activate: p.can_activate,
    unpaid_limit: p.unpaid_limit,
    payment_delay_hours: p.payment_delay_hours,
  };
}

const settingsChanged = computed(() => {
  const p = selected.value;
  if (!p) return false;
  const f = settingsForm.value;
  return (
    f.can_activate !== p.can_activate ||
    f.unpaid_limit !== p.unpaid_limit ||
    f.payment_delay_hours !== p.payment_delay_hours
  );
});

async function loadDrawerData(p: PartnerSummaryResponse) {
  loadingDrawer.value = true;
  drawerError.value = null;
  const type = p.partner_type as PartnerType;
  const [salesRes, settlementsRes] = await Promise.all([
    sales.fetchPartnerSales(type, p.partner_id),
    sales.fetchPartnerSettlements(type, p.partner_id),
  ]);
  partnerSales.value = salesRes.success ? salesRes.data : [];
  partnerSettlements.value = settlementsRes.success ? settlementsRes.data : [];
  if (!salesRes.success) drawerError.value = salesRes.error;
  else if (!settlementsRes.success) drawerError.value = settlementsRes.error;
  loadingDrawer.value = false;
}

function openPartner(p: PartnerSummaryResponse) {
  selectedKey.value = { type: p.partner_type, id: p.partner_id };
  resetSettingsForm(p);
  resetTrialForm(p);
  partnerSales.value = [];
  partnerSettlements.value = [];
  showDrawer.value = true;
  loadDrawerData(p);
}

function saleBadge(s: PartnerSaleResponse) {
  if (s.status === "settled")
    return { label: "Réglée", class: "bg-emerald-500/10 text-emerald-600" };
  if (s.is_overdue)
    return { label: "En retard", class: "bg-red-500/10 text-red-600" };
  if (s.status === "partial")
    return { label: "Partielle", class: "bg-sky-500/10 text-sky-600" };
  return { label: "Due", class: "bg-amber-500/15 text-amber-600" };
}

const savingSettings = ref(false);

async function saveSettings() {
  const p = selected.value;
  if (!p) return;
  savingSettings.value = true;
  const res = await sales.updatePartnerSettings(
    p.partner_type as PartnerType,
    p.partner_id,
    { ...settingsForm.value },
  );
  savingSettings.value = false;
  if (res.success) {
    resetSettingsForm(res.data);
    toast.add({
      severity: "success",
      summary: "Réglages enregistrés",
      life: 2500,
    });
  } else {
    drawerError.value = res.error;
  }
}

// ── Période d'essai (centres) ──
const TRIAL_PRESETS = [
  { label: "7 jours · 3 élèves", days: 7, activations: 3 },
  { label: "14 jours · 5 élèves", days: 14, activations: 5 },
  { label: "30 jours · 10 élèves", days: 30, activations: 10 },
];

const trialForm = ref({ ends_at: null as Date | null, activations: null as number | null });
const savingTrial = ref(false);

function resetTrialForm(p: PartnerSummaryResponse) {
  trialForm.value = {
    ends_at: p.trial_ends_at ? new Date(p.trial_ends_at) : null,
    activations: p.trial_activations_left || null,
  };
}

function applyTrialPreset(days: number, activations: number) {
  const end = new Date();
  end.setDate(end.getDate() + days);
  trialForm.value = { ends_at: end, activations };
}

async function sendTrial(payload: { trial_ends_at: string | null; trial_activations_left: number }) {
  const p = selected.value;
  if (!p) return;
  savingTrial.value = true;
  const res = await sales.updatePartnerSettings(p.partner_type as PartnerType, p.partner_id, payload);
  savingTrial.value = false;
  if (!res.success) {
    drawerError.value = res.error;
    return false;
  }
  await sales.fetchPartners(); // badges et filtre « En essai » à jour
  if (selected.value) resetTrialForm(selected.value);
  return true;
}

async function saveTrial() {
  const f = trialForm.value;
  if (!f.ends_at || !f.activations) return;
  // Fin de journée : l'essai couvre tout le dernier jour choisi
  const end = new Date(f.ends_at);
  end.setHours(23, 59, 59, 0);
  if (await sendTrial({ trial_ends_at: end.toISOString(), trial_activations_left: f.activations })) {
    toast.add({ severity: "success", summary: "Période d'essai enregistrée", life: 2500 });
  }
}

function endTrial() {
  confirm.require({
    header: "Terminer l'essai",
    message: "Les prochaines activations de ce centre redeviendront payantes. Les activations déjà offertes restent valables.",
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "Terminer",
    rejectLabel: "Annuler",
    acceptClass: "p-button-danger",
    accept: async () => {
      if (await sendTrial({ trial_ends_at: null, trial_activations_left: 0 })) {
        toast.add({ severity: "success", summary: "Essai terminé", life: 2500 });
      }
    },
  });
}

// ── Règlement ──
const METHODS = ["Mobile Money", "Orange Money", "Espèces", "Virement"];

const showSettlement = ref(false);
const savingSettlement = ref(false);
const settlementError = ref<string | null>(null);
const settlementForm = ref({
  direction: SettlementCreate.direction.TO_PLATFORM,
  amount: null as number | null,
  method: "",
  reference: "",
  note: "",
});

const directions = computed(() => [
  {
    value: SettlementCreate.direction.TO_PLATFORM,
    label: "Reçu du partenaire",
    remaining: selected.value?.owed_to_platform ?? 0,
  },
  {
    value: SettlementCreate.direction.TO_PARTNER,
    label: "Versé au partenaire",
    remaining: selected.value?.owed_to_partner ?? 0,
  },
]);

function setDirection(d: SettlementCreate.direction) {
  settlementForm.value.direction = d;
  const remaining = directions.value.find((x) => x.value === d)?.remaining ?? 0;
  settlementForm.value.amount = remaining > 0 ? Math.round(remaining) : null;
}

function openSettlement() {
  const p = selected.value;
  if (!p) return;
  settlementForm.value = {
    direction: SettlementCreate.direction.TO_PLATFORM,
    amount: null,
    method: "",
    reference: "",
    note: "",
  };
  // Sens présélectionné : celui où il reste quelque chose à régler
  setDirection(
    p.owed_to_platform > 0 || p.owed_to_partner === 0
      ? SettlementCreate.direction.TO_PLATFORM
      : SettlementCreate.direction.TO_PARTNER,
  );
  settlementError.value = null;
  showSettlement.value = true;
}

async function saveSettlement() {
  const p = selected.value;
  const f = settlementForm.value;
  if (!p) return;
  if (!f.amount || f.amount <= 0 || !f.method.trim()) {
    settlementError.value = "Le montant et le moyen de paiement sont requis.";
    return;
  }
  savingSettlement.value = true;
  settlementError.value = null;
  const res = await sales.createSettlement({
    partner_type: p.partner_type as SettlementCreate.partner_type,
    partner_id: p.partner_id,
    direction: f.direction,
    amount: f.amount,
    method: f.method.trim(),
    reference: f.reference.trim() || null,
    note: f.note.trim() || null,
  });
  savingSettlement.value = false;
  if (res.success) {
    showSettlement.value = false;
    toast.add({
      severity: "success",
      summary: "Règlement enregistré",
      life: 3000,
    });
    // Soldes et ventes recalculés côté backend : on recharge
    await sales.fetchPartners();
    if (selected.value) await loadDrawerData(selected.value);
  } else {
    settlementError.value = res.error;
  }
}

// ══════════ Règles de commission ══════════
const loadingRules = ref(true);

const PARTNER_TYPES = [
  { value: CommissionRuleCreate.partner_type.CENTER, label: "Centres" },
  {
    value: CommissionRuleCreate.partner_type.AMBASSADOR,
    label: "Ambassadeurs",
  },
];
const RULE_TYPES = [
  { value: "percent", label: "%" },
  { value: "fixed", label: "Fixe" },
];

function partnerNameOf(type: string, id: string | null) {
  if (!id) return null;
  return (
    sales.partners.find((p) => p.partner_type === type && p.partner_id === id)
      ?.name ?? id.slice(0, 8)
  );
}

function planName(id: string) {
  return plans.value.find((p) => p.id === id)?.name ?? id.slice(0, 8);
}

function ruleScope(rule: CommissionRuleResponse) {
  const target = partnerNameOf(
    rule.partner_type,
    rule.partner_type === "center" ? rule.center_id : rule.user_id,
  );
  if (target) return target;
  return rule.partner_type === "center"
    ? "Tous les centres (par défaut)"
    : "Tous les ambassadeurs (par défaut)";
}

function ruleValue(rule: CommissionRuleResponse) {
  return rule.rule_type === "percent" ? `${rule.value} %` : fcfa(rule.value);
}

// Par type ; dans chaque type, la règle par défaut d'abord
const ruleGroups = computed(() =>
  (["center", "ambassador"] as const)
    .map((type) => ({
      type,
      label: type === "center" ? "Centres" : "Ambassadeurs",
      rules: sales.rules
        .filter((r) => r.partner_type === type)
        .sort((a, b) => {
          const specA =
            Number(!!(a.center_id || a.user_id)) + Number(!!a.plan_id);
          const specB =
            Number(!!(b.center_id || b.user_id)) + Number(!!b.plan_id);
          return specA - specB;
        }),
    }))
    .filter((g) => g.rules.length),
);

async function toggleRule(rule: CommissionRuleResponse, value: boolean) {
  const res = await sales.updateRule(rule.id, { is_active: value });
  if (!res.success)
    toast.add({ severity: "error", summary: res.error, life: 4000 });
}

function confirmDeleteRule(rule: CommissionRuleResponse) {
  confirm.require({
    header: "Supprimer la règle",
    message: `Supprimer la règle « ${ruleScope(rule)} · ${ruleValue(rule)} » ? Les ventes déjà enregistrées gardent leur commission.`,
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "Supprimer",
    rejectLabel: "Annuler",
    acceptClass: "p-button-danger",
    accept: async () => {
      const res = await sales.deleteRule(rule.id);
      if (res.success)
        toast.add({
          severity: "success",
          summary: "Règle supprimée",
          life: 2500,
        });
      else toast.add({ severity: "error", summary: res.error, life: 4000 });
    },
  });
}

const showRuleDialog = ref(false);
const editingRule = ref<CommissionRuleResponse | null>(null);
const savingRule = ref(false);
const ruleError = ref<string | null>(null);
const ruleForm = ref({
  partner_type: CommissionRuleCreate.partner_type.CENTER,
  partner_id: null as string | null,
  plan_id: null as string | null,
  rule_type: "percent" as "percent" | "fixed",
  value: null as number | null,
});

const partnerOptions = computed(() =>
  sales.partners.filter((p) => p.partner_type === ruleForm.value.partner_type),
);

function openRuleCreate() {
  editingRule.value = null;
  ruleForm.value = {
    partner_type: CommissionRuleCreate.partner_type.CENTER,
    partner_id: null,
    plan_id: null,
    rule_type: "percent",
    value: null,
  };
  ruleError.value = null;
  showRuleDialog.value = true;
}

function openRuleEdit(rule: CommissionRuleResponse) {
  editingRule.value = rule;
  ruleForm.value = {
    partner_type: rule.partner_type as CommissionRuleCreate.partner_type,
    partner_id: rule.center_id ?? rule.user_id,
    plan_id: rule.plan_id,
    rule_type: rule.rule_type as "percent" | "fixed",
    value: rule.value,
  };
  ruleError.value = null;
  showRuleDialog.value = true;
}

async function saveRule() {
  const f = ruleForm.value;
  if (f.value === null || f.value < 0) {
    ruleError.value = "La valeur est requise.";
    return;
  }
  if (f.rule_type === "percent" && f.value > 100) {
    ruleError.value = "Un pourcentage ne peut pas dépasser 100.";
    return;
  }
  savingRule.value = true;
  ruleError.value = null;

  const res = editingRule.value
    ? await sales.updateRule(editingRule.value.id, {
        rule_type: f.rule_type,
        value: f.value,
      })
    : await sales.createRule({
        partner_type: f.partner_type,
        center_id:
          f.partner_type === CommissionRuleCreate.partner_type.CENTER
            ? f.partner_id
            : null,
        user_id:
          f.partner_type === CommissionRuleCreate.partner_type.AMBASSADOR
            ? f.partner_id
            : null,
        plan_id: f.plan_id,
        rule_type: f.rule_type as CommissionRuleCreate.rule_type,
        value: f.value,
      });

  savingRule.value = false;
  if (res.success) {
    showRuleDialog.value = false;
    toast.add({
      severity: "success",
      summary: editingRule.value ? "Règle modifiée" : "Règle créée",
      life: 2500,
    });
  } else {
    ruleError.value = res.error;
  }
}

// ── Chargement ──
onMounted(async () => {
  const [partnersRes, rulesRes] = await Promise.all([
    sales.fetchPartners(),
    sales.fetchRules(),
    loadPlans(),
  ]);
  loadingPartners.value = false;
  loadingRules.value = false;
  if (!partnersRes.success)
    toast.add({ severity: "error", summary: partnersRes.error, life: 4000 });
  if (!rulesRes.success)
    toast.add({ severity: "error", summary: rulesRes.error, life: 4000 });
});
</script>
