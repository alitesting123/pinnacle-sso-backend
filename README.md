# Proposal Portal API with SSO

A secure FastAPI application for B2B event planning proposal management with Single Sign-On (SSO) integration.

## Quick Start

### 1. Setup Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure your database (SQLite for local dev is recommended)
# DATABASE_URL=sqlite:///./proposal_portal.db
```

**Database Issues?** If you get a "Tenant or user not found" error, see [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed troubleshooting.

### 2. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Start Development Server

```bash
# Start development server
make dev

# Or manually:
uvicorn app.main:app --reload --port 8080
```

Visit http://localhost:8080/docs for API documentation.

## Test the API

```bash
# Health check
curl http://localhost:8080/health

# Get user info
curl http://localhost:8080/api/v1/users/me

# Get proposals
curl http://localhost:8080/api/v1/proposals
```

## Configuration

1. Copy `.env.example` to `.env`
2. Edit `.env` to configure:
   - Database connection (SQLite for dev, PostgreSQL for production)
   - AWS Cognito credentials (for SSO)
   - Frontend URL and CORS settings
   - Other application settings

For detailed database setup instructions, see [DATABASE_SETUP.md](DATABASE_SETUP.md).

## Troubleshooting

### "Tenant or user not found" Error
This is a database connection error. See [DATABASE_SETUP.md](DATABASE_SETUP.md) for solutions.

### Application Won't Start
1. Check if your `.env` file exists
2. Verify DATABASE_URL is configured correctly
3. For local development, use SQLite: `DATABASE_URL=sqlite:///./proposal_portal.db`

## Documentation

- [Database Setup & Troubleshooting](DATABASE_SETUP.md) - Complete guide for database configuration
- API Documentation: http://localhost:8080/docs (when running locally)
