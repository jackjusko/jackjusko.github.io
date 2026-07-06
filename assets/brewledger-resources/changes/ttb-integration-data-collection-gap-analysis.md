# TTB Integration – Critical Data Collection Gap Analysis

**Review date:** 2026-02-06 (Third pass - Data Collection Focus)  
**Scope:** Verify mobile app (`platforms/brewledger-app/`) collects all data needed for TTB Form 5130.9  
**Critical Finding:** ⚠️ **MAJOR DATA COLLECTION GAPS IDENTIFIED**

---

## Executive Summary

**CRITICAL ISSUE:** While the TTB integration infrastructure exists (repositories support TTB fields, console app has UI for TTB data entry), **the mobile app does NOT collect TTB-specific data**. Since most operational data is collected through the mobile app, users cannot generate accurate TTB forms without manually entering data in the console app.

**Impact:** Users will need to:
1. Record operations in mobile app (without TTB classification)
2. Manually re-enter or classify data in console app for TTB reporting
3. Or rely on console app exclusively for TTB-compliant operations

---

## TTB Form Line-by-Line Data Collection Status

### Part 1: Additions to Inventory

| Line | TTB Requirement | Mobile App Collection | Console App Collection | Status |
|------|-----------------|----------------------|----------------------|--------|
| **Line 1** | Beginning inventory | ✅ Can calculate from ledger | ✅ Can calculate from ledger | ✅ OK |
| **Line 2** | Beer produced (volume_produced) | ❌ **NO UI** | ✅ Production complete modal | ❌ **GAP** |
| **Line 3** | Water/liquid additions | ❌ **NO UI** | ✅ Water addition modal | ❌ **GAP** |
| **Line 4** | Beer from racking/bottling | ❌ **NO UI** | ✅ Racking view | ❌ **GAP** |
| **Line 5** | Beer received in bond | ❌ **NO UI** | ❌ No UI | ❌ **GAP** |
| **Line 6** | Beer from cellars | ⚠️ Partial (TRANSFER_IN) | ⚠️ Partial (TRANSFER_IN) | ⚠️ **PARTIAL** |
| **Line 7** | Beer returned after removal | ❌ **NO UI** | ❌ No UI | ❌ **GAP** |
| **Line 8** | Beer from other brewery | ❌ **NO UI** | ❌ No UI | ❌ **GAP** |
| **Line 9** | Beer racked | ❌ **NO UI** | ✅ Racking view | ❌ **GAP** |
| **Line 10** | Beer bottled | ⚠️ Partial (packaging, no volume_bottled) | ⚠️ Partial (packaging, no volume_bottled) | ⚠️ **PARTIAL** |
| **Line 11** | Inventory overage | ⚠️ Partial (variance, no classification) | ⚠️ Partial (variance, no classification) | ⚠️ **PARTIAL** |
| **Line 13** | Total additions | ✅ Can calculate | ✅ Can calculate | ✅ OK |

### Part 2: Removals from Inventory

| Line | TTB Requirement | Mobile App Collection | Console App Collection | Status |
|------|-----------------|----------------------|----------------------|--------|
| **Lines 14-20** | Removals by purpose | ❌ **NO UI** | ✅ Removals view | ❌ **GAP** |
| **Line 21** | Consumed on premises | ❌ **NO UI** | ⚠️ Partial (Removals view) | ❌ **GAP** |
| **Line 22** | Transferred for racking | ❌ **NO UI** | ✅ Racking view | ❌ **GAP** |
| **Line 23** | Transferred for bottling | ❌ **NO UI** | ⚠️ Partial (packaging) | ❌ **GAP** |
| **Line 24** | Returned to cellars | ❌ **NO UI** | ⚠️ Partial (transfers) | ❌ **GAP** |
| **Line 25** | Beer racked (removal) | ❌ **NO UI** | ✅ Racking view | ❌ **GAP** |
| **Line 26** | Beer bottled (removal) | ❌ **NO UI** | ⚠️ Partial (packaging) | ❌ **GAP** |
| **Line 27** | Laboratory samples | ❌ **NO UI** | ⚠️ Partial (Removals view) | ❌ **GAP** |
| **Line 28** | Beer destroyed | ❌ **NO UI** | ⚠️ Partial (Removals view) | ❌ **GAP** |
| **Line 29** | Transferred to DSP | ❌ **NO UI** | ❌ No UI | ❌ **GAP** |
| **Line 30** | Losses including theft | ❌ **NO UI** | ✅ Losses view | ❌ **GAP** |
| **Line 31** | Inventory shortage | ⚠️ Partial (variance, no classification) | ⚠️ Partial (variance, no classification) | ⚠️ **PARTIAL** |
| **Line 33** | Ending inventory | ✅ Can calculate | ✅ Can calculate | ✅ OK |
| **Line 34** | Total beer | ✅ Can calculate | ✅ Can calculate | ✅ OK |

---

## Detailed Gap Analysis

### 1. Production Completion (Line 2) - CRITICAL GAP

**TTB Requirement:** Track when fermentation completes and beer is produced, with volume_produced.

**Mobile App:**
- ❌ No UI to mark production complete
- ❌ No way to record `volume_produced`
- ❌ Batch milestones exist but no FG_CONFIRMED milestone with volume data

**Console App:**
- ✅ "Mark Production Complete" button in BatchDetail
- ✅ Modal collects volume_produced, location, date
- ✅ Stores in milestone with TTB metadata

**Impact:** Mobile app users cannot record production completion for TTB Line 2.

---

### 2. Water/Liquid Additions (Line 3) - CRITICAL GAP

**TTB Requirement:** Track water and liquid additions separately from ingredient additions.

**Mobile App:**
- ❌ Batch additions don't distinguish WATER_ADDITION or LIQUID_ADDITION
- ❌ No UI to record water additions specifically
- ❌ All additions treated as ingredient consumption

**Console App:**
- ✅ "Add Water/Liquid" button in BatchDetail
- ✅ Modal distinguishes Water vs Other Liquid
- ✅ Stores with `event_type: 'WATER_ADDITION'` or `'LIQUID_ADDITION'`
- ✅ Does NOT create ledger entry (correct - water doesn't consume inventory)

**Impact:** Mobile app users cannot record water additions for TTB Line 3.

---

### 3. Removals Classification (Lines 14-20, 21, 27, 28) - CRITICAL GAP

**TTB Requirement:** Classify all beer removals by purpose (sale, consumption, export, R&D, etc.) and tax status.

**Mobile App:**
- ❌ `Consume.vue` does NOT collect `removal_purpose` or `tax_status`
- ❌ Creates CONSUME entries without TTB classification
- ❌ No way to distinguish sale vs consumption vs export vs R&D

**Console App:**
- ✅ `Removals.vue` dedicated view for classified removals
- ✅ Form collects removal_purpose, tax_status, export destination, related brewery
- ✅ Auto-sets tax_status based on purpose
- ✅ Recent removals table shows classified entries

**Impact:** Mobile app users cannot classify removals for TTB Lines 14-20, 21, 27, 28.

---

### 4. Racking Operations (Lines 4, 9, 22, 25) - CRITICAL GAP

**TTB Requirement:** Track racking operations separately from other transfers, with operation_type: 'racking'.

**Mobile App:**
- ❌ `Transfer.vue` does NOT collect `operation_type`
- ❌ No way to distinguish racking from other transfers
- ❌ No UI specifically for racking operations

**Console App:**
- ✅ `Racking.vue` dedicated view for racking operations
- ✅ Collects batch, beer item, source/destination, quantity racked, kegs filled
- ✅ Creates transfer with `operation_type: 'racking'`
- ✅ Creates packaging run (format: KEG) for consistency

**Impact:** Mobile app users cannot record racking operations for TTB Lines 4, 9, 22, 25.

---

### 5. Packaging Volume (Lines 10, 23, 26) - PARTIAL GAP

**TTB Requirement:** Track volume_bottled and format_type (bottle/can/keg) for bottling operations.

**Mobile App:**
- ⚠️ `BatchDetail.vue` packaging modal collects format and units_count
- ❌ Does NOT collect `volume_bottled` (relies on estimation)
- ❌ Does NOT store `format_type` in packaging run data
- ⚠️ Can estimate from units_count but not accurate

**Console App:**
- ⚠️ Enhanced packaging modal collects `volume_bottled`
- ⚠️ Stores `format_type` in packaging run data
- ⚠️ Auto-calculates volume from units if not provided (assumes 12oz bottles)

**Impact:** Mobile app packaging data is less accurate for TTB Lines 10, 23, 26.

---

### 6. Losses & Theft (Line 30) - CRITICAL GAP

**TTB Requirement:** Classify losses by type (theft, spoilage, breakage) and track separately.

**Mobile App:**
- ❌ `CountSession.vue` creates variance events but does NOT collect `loss_type`
- ❌ No UI to classify losses as theft, spoilage, breakage, other
- ❌ Variance events created without TTB classification

**Console App:**
- ✅ `Losses.vue` dedicated view for loss recording
- ✅ Form collects loss_type (theft, spoilage, breakage, other)
- ✅ Creates variance event with `variance_type: 'shortage'` and `loss_type`
- ✅ Creates ledger entry with `removal_purpose: 'loss_theft'`

**Impact:** Mobile app users cannot classify losses for TTB Line 30.

---

### 7. Variance Classification (Lines 11, 31) - PARTIAL GAP

**TTB Requirement:** Distinguish overages (Line 11) from shortages (Line 31), classify loss types.

**Mobile App:**
- ⚠️ `VarianceEventRepository.create()` auto-determines `variance_type` from delta_qty
- ❌ Does NOT collect `loss_type` in count session UI
- ⚠️ Variance events created but not fully classified for TTB

**Console App:**
- ⚠️ Same auto-classification in VarianceEventRepository
- ✅ `Losses.vue` collects `loss_type` for manual loss recording
- ⚠️ Count sessions still don't collect loss_type

**Impact:** Mobile app variance events are partially classified but missing loss_type.

---

## Repository Support vs UI Collection

### What Repositories Support (Both Platforms)

✅ **LedgerRepository:**
- `addEntry()` accepts: `removal_purpose`, `tax_status`, `operation_type`, `related_brewery_id`, `return_of_ledger_id`
- `transfer()` accepts: `operationType` parameter
- Fields stored in entry object, synced to server JSON blob

✅ **VarianceEventRepository:**
- `create()` auto-determines `variance_type` from `delta_qty`
- Accepts `loss_type` field (theft, spoilage, breakage, other)
- Fields stored in variance event object, synced to server JSON blob

✅ **BatchMilestoneRepository:**
- Supports storing `volume_produced` in milestone data
- Supports FG_CONFIRMED milestone type

✅ **BatchAdditionRepository:**
- Supports `event_type` field (can store 'WATER_ADDITION', 'LIQUID_ADDITION')
- Supports `liquid_type` metadata

✅ **PackagingRunRepository:**
- Supports storing `volume_bottled` and `format_type` in packaging run data

### What Mobile App UI Collects

❌ **Consume.vue:**
- Does NOT collect `removal_purpose` or `tax_status`
- Creates CONSUME entries without TTB classification

❌ **Transfer.vue:**
- Does NOT collect `operation_type`
- Creates transfers without TTB classification

❌ **BatchDetail.vue:**
- Does NOT have production complete UI
- Does NOT have water addition UI
- Packaging modal does NOT collect `volume_bottled` or `format_type`

❌ **CountSession.vue:**
- Does NOT collect `loss_type` when creating variance events

---

## Recommendations

### Option 1: Add TTB Data Collection to Mobile App (RECOMMENDED)

**Priority:** HIGH - Required for accurate TTB form generation from mobile-collected data

**Changes Needed:**

1. **Consume.vue Enhancement:**
   - Add removal purpose dropdown (sale, consumption, export, R&D, supplies, other_brewery, unfit)
   - Add tax status field (auto-set based on purpose, can override)
   - Add conditional fields (export destination, related brewery)
   - Pass `removal_purpose` and `tax_status` to `LedgerRepository.addEntry()`

2. **Transfer.vue Enhancement:**
   - Add operation type dropdown (transfer, racking, bottling, return)
   - Pass `operationType` to `LedgerRepository.transfer()`

3. **BatchDetail.vue Enhancements:**
   - Add "Mark Production Complete" button and modal (similar to console)
   - Add "Add Water/Liquid" button and modal (similar to console)
   - Enhance packaging modal to collect `volume_bottled` and `format_type`

4. **New Losses View:**
   - Create `Losses.vue` view (similar to console)
   - Form for recording losses with classification

5. **New Racking View (Optional):**
   - Create `Racking.vue` view (similar to console)
   - Or enhance Transfer.vue to handle racking specifically

**Effort:** Medium-High (multiple UI changes, new views)

**Impact:** ✅ Mobile app users can collect all TTB data needed for accurate form generation

---

### Option 2: Console-Only TTB Workflow (CURRENT STATE)

**Priority:** LOW - Users must use console app for TTB-compliant operations

**Workflow:**
1. Record operations in mobile app (without TTB classification)
2. Manually classify/update data in console app:
   - Use Removals view to classify existing CONSUME entries
   - Use Racking view to record racking operations
   - Use Losses view to classify variance events
   - Use BatchDetail production complete modal
   - Use BatchDetail water addition modal

**Effort:** None (current state)

**Impact:** ❌ Double data entry, error-prone, time-consuming

---

### Option 3: Hybrid Approach (PARTIAL)

**Priority:** MEDIUM - Add critical TTB fields to mobile app, keep advanced features in console

**Changes Needed:**
1. Add removal_purpose to Consume.vue (most critical)
2. Add operation_type to Transfer.vue
3. Add production complete to BatchDetail.vue
4. Keep advanced features (Removals view, Racking view, Losses view) in console only

**Effort:** Medium (fewer UI changes)

**Impact:** ⚠️ Partial - Mobile app collects some TTB data, console needed for advanced classification

---

## Data Completeness Assessment

### Can Generate TTB Form with Current Mobile App Data?

**Answer: ⚠️ PARTIALLY**

**What Works:**
- ✅ Line 1: Beginning inventory (calculated from ledger)
- ✅ Line 6: Beer from cellars (TRANSFER_IN entries)
- ✅ Line 13: Total additions (calculated)
- ✅ Line 33: Ending inventory (calculated)
- ✅ Line 34: Total beer (calculated)

**What's Missing/Inaccurate:**
- ❌ Line 2: Beer produced (no production completion data)
- ❌ Line 3: Water additions (no water addition data)
- ❌ Lines 4, 9, 22, 25: Racking operations (no racking classification)
- ❌ Lines 14-20: Removals by purpose (no removal_purpose)
- ❌ Line 21: On-premise consumption (no classification)
- ❌ Lines 23, 26: Bottling (no volume_bottled, format_type)
- ❌ Line 27: Laboratory samples (no classification)
- ❌ Line 28: Beer destroyed (no classification)
- ❌ Line 30: Losses (no loss_type classification)
- ⚠️ Lines 10, 11, 31: Partial (packaging volume estimated, variance partially classified)

**Result:** TTB form will have **significant gaps** and **inaccurate data** if generated from mobile app data only.

---

## Conclusion

**CRITICAL FINDING:** The mobile app does NOT collect TTB-specific data fields, even though the repositories support them. This creates a major gap where:

1. Users collect most operational data in the mobile app
2. TTB form generation requires TTB-specific classifications
3. Users must manually re-enter or classify data in the console app

**RECOMMENDATION:** Implement Option 1 (Add TTB Data Collection to Mobile App) to enable accurate TTB form generation from mobile-collected data.

**PRIORITY:** HIGH - This is a fundamental data collection gap that prevents accurate TTB reporting.

---

## Next Steps

1. **Decision:** Choose implementation option (1, 2, or 3)
2. **If Option 1:** Create implementation plan for mobile app TTB UI enhancements
3. **If Option 2:** Document console-only workflow and user training requirements
4. **If Option 3:** Prioritize which TTB fields to add to mobile app

---

**Review Status:** COMPLETE  
**Critical Issues Found:** 7 major data collection gaps  
**Recommendation:** Add TTB data collection to mobile app (Option 1)
