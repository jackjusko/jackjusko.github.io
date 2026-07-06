# TTB Data Collection - Mobile App Implementation Plan

**Date:** 2026-02-06  
**Goal:** Add TTB data collection to mobile app without overcomplicating day-to-day UI  
**Principle:** Integrate TTB fields into existing workflows, keep UI simple and practical

---

## Implementation Philosophy

### Design Principles
1. **Minimal disruption** - Add fields to existing views, don't create separate TTB workflows
2. **Smart defaults** - Auto-set values where possible (tax status, operation type inference)
3. **Progressive disclosure** - Common options first, advanced options hidden/collapsible
4. **Mobile-first** - Use mobile UI patterns (bottom sheets, simple pickers, inline fields)
5. **Practical workflow** - Match how brewers actually work day-to-day

### Data Collection Strategy
- **Consume view** - Add removal purpose (most critical)
- **Transfer view** - Add operation type (simple dropdown)
- **BatchDetail** - Add production complete and water addition (quick actions)
- **CountSession** - Add loss type (simple dropdown)
- **Packaging** - Add volume_bottled (optional field)

---

## Phase 1: Removals Classification (Consume.vue) - HIGHEST PRIORITY

### Goal
Enable TTB removal classification (Lines 14-20, 21, 27, 28) without complicating daily consumption workflow.

### Current State
- `Consume.vue` creates CONSUME entries without `removal_purpose` or `tax_status`
- Used for batch ingredient consumption (not beer removals)
- Simple form: batch, location, items, quantities

### Challenge
Consume view is used for **ingredient consumption** (batch additions), but TTB removals are **beer removals** (finished product). Need to distinguish these use cases.

### Solution: Smart Context Detection

**Option A: Separate "Remove Beer" Action (RECOMMENDED)**
- Add "Remove Beer" button to bottom nav or batch detail
- Separate from ingredient consumption
- Clear distinction: ingredients vs finished beer

**Option B: Enhance Consume.vue with Context Detection**
- Detect if consuming beer items (finished product)
- Show removal purpose fields only for beer items
- Keep ingredient consumption simple

**Recommendation: Option A** - Cleaner separation, less confusion

### Implementation Details

#### 1.1 Create RemoveBeer.vue View

**Location:** `platforms/brewledger-app/src/views/RemoveBeer.vue`

**UI Design:**
- Similar to Consume.vue but focused on beer removals
- Mobile-optimized: single item per screen, swipe to add more
- Simple, focused workflow

**Form Fields:**
```
- Beer Item (dropdown) - Required
- Location (dropdown) - Required  
- Quantity (number input, barrels) - Required
- Purpose (dropdown) - Required, simplified options
  - Sale
  - Consumption  
  - Export
  - R&D
  - Other (expands to show more options)
- Date (datetime-local, defaults to now)
- Note (optional textarea)
```

**Simplified Purpose Options (Primary Screen):**
- Sale
- Consumption
- Export
- R&D
- Other (shows full list)

**Full Purpose Options (When "Other" selected):**
- Supplies (vessels/aircraft)
- Inter-brewery transfer
- Unfit for sale
- On-premise consumption
- Laboratory sample
- Destroyed at brewery
- DSP transfer
- Loss/theft

**Tax Status:**
- Auto-set based on purpose (no user input needed)
- Tax-free: export, R&D, supplies, inter-brewery
- Taxable: sale, consumption, on-premise
- Tax-determined: tavern (if purpose is on-premise)

**Code Structure:**
```javascript
// Simplified removal purposes for mobile
const PRIMARY_PURPOSES = [
  { value: 'sale', label: 'Sale' },
  { value: 'consumption', label: 'Consumption' },
  { value: 'export', label: 'Export' },
  { value: 'rnd', label: 'R&D' },
  { value: 'other', label: 'Other...' }
]

const ALL_PURPOSES = [
  ...PRIMARY_PURPOSES,
  { value: 'supplies', label: 'Supplies (vessels/aircraft)' },
  { value: 'inter_brewery', label: 'Inter-brewery transfer' },
  { value: 'unfit', label: 'Unfit for sale' },
  { value: 'on_premise', label: 'On-premise consumption' },
  { value: 'sample', label: 'Laboratory sample' },
  { value: 'destruction', label: 'Destroyed at brewery' },
  { value: 'dsp_transfer', label: 'DSP transfer' },
  { value: 'loss_theft', label: 'Loss or theft' }
]

// Auto-set tax status
function getTaxStatus(purpose) {
  const taxFree = ['export', 'rnd', 'supplies', 'inter_brewery']
  return taxFree.includes(purpose) ? 'tax_free' : 'taxable'
}
```

**Save Logic:**
```javascript
await LedgerRepository.addEntry({
  type: 'CONSUME',
  item_id: form.item_id,
  location_id: form.location_id,
  quantity: -Math.abs(form.quantity), // Negative for consumption
  removal_purpose: form.removal_purpose,
  tax_status: getTaxStatus(form.removal_purpose), // Auto-set
  created_at: new Date(form.date).toISOString(),
  note: form.note || undefined
})
```

**Navigation:**
- Add to bottom nav: "Remove Beer" icon (🚚 or 📤)
- Or add button to BatchDetail: "Remove Beer" (for batch context)
- Or add to main menu/dashboard

**Files to Create:**
- `platforms/brewledger-app/src/views/RemoveBeer.vue`

**Files to Modify:**
- `platforms/brewledger-app/src/router/index.js` - Add route `/remove-beer`
- `platforms/brewledger-app/src/App.vue` or navigation component - Add nav item

**Testing Checklist:**
- [ ] Can select beer item
- [ ] Can select location
- [ ] Can enter quantity (barrels)
- [ ] Purpose dropdown shows primary options
- [ ] "Other" expands to show full list
- [ ] Tax status auto-sets correctly
- [ ] Creates ledger entry with removal_purpose and tax_status
- [ ] Syncs to server correctly
- [ ] Data appears in console app Removals view

---

## Phase 2: Transfer Operation Type (Transfer.vue) - HIGH PRIORITY

### Goal
Enable TTB transfer classification (Lines 4, 9, 22, 23, 24, 25) by adding operation type to transfers.

### Current State
- `Transfer.vue` creates transfers without `operation_type`
- Simple form: item, from location, to location, quantity, note

### Solution: Add Simple Operation Type Dropdown

**UI Change:**
- Add "Operation Type" dropdown (optional field, defaults to "Transfer")
- Simple options, most common first
- Only show when relevant (beer items)

**Form Fields Added:**
```
- Operation Type (dropdown, optional)
  - Transfer (default)
  - Racking
  - Bottling
  - Return to Cellar
  - Other
```

**Smart Defaults:**
- If note contains "rack" or "keg" → suggest "Racking"
- If note contains "bottle" or "can" → suggest "Bottling"
- If note contains "return" → suggest "Return to Cellar"
- Default: "Transfer"

**Code Changes:**
```javascript
// In Transfer.vue form
const form = reactive({
  itemId: '',
  fromLocationId: '',
  toLocationId: '',
  quantity: '',
  note: '',
  operationType: 'transfer' // NEW: Default to 'transfer'
})

// Watch note for smart suggestions
watch(() => form.note, (note) => {
  if (!note) return
  const lower = note.toLowerCase()
  if (lower.includes('rack') || lower.includes('keg')) {
    form.operationType = 'racking'
  } else if (lower.includes('bottle') || lower.includes('can')) {
    form.operationType = 'bottling'
  } else if (lower.includes('return')) {
    form.operationType = 'return'
  }
})

// In submit function
await LedgerRepository.transfer({
  itemId: form.itemId,
  fromLocationId: form.fromLocationId,
  toLocationId: form.toLocationId,
  quantity: form.quantity,
  note: form.note,
  operationType: form.operationType || 'transfer' // NEW
})
```

**UI Placement:**
- Add dropdown after "Note" field
- Label: "Operation Type (optional)"
- Small text: "For TTB reporting - defaults to Transfer"
- Collapsible/optional to keep UI clean

**Files to Modify:**
- `platforms/brewledger-app/src/views/Transfer.vue`

**Testing Checklist:**
- [ ] Operation type dropdown appears
- [ ] Defaults to "Transfer"
- [ ] Can select Racking, Bottling, Return
- [ ] Smart suggestions work from note field
- [ ] Creates transfer with operation_type
- [ ] Syncs to server correctly
- [ ] Data appears in TTB form calculations

---

## Phase 3: Production Complete (BatchDetail.vue) - HIGH PRIORITY

### Goal
Enable TTB Line 2 (beer produced) by adding production complete tracking.

### Current State
- `BatchDetail.vue` has batch operations but no production complete
- Has "Add Ingredient" and "Log Reading" buttons
- Has packaging modal

### Solution: Add Quick Action Button

**UI Change:**
- Add "Mark Complete" button to quick actions (next to "Log Reading", "Add Ingredient")
- Simple modal with minimal fields
- One-tap workflow for common case

**Quick Actions Layout:**
```
[📊 Log Reading] [➕ Add Ingredient]
[🍺 Mark Complete] [💧 Add Water]
[📦 Record Packaging]
```

**Modal Fields (Production Complete):**
```
- Vessel (dropdown) - Required
  - Shows batch locations (vessel splits)
  - Or "All vessels" option
- Volume Produced (number, barrels) - Required
- Completion Date (datetime-local, defaults to now)
- Location (dropdown, optional) - Where beer is stored
```

**Simplified UI:**
- Default to first vessel if only one
- Default date to now
- Volume in barrels (with unit label)
- One-tap save for common case

**Code Changes:**
```javascript
// Add to BatchDetail.vue modals
const modals = reactive({
  // ... existing modals
  productionComplete: false
})

const forms = reactive({
  // ... existing forms
  productionComplete: {
    batch_location_id: null,
    volume_produced: null,
    completion_date: new Date().toISOString().slice(0, 16),
    location_id: null
  }
})

const openProductionCompleteModal = () => {
  // Default to first batch location if only one
  if (batchLocations.value.length === 1) {
    forms.productionComplete.batch_location_id = batchLocations.value[0].id
  }
  forms.productionComplete.completion_date = new Date().toISOString().slice(0, 16)
  modals.productionComplete = true
}

const saveProductionComplete = async () => {
  if (!forms.productionComplete.batch_location_id) {
    showAlert('Error', 'Please select a vessel', 'danger')
    return
  }
  if (!forms.productionComplete.volume_produced || forms.productionComplete.volume_produced <= 0) {
    showAlert('Error', 'Please enter volume produced', 'danger')
    return
  }

  const completionDate = new Date(forms.productionComplete.completion_date).toISOString()
  
  // Find or create FG_CONFIRMED milestone
  const existing = milestones.value.find(m => 
    m.milestone_definition_id === 'FG_CONFIRMED' || 
    m.milestone_type === 'FG_CONFIRMED'
  )

  const milestoneData = {
    volume_produced: forms.productionComplete.volume_produced,
    production_location_id: forms.productionComplete.location_id,
    production_batch_location_id: forms.productionComplete.batch_location_id
  }

  if (existing) {
    // Update existing milestone
    await BatchMilestoneRepository.update(existing.id, {
      occurred_at: completionDate,
      note: `Production Complete: ${forms.productionComplete.volume_produced} barrels`,
      data: { ...existing.data, ...milestoneData }
    })
  } else {
    // Create new milestone
    await BatchMilestoneRepository.create({
      batch_id: batch.value.id,
      milestone_definition_id: 'FG_CONFIRMED',
      milestone_type: 'FG_CONFIRMED',
      occurred_at: completionDate,
      note: `Production Complete: ${forms.productionComplete.volume_produced} barrels`,
      data: milestoneData
    })
  }

  modals.productionComplete = false
  showAlert('Success', 'Production marked complete', 'success')
  await refreshBatchData()
}
```

**Modal UI:**
```vue
<ModalDialog 
  :isOpen="modals.productionComplete" 
  title="Mark Production Complete" 
  confirmText="Mark Complete" 
  type="confirm" 
  @confirm="saveProductionComplete" 
  @cancel="modals.productionComplete = false"
>
  <div class="space-y-3">
    <div>
      <label class="block text-sm font-medium mb-1">Vessel</label>
      <select v-model="forms.productionComplete.batch_location_id" class="w-full border p-2 rounded">
        <option :value="null">Select vessel...</option>
        <option v-for="bl in batchLocations" :key="bl.id" :value="bl.id">
          {{ getVesselName(bl.vessel_id) }}
        </option>
      </select>
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Volume Produced (Barrels)</label>
      <input 
        v-model.number="forms.productionComplete.volume_produced" 
        type="number" 
        step="0.01" 
        min="0" 
        class="w-full border p-2 rounded"
        placeholder="0.00"
      />
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Completion Date</label>
      <input 
        v-model="forms.productionComplete.completion_date" 
        type="datetime-local" 
        class="w-full border p-2 rounded"
      />
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Storage Location (optional)</label>
      <select v-model="forms.productionComplete.location_id" class="w-full border p-2 rounded">
        <option :value="null">Select location...</option>
        <option v-for="loc in locations" :key="loc.id" :value="loc.id">
          {{ loc.name }}
        </option>
      </select>
    </div>
  </div>
</ModalDialog>
```

**Files to Modify:**
- `platforms/brewledger-app/src/views/BatchDetail.vue`

**Testing Checklist:**
- [ ] "Mark Complete" button appears in quick actions
- [ ] Modal opens with vessel dropdown
- [ ] Can select vessel (or defaults to first if only one)
- [ ] Can enter volume produced (barrels)
- [ ] Date defaults to now
- [ ] Creates/updates FG_CONFIRMED milestone
- [ ] Stores volume_produced in milestone data
- [ ] Syncs to server correctly
- [ ] Appears in TTB form Line 2 calculation

---

## Phase 4: Water/Liquid Additions (BatchDetail.vue) - MEDIUM PRIORITY

### Goal
Enable TTB Line 3 (water/liquid additions) by adding water addition tracking.

### Solution: Add Quick Action Button

**UI Change:**
- Add "Add Water" button to quick actions
- Simple modal, similar to production complete
- Distinguish water vs other liquids

**Modal Fields:**
```
- Type (dropdown) - Required
  - Water
  - Other Liquid
- Liquid Type (text, shown if "Other Liquid") - Required if Other
- Vessel (dropdown) - Required
- Quantity (number, gallons) - Required
- Date (datetime-local, defaults to now)
- Note (optional)
```

**Code Changes:**
```javascript
// Add to BatchDetail.vue
const modals = reactive({
  // ... existing modals
  waterAddition: false
})

const forms = reactive({
  // ... existing forms
  waterAddition: {
    batch_location_id: null,
    addition_type: 'WATER', // 'WATER' or 'LIQUID'
    liquid_type: '',
    quantity: null,
    added_at: new Date().toISOString().slice(0, 16),
    note: ''
  }
})

const openWaterAdditionModal = () => {
  if (batchLocations.value.length === 1) {
    forms.waterAddition.batch_location_id = batchLocations.value[0].id
  }
  forms.waterAddition.added_at = new Date().toISOString().slice(0, 16)
  modals.waterAddition = true
}

const saveWaterAddition = async () => {
  if (!forms.waterAddition.batch_location_id) {
    showAlert('Error', 'Please select a vessel', 'danger')
    return
  }
  if (!forms.waterAddition.quantity || forms.waterAddition.quantity <= 0) {
    showAlert('Error', 'Please enter quantity', 'danger')
    return
  }
  if (forms.waterAddition.addition_type === 'LIQUID' && !forms.waterAddition.liquid_type) {
    showAlert('Error', 'Please specify liquid type', 'danger')
    return
  }

  const eventType = forms.waterAddition.addition_type === 'WATER' ? 'WATER_ADDITION' : 'LIQUID_ADDITION'

  await BatchAdditionRepository.add({
    batch_id: batch.value.id,
    batch_location_id: forms.waterAddition.batch_location_id,
    event_type: eventType,
    quantity: forms.waterAddition.quantity,
    added_at: new Date(forms.waterAddition.added_at).toISOString(),
    note: forms.waterAddition.note || (forms.waterAddition.addition_type === 'LIQUID' ? `Liquid type: ${forms.waterAddition.liquid_type}` : 'Water addition'),
    liquid_type: forms.waterAddition.addition_type === 'LIQUID' ? forms.waterAddition.liquid_type : null,
    // Don't create ledger entry - water additions don't consume inventory
    item_id: null,
    location_id: null
  })

  modals.waterAddition = false
  showAlert('Success', 'Water/liquid addition recorded', 'success')
  await refreshBatchData()
}
```

**Modal UI:**
```vue
<ModalDialog 
  :isOpen="modals.waterAddition" 
  title="Add Water or Liquid" 
  confirmText="Add" 
  type="confirm" 
  @confirm="saveWaterAddition" 
  @cancel="modals.waterAddition = false"
>
  <div class="space-y-3">
    <div>
      <label class="block text-sm font-medium mb-1">Type</label>
      <select v-model="forms.waterAddition.addition_type" class="w-full border p-2 rounded">
        <option value="WATER">Water</option>
        <option value="LIQUID">Other Liquid</option>
      </select>
    </div>
    <div v-if="forms.waterAddition.addition_type === 'LIQUID'">
      <label class="block text-sm font-medium mb-1">Liquid Type</label>
      <input 
        v-model="forms.waterAddition.liquid_type" 
        type="text" 
        class="w-full border p-2 rounded"
        placeholder="e.g. Fruit juice, flavoring"
      />
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Vessel</label>
      <select v-model="forms.waterAddition.batch_location_id" class="w-full border p-2 rounded">
        <option :value="null">Select vessel...</option>
        <option v-for="bl in batchLocations" :key="bl.id" :value="bl.id">
          {{ getVesselName(bl.vessel_id) }}
        </option>
      </select>
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Quantity (Gallons)</label>
      <input 
        v-model.number="forms.waterAddition.quantity" 
        type="number" 
        step="0.01" 
        min="0" 
        class="w-full border p-2 rounded"
        placeholder="0.00"
      />
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Date</label>
      <input 
        v-model="forms.waterAddition.added_at" 
        type="datetime-local" 
        class="w-full border p-2 rounded"
      />
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Note (optional)</label>
      <textarea 
        v-model="forms.waterAddition.note" 
        rows="2" 
        class="w-full border p-2 rounded"
        placeholder="Optional notes..."
      ></textarea>
    </div>
  </div>
</ModalDialog>
```

**Files to Modify:**
- `platforms/brewledger-app/src/views/BatchDetail.vue`

**Testing Checklist:**
- [ ] "Add Water" button appears in quick actions
- [ ] Modal opens with type dropdown
- [ ] Can select Water or Other Liquid
- [ ] Liquid type field shows when "Other Liquid" selected
- [ ] Can select vessel
- [ ] Can enter quantity (gallons)
- [ ] Creates batch addition with event_type: 'WATER_ADDITION' or 'LIQUID_ADDITION'
- [ ] Does NOT create ledger entry (correct - water doesn't consume inventory)
- [ ] Syncs to server correctly
- [ ] Appears in TTB form Line 3 calculation

---

## Phase 5: Loss Classification (CountSession.vue) - MEDIUM PRIORITY

### Goal
Enable TTB Line 30 (losses including theft) by adding loss type classification to variance events.

### Current State
- `CountSession.vue` creates variance events during physical counts
- Auto-determines variance_type (overage/shortage) from delta_qty
- Does NOT collect loss_type

### Solution: Add Loss Type Field to Variance Review

**UI Change:**
- When reviewing variances (shortages), add "Loss Type" dropdown
- Only show for shortages (negative variances)
- Simple options, defaults to "Other"

**Variance Review Flow:**
1. User completes count
2. System detects variances
3. Review screen shows variances with loss type dropdown (for shortages)
4. User selects loss type, submits

**Code Changes:**
```javascript
// In CountSession.vue variance review
const variances = ref([]) // Existing

// Add loss_type to variance object
const variance = {
  item: item,
  expected: expected,
  counted: counted,
  diff: diff,
  reason: 'Unknown',
  loss_type: null // NEW: Only for shortages
}

// In review mode, show loss type dropdown for shortages
const submitFinal = async () => {
  const countedItems = countItems.value.filter(i => i.counted !== null && i.counted !== '')
  await finalizeClose(countedItems, variances.value)
}

const finalizeClose = async (countedItems, varianceList) => {
  const closedCounts = []
  
  // Process Variances
  for (const v of varianceList) {
    // Create Variance Event
    const varianceEvent = await VarianceEventRepository.create({
      item_id: v.item.id,
      location_id: locationId,
      count_session_id: session.value.id,
      expected_qty: v.expected,
      actual_qty: v.counted,
      delta_qty: v.diff,
      reason: v.reason,
      variance_type: v.diff > 0 ? 'overage' : 'shortage', // Auto-determined
      loss_type: v.diff < 0 ? (v.loss_type || null) : null // NEW: Only for shortages
    })

    // Ledger Entry (only for shortages with loss_type)
    if (v.diff < 0 && v.loss_type) {
      await LedgerRepository.addEntry({
        variance_event_id: varianceEvent.id,
        type: 'CONSUME',
        item_id: v.item.id,
        location_id: locationId,
        quantity: v.diff, // Negative
        count_session_id: session.value.id,
        removal_purpose: 'loss_theft', // For TTB Line 30
        note: `Count variance: ${v.counted} (Exp: ${v.expected}) - ${v.loss_type}`
      })
    } else {
      // Standard COUNT_ADJUST entry
      await LedgerRepository.addEntry({
        variance_event_id: varianceEvent.id,
        type: 'COUNT_ADJUST',
        item_id: v.item.id,
        location_id: locationId,
        quantity: v.diff,
        count_session_id: session.value.id,
        note: `Count: ${v.counted} (Exp: ${v.expected}) - ${v.reason}`
      })
    }
  }

  // ... rest of close logic
}
```

**UI Changes:**
```vue
<!-- In variance review section -->
<div v-for="(v, idx) in variances" :key="idx" class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 mb-3">
  <div class="flex justify-between items-center mb-2">
    <span class="font-medium">{{ v.item.name }}</span>
    <span :class="v.diff < 0 ? 'text-red-600' : 'text-green-600'">
      {{ v.diff > 0 ? '+' : '' }}{{ v.diff }}
    </span>
  </div>
  <div class="text-sm text-gray-500 mb-2">
    Expected: {{ v.expected }} | Counted: {{ v.counted }}
  </div>
  
  <!-- Loss Type (only for shortages) -->
  <div v-if="v.diff < 0" class="mb-2">
    <label class="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-200">Loss Type (for TTB reporting)</label>
    <select 
      v-model="v.loss_type" 
      class="w-full border border-gray-200 dark:border-gray-600 p-1.5 rounded text-sm"
    >
      <option :value="null">Not classified</option>
      <option value="theft">Theft</option>
      <option value="spoilage">Spoilage</option>
      <option value="breakage">Breakage</option>
      <option value="other">Other</option>
    </select>
    <p class="text-xs text-gray-400 mt-1">Optional - helps with TTB reporting</p>
  </div>
  
  <div>
    <label class="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-200">Reason</label>
    <input 
      v-model="v.reason" 
      type="text" 
      class="w-full border border-gray-200 dark:border-gray-600 p-1.5 rounded text-sm"
      placeholder="Reason for variance"
    />
  </div>
</div>
```

**Files to Modify:**
- `platforms/brewledger-app/src/views/CountSession.vue`

**Testing Checklist:**
- [ ] Loss type dropdown appears for shortages in variance review
- [ ] Loss type dropdown does NOT appear for overages
- [ ] Can select loss type (theft, spoilage, breakage, other)
- [ ] Creates variance event with loss_type
- [ ] Creates ledger entry with removal_purpose: 'loss_theft' when loss_type set
- [ ] Syncs to server correctly
- [ ] Appears in TTB form Line 30 calculation

---

## Phase 6: Packaging Volume (BatchDetail.vue) - LOW PRIORITY

### Goal
Improve accuracy of TTB Lines 10, 23, 26 (bottling) by collecting volume_bottled.

### Current State
- `BatchDetail.vue` packaging modal collects format and units_count
- Does NOT collect volume_bottled
- Volume estimated from units_count (inaccurate)

### Solution: Add Optional Volume Field

**UI Change:**
- Add "Volume Bottled (Barrels)" field to packaging modal
- Optional field (can estimate from units if not provided)
- Only show for bottling/canning (not kegs)

**Code Changes:**
```javascript
// In BatchDetail.vue packaging form
const forms = reactive({
  // ... existing forms
  packaging: {
    format: 'KEG',
    units_count: 0,
    volume_bottled: null, // NEW: Optional
    supplies: [],
    batch_id: batch.value.id
  }
})

const savePackaging = async () => {
  if (!forms.packaging.units_count) {
    return showAlert('Validation Error', 'Please enter a unit count.', 'danger')
  }

  // Calculate volume_bottled if not provided (for bottling/canning)
  let volumeBottled = forms.packaging.volume_bottled
  if (!volumeBottled && (forms.packaging.format === 'BOTTLE' || forms.packaging.format === 'CAN')) {
    // Estimate: assume 12oz bottles (0.094 gallons per bottle)
    const gallonsPerUnit = 0.094
    volumeBottled = (forms.packaging.units_count * gallonsPerUnit) / 31 // Convert to barrels
  }

  // ... existing supply processing

  const packagingData = {
    format: forms.packaging.format,
    units_count: forms.packaging.units_count,
    volume_bottled: volumeBottled || null,
    format_type: forms.packaging.format.toLowerCase() // 'bottle', 'can', or 'keg'
  }

  await PackagingRunRepository.create({
    ...forms.packaging,
    data: packagingData // Store TTB metadata in data blob
  }, validSupplies)

  // ... rest of save logic
}
```

**Modal UI Addition:**
```vue
<!-- In packaging modal, after units_count field -->
<div v-if="forms.packaging.format === 'BOTTLE' || forms.packaging.format === 'CAN'">
  <label class="block text-sm font-medium mb-1">Volume Bottled (Barrels) - Optional</label>
  <input 
    v-model.number="forms.packaging.volume_bottled" 
    type="number" 
    step="0.01" 
    min="0" 
    class="w-full border p-2 rounded"
    placeholder="Auto-calculated if not provided"
  />
  <p class="text-xs text-gray-400 mt-1">Leave blank to auto-calculate from unit count</p>
</div>
```

**Files to Modify:**
- `platforms/brewledger-app/src/views/BatchDetail.vue`

**Testing Checklist:**
- [ ] Volume bottled field appears for bottling/canning
- [ ] Field does NOT appear for kegs
- [ ] Can enter volume manually (barrels)
- [ ] Auto-calculates if not provided (from units_count)
- [ ] Stores volume_bottled in packaging run data
- [ ] Stores format_type in packaging run data
- [ ] Syncs to server correctly
- [ ] Appears in TTB form Lines 10, 23, 26 calculations

---

## Implementation Summary

### Files to Create
1. `platforms/brewledger-app/src/views/RemoveBeer.vue` - New view for beer removals

### Files to Modify
1. `platforms/brewledger-app/src/views/Transfer.vue` - Add operation_type dropdown
2. `platforms/brewledger-app/src/views/BatchDetail.vue` - Add production complete, water addition, packaging volume
3. `platforms/brewledger-app/src/views/CountSession.vue` - Add loss_type dropdown
4. `platforms/brewledger-app/src/router/index.js` - Add RemoveBeer route
5. Navigation component (App.vue or bottom nav) - Add RemoveBeer nav item

### Data Collected (Mobile App)

| TTB Line | Data Field | Collection Method | Status |
|----------|------------|-------------------|--------|
| **Line 2** | volume_produced | BatchDetail "Mark Complete" button | ✅ Phase 3 |
| **Line 3** | WATER_ADDITION/LIQUID_ADDITION | BatchDetail "Add Water" button | ✅ Phase 4 |
| **Lines 4, 9, 22, 25** | operation_type: 'racking' | Transfer.vue dropdown | ✅ Phase 2 |
| **Lines 10, 23, 26** | volume_bottled, format_type | BatchDetail packaging modal | ✅ Phase 6 |
| **Lines 14-20, 21, 27, 28** | removal_purpose, tax_status | RemoveBeer.vue view | ✅ Phase 1 |
| **Line 30** | loss_type | CountSession.vue variance review | ✅ Phase 5 |

### Implementation Order (Recommended)

1. **Phase 1: RemoveBeer.vue** (Highest impact - enables most TTB lines)
2. **Phase 2: Transfer.vue** (Quick win - simple dropdown)
3. **Phase 3: BatchDetail production complete** (Critical for Line 2)
4. **Phase 4: BatchDetail water addition** (Critical for Line 3)
5. **Phase 5: CountSession loss type** (Important for Line 30)
6. **Phase 6: BatchDetail packaging volume** (Nice-to-have, improves accuracy)

### Testing Strategy

**Per Phase:**
1. Test UI flow (open modal, fill form, submit)
2. Verify data stored correctly (check IndexedDB)
3. Verify sync to server (check server database)
4. Verify TTB form calculation (generate form in console app)
5. Test edge cases (empty fields, invalid data, etc.)

**End-to-End:**
1. Record operations in mobile app with TTB data
2. Sync to server
3. Generate TTB form in console app
4. Verify all lines populated correctly
5. Export PDF and verify form fields

---

## UI/UX Considerations

### Mobile-First Design
- Use bottom sheets/modals for forms (not full-screen pages)
- Large touch targets (44px minimum)
- Simple dropdowns (not complex multi-select)
- Auto-fill defaults where possible
- Progressive disclosure (common options first)

### Workflow Integration
- Add TTB fields to existing workflows (don't create separate TTB workflow)
- Make TTB fields optional where possible (don't block daily operations)
- Provide helpful hints/descriptions for TTB fields
- Show TTB context only when relevant (beer items, not ingredients)

### User Education
- Add tooltips/help text for TTB fields
- Show "Why?" explanations (e.g., "For TTB reporting")
- Provide examples/defaults
- Don't overwhelm with TTB terminology

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Users can record beer removals with purpose classification
- ✅ Removals sync to server with removal_purpose and tax_status
- ✅ TTB form Lines 14-20, 21, 27, 28 populated from mobile data

### Phase 2 Complete When:
- ✅ Users can classify transfers by operation type
- ✅ Transfers sync with operation_type
- ✅ TTB form Lines 4, 9, 22, 23, 24, 25 populated from mobile data

### Phase 3 Complete When:
- ✅ Users can mark production complete with volume
- ✅ Production data syncs to server
- ✅ TTB form Line 2 populated from mobile data

### Phase 4 Complete When:
- ✅ Users can record water/liquid additions
- ✅ Additions sync with event_type
- ✅ TTB form Line 3 populated from mobile data

### Phase 5 Complete When:
- ✅ Users can classify losses during count sessions
- ✅ Losses sync with loss_type
- ✅ TTB form Line 30 populated from mobile data

### Phase 6 Complete When:
- ✅ Users can enter volume_bottled for packaging
- ✅ Packaging syncs with volume_bottled and format_type
- ✅ TTB form Lines 10, 23, 26 more accurate

### Overall Success When:
- ✅ All TTB form lines can be populated from mobile app data
- ✅ No manual data entry required in console app
- ✅ Mobile UI remains simple and practical for daily use
- ✅ TTB data collection doesn't slow down daily operations

---

## Future Enhancements (Post-Implementation)

1. **Bulk Classification Tool** - Classify existing removals/transfers in console app
2. **Beer Item Filtering** - Auto-detect beer items vs ingredients
3. **Smart Suggestions** - ML/AI to suggest removal purposes based on patterns
4. **TTB Preview** - Show TTB impact when recording operations in mobile app
5. **Export Destination Tracking** - Enhanced export removal tracking
6. **In-Bond/DSP Transfers** - Add classification for Lines 5 and 29

---

**Implementation Status:** PLANNED  
**Estimated Effort:** 2-3 weeks (one phase per 2-3 days)  
**Priority:** HIGH - Required for accurate TTB form generation from mobile data
