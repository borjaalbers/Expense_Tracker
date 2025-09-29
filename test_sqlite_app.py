#!/usr/bin/env python3
"""
Test script to verify that the SQLite-only application works correctly.
This script will test all the main functionality of your expense tracker.
"""

import requests
import json
from datetime import datetime, date


class ExpenseTrackerTester:
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = {
            "username": "testuser_sqlite",
            "password": "TestPassword123"
        }
        self.test_expenses = [
            {
                "amount": 25.50,
                "category": "Groceries",
                "date": "2024-01-15",
                "note": "Weekly grocery shopping"
            },
            {
                "amount": 1200.00,
                "category": "Rent",
                "date": "2024-01-01",
                "note": "Monthly rent payment"
            },
            {
                "amount": 45.75,
                "category": "Dining",
                "date": "2024-01-10",
                "note": "Dinner with friends"
            }
        ]
    
    def test_health(self):
        """Test health endpoint."""
        print("Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_signup(self):
        """Test user signup."""
        print("Testing user signup...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/signup",
                json=self.test_user,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                print("✅ User signup successful")
                return True
            else:
                print(f"❌ User signup failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ User signup error: {e}")
            return False
    
    def test_signin(self):
        """Test user signin."""
        print("Testing user signin...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/signin",
                json=self.test_user,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print("✅ User signin successful")
                return True
            else:
                print(f"❌ User signin failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ User signin error: {e}")
            return False
    
    def test_add_expenses(self):
        """Test adding expenses."""
        print("Testing expense creation...")
        success_count = 0
        
        for i, expense in enumerate(self.test_expenses):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/expenses",
                    json=expense,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 201:
                    print(f"✅ Expense {i+1} added successfully")
                    success_count += 1
                else:
                    print(f"❌ Expense {i+1} failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Expense {i+1} error: {e}")
        
        return success_count == len(self.test_expenses)
    
    def test_list_expenses(self):
        """Test listing expenses."""
        print("Testing expense listing...")
        try:
            response = self.session.get(f"{self.base_url}/api/expenses")
            if response.status_code == 200:
                expenses = response.json()
                print(f"✅ Retrieved {len(expenses)} expenses")
                return len(expenses) >= len(self.test_expenses)
            else:
                print(f"❌ Expense listing failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Expense listing error: {e}")
            return False
    
    def test_expense_filtering(self):
        """Test expense filtering."""
        print("Testing expense filtering...")
        try:
            # Test category filter
            response = self.session.get(f"{self.base_url}/api/expenses?category=Groceries")
            if response.status_code == 200:
                expenses = response.json()
                groceries_count = len([e for e in expenses if e.get("category") == "Groceries"])
                print(f"✅ Category filtering: {groceries_count} Groceries expenses")
            else:
                print(f"❌ Category filtering failed: {response.status_code}")
                return False
            
            # Test date range filter
            response = self.session.get(f"{self.base_url}/api/expenses?date_from=2024-01-01&date_to=2024-01-31")
            if response.status_code == 200:
                expenses = response.json()
                print(f"✅ Date filtering: {len(expenses)} expenses in January 2024")
            else:
                print(f"❌ Date filtering failed: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Expense filtering error: {e}")
            return False
    
    def test_update_expense(self):
        """Test updating an expense."""
        print("Testing expense update...")
        try:
            # First get an expense to update
            response = self.session.get(f"{self.base_url}/api/expenses")
            if response.status_code != 200:
                print("❌ Could not retrieve expenses for update test")
                return False
            
            expenses = response.json()
            if not expenses:
                print("❌ No expenses found for update test")
                return False
            
            expense_id = expenses[0]["id"]
            update_data = {
                "amount": 30.00,
                "note": "Updated expense"
            }
            
            response = self.session.put(
                f"{self.base_url}/api/expenses/{expense_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Expense update successful")
                return True
            else:
                print(f"❌ Expense update failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Expense update error: {e}")
            return False
    
    def test_summary(self):
        """Test summary endpoint."""
        print("Testing summary endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/summary")
            if response.status_code == 200:
                summary = response.json()
                print(f"✅ Summary retrieved: {summary}")
                return True
            else:
                print(f"❌ Summary failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Summary error: {e}")
            return False
    
    def test_monthly_totals(self):
        """Test monthly totals endpoint."""
        print("Testing monthly totals...")
        try:
            response = self.session.get(f"{self.base_url}/api/monthly")
            if response.status_code == 200:
                monthly = response.json()
                print(f"✅ Monthly totals retrieved: {monthly}")
                return True
            else:
                print(f"❌ Monthly totals failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Monthly totals error: {e}")
            return False
    
    def test_delete_expense(self):
        """Test deleting an expense."""
        print("Testing expense deletion...")
        try:
            # First get an expense to delete
            response = self.session.get(f"{self.base_url}/api/expenses")
            if response.status_code != 200:
                print("❌ Could not retrieve expenses for delete test")
                return False
            
            expenses = response.json()
            if not expenses:
                print("❌ No expenses found for delete test")
                return False
            
            expense_id = expenses[0]["id"]
            
            response = self.session.delete(f"{self.base_url}/api/expenses/{expense_id}")
            
            if response.status_code == 200:
                print("✅ Expense deletion successful")
                return True
            else:
                print(f"❌ Expense deletion failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Expense deletion error: {e}")
            return False
    
    def test_signout(self):
        """Test user signout."""
        print("Testing user signout...")
        try:
            response = self.session.post(f"{self.base_url}/api/signout")
            if response.status_code == 200:
                print("✅ User signout successful")
                return True
            else:
                print(f"❌ User signout failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ User signout error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("Starting SQLite Expense Tracker Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("User Signup", self.test_signup),
            ("User Signin", self.test_signin),
            ("Add Expenses", self.test_add_expenses),
            ("List Expenses", self.test_list_expenses),
            ("Filter Expenses", self.test_expense_filtering),
            ("Update Expense", self.test_update_expense),
            ("Summary", self.test_summary),
            ("Monthly Totals", self.test_monthly_totals),
            ("Delete Expense", self.test_delete_expense),
            ("User Signout", self.test_signout)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed += 1
            print()
        
        print("=" * 50)
        print(f"Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your SQLite-only expense tracker is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the application and try again.")
        
        return passed == total


def main():
    """Main test function."""
    print("SQLite Expense Tracker Test Suite")
    print("Make sure your application is running on http://localhost:5002")
    print("Starting tests automatically...")
    
    tester = ExpenseTrackerTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("Your expense tracker has been successfully migrated to SQLite-only mode.")
    else:
        print("\n❌ Some tests failed. Please check the application logs and try again.")


if __name__ == "__main__":
    main()
