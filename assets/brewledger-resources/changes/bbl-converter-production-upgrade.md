# BBL to Case Converter – Production Manager Upgrade

## Overview

Expanded the BBL to Case converter from a simple sales-equivalent calculator into a full production planning tool with loss/yield, multi-format split, materials, revenue, and comparison table.

## Features Implemented

### 1. Loss & Yield Variables

- **Yield % slider** (80–100%, default 95%)—accounts for tank bottoms, foam, low-fills
- **Theoretical max** (100% yield) vs **Realistic pack-out** (selected yield %) in comparison table

### 2. Expanded Packaging Formats

- 12 oz case (24-pack)
- 12 oz 6-pack
- 16 oz 4-pack
- 19.2 oz stovepipe (6-pack)
- 750 ml bottle
- 1/2 BBL keg
- 1/6 BBL keg (sixtel)

### 3. Multi-Format Batch Split

- "Split the batch" section with allocation rows
- Each row: BBL amount + format dropdown
- Add/remove allocation rows
- Net BBL (after yield) applied per allocation
- Warning when allocated total ≠ batch total

### 4. Materials Estimator

- Shown when split includes can/bottle formats
- Cans, lids/caps, flats/carriers, 750 ml bottles
- Per-format unit counts (24 cans/case, 6 cans/6-pack, etc.)

### 5. Revenue Estimator

- Price per 24-pack case, price per 1/2 BBL keg
- With split: total revenue from allocation (sixtels use 1/3 of half-BBL price)
- Without split: "If all cases" and "If all kegs" separate estimates

### 6. Comparison Table

- What-if table: Format (rows) × 100% theoretical | yield % realistic (columns)
- All 7 formats shown

## Conversion Constants

- 1 BBL = 31 US gal = 3,968 fl oz
- 1/2 BBL = 15.5 gal; 1/6 BBL = 5.17 gal
- 750 ml ≈ 25.36 fl oz

## Calculation Verification (2026-02)

All conversions verified:
- 1 US BBL = 31 gal = 3,968 fl oz ✓
- 2 × 1/2 BBL = 1 BBL ✓; 6 × sixtel = 1 BBL ✓
- 750 ml = 25.36 fl oz (÷ 29.5735) ✓
- Theoretical = gross BBL × oz/format; Realistic = effective BBL (× yield %) × oz/format ✓
- Revenue: case equiv = (units × ozPerUnit) / 288 × casePrice; sixtel = kegPrice/3 ✓

Materials: rounded up with `Math.ceil` (can't order fractional cans/lids/flats).

## Edge Cases

- No split allocation: materials show "if all 24-pack"; revenue shows single-format "if all" estimates
- 750 ml bottles: materials show bottles + caps; revenue not included (no bottle price field)
- Sixtel revenue: uses kegPrice × (1/6)/(1/2) ≈ kegPrice/3 (volume-proportional)
