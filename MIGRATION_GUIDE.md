# Migration Guide: JSON to SQLite

This guide will help you migrate your expense tracker from JSON file storage to SQLite database storage.

## What Changed

Your application has been updated to use SQLite database exclusively. The following changes were made:

1. **app.py**: Removed JSON file dependency, now uses SQLite only
2. **Database tables**: Automatically created on startup
3. **Migration script**: Created to move existing JSON data to database
4. **Test script**: Created to verify everything works correctly

## Migration Steps

### Step 1: Backup Your Data (Important!)

Before starting the migration, make sure you have backups of your JSON files:
- `users.json`
- `expenses.json`

### Step 2: Run the Migration Script

```bash
python migrate_to_sqlite.py
```

This script will:
- Create backup copies of your JSON files
- Migrate all users from `users.json` to the database
- Migrate all expenses from `expenses.json` to the database
- Verify the migration was successful

### Step 3: Test Your Application

1. Start your application:
   ```bash
   python app.py
   ```

2. Run the test script to verify everything works:
   ```bash
   python test_sqlite_app.py
   ```

### Step 4: Clean Up (Optional)

Once you've verified everything works correctly, you can safely delete:
- `users.json` (after migration)
- `expenses.json` (after migration)
- Backup files (`.backup_*`)

## Benefits of SQLite

- **Better Performance**: Database queries are faster than JSON file operations
- **Data Integrity**: ACID transactions ensure data consistency
- **Concurrent Access**: Multiple users can access the application simultaneously
- **Scalability**: Better handling of large amounts of data
- **Standard SQL**: Use familiar SQL queries for data analysis

## Database Schema

Your SQLite database will have two main tables:

### Users Table
- `id`: Primary key (auto-increment)
- `username`: Unique username
- `password_hash`: Hashed password

### Expenses Table
- `id`: Primary key (auto-increment)
- `user_id`: Foreign key to users table
- `amount`: Expense amount
- `category`: Expense category
- `date`: Expense date
- `note`: Additional notes

## Troubleshooting

### If Migration Fails
1. Check that your JSON files are valid JSON
2. Ensure all required fields are present
3. Check the error messages in the migration script output

### If Tests Fail
1. Make sure your application is running on `http://localhost:5001`
2. Check the application logs for errors
3. Verify the database file was created (`expense_tracker.db`)

### If You Need to Rollback
1. Stop the application
2. Restore your JSON files from backup
3. Revert the changes to `app.py` (change back to JSON storage)
4. Restart the application

## File Structure After Migration

```
expense_tracker/
├── app.py                    # Updated to use SQLite only
├── db.py                     # Database configuration
├── models.py                 # SQLAlchemy models
├── storage_db.py             # Database storage functions
├── migrate_to_sqlite.py      # Migration script
├── test_sqlite_app.py        # Test script
├── expense_tracker.db        # SQLite database (created automatically)
├── users.json.backup_*       # Backup of original JSON files
├── expenses.json.backup_*    # Backup of original JSON files
└── ... (other files unchanged)
```

## Next Steps

After successful migration, you can:
1. Add database indexes for better performance
2. Implement database migrations for schema changes
3. Add database connection pooling
4. Implement caching for better performance
5. Add database monitoring and logging

## Support

If you encounter any issues during migration:
1. Check the migration script output for error messages
2. Verify your JSON files are valid
3. Ensure all dependencies are installed
4. Check that the database file has proper permissions
