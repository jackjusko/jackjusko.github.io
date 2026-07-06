# TTB Form 5130.9 Data Gap Analysis

## Purpose

This document identifies the data fields required to automatically populate TTB Form 5130.9 (Monthly/Quarterly Report of Operations) that are currently missing from the BrewLedger system.

## TTB Form Structure Overview

The form tracks beer inventory movements across different operational stages:

- **Operations** (a) - General operations
- **Cellar Bulk** (b) - Bulk beer in cellars
- **Racking Keg** (c) - Beer in kegs from racking
- **Bottling Bulk** (d) - Bulk beer for bottling
- **Case** (e) - Packaged beer in cases
- **Totals** (f, g) - Column totals

## Current System Capabilities

### What We Currently Track:

1. **Batches**: Name, date, vessel, status, planned volume
2. **Batch Additions**: Ingredients added to batches (malt, hops, yeast, etc.)
3. **Batch Readings**: Gravity, temperature, pH measurements
4. **Packaging Runs**: Format (bottles/cans/kegs), units_count
5. **Ledger Entries**:
  - `RECEIVE` - Inventory received
  - `CONSUME` - Inventory consumed (for batch additions)
  - `TRANSFER_IN/OUT` - Inventory moved between locations
  - `COUNT_ADJUST` - Physical count corrections
  - `REVERSAL` - Undo previous transactions
  - `CORRECTION` - Manual adjustments
6. **Inventory by Location**: On-hand quantities at each location
7. **Vessel Splits**: Batch volumes split across multiple vessels

## Missing Data Fields for TTB Form 5130.9

### Header Information (Currently Missing)

- **Brewery EIN** (Employer Identification Number)
- **TTB Brewery Number** (BR-XXXXX format)
- **Brewery Contact Phone**
- **Brewery Full Address** (Number & Street, City, County, State, ZIP Code)
- **Reporting Period** (Year, Month or Quarter)

### Part 1 - Beer Summary: Additions to Inventory

#### Line 1: On hand beginning of period

**Status**: ✅ **Can Calculate** - Can derive from previous period's ending inventory

#### Line 2: Beer produced by fermentation

**Status**: ❌ **MISSING**

- **What's Needed**: Track when a batch completes fermentation and becomes "beer"
- **Current Gap**: We track batch creation and status, but don't explicitly mark when fermentation completes and beer is produced
- **Required Data**: 
  - Batch completion date (when fermentation completes)
  - Volume of beer produced (from batch volume)
  - Location where beer is produced (vessel/cellar location)

#### Line 3: Addition of water and other liquids

**Status**: ❌ **MISSING**

- **What's Needed**: Track water and liquid additions to beer (post-fermentation)
- **Current Gap**: We track ingredient additions (batch_additions) but don't distinguish water/liquid additions separately
- **Required Data**:
  - Water additions (quantity, date, batch)
  - Other liquid additions (quantity, date, batch, liquid type)
  - Location where addition occurs

#### Line 4: Beer received from racking and bottling

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer that returns from racking/bottling operations (e.g., leftover beer not packaged)
- **Current Gap**: We track packaging runs but don't track returns from packaging operations
- **Required Data**:
  - Quantity returned from racking
  - Quantity returned from bottling
  - Date of return
  - Source location (racking/bottling area)
  - Destination location (cellar)

#### Line 5: Beer received in bond

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer received from other breweries under bond (tax-free transfer)
- **Current Gap**: No mechanism to track beer received from external breweries
- **Required Data**:
  - Quantity received
  - Date received
  - Source brewery information
  - Bond documentation reference
  - Location where received

#### Line 6: Beer received from cellars

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track beer transferred between cellar locations
- **Current Gap**: We have TRANSFER_IN/OUT but don't distinguish cellar-to-cellar transfers specifically
- **Required Data**:
  - Transfer type classification (cellar-to-cellar vs. other transfers)
  - Source cellar location
  - Destination location
  - Quantity transferred

#### Line 7: Beer returned to this brewery after removal from this brewery

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer that was removed (sold/consumed) but then returned
- **Current Gap**: No mechanism to track returns after removal
- **Required Data**:
  - Original removal date and quantity
  - Return date and quantity
  - Reason for return
  - Original removal type (sale, consumption, etc.)

#### Line 8: Beer returned to the brewery after removal from another brewery of same ownership

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer returned from related breweries
- **Current Gap**: No mechanism to track inter-brewery returns
- **Required Data**:
  - Source brewery information
  - Return date and quantity
  - Original removal date
  - Related brewery ownership information

#### Line 9: Racked

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer that has been racked (transferred to kegs)
- **Current Gap**: We track packaging runs but don't distinguish racking as a separate operation
- **Required Data**:
  - Racking date
  - Quantity racked
  - Source location (cellar/vessel)
  - Destination (keg location)
  - Number of kegs filled

#### Line 10: Bottled

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track beer that has been bottled
- **Current Gap**: We track packaging runs with format, but need to distinguish bottling specifically and track volume bottled
- **Required Data**:
  - Bottling date
  - Volume bottled (in barrels)
  - Number of bottles/cases
  - Source location
  - Destination location (packaged goods storage)

#### Line 11: Physical inventory disclosed an overage

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track positive inventory variances (overages)
- **Current Gap**: We have variance_events but need to distinguish overages from shortages
- **Required Data**:
  - Overage quantity
  - Date discovered
  - Location
  - Reason for overage

#### Line 12: (Blank line - no data needed)

#### Line 13: Total additions to inventory

**Status**: ✅ **Can Calculate** - Sum of lines 1-12

### Part 1 - Beer Summary: Removals from Inventory

#### Line 14: Removed for consumption or sale

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed for sale or consumption
- **Current Gap**: No mechanism to track removals with purpose classification
- **Required Data**:
  - Removal date
  - Quantity removed
  - Purpose (sale vs. consumption)
  - Location removed from
  - Customer/sale information (if applicable)

#### Line 15: Removed tax-determined for consumption or sale to tavern on brewery premises

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed for on-premise tavern sales
- **Current Gap**: No mechanism to track on-premise removals separately
- **Required Data**:
  - Removal date
  - Quantity removed
  - Tax determination status
  - Location (brewery premises tavern)

#### Line 16: Removed without payment of tax for export

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed for export (tax-free)
- **Current Gap**: No mechanism to track export removals
- **Required Data**:
  - Export date
  - Quantity exported
  - Export destination country
  - Export documentation reference
  - Location removed from

#### Line 17: Removed without payment of tax for use as supplies (vessels/aircraft)

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed for vessel/aircraft supplies (tax-free)
- **Current Gap**: No mechanism to track removals for supplies
- **Required Data**:
  - Removal date
  - Quantity removed
  - Vessel/aircraft information
  - Location removed from

#### Line 18: Removed without payment of tax for use in research and development

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed for R&D purposes (tax-free)
- **Current Gap**: No mechanism to track R&D removals
- **Required Data**:
  - Removal date
  - Quantity removed
  - R&D project information
  - Location removed from

#### Line 19: Removed without payment of tax to other breweries and pilot brewing plants of same ownership

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer transferred to related breweries (tax-free)
- **Current Gap**: No mechanism to track inter-brewery transfers
- **Required Data**:
  - Transfer date
  - Quantity transferred
  - Destination brewery information
  - Related ownership information
  - Location removed from

#### Line 20: Removed without payment of tax as beer unfit for sale removed for use in manufacturing

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed as unfit for sale (for manufacturing use)
- **Current Gap**: No mechanism to track unfit beer removals
- **Required Data**:
  - Removal date
  - Quantity removed
  - Reason for being unfit
  - Manufacturing use information
  - Location removed from

#### Line 21: Beer consumed on premises

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer consumed at the brewery (not sold)
- **Current Gap**: No mechanism to track on-premise consumption separately
- **Required Data**:
  - Consumption date
  - Quantity consumed
  - Location consumed
  - Purpose (tasting, employee consumption, etc.)

#### Line 22: Beer transferred for racking

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track beer transferred to racking operations
- **Current Gap**: We have transfers but don't classify them as "for racking"
- **Required Data**:
  - Transfer date
  - Quantity transferred
  - Source location
  - Destination (racking area)

#### Line 23: Beer transferred for bottling

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track beer transferred to bottling operations
- **Current Gap**: We have transfers but don't classify them as "for bottling"
- **Required Data**:
  - Transfer date
  - Quantity transferred
  - Source location
  - Destination (bottling area)

#### Line 24: Beer returned to cellars

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track beer returned to cellar storage
- **Current Gap**: We have transfers but don't classify returns to cellars specifically
- **Required Data**:
  - Return date
  - Quantity returned
  - Source location
  - Destination cellar location

#### Line 25: Beer racked

**Status**: ❌ **MISSING** (Same as Line 9)

- **What's Needed**: Track beer that has been racked
- **Current Gap**: See Line 9 above

#### Line 26: Beer bottled

**Status**: ⚠️ **PARTIALLY TRACKED** (Same as Line 10)

- **What's Needed**: Track beer that has been bottled
- **Current Gap**: See Line 10 above

#### Line 27: Laboratory samples

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer removed for lab testing
- **Current Gap**: No mechanism to track sample removals
- **Required Data**:
  - Sample date
  - Quantity sampled
  - Location sampled from
  - Lab/test information

#### Line 28: Beer destroyed at brewery

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer destroyed/wasted at the brewery
- **Current Gap**: No mechanism to track destruction events
- **Required Data**:
  - Destruction date
  - Quantity destroyed
  - Reason for destruction
  - Location where destroyed
  - Destruction method

#### Line 29: Beer transferred to a distilled spirits plant

**Status**: ❌ **MISSING**

- **What's Needed**: Track beer transferred to DSP for spirits production
- **Current Gap**: No mechanism to track DSP transfers
- **Required Data**:
  - Transfer date
  - Quantity transferred
  - Destination DSP information
  - Location removed from

#### Line 30: Losses, including theft

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track inventory losses and theft
- **Current Gap**: We have variance_events but need to distinguish losses/theft specifically
- **Required Data**:
  - Loss date
  - Quantity lost
  - Loss type (theft, spoilage, breakage, etc.)
  - Location where loss occurred
  - Incident details

#### Line 31: Physical inventory disclosed a shortage

**Status**: ⚠️ **PARTIALLY TRACKED**

- **What's Needed**: Track negative inventory variances (shortages)
- **Current Gap**: We have variance_events but need to distinguish shortages from overages
- **Required Data**:
  - Shortage quantity
  - Date discovered
  - Location
  - Reason for shortage

#### Line 32: (Blank line - no data needed)

#### Line 33: Total amount of beer on hand at end of period

**Status**: ✅ **Can Calculate** - Ending inventory from ledger

#### Line 34: Total beer

**Status**: ✅ **Can Calculate** - Sum of all beer

### Part 2 - Cereal Beverage Summary (Products < 0.5% ABV)

#### Line 1: Produced

**Status**: ❌ **MISSING**

- **What's Needed**: Track production of non-alcoholic beverages (< 0.5% ABV)
- **Current Gap**: No mechanism to distinguish low-alcohol products
- **Required Data**:
  - Production date
  - Quantity produced
  - Product type/name
  - ABV verification

#### Line 2: Removed

**Status**: ❌ **MISSING**

- **What's Needed**: Track removals of cereal beverages
- **Current Gap**: No mechanism to track low-alcohol product removals
- **Required Data**:
  - Removal date
  - Quantity removed
  - Removal purpose

#### Line 3: Received

**Status**: ❌ **MISSING**

- **What's Needed**: Track cereal beverages received
- **Current Gap**: No mechanism to track low-alcohol product receipts
- **Required Data**:
  - Receipt date
  - Quantity received
  - Source information

#### Line 4: Loss and wastage

**Status**: ❌ **MISSING**

- **What's Needed**: Track losses of cereal beverages
- **Current Gap**: No mechanism to track low-alcohol product losses
- **Required Data**:
  - Loss date
  - Quantity lost
  - Loss reason

#### Line 5: (Blank line - no data needed)

#### Line 6: Total on hand end of period

**Status**: ✅ **Can Calculate** - If cereal beverages are tracked

### Part 3 - Remarks

**Status**: ✅ **Can Support** - Free text field, no additional data structure needed

## Summary of Missing Data Collection Requirements

### Critical Missing Features:

1. **Beer Production Tracking**
  - Mark batch completion/fermentation completion
  - Track volume of beer produced
  - Associate production with location
2. **Removal Purpose Classification**
  - Add removal purpose/reason to ledger entries
  - Categories: sale, consumption, export, R&D, supplies, inter-brewery transfer, unfit, on-premise consumption, samples, destruction, DSP transfer
3. **Water/Liquid Additions**
  - Track water additions separately from other ingredients
  - Track other liquid additions post-fermentation
  - Associate with batch and location
4. **Racking Operations**
  - Track racking as separate operation from packaging
  - Record quantity racked, date, source/destination
  - Track keg fills
5. **Packaging Detail**
  - Distinguish bottling from other packaging
  - Track volume bottled (not just unit count)
  - Track returns from packaging operations
6. **Inter-Brewery Operations**
  - Track beer received in bond from other breweries
  - Track transfers to related breweries
  - Track returns from related breweries
7. **Tax Status Tracking**
  - Track tax-determined removals
  - Track tax-free removals (export, R&D, supplies, inter-brewery)
  - Associate tax status with removals
8. **Return Tracking**
  - Track beer returned after removal
  - Track returns from packaging operations
  - Associate returns with original removal
9. **Variance Classification**
  - Distinguish overages from shortages
  - Classify loss types (theft, spoilage, breakage)
  - Track physical inventory adjustments
10. **Cereal Beverage Tracking**
  - Distinguish products < 0.5% ABV
    - Track production, removals, receipts, losses separately
11. **Brewery Information**
  - Store brewery EIN
    - Store TTB brewery number
    - Store full brewery address
    - Store contact phone

## Recommended Implementation Approach

### Phase 1: Core Data Structures

1. Add brewery information fields to `orgs` table
2. Extend `ledger_entries` with removal purpose/reason field
3. Add batch completion/production tracking
4. Add water/liquid addition tracking

### Phase 2: Operational Tracking

1. Add racking operations tracking
2. Enhance packaging runs with volume and return tracking
3. Add removal purpose classification system
4. Add return tracking mechanism

### Phase 3: Advanced Features

1. Add inter-brewery transfer tracking
2. Add tax status tracking
3. Add cereal beverage classification
4. Build TTB form generation/reporting

### Phase 4: Reporting

1. Build TTB form auto-population logic
2. Add period-based reporting (monthly/quarterly)
3. Add form validation and submission tracking

## Next Steps

1. Review this analysis with stakeholders
2. Prioritize which TTB fields are most critical for initial implementation
3. Design data model extensions for missing fields
4. Plan UI/UX for collecting new data points
5. Implement data collection features incrementally
6. Build TTB form generation and export functionality

