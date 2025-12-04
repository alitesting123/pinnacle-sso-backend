# Database Schema Documentation

This document provides a comprehensive overview of the Pinnacle SSO Backend database schema.

## Overview

The database consists of **10 tables** with **146 total columns** and **14 relationships**. The schema is designed for PostgreSQL but can fall back to SQLite for local development.

## Table Categories

### User Management Tables (2 tables)

#### 1. `pre_approved_users`
**Model Class:** `PreApprovedUser`
**Description:** Read-only table managed by admin interface

| Column | Type | Nullable | Key | Description |
|--------|------|----------|-----|-------------|
| id | VARCHAR | No | PK | Primary identifier |
| email | VARCHAR | No | | User email address (unique, indexed) |
| full_name | VARCHAR | Yes | | User's full name |
| company | VARCHAR | Yes | | Company name |
| department | VARCHAR | Yes | | Department name |
| roles | JSON | Yes | | User roles array (e.g., ["user", "admin", "manager"]) |
| is_active | BOOLEAN | Yes | | Account active status (default: true) |
| created_at | DATETIME | Yes | | Account creation timestamp |
| cognito_user_id | VARCHAR | Yes | | Cognito user ID (unique) |
| last_login | DATETIME | Yes | | Last login timestamp |

#### 2. `active_users`
**Model Class:** `User`
**Description:** Active user sessions created by the app

| Column | Type | Nullable | Key | Description |
|--------|------|----------|-----|-------------|
| user_id | VARCHAR | No | PK | Primary identifier (Cognito sub) |
| email | VARCHAR | No | | User email address (unique, indexed) |
| full_name | VARCHAR | Yes | | User's full name |
| company | VARCHAR | Yes | | Company name |
| department | VARCHAR | Yes | | Department name |
| roles | JSON | Yes | | User roles array |
| is_active | BOOLEAN | Yes | | Account active status (default: true) |
| last_login | DATETIME | Yes | | Last login timestamp (auto-updated) |
| created_at | DATETIME | Yes | | Account creation timestamp (auto-set) |
| pre_approved_id | VARCHAR | Yes | | Links to pre_approved_users.id |

---

### Proposal Management Tables (8 tables)

#### 3. `proposals`
**Model Class:** `Proposal`
**Description:** Main proposal/quote table (parent table)

**Key Columns:**
- `id` (UUID, PK) - Primary identifier
- `job_number` (VARCHAR(50), unique, indexed) - Unique job identifier
- **Client Information:** client_name, client_email, client_company, client_contact, client_phone
- **Event Details:** event_location, venue_name, start_date, end_date
- **Proposal Metadata:** prepared_by, salesperson, status, version
- **Pricing:** product_subtotal, product_discount, product_total, labor_total, service_charge, tax_amount, total_cost
- **Terms:** terms_accepted, terms_accepted_at, terms_accepted_by
- **Timestamps:** created_at, updated_at, last_modified_by

**Relationships:**
- One-to-Many with: `proposal_sections`, `proposal_line_items`, `proposal_timeline`, `proposal_labor`, `proposal_questions`

#### 4. `proposal_sections`
**Model Class:** `ProposalSection`
**Description:** Proposal sections (Audio, Video, Lighting, etc.)

**Key Columns:**
- `id` (UUID, PK)
- `proposal_id` (UUID, FK → proposals.id)
- `section_name` (VARCHAR(100)) - Section name
- `section_type` (VARCHAR(50)) - Type of section
- `display_order` (INTEGER) - Display order
- `is_expanded` (BOOLEAN) - UI state
- `section_total` (NUMERIC(10, 2)) - Section total cost

**Relationships:**
- Many-to-One with: `proposals`
- One-to-Many with: `proposal_line_items`

#### 5. `proposal_line_items`
**Model Class:** `ProposalLineItem`
**Description:** Individual line items (equipment, services)

**Key Columns:**
- `id` (UUID, PK)
- `section_id` (UUID, FK → proposal_sections.id)
- `proposal_id` (UUID, FK → proposals.id)
- `description` (TEXT) - Item description
- `quantity` (INTEGER) - Quantity
- `unit_price` (NUMERIC(10, 2)) - Price per unit
- `discount` (NUMERIC(10, 2)) - Discount amount
- `subtotal` (NUMERIC(10, 2)) - Line total
- `category`, `item_type` - Classification fields

**Relationships:**
- Many-to-One with: `proposal_sections`, `proposals`
- One-to-Many with: `proposal_questions`

#### 6. `proposal_timeline`
**Model Class:** `ProposalTimeline`
**Description:** Event timeline and schedule

**Key Columns:**
- `id` (UUID, PK)
- `proposal_id` (UUID, FK → proposals.id)
- `event_date` (DATE) - Event date
- `start_time`, `end_time` (TIME) - Time range
- `title` (VARCHAR(255)) - Timeline entry title
- `location` (VARCHAR(255)) - Event location
- `setup_tasks` (ARRAY) - PostgreSQL array of setup tasks
- `equipment_needed` (ARRAY) - PostgreSQL array of equipment
- `cost` (NUMERIC(10, 2)) - Associated cost

#### 7. `proposal_labor`
**Model Class:** `ProposalLabor`
**Description:** Labor schedule and costs

**Key Columns:**
- `id` (UUID, PK)
- `proposal_id` (UUID, FK → proposals.id)
- `task_name` (VARCHAR(255)) - Labor task name
- `labor_date` (DATE) - Labor date
- `start_time`, `end_time` (TIME) - Work hours
- `regular_hours`, `overtime_hours`, `double_time_hours` (NUMERIC(5, 2)) - Hour breakdown
- `hourly_rate` (NUMERIC(10, 2)) - Rate per hour
- `subtotal` (NUMERIC(10, 2)) - Total labor cost

#### 8. `proposal_questions`
**Model Class:** `ProposalQuestion`
**Description:** Client questions about proposal items

**Key Columns:**
- `id` (UUID, PK)
- `proposal_id` (UUID, FK → proposals.id)
- `line_item_id` (UUID, FK → proposal_line_items.id, nullable)
- `question_text` (TEXT) - The question
- `status` (VARCHAR(50)) - Status: pending, answered, resolved (default: 'pending')
- `priority` (VARCHAR(20)) - Priority: normal, high, urgent (default: 'normal')
- `asked_by_name`, `asked_by_email` - Questioner info
- `asked_at` (DATETIME) - Question timestamp
- `answer_text` (TEXT) - The answer
- `answered_by`, `answered_at` - Answer metadata
- `ai_generated` (BOOLEAN) - Flag for AI-generated answers (default: false)
- `requires_follow_up` (BOOLEAN) - Follow-up flag

**Relationships:**
- Many-to-One with: `proposals`, `proposal_line_items`

#### 9. `proposal_temp_links`
**Model Class:** `SecureProposalLink`
**Description:** Temporary JWT access links for clients

**Key Columns:**
- `token` (VARCHAR(255), PK) - JWT token
- `proposal_id` (UUID, FK → proposals.id)
- `user_email` (VARCHAR(255), indexed) - Client email
- `user_name`, `company` - Client info
- `permissions` (JSONB) - PostgreSQL JSONB permissions object (default: {"permissions": ["view"]})
- `expires_at` (DATETIME) - Token expiration
- `session_duration_minutes` (INTEGER) - Session duration (default: 20)
- `is_active` (BOOLEAN, indexed) - Link active status
- `access_count` (INTEGER) - Number of times accessed
- `created_at`, `last_accessed` - Timestamps
- `revoked_at`, `revoked_by` - Revocation info

#### 10. `proposal_sessions`
**Model Class:** `ProposalSession`
**Description:** Active client viewing sessions

**Key Columns:**
- `session_id` (VARCHAR(255), PK) - Session identifier
- `proposal_id` (UUID, FK → proposals.id)
- `temp_token` (VARCHAR(255), FK → proposal_temp_links.token)
- `user_email`, `user_name`, `company` - User info
- `created_at`, `expires_at`, `last_accessed` - Timestamps
- `is_active` (BOOLEAN, indexed) - Session active status
- `extension_count` (INTEGER) - Number of extensions (default: 0)

---

## Database Relationship Diagram

```
USER TABLES:
  • pre_approved_users
  • active_users

PROPOSAL TABLES:
  • proposals (parent table)
    ├── proposal_sections
    │   └── proposal_line_items
    │       └── proposal_questions
    ├── proposal_timeline
    ├── proposal_labor
    ├── proposal_questions (can also link to proposals directly)
    ├── proposal_temp_links
    └── proposal_sessions
```

## Key Features

### PostgreSQL-Specific Features
- **UUID** columns for primary keys in proposal tables
- **JSONB** for flexible permissions storage
- **ARRAY** types for lists (setup_tasks, equipment_needed)
- **Automatic timestamps** with triggers (created_at, updated_at)

### Indexing Strategy
- All foreign keys are indexed
- Email fields are indexed for quick lookups
- Status fields are indexed for filtering
- Date fields (start_date, end_date) are indexed for range queries
- Unique indexes on: email, job_number, cognito_user_id, token

### Cascade Behavior
All relationships use `CASCADE DELETE` to maintain referential integrity:
- Deleting a proposal deletes all related sections, items, timeline, labor, questions, links, and sessions
- Deleting a section deletes all related line items
- Deleting a line item deletes all related questions

---

## Schema Exploration Scripts

### 1. `explore_database_schema.py`
Queries a live database to show all tables, columns, indexes, and row counts.

**Usage:**
```bash
python scripts/explore_database_schema.py

# Or with custom database URL:
python scripts/explore_database_schema.py "postgresql://user:pass@host:port/dbname"
```

**Output:**
- Console display of all tables and columns
- Exports to `scripts/database_schema.json`

### 2. `explore_schema_from_models.py`
Reads the SQLAlchemy ORM models to display schema without needing a populated database.

**Usage:**
```bash
python scripts/explore_schema_from_models.py
```

**Output:**
- Console display of all models with columns and relationships
- Exports to `scripts/database_schema_from_models.json`
- Works even when database is empty or not initialized

---

## Statistics

- **Total Tables:** 10
- **Total Columns:** 146
- **Total Relationships:** 14
- **Primary Keys:** 10
- **Foreign Keys:** 12
- **Indexed Columns:** ~20+

## Database Configuration

The application supports both PostgreSQL (production) and SQLite (development).

**Environment Variable:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/pinnacle_sso
```

**Configuration File:** `app/config.py`

**Models:**
- User models: `app/models/users.py`
- Proposal models: `app/models/proposals.py`

## Initialization Scripts

Located in `scripts/`:

| Script | Purpose |
|--------|---------|
| `create_proposal_schema.py` | Creates complete PostgreSQL schema with triggers |
| `create_tables.py` | Creates user tables |
| `create_proposal_tables.py` | Creates proposal tables |
| `test_connection.py` | Tests database connection |
| `seed_*.py` | Various data seeding scripts |

---

## Migration History

### 2024-11-17: Add AI-Generated Field
- Added `ai_generated` BOOLEAN field to `proposal_questions`
- Added index: `idx_proposal_questions_ai_generated`
- Migration file: `migrations/add_ai_generated_field.sql`

---

*Generated: 2025-12-04*
*Database Version: PostgreSQL (Production) / SQLite (Development)*
