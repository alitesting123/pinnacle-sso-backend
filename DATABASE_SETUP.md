# Database Setup Guide

## Quick Fix for "Tenant or user not found" Error

If you're seeing this error when starting the application:
```
psycopg2.OperationalError: FATAL:  Tenant or user not found
```

This means your database credentials are incorrect or your database instance no longer exists.

## Solution Options

### Option 1: Use SQLite (Recommended for Local Development)

The simplest solution for local development is to use SQLite instead of PostgreSQL.

1. **Create or edit your `.env` file** in the project root:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```

2. **Set the DATABASE_URL to use SQLite**:
   ```env
   DATABASE_URL=sqlite:///./proposal_portal.db
   DEBUG=True
   ENVIRONMENT=development
   ```

3. **Restart your application**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

SQLite is perfect for:
- Local development
- Testing
- Quick prototypes
- No additional setup required

### Option 2: Fix Your PostgreSQL Connection

If you need to use PostgreSQL (for production or specific features), follow these steps:

#### For Cloud PostgreSQL Providers (Neon, Supabase, etc.)

1. **Log into your database provider dashboard** (e.g., neon.tech, supabase.com)

2. **Get the correct connection string**:
   - Navigate to your database/project
   - Find the "Connection String" or "Connection Details"
   - Copy the connection string (it should look like this):
     ```
     postgresql://username:password@host.region.provider.com/dbname?sslmode=require
     ```

3. **Update your `.env` file**:
   ```env
   DATABASE_URL=postgresql://your-username:your-password@ep-xxx-xxx.region.aws.neon.tech/your-database?sslmode=require
   ```

4. **Common Issues**:
   - **Database deleted**: Create a new database in your provider's dashboard
   - **Wrong credentials**: Reset your password in the dashboard
   - **IP restrictions**: Add your IP to the allowlist
   - **Free tier expired**: Check if your free tier database was paused/deleted

#### For Local PostgreSQL

If you're running PostgreSQL locally:

1. **Make sure PostgreSQL is running**:
   ```bash
   # macOS (with Homebrew)
   brew services start postgresql@14

   # Or check if it's running
   pg_isready
   ```

2. **Create a database**:
   ```bash
   createdb proposal_portal
   ```

3. **Update your `.env` file**:
   ```env
   DATABASE_URL=postgresql://your-username:your-password@localhost:5432/proposal_portal
   ```

   Replace `your-username` and `your-password` with your PostgreSQL credentials.

4. **Test the connection**:
   ```bash
   psql -d proposal_portal
   ```

## Environment Variables Setup

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual values:
   ```env
   # Database (choose one option)
   DATABASE_URL=sqlite:///./proposal_portal.db
   # OR
   # DATABASE_URL=postgresql://user:pass@host:5432/dbname

   # Security
   SECRET_KEY=your-secret-key-here

   # AWS Cognito (for SSO)
   AWS_REGION=us-east-1
   COGNITO_USER_POOL_ID=your-pool-id
   COGNITO_CLIENT_ID=your-client-id
   COGNITO_CLIENT_SECRET=your-client-secret

   # Other settings
   ENVIRONMENT=development
   DEBUG=True
   ```

## Verifying Your Setup

1. **Start the application**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

2. **Check the logs** - you should see:
   ```
   ✅ Database connection successful
   ✅ Database tables created successfully
   ✅ Database initialized successfully
   ```

3. **Test the health endpoint**:
   ```bash
   curl http://localhost:8080/health
   ```

## Troubleshooting

### Error: "Tenant or user not found"
- **Cause**: Incorrect PostgreSQL credentials or deleted database
- **Solution**: Use SQLite or update your PostgreSQL credentials

### Error: "No module named 'psycopg2'"
- **Cause**: PostgreSQL driver not installed
- **Solution**: `pip install psycopg2-binary`

### Error: "could not connect to server"
- **Cause**: PostgreSQL server not running
- **Solution**: Start PostgreSQL or switch to SQLite

### Database file gets very large with SQLite
- **Cause**: Normal for local development
- **Solution**: This is fine for development. Use PostgreSQL for production.

## Production Deployment

For production, you should:

1. **Use PostgreSQL** (not SQLite) for better performance and reliability
2. **Use a managed database service** (AWS RDS, Neon, Supabase, etc.)
3. **Set proper environment variables**:
   ```env
   ENVIRONMENT=production
   DEBUG=False
   DATABASE_URL=postgresql://...with-ssl-mode-require
   ```
4. **Keep your `.env` file secure** - never commit it to git

## Need Help?

- Check the application logs for detailed error messages
- The improved error handling will guide you to the solution
- Refer to `.env.example` for configuration examples
- For cloud databases, check your provider's documentation
