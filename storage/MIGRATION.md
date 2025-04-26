# Migrating from SQLite to PostgreSQL

This guide provides step-by-step instructions for migrating your SAMODES application from SQLite to PostgreSQL.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL client tools (optional, for direct database access)

## Migration Steps

### 1. Backup your existing SQLite database

Before making any changes, create a backup of your SQLite database:

```bash
# From the root of the project
cp storage/db.sqlite3 storage/db.sqlite3.backup
```

### 2. Dump data from SQLite

We'll use our migration script to dump the data from SQLite:

```bash
# Navigate to the storage directory
cd storage

# Make the migration script executable
chmod +x migrate_to_postgres.py

# Dump data from SQLite
python migrate_to_postgres.py --dump
```

This will create JSON fixtures in `storage/fixtures/` directory.

### 3. Start PostgreSQL and update environment variables

Add the following environment variables to your `.env` file:

```
DB_NAME=samodesdb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Start the PostgreSQL container:

```bash
docker-compose up -d db
```

Wait for the PostgreSQL service to be fully up and running (check with `docker-compose ps`).

### 4. Load data to PostgreSQL

Now you can load the data from the fixtures to PostgreSQL:

```bash
# Navigate to the storage directory if you're not already there
cd storage

# Load data to PostgreSQL
docker-compose exec storage-service python migrate_to_postgres.py --load
```

Alternatively, you can run the Django management commands manually:

```bash
# Apply migrations to create tables in PostgreSQL
docker-compose exec storage-service python manage.py migrate

# Load fixtures
docker-compose exec storage-service python manage.py loaddata fixtures/auth.json fixtures/templates.json
```

### 5. Restart the application

```bash
docker-compose down
docker-compose up -d
```

### 6. Verify the migration

Check that the application is working correctly with PostgreSQL. You can verify the database connection by:

```bash
# Connect to the storage service container
docker-compose exec storage-service bash

# Start a Django shell
python manage.py shell

# In the shell, run:
from django.db import connection
connection.ensure_connection()
print("Database connection successful!")
```

## Troubleshooting

### Connection Issues

If you're experiencing connection issues:

1. Check that the PostgreSQL service is running:
```bash
docker-compose ps db
```

2. Verify database credentials in `storage/storage/settings.py`

3. Check database logs:
```bash
docker-compose logs db
```

### Data Migration Issues

If fixtures aren't loading correctly:

1. Check the fixture files for formatting issues
2. Try loading fixtures one by one to identify problematic data
3. For specific model issues, you may need to adjust models or clean fixtures manually

## Rolling Back

If you need to roll back to SQLite:

1. Update the `DATABASES` setting in `storage/storage/settings.py` to use SQLite
2. Restore your backup:
```bash
cp storage/db.sqlite3.backup storage/db.sqlite3
```
3. Restart the application 