# Add Missing Sections for Job #302946

This script adds missing sections, line items, timeline events, and labor data to proposal 302946.

## Problem

Job #302946 currently has:
- **Database:** 1 section, 14 line items, 3 timeline events, 11 labor items
- **Should have:** 18 sections, 714 line items, 18 timeline events, 54 labor items

This represents **~700 missing line items** and **17 missing sections**!

## Setup Instructions

### Step 1: Edit the Script

Open `scripts/add_missing_sections_302946.py` and replace the empty data arrays with your complete data:

1. **Find the section that says `# PASTE YOUR DATA HERE`** (around line 20)

2. **Paste your sections data into `MISSING_SECTIONS_DATA`:**
   ```python
   MISSING_SECTIONS_DATA = [
       {
           "section_name": "Royal Ballroom 1 - Set Day",
           "section_type": "Audio",
           "display_order": 1,
           "section_total": "2156.25",
           "is_expanded": True,
           "notes": "",
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
                   "notes": ""
               },
               # ... all your items
           ]
       },
       # ... all your sections (18 total with Royal Ballroom 1/2/3-4 and Palmetto 5/6/7)
   ]
   ```

3. **Paste your timeline data into `TIMELINE_DATA`:**
   ```python
   TIMELINE_DATA = [
       {
           "event_date": "2024-03-15",
           "start_time": "08:00:00",
           "end_time": "17:00:00",
           "title": "Setup Day - Royal Ballroom 1",
           "location": "Royal Ballroom 1",
           "cost": "0.00",
           "display_order": 1
       },
       # ... all 18 timeline events
   ]
   ```

4. **Paste your labor data into `LABOR_DATA`:**
   ```python
   LABOR_DATA = [
       {
           "task_name": "Audio Technician",
           "quantity": 2,
           "labor_date": "2024-03-15",
           "start_time": "08:00:00",
           "end_time": "17:00:00",
           "regular_hours": "8.00",
           "overtime_hours": "0.00",
           "double_time_hours": "0.00",
           "hourly_rate": "45.00",
           "subtotal": "720.00",
           "notes": "",
           "display_order": 1
       },
       # ... all 54 labor items
   ]
   ```

### Step 2: Preview First (Dry Run)

```bash
python scripts/add_missing_sections_302946.py
```

This shows you exactly what will be added **WITHOUT making any changes**.

You'll see:
- How many sections, items, timeline events, and labor items will be added
- Current database state vs. what will be added
- Preview of the first few items in each section

### Step 3: Apply Changes

Once you've verified the preview looks correct:

```bash
python scripts/add_missing_sections_302946.py --execute
```

This will:
- Show the summary
- Ask for confirmation
- Add all sections with line items
- Add all timeline events
- Add all labor items
- Verify the changes

### Step 4: Connect to Production Database

If you're running this locally, you need to connect to your production database:

```bash
python scripts/add_missing_sections_302946.py --execute --db-url "postgresql://user:password@host:port/database"
```

Replace with your actual database connection string.

## What It Does

1. **Verifies** the proposal exists in database
2. **Displays** current state vs. what will be added
3. **Shows** detailed preview of all data
4. **Generates** proper UUIDs for all new records
5. **Sets** appropriate timestamps
6. **Inserts** sections into `proposal_sections` table
7. **Inserts** line items into `proposal_line_items` table
8. **Inserts** timeline events into `proposal_timeline` table
9. **Inserts** labor items into `proposal_labor` table
10. **Verifies** the changes were applied correctly

## Safety Features

- ✅ **Dry run by default** - must explicitly use `--execute`
- ✅ **Confirmation prompt** before making changes
- ✅ **Transaction-based** - all changes rollback if error occurs
- ✅ **Verification** after completion
- ✅ **Detailed preview** showing exactly what will be added

## Expected Results

### Before:
- Sections: 1
- Line Items: 14
- Timeline Events: 3
- Labor Items: 11

### After:
- Sections: 19 (1 + 18)
- Line Items: 714+ (14 + ~700)
- Timeline Events: 21 (3 + 18)
- Labor Items: 65 (11 + 54)

## Verification

After running the script, verify with:

```bash
python scripts/client_report.py "302946" --db-url "your-production-db-url"
```

You should see all 18+ sections with all line items, timeline events, and labor items.

## Data Structure

The proposal should have sections for:
- **Royal Ballroom 1** - Set Day, Day 1, Day 2
- **Royal Ballroom 2** - Set Day, Day 1, Day 2
- **Royal Ballroom 3-4** - Set Day, Day 1, Day 2
- **Palmetto 5** - Set Day, Day 1, Day 2
- **Palmetto 6** - Set Day, Day 1, Day 2
- **Palmetto 7** - Set Day, Day 1, Day 2

Each with Audio/Video/Lighting/Computer/Networking/Staging/Projection equipment.

## Notes

- The script will NOT modify existing data, only add new records
- All UUIDs are auto-generated
- Timestamps are set to current time
- The script does NOT modify proposal-level fields
