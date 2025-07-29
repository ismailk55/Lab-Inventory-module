#!/usr/bin/env python3
"""
Laboratory Inventory Management System - Backend API Testing
Tests all backend endpoints systematically with real test data
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

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
print(f"Testing backend at: {API_URL}")

# Global variables for test data
auth_token = None
admin_user_data = None
test_item_id = None
test_request_id = None

def print_test_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()

def test_authentication():
    """Test authentication system with default admin credentials"""
    global auth_token, admin_user_data
    
    print("=" * 60)
    print("TESTING AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    # Test 1: Login with default admin credentials
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            admin_user_data = data.get("user")
            
            print_test_result(
                "Admin Login (ADMIN001/admin123)", 
                True, 
                f"Token received, User: {admin_user_data.get('full_name')} ({admin_user_data.get('role')})"
            )
        else:
            print_test_result(
                "Admin Login (ADMIN001/admin123)", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Admin Login (ADMIN001/admin123)", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: Access profile with JWT token
    if auth_token:
        headers = {"Authorization": f"Bearer {auth_token}"}
        try:
            response = requests.get(f"{API_URL}/profile", headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                print_test_result(
                    "Profile Access with JWT", 
                    True, 
                    f"Profile: {profile_data.get('full_name')} - {profile_data.get('employee_number')}"
                )
            else:
                print_test_result(
                    "Profile Access with JWT", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
        except Exception as e:
            print_test_result("Profile Access with JWT", False, f"Exception: {str(e)}")
            return False
    
    # Test 3: Invalid login credentials
    invalid_login = {
        "employee_number": "INVALID001",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{API_URL}/login", json=invalid_login)
        if response.status_code == 401:
            print_test_result("Invalid Login Rejection", True, "Correctly rejected invalid credentials")
        else:
            print_test_result(
                "Invalid Login Rejection", 
                False, 
                f"Expected 401, got {response.status_code}"
            )
    except Exception as e:
        print_test_result("Invalid Login Rejection", False, f"Exception: {str(e)}")
    
    return auth_token is not None

def test_inventory_management():
    """Test inventory CRUD operations"""
    global test_item_id
    
    print("=" * 60)
    print("TESTING INVENTORY MANAGEMENT")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Inventory Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Add new inventory item
    inventory_item = {
        "item_name": "Digital pH Meter Model 3510",
        "category": "Analytical Instruments",
        "sub_category": "pH Meters",
        "location": "Lab Storage Room A - Shelf 3",
        "manufacturer": "Hanna Instruments",
        "supplier": "Scientific Equipment Corp",
        "model": "HI-3510",
        "uom": "pieces",
        "catalogue_no": "HI3510-02",
        "quantity": 15,
        "target_stock_level": 20,
        "reorder_level": 5,
        "validity": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "use_case": "pH measurement for water quality testing and chemical analysis"
    }
    
    try:
        response = requests.post(f"{API_URL}/inventory", json=inventory_item, headers=headers)
        if response.status_code == 200:
            item_data = response.json()
            test_item_id = item_data.get("id")
            print_test_result(
                "Add Inventory Item", 
                True, 
                f"Item added: {item_data.get('item_name')} (ID: {test_item_id})"
            )
        else:
            print_test_result(
                "Add Inventory Item", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Add Inventory Item", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: List all inventory items
    try:
        response = requests.get(f"{API_URL}/inventory", headers=headers)
        if response.status_code == 200:
            items = response.json()
            print_test_result(
                "List Inventory Items", 
                True, 
                f"Retrieved {len(items)} items from inventory"
            )
        else:
            print_test_result(
                "List Inventory Items", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("List Inventory Items", False, f"Exception: {str(e)}")
    
    # Test 3: Get specific inventory item
    if test_item_id:
        try:
            response = requests.get(f"{API_URL}/inventory/{test_item_id}", headers=headers)
            if response.status_code == 200:
                item = response.json()
                print_test_result(
                    "Get Specific Item", 
                    True, 
                    f"Retrieved: {item.get('item_name')}"
                )
            else:
                print_test_result(
                    "Get Specific Item", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            print_test_result("Get Specific Item", False, f"Exception: {str(e)}")
    
    # Test 4: Update inventory item
    if test_item_id:
        update_data = inventory_item.copy()
        update_data["quantity"] = 25
        update_data["location"] = "Lab Storage Room B - Shelf 1"
        
        try:
            response = requests.put(f"{API_URL}/inventory/{test_item_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                print_test_result(
                    "Update Inventory Item", 
                    True, 
                    "Item updated successfully (quantity: 15→25, location changed)"
                )
            else:
                print_test_result(
                    "Update Inventory Item", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            print_test_result("Update Inventory Item", False, f"Exception: {str(e)}")
    
    return test_item_id is not None

def test_withdrawal_requests():
    """Test withdrawal request system"""
    global test_request_id
    
    print("=" * 60)
    print("TESTING WITHDRAWAL REQUEST SYSTEM")
    print("=" * 60)
    
    if not auth_token or not test_item_id:
        print_test_result("Withdrawal Request Tests", False, "Missing auth token or test item")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Create withdrawal request
    withdrawal_request = {
        "item_id": test_item_id,
        "requested_quantity": 3,
        "purpose": "Quality control testing for batch QC-2025-001 - pH calibration and validation"
    }
    
    try:
        response = requests.post(f"{API_URL}/withdrawal-requests", json=withdrawal_request, headers=headers)
        if response.status_code == 200:
            request_data = response.json()
            test_request_id = request_data.get("id")
            print_test_result(
                "Create Withdrawal Request", 
                True, 
                f"Request created: {request_data.get('requested_quantity')} units of {request_data.get('item_name')}"
            )
        else:
            print_test_result(
                "Create Withdrawal Request", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Create Withdrawal Request", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: List withdrawal requests
    try:
        response = requests.get(f"{API_URL}/withdrawal-requests", headers=headers)
        if response.status_code == 200:
            requests_list = response.json()
            print_test_result(
                "List Withdrawal Requests", 
                True, 
                f"Retrieved {len(requests_list)} withdrawal requests"
            )
        else:
            print_test_result(
                "List Withdrawal Requests", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("List Withdrawal Requests", False, f"Exception: {str(e)}")
    
    # Test 3: Process withdrawal request (approve)
    if test_request_id:
        process_data = {
            "request_id": test_request_id,
            "action": "approve",
            "comments": "Approved for quality control testing. Ensure proper documentation."
        }
        
        try:
            response = requests.post(f"{API_URL}/withdrawal-requests/process", json=process_data, headers=headers)
            if response.status_code == 200:
                print_test_result(
                    "Approve Withdrawal Request", 
                    True, 
                    "Request approved successfully - inventory should be reduced"
                )
            else:
                print_test_result(
                    "Approve Withdrawal Request", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            print_test_result("Approve Withdrawal Request", False, f"Exception: {str(e)}")
    
    # Test 4: Create another request to test rejection
    rejection_request = {
        "item_id": test_item_id,
        "requested_quantity": 2,
        "purpose": "Additional testing for method validation"
    }
    
    try:
        response = requests.post(f"{API_URL}/withdrawal-requests", json=rejection_request, headers=headers)
        if response.status_code == 200:
            reject_request_data = response.json()
            reject_request_id = reject_request_data.get("id")
            
            # Now reject this request
            reject_process_data = {
                "request_id": reject_request_id,
                "action": "reject",
                "comments": "Request rejected - insufficient justification for additional testing"
            }
            
            reject_response = requests.post(f"{API_URL}/withdrawal-requests/process", json=reject_process_data, headers=headers)
            if reject_response.status_code == 200:
                print_test_result(
                    "Reject Withdrawal Request", 
                    True, 
                    "Request rejected successfully"
                )
            else:
                print_test_result(
                    "Reject Withdrawal Request", 
                    False, 
                    f"Status: {reject_response.status_code}, Response: {reject_response.text}"
                )
        else:
            print_test_result("Create Request for Rejection Test", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Reject Withdrawal Request", False, f"Exception: {str(e)}")
    
    return test_request_id is not None

def test_dashboard_analytics():
    """Test dashboard analytics endpoints"""
    
    print("=" * 60)
    print("TESTING DASHBOARD ANALYTICS")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Dashboard Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Get dashboard stats
    try:
        response = requests.get(f"{API_URL}/dashboard/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print_test_result(
                "Dashboard Stats", 
                True, 
                f"Stats: {stats.get('total_items')} items, {stats.get('low_stock_items')} low stock, {stats.get('pending_requests')} pending requests"
            )
        else:
            print_test_result(
                "Dashboard Stats", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Dashboard Stats", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: Get category stats
    try:
        response = requests.get(f"{API_URL}/dashboard/category-stats", headers=headers)
        if response.status_code == 200:
            category_stats = response.json()
            print_test_result(
                "Category Statistics", 
                True, 
                f"Retrieved category breakdown for {len(category_stats)} categories"
            )
        else:
            print_test_result(
                "Category Statistics", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("Category Statistics", False, f"Exception: {str(e)}")
    
    # Test 3: Get low stock items
    try:
        response = requests.get(f"{API_URL}/dashboard/low-stock-items", headers=headers)
        if response.status_code == 200:
            low_stock = response.json()
            print_test_result(
                "Low Stock Items", 
                True, 
                f"Retrieved {len(low_stock)} low stock items"
            )
        else:
            print_test_result(
                "Low Stock Items", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("Low Stock Items", False, f"Exception: {str(e)}")
    
    # Test 4: Get expiring items
    try:
        response = requests.get(f"{API_URL}/dashboard/expiring-items", headers=headers)
        if response.status_code == 200:
            expiring = response.json()
            print_test_result(
                "Expiring Items", 
                True, 
                f"Retrieved {len(expiring)} items expiring soon"
            )
        else:
            print_test_result(
                "Expiring Items", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("Expiring Items", False, f"Exception: {str(e)}")
    
    return True

def test_email_configuration():
    """Test email configuration management (admin only)"""
    
    print("=" * 60)
    print("TESTING EMAIL CONFIGURATION MANAGEMENT")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Email Config Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Add email configuration
    email_config = {
        "email": "lab.manager@company.com"
    }
    
    try:
        response = requests.post(f"{API_URL}/email-config", json=email_config, headers=headers)
        if response.status_code == 200:
            print_test_result(
                "Add Email Configuration", 
                True, 
                f"Email added: {email_config['email']}"
            )
        else:
            print_test_result(
                "Add Email Configuration", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Add Email Configuration", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: Get email configurations
    try:
        response = requests.get(f"{API_URL}/email-config", headers=headers)
        if response.status_code == 200:
            email_configs = response.json()
            print_test_result(
                "List Email Configurations", 
                True, 
                f"Retrieved {len(email_configs)} email configurations"
            )
        else:
            print_test_result(
                "List Email Configurations", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("List Email Configurations", False, f"Exception: {str(e)}")
    
    return True

def test_user_management():
    """Test new user management functionality"""
    
    print("=" * 60)
    print("TESTING USER MANAGEMENT FUNCTIONALITY")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("User Management Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_user_id = None
    
    # Test 1: Verify login response includes section field
    try:
        login_data = {
            "employee_number": "ADMIN001",
            "password": "admin123"
        }
        response = requests.post(f"{API_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("user", {})
            section = user_data.get("section")
            if section == "IT Administration":
                print_test_result(
                    "Login Response Includes Section Field", 
                    True, 
                    f"Section field present: {section}"
                )
            else:
                print_test_result(
                    "Login Response Includes Section Field", 
                    False, 
                    f"Expected 'IT Administration', got: {section}"
                )
        else:
            print_test_result(
                "Login Response Includes Section Field", 
                False, 
                f"Login failed with status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Login Response Includes Section Field", False, f"Exception: {str(e)}")
    
    # Test 2: Verify profile response includes section field
    try:
        response = requests.get(f"{API_URL}/profile", headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            section = profile_data.get("section")
            if section == "IT Administration":
                print_test_result(
                    "Profile Response Includes Section Field", 
                    True, 
                    f"Section field present: {section}"
                )
            else:
                print_test_result(
                    "Profile Response Includes Section Field", 
                    False, 
                    f"Expected 'IT Administration', got: {section}"
                )
        else:
            print_test_result(
                "Profile Response Includes Section Field", 
                False, 
                f"Profile access failed with status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Profile Response Includes Section Field", False, f"Exception: {str(e)}")
    
    # Test 3: List all users (admin only)
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
                    "List All Users with Section Field", 
                    True, 
                    f"Retrieved {len(users)} users, admin section: {admin_user.get('section')}"
                )
            else:
                print_test_result(
                    "List All Users with Section Field", 
                    False, 
                    f"Admin user section not found or incorrect"
                )
        else:
            print_test_result(
                "List All Users with Section Field", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("List All Users with Section Field", False, f"Exception: {str(e)}")
    
    # Test 4: Create new test user with section field
    test_user_data = {
        "employee_number": "QC001",
        "password": "test123",
        "role": "user",
        "full_name": "John Doe",
        "email": "john.doe@company.com",
        "section": "Quality Control Department"
    }
    
    try:
        response = requests.post(f"{API_URL}/register", json=test_user_data, headers=headers)
        if response.status_code == 200:
            print_test_result(
                "Create New User with Section Field", 
                True, 
                f"User created: {test_user_data['full_name']} in {test_user_data['section']}"
            )
            
            # Get the user ID for deletion test
            users_response = requests.get(f"{API_URL}/users", headers=headers)
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if user.get("employee_number") == "QC001":
                        test_user_id = user.get("id")
                        break
        else:
            print_test_result(
                "Create New User with Section Field", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("Create New User with Section Field", False, f"Exception: {str(e)}")
    
    # Test 5: Verify new user appears in users list
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
                    "Verify New User in List", 
                    True, 
                    f"New user found: {new_user.get('full_name')} - {new_user.get('section')}"
                )
            else:
                print_test_result(
                    "Verify New User in List", 
                    False, 
                    "New user not found in users list or section incorrect"
                )
        else:
            print_test_result(
                "Verify New User in List", 
                False, 
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Verify New User in List", False, f"Exception: {str(e)}")
    
    # Test 6: Test user deletion
    if test_user_id:
        try:
            response = requests.delete(f"{API_URL}/users/{test_user_id}", headers=headers)
            if response.status_code == 200:
                print_test_result(
                    "Delete Test User", 
                    True, 
                    "Test user deleted successfully"
                )
            else:
                print_test_result(
                    "Delete Test User", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            print_test_result("Delete Test User", False, f"Exception: {str(e)}")
    
    # Test 7: Test admin self-deletion prevention
    if admin_user_data:
        admin_id = admin_user_data.get("id")
        try:
            response = requests.delete(f"{API_URL}/users/{admin_id}", headers=headers)
            if response.status_code == 400:
                print_test_result(
                    "Prevent Admin Self-Deletion", 
                    True, 
                    "Correctly prevented admin from deleting own account"
                )
            else:
                print_test_result(
                    "Prevent Admin Self-Deletion", 
                    False, 
                    f"Expected 400, got {response.status_code}"
                )
        except Exception as e:
            print_test_result("Prevent Admin Self-Deletion", False, f"Exception: {str(e)}")
    
    # Test 8: Test role-based access to user management endpoints
    try:
        # Try to access users endpoint without token
        response = requests.get(f"{API_URL}/users")
        if response.status_code == 403 or response.status_code == 401:
            print_test_result(
                "User Management Endpoint Protection", 
                True, 
                f"Correctly blocked unauthorized access (Status: {response.status_code})"
            )
        else:
            print_test_result(
                "User Management Endpoint Protection", 
                False, 
                f"Expected 401/403, got {response.status_code}"
            )
    except Exception as e:
        print_test_result("User Management Endpoint Protection", False, f"Exception: {str(e)}")
    
    return True

def test_excel_export():
    """Test Excel export functionality for inventory management"""
    
    print("=" * 60)
    print("TESTING EXCEL EXPORT FUNCTIONALITY")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Excel Export Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Authentication Test - Valid JWT token
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel", headers=headers)
        if response.status_code == 200:
            print_test_result(
                "Excel Export Authentication (Valid Token)", 
                True, 
                "Successfully authenticated with valid JWT token"
            )
        else:
            print_test_result(
                "Excel Export Authentication (Valid Token)", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Excel Export Authentication (Valid Token)", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: Authentication Test - No token (should fail)
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel")
        if response.status_code == 401 or response.status_code == 403:
            print_test_result(
                "Excel Export Authentication (No Token)", 
                True, 
                f"Correctly rejected request without authentication (Status: {response.status_code})"
            )
        else:
            print_test_result(
                "Excel Export Authentication (No Token)", 
                False, 
                f"Expected 401/403, got {response.status_code}"
            )
    except Exception as e:
        print_test_result("Excel Export Authentication (No Token)", False, f"Exception: {str(e)}")
    
    # Test 3: Excel File Generation with Correct Headers
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel", headers=headers)
        if response.status_code == 200:
            # Check Content-Type header
            content_type = response.headers.get('content-type', '')
            expected_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            if content_type == expected_content_type:
                print_test_result(
                    "Excel Export Content-Type Header", 
                    True, 
                    f"Correct Content-Type: {content_type}"
                )
            else:
                print_test_result(
                    "Excel Export Content-Type Header", 
                    False, 
                    f"Expected: {expected_content_type}, Got: {content_type}"
                )
            
            # Check Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            if 'attachment' in content_disposition and 'inventory_export_' in content_disposition and '.xlsx' in content_disposition:
                print_test_result(
                    "Excel Export Content-Disposition Header", 
                    True, 
                    f"Correct filename format: {content_disposition}"
                )
            else:
                print_test_result(
                    "Excel Export Content-Disposition Header", 
                    False, 
                    f"Incorrect Content-Disposition: {content_disposition}"
                )
        else:
            print_test_result(
                "Excel Export Headers Test", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        print_test_result("Excel Export Headers Test", False, f"Exception: {str(e)}")
    
    # Test 4: Content Validation - Binary Data and File Size
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel", headers=headers)
        if response.status_code == 200:
            content = response.content
            content_length = len(content)
            
            # Check if content is not empty
            if content_length > 0:
                print_test_result(
                    "Excel Export Content Size", 
                    True, 
                    f"File size: {content_length} bytes (not empty)"
                )
            else:
                print_test_result(
                    "Excel Export Content Size", 
                    False, 
                    "File is empty"
                )
            
            # Check if content appears to be binary (Excel file)
            # Excel files start with specific bytes (PK for ZIP format)
            if content.startswith(b'PK'):
                print_test_result(
                    "Excel Export Binary Content", 
                    True, 
                    "Content appears to be valid Excel file (ZIP format)"
                )
            else:
                print_test_result(
                    "Excel Export Binary Content", 
                    False, 
                    "Content does not appear to be valid Excel file"
                )
            
            # Check reasonable file size (should be at least 5KB for a proper Excel file)
            if content_length >= 5000:
                print_test_result(
                    "Excel Export Reasonable File Size", 
                    True, 
                    f"File size is reasonable: {content_length} bytes"
                )
            else:
                print_test_result(
                    "Excel Export Reasonable File Size", 
                    False, 
                    f"File size too small: {content_length} bytes"
                )
        else:
            print_test_result(
                "Excel Export Content Validation", 
                False, 
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Excel Export Content Validation", False, f"Exception: {str(e)}")
    
    # Test 5: Edge Case - Test with existing inventory data
    try:
        # First check if we have inventory items
        inventory_response = requests.get(f"{API_URL}/inventory", headers=headers)
        if inventory_response.status_code == 200:
            inventory_items = inventory_response.json()
            item_count = len(inventory_items)
            
            # Now test Excel export
            response = requests.get(f"{API_URL}/inventory/export/excel", headers=headers)
            if response.status_code == 200:
                print_test_result(
                    "Excel Export with Existing Data", 
                    True, 
                    f"Successfully exported {item_count} inventory items to Excel"
                )
            else:
                print_test_result(
                    "Excel Export with Existing Data", 
                    False, 
                    f"Export failed with status: {response.status_code}"
                )
        else:
            print_test_result(
                "Excel Export Data Check", 
                False, 
                "Could not retrieve inventory data for validation"
            )
    except Exception as e:
        print_test_result("Excel Export with Existing Data", False, f"Exception: {str(e)}")
    
    # Test 6: Test filename format validation
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel", headers=headers)
        if response.status_code == 200:
            content_disposition = response.headers.get('content-disposition', '')
            # Extract filename from Content-Disposition header
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip()
                # Check if filename matches expected format: inventory_export_YYYYMMDD_HHMMSS.xlsx
                import re
                pattern = r'inventory_export_\d{8}_\d{6}\.xlsx'
                if re.match(pattern, filename):
                    print_test_result(
                        "Excel Export Filename Format", 
                        True, 
                        f"Filename matches expected format: {filename}"
                    )
                else:
                    print_test_result(
                        "Excel Export Filename Format", 
                        False, 
                        f"Filename format incorrect: {filename}"
                    )
            else:
                print_test_result(
                    "Excel Export Filename Format", 
                    False, 
                    "No filename found in Content-Disposition header"
                )
        else:
            print_test_result(
                "Excel Export Filename Format", 
                False, 
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Excel Export Filename Format", False, f"Exception: {str(e)}")
    
    return True

def test_withdrawal_requests_ordering():
    """Test that withdrawal requests are ordered from newest to oldest"""
    
    print("=" * 60)
    print("TESTING WITHDRAWAL REQUESTS ORDERING")
    print("=" * 60)
    
    if not auth_token or not test_item_id:
        print_test_result("Withdrawal Requests Ordering Tests", False, "Missing auth token or test item")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create multiple withdrawal requests with slight delays to ensure different timestamps
    request_ids = []
    request_purposes = [
        "First request - should appear last in list",
        "Second request - should appear second to last",
        "Third request - should appear first in list"
    ]
    
    import time
    
    for i, purpose in enumerate(request_purposes):
        withdrawal_request = {
            "item_id": test_item_id,
            "requested_quantity": 1,
            "purpose": purpose
        }
        
        try:
            response = requests.post(f"{API_URL}/withdrawal-requests", json=withdrawal_request, headers=headers)
            if response.status_code == 200:
                request_data = response.json()
                request_ids.append({
                    'id': request_data.get("id"),
                    'purpose': purpose,
                    'created_at': request_data.get("created_at")
                })
                print(f"Created request {i+1}: {purpose}")
                time.sleep(1)  # Small delay to ensure different timestamps
            else:
                print_test_result(
                    f"Create Withdrawal Request {i+1}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
        except Exception as e:
            print_test_result(f"Create Withdrawal Request {i+1}", False, f"Exception: {str(e)}")
            return False
    
    # Now fetch all withdrawal requests and verify ordering
    try:
        response = requests.get(f"{API_URL}/withdrawal-requests", headers=headers)
        if response.status_code == 200:
            requests_list = response.json()
            
            if len(requests_list) >= 3:
                # Check if the first request in the list has the most recent created_at timestamp
                first_request = requests_list[0]
                first_created_at = first_request.get('created_at')
                
                # Verify that requests are in descending order by created_at
                is_properly_ordered = True
                previous_timestamp = None
                
                for i, req in enumerate(requests_list[:3]):  # Check first 3 requests
                    current_timestamp = req.get('created_at')
                    if previous_timestamp and current_timestamp > previous_timestamp:
                        is_properly_ordered = False
                        break
                    previous_timestamp = current_timestamp
                
                if is_properly_ordered:
                    print_test_result(
                        "Withdrawal Requests Descending Order", 
                        True, 
                        f"Requests properly ordered by created_at (newest first). First request created at: {first_created_at}"
                    )
                else:
                    print_test_result(
                        "Withdrawal Requests Descending Order", 
                        False, 
                        "Requests are not properly ordered by created_at in descending order"
                    )
                
                # Verify that the newest request (last created) appears first in the list
                newest_request_purpose = request_purposes[-1]  # "Third request - should appear first"
                first_request_purpose = first_request.get('purpose', '')
                
                if newest_request_purpose in first_request_purpose:
                    print_test_result(
                        "Newest Request Appears First", 
                        True, 
                        f"Newest request correctly appears first: {first_request_purpose}"
                    )
                else:
                    print_test_result(
                        "Newest Request Appears First", 
                        False, 
                        f"Expected newest request first, but got: {first_request_purpose}"
                    )
                
            else:
                print_test_result(
                    "Withdrawal Requests Ordering", 
                    False, 
                    f"Not enough requests to test ordering. Found: {len(requests_list)}"
                )
                
        else:
            print_test_result(
                "Fetch Withdrawal Requests for Ordering Test", 
                False, 
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
            
    except Exception as e:
        print_test_result("Withdrawal Requests Ordering Test", False, f"Exception: {str(e)}")
        return False
    
    return True

def test_removed_inventory_filters():
    """Test that below_reorder and below_target filters are no longer supported"""
    
    print("=" * 60)
    print("TESTING REMOVED INVENTORY FILTERS")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Removed Filters Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test that below_reorder and below_target filters are not supported in Excel export
    removed_filters = ['below_reorder', 'below_target']
    
    for filter_name in removed_filters:
        try:
            response = requests.get(f"{API_URL}/inventory/export/excel?filter={filter_name}", headers=headers)
            
            # The filter should either:
            # 1. Return 404 (no items found - treating as invalid filter)
            # 2. Return 400 (bad request - filter not supported)
            # 3. Default to 'all' filter behavior (fallback)
            
            if response.status_code == 404:
                print_test_result(
                    f"Removed Filter '{filter_name}' Not Supported", 
                    True, 
                    f"Filter correctly not supported (404 - no items found for invalid filter)"
                )
            elif response.status_code == 400:
                print_test_result(
                    f"Removed Filter '{filter_name}' Not Supported", 
                    True, 
                    f"Filter correctly rejected (400 - bad request)"
                )
            elif response.status_code == 200:
                # If it returns 200, it might be defaulting to 'all' - check if it's actually filtering
                content_disposition = response.headers.get('content-disposition', '')
                if filter_name not in content_disposition:
                    print_test_result(
                        f"Removed Filter '{filter_name}' Not Supported", 
                        True, 
                        f"Filter ignored and defaulted to general export (filename doesn't contain filter name)"
                    )
                else:
                    print_test_result(
                        f"Removed Filter '{filter_name}' Not Supported", 
                        False, 
                        f"Filter appears to be still supported (filename contains filter name)"
                    )
            else:
                print_test_result(
                    f"Removed Filter '{filter_name}' Not Supported", 
                    False, 
                    f"Unexpected status code: {response.status_code}"
                )
                
        except Exception as e:
            print_test_result(f"Removed Filter '{filter_name}' Test", False, f"Exception: {str(e)}")
    
    return True

def test_excel_export_valid_filters():
    """Test that only valid filters are supported in Excel export"""
    
    print("=" * 60)
    print("TESTING EXCEL EXPORT VALID FILTERS")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Excel Export Valid Filters Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Valid filters that should be supported
    valid_filters = ['all', 'low_stock', 'zero_stock', 'expiring_soon', 'expired']
    
    for filter_name in valid_filters:
        try:
            response = requests.get(f"{API_URL}/inventory/export/excel?filter={filter_name}", headers=headers)
            
            if response.status_code == 200:
                # Check that it's a valid Excel file
                content_type = response.headers.get('content-type', '')
                expected_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                content = response.content
                
                if content_type == expected_content_type and content.startswith(b'PK'):
                    print_test_result(
                        f"Valid Filter '{filter_name}' Supported", 
                        True, 
                        f"Filter works correctly, returns valid Excel file ({len(content)} bytes)"
                    )
                else:
                    print_test_result(
                        f"Valid Filter '{filter_name}' Supported", 
                        False, 
                        f"Filter returns invalid Excel file or wrong content type"
                    )
            elif response.status_code == 404:
                # 404 is acceptable if no items match the filter
                print_test_result(
                    f"Valid Filter '{filter_name}' Supported", 
                    True, 
                    f"Filter supported but no matching items found (404 - acceptable)"
                )
            else:
                print_test_result(
                    f"Valid Filter '{filter_name}' Supported", 
                    False, 
                    f"Unexpected status code: {response.status_code}"
                )
                
        except Exception as e:
            print_test_result(f"Valid Filter '{filter_name}' Test", False, f"Exception: {str(e)}")
    
    return True

def test_enhanced_excel_export_filtering():
    """Test enhanced Excel export functionality with filtering parameters"""
    
    print("=" * 60)
    print("TESTING ENHANCED EXCEL EXPORT WITH FILTERING")
    print("=" * 60)
    
    if not auth_token:
        print_test_result("Enhanced Excel Export Tests", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Available filters to test (UPDATED - removed below_reorder and below_target)
    filters_to_test = [
        'all',
        'low_stock', 
        'zero_stock',
        'expiring_soon',
        'expired'
    ]
    
    # First, let's add some test inventory items with different conditions to ensure we have data for filtering
    test_items = [
        {
            "item_name": "Low Stock Test Item",
            "category": "Test Equipment",
            "location": "Test Lab A",
            "manufacturer": "Test Manufacturer",
            "supplier": "Test Supplier",
            "model": "LOW-001",
            "uom": "pieces",
            "catalogue_no": "LOW001",
            "quantity": 2,  # Below reorder level
            "target_stock_level": 20,
            "reorder_level": 5,
            "validity": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "use_case": "Testing low stock filtering"
        },
        {
            "item_name": "Zero Stock Test Item",
            "category": "Test Equipment",
            "location": "Test Lab B",
            "manufacturer": "Test Manufacturer",
            "supplier": "Test Supplier",
            "model": "ZERO-001",
            "uom": "pieces",
            "catalogue_no": "ZERO001",
            "quantity": 0,  # Zero stock
            "target_stock_level": 15,
            "reorder_level": 3,
            "validity": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "use_case": "Testing zero stock filtering"
        },
        {
            "item_name": "Expiring Soon Test Item",
            "category": "Test Chemicals",
            "location": "Test Lab C",
            "manufacturer": "Test Manufacturer",
            "supplier": "Test Supplier",
            "model": "EXP-001",
            "uom": "bottles",
            "catalogue_no": "EXP001",
            "quantity": 10,
            "target_stock_level": 15,
            "reorder_level": 3,
            "validity": (datetime.utcnow() + timedelta(days=15)).isoformat(),  # Expiring in 15 days
            "use_case": "Testing expiring soon filtering"
        },
        {
            "item_name": "Expired Test Item",
            "category": "Test Chemicals",
            "location": "Test Lab D",
            "manufacturer": "Test Manufacturer",
            "supplier": "Test Supplier",
            "model": "EXPIRED-001",
            "uom": "bottles",
            "catalogue_no": "EXPIRED001",
            "quantity": 5,
            "target_stock_level": 10,
            "reorder_level": 2,
            "validity": (datetime.utcnow() - timedelta(days=30)).isoformat(),  # Expired 30 days ago
            "use_case": "Testing expired filtering"
        }
    ]
    
    # Add test items for filtering
    added_item_ids = []
    for item in test_items:
        try:
            response = requests.post(f"{API_URL}/inventory", json=item, headers=headers)
            if response.status_code == 200:
                item_data = response.json()
                added_item_ids.append(item_data.get("id"))
        except Exception as e:
            print(f"Warning: Could not add test item {item['item_name']}: {str(e)}")
    
    print(f"Added {len(added_item_ids)} test items for filtering tests")
    
    # Test each filter
    for filter_name in filters_to_test:
        try:
            response = requests.get(f"{API_URL}/inventory/export/excel?filter={filter_name}", headers=headers)
            
            if response.status_code == 200:
                # Check Content-Type header
                content_type = response.headers.get('content-type', '')
                expected_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                # Check Content-Disposition header for filename
                content_disposition = response.headers.get('content-disposition', '')
                filename = ""
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip()
                
                # Verify filename includes filter suffix when not 'all'
                expected_filter_in_filename = filter_name != 'all'
                has_filter_in_filename = filter_name in filename if expected_filter_in_filename else True
                
                # Check file content
                content = response.content
                content_length = len(content)
                is_valid_excel = content.startswith(b'PK')
                
                # Determine test success
                test_success = (
                    content_type == expected_content_type and
                    content_length > 1000 and  # Reasonable file size
                    is_valid_excel and
                    has_filter_in_filename
                )
                
                print_test_result(
                    f"Excel Export Filter: {filter_name}", 
                    test_success, 
                    f"Status: 200, Size: {content_length} bytes, Filename: {filename}, Filter in name: {has_filter_in_filename}"
                )
                
            elif response.status_code == 404:
                # This is acceptable for some filters if no matching data exists
                print_test_result(
                    f"Excel Export Filter: {filter_name}", 
                    True, 
                    f"Status: 404 - No items found for filter (acceptable)"
                )
                
            else:
                print_test_result(
                    f"Excel Export Filter: {filter_name}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            print_test_result(f"Excel Export Filter: {filter_name}", False, f"Exception: {str(e)}")
    
    # Test invalid filter parameter
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel?filter=invalid_filter", headers=headers)
        # Should still work but treat as 'all' or return appropriate error
        if response.status_code in [200, 404]:
            print_test_result(
                "Excel Export Invalid Filter", 
                True, 
                f"Handled invalid filter gracefully (Status: {response.status_code})"
            )
        else:
            print_test_result(
                "Excel Export Invalid Filter", 
                False, 
                f"Unexpected status for invalid filter: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Excel Export Invalid Filter", False, f"Exception: {str(e)}")
    
    # Test multiple filter parameters (should use the first one)
    try:
        response = requests.get(f"{API_URL}/inventory/export/excel?filter=all&filter=low_stock", headers=headers)
        if response.status_code in [200, 404]:
            print_test_result(
                "Excel Export Multiple Filter Parameters", 
                True, 
                f"Handled multiple filter parameters (Status: {response.status_code})"
            )
        else:
            print_test_result(
                "Excel Export Multiple Filter Parameters", 
                False, 
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test_result("Excel Export Multiple Filter Parameters", False, f"Exception: {str(e)}")
    
    # Clean up test items
    for item_id in added_item_ids:
        try:
            requests.delete(f"{API_URL}/inventory/{item_id}", headers=headers)
        except:
            pass  # Ignore cleanup errors
    
    print(f"Cleaned up {len(added_item_ids)} test items")
    
    return True

def test_role_based_access():
    """Test role-based access control"""
    
    print("=" * 60)
    print("TESTING ROLE-BASED ACCESS CONTROL")
    print("=" * 60)
    
    # Test accessing admin-only endpoints without proper role
    # For this test, we'll try to access admin endpoints with no token
    
    # Test 1: Try to add inventory without token
    inventory_item = {
        "item_name": "Test Item",
        "category": "Test Category",
        "location": "Test Location",
        "manufacturer": "Test Manufacturer",
        "supplier": "Test Supplier",
        "model": "Test Model",
        "uom": "pieces",
        "catalogue_no": "TEST001",
        "quantity": 10,
        "target_stock_level": 15,
        "reorder_level": 5,
        "use_case": "Testing purposes"
    }
    
    try:
        response = requests.post(f"{API_URL}/inventory", json=inventory_item)
        if response.status_code == 403 or response.status_code == 401:
            print_test_result(
                "Admin Endpoint Protection", 
                True, 
                f"Correctly blocked unauthorized access (Status: {response.status_code})"
            )
        else:
            print_test_result(
                "Admin Endpoint Protection", 
                False, 
                f"Expected 401/403, got {response.status_code}"
            )
    except Exception as e:
        print_test_result("Admin Endpoint Protection", False, f"Exception: {str(e)}")
    
    return True

def run_all_tests():
    """Run all backend tests in sequence"""
    
    print("🧪 LABORATORY INVENTORY MANAGEMENT SYSTEM - BACKEND API TESTING")
    print("=" * 80)
    print(f"Backend URL: {API_URL}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_results = {}
    
    # Run tests in priority order
    test_results['authentication'] = test_authentication()
    test_results['user_management'] = test_user_management()
    test_results['inventory'] = test_inventory_management()
    test_results['withdrawal_requests'] = test_withdrawal_requests()
    test_results['dashboard'] = test_dashboard_analytics()
    test_results['email_config'] = test_email_configuration()
    test_results['excel_export'] = test_excel_export()
    test_results['role_access'] = test_role_based_access()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 ALL BACKEND TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Check details above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)