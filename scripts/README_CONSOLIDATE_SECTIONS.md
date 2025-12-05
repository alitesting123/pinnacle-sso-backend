# Consolidate Duplicate Sections

This script merges multiple sections with the same name into ONE section, organizing equipment by category instead of separate sections.

## Problem

Currently, "General Session | Hudson Ballroom IV,V, VI" is split into **7 separate sections**:

```
❌ General Session | Hudson Ballroom IV,V, VI - Audio
❌ General Session | Hudson Ballroom IV,V, VI - Computer
❌ General Session | Hudson Ballroom IV,V, VI - Lighting
❌ General Session | Hudson Ballroom IV,V, VI - Networking
❌ General Session | Hudson Ballroom IV,V, VI - Projection
❌ General Session | Hudson Ballroom IV,V, VI - Staging
❌ General Session | Hudson Ballroom IV,V, VI - Video
```

## Solution

The script consolidates them into **ONE section** with equipment organized by category:

```
✅ General Session | Hudson Ballroom IV,V, VI - $13,452.50
    └── Line Items grouped by category:
        • Audio items
        • Computer items
        • Lighting items
        • Networking items
        • Projection items
        • Staging items
        • Video items
```

## Usage

### Dry Run (Preview Only):
```bash
python scripts/consolidate_sections.py
```

Shows what will be consolidated WITHOUT making changes.

### Execute (Apply Changes):
```bash
python scripts/consolidate_sections.py --execute
```

Consolidates duplicate sections after confirmation.

### Custom Job Number:
```bash
python scripts/consolidate_sections.py JOB123 --execute
```

### Custom Database:
```bash
python scripts/consolidate_sections.py --db-url "postgresql://user:pass@host:port/db" --execute
```

## What It Does

1. **Identifies** sections with duplicate names
2. **Displays** all duplicates found
3. **Keeps** the first section (lowest display_order)
4. **Moves** all line items from duplicate sections to the primary section
5. **Updates** the category field on each item to reflect equipment type
6. **Updates** the primary section total to sum of all items
7. **Deletes** the duplicate sections
8. **Verifies** no duplicates remain

## Example Output

```
========================================================
CONSOLIDATE DUPLICATE SECTIONS
========================================================

✅ Found proposal: 305342 - User Conference option 2

📊 FOUND 1 SECTION NAME(S) WITH DUPLICATES:
------------------------------------------------------------

  Section: General Session | Hudson Ballroom IV,V, VI
  Duplicates: 7 sections
  Types: Audio, Computer, Lighting, Networking, Projection, Staging, Video
  Combined Total: $13,452.50

========================================================
CONSOLIDATING: General Session | Hudson Ballroom IV,V, VI
========================================================

Found 7 sections to merge:
------------------------------------------------------------

  1. Section ID: abc123...
     Type: Audio
     Total: $2,894.25
     Items: 7
        - 16ch Digital Audio Mixer (Qty: 1, Cat: audio, $255.00)
        - 12" Powered Speaker (Qty: 2, Cat: audio, $246.50)
        ...

  2. Section ID: def456...
     Type: Computer
     Total: $229.50
     Items: 1
        - Laptop | Standard (Qty: 1, Cat: computer, $229.50)

  ... (continues for all 7 sections)

------------------------------------------------------------
CONSOLIDATED RESULT:
  Total Items: 28
  Total Value: $13,452.50

🔄 CONSOLIDATING...

  ✅ Keeping section: abc123... (Type: Audio)
  ✅ Moved 21 items to primary section
  ✅ Updated section total to $13,452.50
  ✅ Deleted 6 duplicate sections

  ✅ CONSOLIDATION COMPLETE!
```

## Expected Results

### Before:
- Sections: 14
- "General Session | Hudson Ballroom IV,V, VI": 7 separate sections

### After:
- Sections: 8
- "General Session | Hudson Ballroom IV,V, VI": 1 consolidated section
- Same total value: $13,452.50
- All items organized by category field

## Safety Features

- ✅ **Dry run by default** - previews without changes
- ✅ **Keeps oldest section** - preserves creation history
- ✅ **Preserves all items** - nothing deleted except duplicate section containers
- ✅ **Updates categories** - ensures items have proper category tags
- ✅ **Transaction-based** - rollback on error
- ✅ **Verification** - confirms consolidation success

## Verification

After running, verify with:
```bash
python scripts/client_report.py "305342"
```

You should see ONE "General Session | Hudson Ballroom IV,V, VI" section with all items properly categorized.

## Notes

- The script updates `section_type` to "Multiple" since the consolidated section contains multiple equipment types
- The `category` field on each line item is used to preserve the equipment type
- Display order is preserved for line items
- Original section totals are summed for the consolidated section
