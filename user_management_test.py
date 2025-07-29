#!/usr/bin/env python3
"""
User Management Functionality Test - Focused testing of new user management features
"""

import requests
import json
import sys

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing User Management at: {API_URL}")

def print_test_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()

def test_user_management_comprehensive():
    """Comprehensive test of all user management functionality"""
    
    print("=" * 80)
    print("COMPREHENSIVE USER MANAGEMENT FUNCTIONALITY TEST")
    print("=" * 80)
    
    # Step 1: Login with admin credentials
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_URL}/login", json=login_data)
        if response.status_code != 200:
            print_test_result("Admin Login", False, f"Status: {response.status_code}")
            return False
        
        data = response.json()
        auth_token = data.get("access_token")
        admin_user_data = data.get("user")
        
        # Verify section field in login response
        section = admin_user_data.get("section")
        if section == "IT Administration":
            print_test_result(
                "1. Login Response Includes Section Field", 
                True, 
                f"✓ Section: {section}"
            )
        else:
            print_test_result(
                "1. Login Response Includes Section Field", 
                False, 
                f"Expected 'IT Administration', got: {section}"
            )
            
    except Exception as e:
        print_test_result("Admin Login", False, f"Exception: {str(e)}")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 2: Test profile endpoint includes section
    try:
        response = requests.get(f"{API_URL}/profile", headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            section = profile_data.get("section")
            if section == "IT Administration":
                print_test_result(
                    "2. Profile Response Includes Section Field", 
                    True, 
                    f"✓ Section: {section}"
                )
            else:
                print_test_result(
                    "2. Profile Response Includes Section Field", 
                    False, 
                    f"Expected 'IT Administration', got: {section}"
                )
        else:
            print_test_result(
                "2. Profile Response Includes Section Field", 
                False, 
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("2. Profile Response Includes Section Field", False, f"Exception: {str(e)}")
    
    # Step 3: Test GET /api/users (admin only)
    try:
        response = requests.get(f"{API_URL}/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            admin_user = None
            for user in users:
                if user.get("employee_number") == "ADMIN001":
                    admin_user = user
                    break
            
            if admin_user and admin_user.get("section") == "IT Administration":
                print_test_result(
                    "3. List All Users (Admin Only)", 
                    True, 
                    f"✓ Retrieved {len(users)} users, admin section verified"
                )
            else:
                print_test_result(
                    "3. List All Users (Admin Only)", 
                    False, 
                    "Admin user section not found or incorrect"
                )
        else:
            print_test_result(
                "3. List All Users (Admin Only)", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("3. List All Users (Admin Only)", False, f"Exception: {str(e)}")
    
    # Step 4: Test POST /api/register with section field
    test_user_data = {
        "employee_number": "QC001",
        "password": "test123",
        "role": "user",
        "full_name": "John Doe",
        "email": "john.doe@company.com",
        "section": "Quality Control Department"
    }
    
    test_user_id = None
    try:
        response = requests.post(f"{API_URL}/register", json=test_user_data, headers=headers)
        if response.status_code == 200:
            print_test_result(
                "4. Create New User with Section Field", 
                True, 
                f"✓ User created: {test_user_data['full_name']} in {test_user_data['section']}"
            )
            
            # Get the user ID for later tests
            users_response = requests.get(f"{API_URL}/users", headers=headers)
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if user.get("employee_number") == "QC001":
                        test_user_id = user.get("id")
                        break
        else:
            print_test_result(
                "4. Create New User with Section Field", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("4. Create New User with Section Field", False, f"Exception: {str(e)}")
    
    # Step 5: Verify new user appears in users list with correct section
    try:
        response = requests.get(f"{API_URL}/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            new_user = None
            for user in users:
                if user.get("employee_number") == "QC001":
                    new_user = user
                    break
            
            if new_user and new_user.get("section") == "Quality Control Department":
                print_test_result(
                    "5. Verify New User in List with Section", 
                    True, 
                    f"✓ User found: {new_user.get('full_name')} - {new_user.get('section')}"
                )
            else:
                print_test_result(
                    "5. Verify New User in List with Section", 
                    False, 
                    "New user not found or section incorrect"
                )
        else:
            print_test_result(
                "5. Verify New User in List with Section", 
                False, 
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("5. Verify New User in List with Section", False, f"Exception: {str(e)}")
    
    # Step 6: Test user deletion
    if test_user_id:
        try:
            response = requests.delete(f"{API_URL}/users/{test_user_id}", headers=headers)
            if response.status_code == 200:
                print_test_result(
                    "6. Delete User Functionality", 
                    True, 
                    "✓ Test user deleted successfully"
                )
            else:
                print_test_result(
                    "6. Delete User Functionality", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            print_test_result("6. Delete User Functionality", False, f"Exception: {str(e)}")
    
    # Step 7: Test admin self-deletion prevention
    admin_id = admin_user_data.get("id")
    try:
        response = requests.delete(f"{API_URL}/users/{admin_id}", headers=headers)
        if response.status_code == 400:
            print_test_result(
                "7. Prevent Admin Self-Deletion", 
                True, 
                "✓ Correctly prevented admin from deleting own account"
            )
        else:
            print_test_result(
                "7. Prevent Admin Self-Deletion", 
                False, 
                f"Expected 400, got {response.status_code}"
            )
    except Exception as e:
        print_test_result("7. Prevent Admin Self-Deletion", False, f"Exception: {str(e)}")
    
    # Step 8: Test role-based access control
    try:
        # Try to access users endpoint without token
        response = requests.get(f"{API_URL}/users")
        if response.status_code == 403 or response.status_code == 401:
            print_test_result(
                "8. Role-Based Access Control", 
                True, 
                f"✓ Correctly blocked unauthorized access (Status: {response.status_code})"
            )
        else:
            print_test_result(
                "8. Role-Based Access Control", 
                False, 
                f"Expected 401/403, got {response.status_code}"
            )
    except Exception as e:
        print_test_result("8. Role-Based Access Control", False, f"Exception: {str(e)}")
    
    print("=" * 80)
    print("USER MANAGEMENT TEST COMPLETED")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_user_management_comprehensive()
    sys.exit(0 if success else 1)