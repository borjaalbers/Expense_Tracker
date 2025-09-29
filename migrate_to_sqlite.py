#!/usr/bin/env python3
"""
Migration script to move data from JSON files to SQLite database.
This script will help you migrate any existing data from users.json and expenses.json
to the SQLite database before switching to database-only mode.
"""

import json
import os
from datetime import datetime
from db import get_session
from models import User, Expense
from storage_db import find_user_by_username, find_user_by_id


def load_json_data(file_path):
    """Load data from JSON file."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist, skipping...")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading {file_path}: {e}")
        return []


def migrate_users():
    """Migrate users from JSON to database."""
    print("Migrating users...")
    users_data = load_json_data("users.json")
    
    if not users_data:
        print("No users to migrate.")
        return
    
    migrated_count = 0
    skipped_count = 0
    
    for user_data in users_data:
        username = user_data.get("username")
        if not username:
            print(f"Skipping user with missing username: {user_data}")
            skipped_count += 1
            continue
        
        # Check if user already exists
        existing_user = find_user_by_username(username)
        if existing_user:
            print(f"User {username} already exists, skipping...")
            skipped_count += 1
            continue
        
        # Create new user in database
        try:
            with get_session() as session:
                user = User(
                    username=username,
                    password_hash=user_data.get("password_hash", "")
                )
                session.add(user)
                session.flush()
                print(f"Migrated user: {username} (ID: {user.id})")
                migrated_count += 1
        except Exception as e:
            print(f"Error migrating user {username}: {e}")
            skipped_count += 1
    
    print(f"Users migration complete: {migrated_count} migrated, {skipped_count} skipped")


def migrate_expenses():
    """Migrate expenses from JSON to database."""
    print("Migrating expenses...")
    expenses_data = load_json_data("expenses.json")
    
    if not expenses_data:
        print("No expenses to migrate.")
        return
    
    migrated_count = 0
    skipped_count = 0
    
    for expense_data in expenses_data:
        user_id = expense_data.get("user_id")
        if not user_id:
            print(f"Skipping expense with missing user_id: {expense_data}")
            skipped_count += 1
            continue
        
        # Check if user exists
        user = find_user_by_id(user_id)
        if not user:
            print(f"User {user_id} not found, skipping expense {expense_data.get('id')}")
            skipped_count += 1
            continue
        
        # Create new expense in database
        try:
            with get_session() as session:
                # Parse date if provided
                date_value = None
                date_str = expense_data.get("date")
                if date_str:
                    try:
                        date_value = datetime.fromisoformat(date_str).date()
                    except ValueError:
                        print(f"Invalid date format for expense {expense_data.get('id')}: {date_str}")
                        date_value = None
                
                expense = Expense(
                    user_id=user_id,
                    amount=float(expense_data.get("amount", 0)),
                    category=expense_data.get("category", "Uncategorized"),
                    date=date_value,
                    note=expense_data.get("note", "")
                )
                session.add(expense)
                session.flush()
                print(f"Migrated expense: {expense.id} for user {user_id} (${expense.amount})")
                migrated_count += 1
        except Exception as e:
            print(f"Error migrating expense {expense_data.get('id')}: {e}")
            skipped_count += 1
    
    print(f"Expenses migration complete: {migrated_count} migrated, {skipped_count} skipped")


def backup_json_files():
    """Create backup copies of JSON files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    files_to_backup = ["users.json", "expenses.json"]
    
    for filename in files_to_backup:
        if os.path.exists(filename):
            backup_filename = f"{filename}.backup_{timestamp}"
            try:
                import shutil
                shutil.copy2(filename, backup_filename)
                print(f"Created backup: {backup_filename}")
            except Exception as e:
                print(f"Error creating backup for {filename}: {e}")


def verify_migration():
    """Verify that migration was successful."""
    print("\nVerifying migration...")
    
    # Check users
    from storage_db import get_all_users
    users = get_all_users()
    print(f"Total users in database: {len(users)}")
    
    # Check expenses
    from storage_db import get_all_expenses
    expenses = get_all_expenses()
    print(f"Total expenses in database: {len(expenses)}")
    
    # Show summary by user
    user_expense_counts = {}
    for expense in expenses:
        user_id = expense["user_id"]
        user_expense_counts[user_id] = user_expense_counts.get(user_id, 0) + 1
    
    print("\nExpenses per user:")
    for user_id, count in user_expense_counts.items():
        user = find_user_by_id(user_id)
        username = user["username"] if user else f"Unknown (ID: {user_id})"
        print(f"  {username}: {count} expenses")


def main():
    """Main migration function."""
    print("Starting migration from JSON files to SQLite database...")
    print("=" * 60)
    
    # Create backup of JSON files
    print("Creating backup of JSON files...")
    backup_json_files()
    
    # Migrate users first
    migrate_users()
    print()
    
    # Migrate expenses
    migrate_expenses()
    print()
    
    # Verify migration
    verify_migration()
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("\nNext steps:")
    print("1. Test your application to ensure everything works correctly")
    print("2. Once verified, you can safely delete the JSON files:")
    print("   - users.json")
    print("   - expenses.json")
    print("3. The backup files (.backup_*) can also be deleted after verification")


if __name__ == "__main__":
    main()
