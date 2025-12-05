# Import Proposal Data from JSON

This script imports missing sections, line items, timeline events, and labor data from a JSON file into the database for a specific proposal.

## Problem

Some proposals in the database are missing large portions of data. For example, Job #302946 currently has:
- Database: 1 section, 14 line items, 3 timeline events, 11 labor items
- Should have: 18 sections, 714 line items, 18 timeline events, 54 labor items

This represents **~700 missing line items** and **17 missing sections**!

## Solution

This script imports complete proposal data from a JSON file structure, checking for duplicates and preserving existing data.

## JSON File Format

The JSON file should have this structure:

```json
{
  "proposals": [
    {
      "proposal": {
        "job_number": "302946",
        "client_name": "Example Client",
        ...
      },
      "sections": [
        {
          "section_name": "Royal Ballroom 1 - Set Day",
          "section_type": "Audio",
          "display_order": 1,
          "section_total": "1234.56",
          "is_expanded": true,
          "notes": "Optional notes",
          "items": [
            {
              "item_number": "1",
              "description": "16ch Digital Audio Mixer",
              "quantity": 1,
              "duration": "1 Days",
              "unit_price": "255.00",
              "discount": "0.00",
              "subtotal": "255.00",
              "category": "audio",
              "item_type": "equipment",
              "notes": "Optional notes"
            }
          ]
        }
      ],
      "timeline": [
        {
          "event_date": "2024-03-15",
          "start_time": "08:00:00",
          "end_time": "17:00:00",
          "title": "Setup Day",
          "location": "Main Ballroom",
          "cost": "0.00",
          "display_order": 1
        }
      ],
      "labor": [
        {
          "task_name": "Audio Tech",
          "quantity": 2,
          "labor_date": "2024-03-15",
          "start_time": "08:00:00",
          "end_time": "17:00:00",
          "regular_hours": "8.00",
          "overtime_hours": "0.00",
          "double_time_hours": "0.00",
          "hourly_rate": "45.00",
          "subtotal": "720.00",
          "notes": "Optional notes",
          "display_order": 1
        }
      ]
    }
  ]
}
```

## Usage

### 1. Prepare Your JSON File

Save your proposal data to a JSON file (e.g., `proposal_302946_data.json`)

### 2. Dry Run (Preview Only - RECOMMENDED FIRST STEP):

```bash
python scripts/import_proposal_from_json.py proposal_302946_data.json
```

or specify job number:

```bash
python scripts/import_proposal_from_json.py proposal_302946_data.json 302946
```

This shows what will be imported **WITHOUT making any changes**.

### 3. Execute (Apply Changes):

```bash
python scripts/import_proposal_from_json.py proposal_302946_data.json 302946 --execute
```

This will import the data after showing a summary and asking for confirmation.

### 4. Custom Database:

```bash
python scripts/import_proposal_from_json.py proposal_302946_data.json 302946 --execute --db-url "postgresql://user:pass@host:port/db"
```

## What It Does

1. **Loads** the JSON file
2. **Finds** the proposal by job number in the JSON
3. **Verifies** the proposal exists in the database
4. **Compares** current database state with JSON data
5. **Shows** detailed preview of what will be imported
6. **Imports** (if --execute flag is used):
   - Sections (skips if already exists by name)
   - Line Items for each section (skips if description already exists in section)
   - Timeline Events (skips if title + date already exists)
   - Labor Items (skips if task_name + date already exists)
7. **Verifies** the import was successful

## Safety Features

- ✅ **Dry run by default** - must explicitly use `--execute`
- ✅ **Confirmation prompt** before making changes
- ✅ **Duplicate detection** - won't add items that already exist
- ✅ **Transaction-based** - all changes rollback if error occurs
- ✅ **Verification** after completion
- ✅ **Detailed preview** showing exactly what will be added

## Example Output

```
============================================================
IMPORT PROPOSAL DATA FROM JSON
============================================================

✅ Found proposal: 302946 - Client Name
   Proposal ID: abc-123-def-456

🔍 DRY RUN MODE - No changes will be made to the database

📊 DATA TO IMPORT:
   Sections: 18
   Line Items: 714
   Timeline Events: 18
   Labor Items: 54

📊 CURRENT DATABASE STATE:
   Sections: 1
   Line Items: 14
   Timeline Events: 3
   Labor Items: 11

📊 TO BE ADDED:
   Sections: 17
   Line Items: 700
   Timeline Events: 15
   Labor Items: 43

============================================================
SECTIONS TO BE IMPORTED:
============================================================

  1. Royal Ballroom 1 - Set Day
      Type: Audio
      Total: $2,156.25
      Items: 28

  2. Royal Ballroom 1 - Day 1
      Type: Audio
      Total: $2,156.25
      Items: 28

  ... (continues for all 18 sections)

============================================================
⚠️  DRY RUN COMPLETE - Run with --execute to apply changes
============================================================
```

## After Import

After successfully importing, verify the data with:

```bash
python scripts/client_report.py "302946"
```

You should see all sections, line items, timeline events, and labor items.

## Duplicate Handling

The script intelligently handles duplicates:

- **Sections**: Checks by `section_name` - if a section with the same name exists, it reuses that section and adds items to it
- **Line Items**: Checks by `description` within each section - skips if already exists
- **Timeline**: Checks by `title` + `event_date` - skips if combination exists
- **Labor**: Checks by `task_name` + `labor_date` - skips if combination exists

This means you can safely re-run the import if it fails partway through, and it will only add missing items.

## Notes

- The script generates UUIDs automatically for all new records
- Timestamps are set to current time
- The script does NOT modify existing proposal-level fields (totals, etc.)
- All imports happen in a single database transaction for safety

## Expected Results for Job #302946

### Before:
- Sections: 1
- Line Items: 14
- Timeline Events: 3
- Labor Items: 11

### After:
- Sections: 18
- Line Items: 714
- Timeline Events: 18
- Labor Items: 54

### Total Value:
Should match the proposal's product_subtotal in the database.
