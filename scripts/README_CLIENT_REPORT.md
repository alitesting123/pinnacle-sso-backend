# Client Report Generator

Generate comprehensive reports for specific clients showing all proposals, line items, labor, timeline, and questions.

## Usage

### Search by Client Name:
```bash
python scripts/client_report.py "User Conference"
```

### Search by Job Number:
```bash
python scripts/client_report.py "305342"
```

### Search by Email:
```bash
python scripts/client_report.py "shanondoah.nicholson@company.com"
```

### Search by Company:
```bash
python scripts/client_report.py "GlobalTech Solutions"
```

### With Custom Database URL:
```bash
python scripts/client_report.py "User Conference" "postgresql://user:pass@host:port/db"
```

## What's Included

### 1. **Client Information**
- Client name
- Company name
- Contact person
- Email address
- Phone number
- Total number of proposals

### 2. **Proposal Details** (for each proposal)
- Job number
- Status and version
- Event location and venue
- Event dates
- Prepared by / Salesperson
- Creation and update timestamps
- Notes

### 3. **Complete Pricing Breakdown**
- Product subtotal (before discount)
- Product discount amount
- Product total (after discount)
- Labor total
- Service charges
- Tax amount
- **Final total cost**

### 4. **Sections & Line Items**
For each section (Audio, Video, Lighting, etc.):
- Section name and type
- Section total
- All line items with:
  - Description
  - Quantity
  - Unit price
  - Discount
  - Subtotal
  - Notes

**Orphaned Items Detection:**
- Identifies line items not assigned to any section
- Shows warning with count
- Lists all orphaned items with details

### 5. **Timeline Events**
- Event title
- Date and time
- Location
- Cost
- Setup tasks
- Equipment needed
- Notes

### 6. **Labor Schedule**
- Task name
- Date and time
- Regular hours
- Overtime hours
- Double-time hours
- Hourly rate
- Subtotal
- **Total hours and cost summary**

### 7. **Client Questions**
- Question text
- Status (pending/answered)
- Priority level
- Asked by (name and email)
- Timestamp
- Answer (if provided)
- AI-generated flag
- Follow-up required flag

**Statistics:**
- Total questions
- Pending count
- Answered count
- AI-generated answers count

### 8. **JSON Export**
Automatically exports complete report to:
`scripts/client_reports/client_report_<search_term>.json`

## Example Output

```
========================================================
CLIENT REPORT GENERATOR
========================================================

Database: aws-1-us-east-2.pooler.supabase.com:6543/postgres

========================================================
🔍 SEARCHING FOR CLIENT: User Conference
========================================================

========================================================
👤 CLIENT INFORMATION
========================================================

  Client Name: User Conference option 2
  Company: N/A
  Contact Person: Shanandoah Nicholson
  Email: shanondoah.nicholson@company.com
  Phone: +1 416 816 0104

  Total Proposals: 1

========================================================
📋 PROPOSAL #1: 305342
========================================================

--------------------------------------------------------
📊 PROPOSAL DETAILS
--------------------------------------------------------

  Job Number: 305342
  Status: tentative
  Version: 1.0

  Event Location: Hyatt Regency Jersey City
  Venue: 2 Exchange Place, Jersey City New Jersey 07302
  Event Dates: 2025-09-30 to 2025-09-30

  Prepared By: Emily Feazel
  Salesperson: Emily Feazel (emily.feazel@pinnaclelive.com)

--------------------------------------------------------
💰 PRICING BREAKDOWN
--------------------------------------------------------

  Product Subtotal: $26,560.00
  Product Discount: -$3,324.00
  Product Total:    $23,236.00

  Labor Total:      $17,960.00
  Service Charge:   $11,434.80
  Tax Amount:       $2,296.95

  ──────────────────────────────────────────────────
  TOTAL COST:       $54,927.75
  ──────────────────────────────────────────────────

--------------------------------------------------------
📦 SECTIONS & LINE ITEMS (5 sections)
--------------------------------------------------------

  📁 Office | Boardroom
     Type: Video
     Section Total: $756.50
     Items: 1

     Item                                               Qty    Unit Price   Discount     Subtotal
     ----------------------------------------------------------------------------------------------------
     LED Monitor, 4K 65"                                1      $890.00      -$133.50     $756.50
     ----------------------------------------------------------------------------------------------------
     Section Items Total: $756.50
     Total Quantity: 1

  ... (continues for all sections)

--------------------------------------------------------
👷 LABOR SCHEDULE (9 items)
--------------------------------------------------------

  Total Labor Items: 9
  Total Hours: 85.5
  Total Labor Cost: $17,960.00

  Task                                     Date         Time            Hours           Rate         Subtotal
  --------------------------------------------------------------------------------------------------------------
  Setup - Office/Boardroom                 2025-09-30   08:00-10:00     R:2.0           $55.00       $110.00
  ... (continues for all labor items)

--------------------------------------------------------
❓ CLIENT QUESTIONS (4 questions)
--------------------------------------------------------

  Total Questions: 4
  Pending: 4
  Answered: 0
  AI-Generated Answers: 0

  ⏳ Question #1:
     Q: is there a smaller size?
     Status: pending | Priority: normal
     Asked by: Anonymous (N/A)
     Asked at: 2025-09-30 15:30:00

  ... (continues for all questions)

========================================================
💾 EXPORTING TO JSON
========================================================

✅ Client report exported to: scripts/client_reports/client_report_User_Conference.json
```

## Features

- **Flexible Search**: Search by name, email, job number, or company
- **Complete Details**: Shows every aspect of client proposals
- **Orphaned Items Detection**: Identifies line items not in sections
- **Pricing Verification**: Detailed breakdown to verify totals
- **JSON Export**: Machine-readable format for further analysis
- **Multi-Proposal Support**: Shows all proposals for a client

## Output Files

All reports are saved to: `scripts/client_reports/`

Files are named: `client_report_<search_term>.json`

## Requirements

- SQLAlchemy
- Database connection configured in `.env`
- PostgreSQL or SQLite database
