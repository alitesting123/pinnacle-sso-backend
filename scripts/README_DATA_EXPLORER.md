# Database Data Explorer

This script queries and displays all actual data stored in your database, including client information, proposals, and related records.

## Usage

### Using your configured database (from .env):
```bash
python scripts/explore_database_data.py
```

### Using a custom database URL:
```bash
python scripts/explore_database_data.py "postgresql://user:pass@host:port/dbname"
```

## What It Shows

### 1. **Clients List**
- All unique clients with their contact information
- Number of proposals per client
- Company details

### 2. **Proposals Summary**
- All proposals with key information:
  - Job number
  - Client name and contact info
  - Event location and venue
  - Event dates
  - Status and total cost
  - Creation date

### 3. **Detailed Proposal View** (for each proposal)
- Complete proposal information
- All sections (Audio, Video, Lighting, etc.)
- Line items count and total
- Timeline events count
- Labor items and costs
- Client questions with answers
  - AI-generated answers flagged
  - Question status and priority

### 4. **User Data**
- Pre-approved users
- Active users/sessions

### 5. **Data Export**
Automatically exports all data to JSON files in `scripts/data_exports/`:
- `proposals.json`
- `proposal_sections.json`
- `proposal_line_items.json`
- `proposal_timeline.json`
- `proposal_labor.json`
- `proposal_questions.json`
- `pre_approved_users.json`
- `active_users.json`
- `proposal_temp_links.json`
- `proposal_sessions.json`

## Example Output

```
CLIENTS LIST
Total Unique Clients: 4

CLIENT #1
Name: University of Texas at Dallas
Company: UTD
Email: events@utd.edu
Number of Proposals: 1

PROPOSAL #1: JOB-2024-001
Client: University of Texas at Dallas
Company: UTD
Event: Great Debates Series
Venue: Student Union Ballroom
Dates: 2024-03-15 to 2024-03-15
Status: confirmed
Total Cost: $45,234.50
```

## Requirements

The script uses:
- SQLAlchemy for database queries
- Your app's configuration from `app/config.py`
- Database connection from `DATABASE_URL` environment variable

## Notes

- The script is read-only - it does not modify any data
- Long text fields are truncated for display (full data in JSON exports)
- UUIDs are shortened for readability (first 8 characters)
- All timestamps are displayed in ISO format
- JSON exports contain complete, untruncated data
