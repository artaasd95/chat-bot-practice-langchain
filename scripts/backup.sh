#!/bin/bash

# Database backup script for production
# This script creates daily backups of the PostgreSQL database

set -e

# Configuration
DB_HOST="postgres"
DB_PORT="5432"
DB_NAME="chatbot_db_prod"
DB_USER="chatbot"
BACKUP_DIR="/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/chatbot_backup_${DATE}.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup at $(date)"

# Create database backup
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

# Compress the backup
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "Backup created: $BACKUP_FILE"

# Check backup file size
BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null || echo "0")
echo "Backup size: $BACKUP_SIZE bytes"

# Verify backup integrity
if [ "$BACKUP_SIZE" -gt 1000 ]; then
    echo "Backup appears to be valid (size > 1KB)"
else
    echo "WARNING: Backup file seems too small, please check!"
    exit 1
fi

# Clean up old backups (keep only last N days)
echo "Cleaning up backups older than $RETENTION_DAYS days"
find "$BACKUP_DIR" -name "chatbot_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# List remaining backups
echo "Current backups:"
ls -lh "$BACKUP_DIR"/chatbot_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "Backup completed successfully at $(date)"