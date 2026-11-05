<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'view' ? t('purchaseOrder.viewTitle') : t('purchaseOrder.createTitle') }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="item-context">
              <div class="context-name">{{ translateProductName(backlogItem.item_name) }}</div>
              <div class="context-meta">
                <span class="mono">{{ t('purchaseOrder.sku') }}: {{ backlogItem.item_sku }}</span>
                <span>{{ t('purchaseOrder.shortage') }}: {{ shortage }} {{ t('purchaseOrder.units') }}</span>
              </div>
            </div>

            <!-- View mode -->
            <template v-if="mode === 'view'">
              <div v-if="viewLoading" class="state-message">{{ t('common.loading') }}</div>
              <div v-else-if="viewError" class="error-message">{{ viewError }}</div>
              <div v-else-if="po" class="info-grid">
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.poId') }}</div>
                  <div class="info-value mono">{{ po.id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.status') }}</div>
                  <div class="info-value"><span class="badge">{{ po.status }}</span></div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.supplier') }}</div>
                  <div class="info-value">{{ po.supplier_name }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.quantity') }}</div>
                  <div class="info-value">{{ po.quantity }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.unitCost') }}</div>
                  <div class="info-value">{{ formatMoney(po.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.total') }}</div>
                  <div class="info-value">{{ formatMoney(po.quantity * po.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.expectedDelivery') }}</div>
                  <div class="info-value">{{ formatDate(po.expected_delivery_date) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrder.createdDate') }}</div>
                  <div class="info-value">{{ formatDate(po.created_date) }}</div>
                </div>
                <div v-if="po.notes" class="info-item full">
                  <div class="info-label">{{ t('purchaseOrder.notesLabel') }}</div>
                  <div class="info-value">{{ po.notes }}</div>
                </div>
              </div>
            </template>

            <!-- Create mode -->
            <form v-else id="po-form" class="po-form" novalidate @submit.prevent="submit">
              <div class="form-group">
                <label for="po-supplier">{{ t('purchaseOrder.supplier') }} *</label>
                <input id="po-supplier" v-model="form.supplier_name" type="text" class="form-input" />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label for="po-quantity">{{ t('purchaseOrder.quantity') }} *</label>
                  <input id="po-quantity" v-model="form.quantity" type="number" min="1" step="1" class="form-input" />
                </div>
                <div class="form-group">
                  <label for="po-unit-cost">{{ t('purchaseOrder.unitCost') }} *</label>
                  <input id="po-unit-cost" v-model="form.unit_cost" type="number" min="0" step="0.01" class="form-input" />
                </div>
              </div>
              <div class="form-group">
                <label for="po-date">{{ t('purchaseOrder.expectedDelivery') }} *</label>
                <input id="po-date" v-model="form.expected_delivery_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label for="po-notes">{{ t('purchaseOrder.notes') }}</label>
                <textarea id="po-notes" v-model="form.notes" rows="3" class="form-input"></textarea>
              </div>

              <div class="total-row">
                <span>{{ t('purchaseOrder.total') }}</span>
                <strong>{{ formatMoney(total) }}</strong>
              </div>

              <div v-if="submitError" class="error-message">{{ submitError }}</div>
            </form>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" type="button" @click="close">{{ t('common.close') }}</button>
            <button
              v-if="mode === 'create'"
              class="btn-primary"
              type="submit"
              form="po-form"
              :disabled="submitting"
            >
              {{ submitting ? t('purchaseOrder.submitting') : t('purchaseOrder.submit') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

const { t, translateProductName } = useI18n()

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  backlogItem: { type: Object, default: null },
  mode: { type: String, default: 'create' }
})

const emit = defineEmits(['close', 'po-created'])

const form = ref({ supplier_name: '', quantity: '', unit_cost: '', expected_delivery_date: '', notes: '' })
const submitting = ref(false)
const submitError = ref(null)
const po = ref(null)
const viewLoading = ref(false)
const viewError = ref(null)

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return Math.max(0, props.backlogItem.quantity_needed - props.backlogItem.quantity_available)
})

const total = computed(() => {
  const q = Number(form.value.quantity)
  const c = Number(form.value.unit_cost)
  return Number.isFinite(q) && Number.isFinite(c) ? q * c : 0
})

const formatMoney = (value) =>
  `$${Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const loadPO = async () => {
  viewLoading.value = true
  viewError.value = null
  po.value = null
  try {
    po.value = await api.getPurchaseOrderByBacklogItem(props.backlogItem.id)
  } catch (err) {
    viewError.value = err?.response?.status === 404 ? t('purchaseOrder.notFound') : t('purchaseOrder.loadFailed')
    console.error('Failed to load purchase order:', err)
  } finally {
    viewLoading.value = false
  }
}

// Reset all state every time the modal opens (or the target item/mode changes while open)
watch(
  () => [props.isOpen, props.backlogItem?.id, props.mode],
  () => {
    if (!props.isOpen || !props.backlogItem) return
    submitError.value = null
    submitting.value = false
    po.value = null
    viewError.value = null
    form.value = {
      supplier_name: '',
      quantity: shortage.value > 0 ? shortage.value : '',
      unit_cost: '',
      expected_delivery_date: '',
      notes: ''
    }
    if (props.mode === 'view') loadPO()
  },
  { immediate: true }
)

const validate = () => {
  const f = form.value
  const q = Number(f.quantity)
  const c = Number(f.unit_cost)
  if (!f.supplier_name.trim()) return t('purchaseOrder.errSupplier')
  if (f.quantity === '' || !Number.isInteger(q) || q <= 0) return t('purchaseOrder.errQuantity')
  if (f.unit_cost === '' || !Number.isFinite(c) || c <= 0) return t('purchaseOrder.errUnitCost')
  if (!f.expected_delivery_date || isNaN(new Date(f.expected_delivery_date).getTime())) return t('purchaseOrder.errDate')
  return null
}

const submit = async () => {
  if (submitting.value) return
  submitError.value = validate()
  if (submitError.value) return
  submitting.value = true
  try {
    const f = form.value
    const created = await api.createPurchaseOrder({
      backlog_item_id: props.backlogItem.id,
      supplier_name: f.supplier_name.trim(),
      quantity: Number(f.quantity),
      unit_cost: Number(f.unit_cost),
      expected_delivery_date: f.expected_delivery_date,
      notes: f.notes.trim() || null
    })
    emit('po-created', created)
  } catch (err) {
    const status = err?.response?.status
    submitError.value = status === 409 ? t('purchaseOrder.alreadyExists') : t('purchaseOrder.createFailed')
    console.error('Failed to create purchase order:', err)
  } finally {
    submitting.value = false
  }
}

const close = () => emit('close')
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.item-context {
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.context-name {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.context-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.875rem;
  color: #64748b;
}

.mono {
  font-family: 'Monaco', 'Courier New', monospace;
}

.po-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.form-input {
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: inherit;
  color: #0f172a;
  background: white;
  resize: vertical;
}

.form-input:focus {
  outline: none;
  border-color: #64748b;
  box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.15);
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f1f5f9;
  border-radius: 8px;
  color: #334155;
}

.total-row strong {
  font-size: 1.125rem;
  color: #0f172a;
}

.error-message {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
}

.state-message {
  text-align: center;
  color: #64748b;
  padding: 2rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.info-item.full {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
  word-break: break-word;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: capitalize;
  background: #dbeafe;
  color: #1e40af;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary,
.btn-primary {
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #334155;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  background: #0f172a;
  border: 1px solid #0f172a;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1e293b;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
