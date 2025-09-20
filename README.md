# Proposal Portal API with SSO

A secure FastAPI application for B2B event planning proposal management with Single Sign-On (SSO) integration.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
make dev
```

Visit http://localhost:8000/docs for API documentation.

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get user info
curl http://localhost:8000/api/v1/users/me

# Get proposals
curl http://localhost:8000/api/v1/proposals
```

## Configuration

Edit `.env` file to configure SSO providers and other settings.
