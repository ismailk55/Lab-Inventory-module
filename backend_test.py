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
    test_results['inventory'] = test_inventory_management()
    test_results['withdrawal_requests'] = test_withdrawal_requests()
    test_results['dashboard'] = test_dashboard_analytics()
    test_results['email_config'] = test_email_configuration()
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