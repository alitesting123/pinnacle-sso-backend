# Add Missing Sections Script

This script adds the 9 missing sections and 59 line items to proposal 305342 ("User Conference option 2") to fix the $14,714.75 pricing discrepancy.

## Problem

Proposal 305342 had only **5 sections** with **11 line items** totaling **$8,521.25**, but the product_subtotal shows **$26,560.00** - a discrepancy of **$18,038.75**.

## Solution

This script adds the missing **9 sections** with **59 line items**:

| Section | Type | Items | Total |
|---------|------|-------|-------|
| General Session \| Hudson Ballroom IV,V,VI | Networking | 1 | $0.00 |
| General Session \| Hudson Ballroom IV,V,VI | Staging | 2 | $4,400.00 |
| General Session \| Hudson Ballroom IV,V,VI | Video | 2 | $1,287.75 |
| Breakout \| Holland | Breakout Room | 7 | $2,078.25 |
| Breakout \| Liberty | Breakout Room | 6 | $1,377.00 |
| Breakout \| Palisades | Breakout Room | 7 | $1,836.00 |
| Breakout \| Hudson I, II | Breakout Room | 7 | $1,848.75 |
| Exhibitor Booths \| Manhattan & Prefunction | Exhibitor Space | 4 | $1,130.50 |
| Copy-Office \| Boardroom | Video | 1 | $756.50 |

**Total:** 59 items, $15,414.75

## Usage

### Dry Run (Preview Only):
```bash
python scripts/add_missing_sections.py
```

This will show you exactly what will be added WITHOUT making any changes.

### Execute (Apply Changes):
```bash
python scripts/add_missing_sections.py --execute
```

This will add the sections and line items to the database after confirmation.

### Custom Job Number:
```bash
python scripts/add_missing_sections.py JOB123 --execute
```

### Custom Database:
```bash
python scripts/add_missing_sections.py --db-url "postgresql://user:pass@host:port/db" --execute
```

## What It Does

1. **Verifies** the proposal exists
2. **Displays** a summary of sections and items to be added
3. **Generates** proper UUIDs for all new records
4. **Sets** appropriate timestamps
5. **Inserts** sections into `proposal_sections` table
6. **Inserts** line items into `proposal_line_items` table
7. **Verifies** the changes were applied correctly

## Safety Features

- **Dry run by default** - must explicitly use `--execute`
- **Confirmation prompt** before making changes
- **Transaction-based** - all changes rollback if error occurs
- **Verification** after completion

## Expected Results

### Before:
- Sections: 5
- Line Items: 11
- Section Total: $8,521.25

### After:
- Sections: 14 (5 + 9)
- Line Items: 70 (11 + 59)
- Section Total: $26,560.00 ✓ (matches product_subtotal!)

## Example Output

```
========================================================
ADD MISSING SECTIONS AND LINE ITEMS
========================================================

✅ Found proposal: 305342 - User Conference option 2
   Proposal ID: d60d0702-7995-4234-90af-5a356636b41f

🔍 DRY RUN MODE - No changes will be made to the database

📊 SUMMARY OF CHANGES:
   Sections to add: 9
   Line items to add: 59
   Total value: $15,414.75

========================================================
SECTIONS TO BE ADDED:
========================================================

1. General Session | Hudson Ballroom IV,V, VI (Networking)
   Section Total: $0.00
   Items: 1
      1. MIS | Internet Access (5 Mbps Aggregate)
         Qty: 250, Price: $0.00, Discount: $0.00, Subtotal: $0.00

2. General Session | Hudson Ballroom IV,V, VI (Staging)
   Section Total: $4,400.00
   Items: 2
      1. Drape Panel, 16' x 10' Slate
         Qty: 6, Price: $100.00, Discount: $0.00, Subtotal: $600.00
      2. Scenic Design
         Qty: 1, Price: $3,800.00, Discount: $0.00, Subtotal: $3,800.00

... (continues for all sections)
```

## Notes

- The script uses the exact data provided in the missing sections JSON
- All UUIDs are auto-generated
- Timestamps are set to current time
- The script does NOT modify the proposal totals (they should already be correct)
- Run the client_report.py script after to verify the changes

## Verification

After running the script, verify with:
```bash
python scripts/client_report.py "305342"
```

You should see all 14 sections with 70 line items totaling $26,560.00.
