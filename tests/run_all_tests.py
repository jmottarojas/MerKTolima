"""Comprehensive test runner for Task 14.2 - Execute complete test suite."""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Duration: {end_time - start_time:.2f} seconds")
    print(f"Return code: {result.returncode}")
    
    if result.stdout:
        print(f"\nSTDOUT:\n{result.stdout}")
    
    if result.stderr:
        print(f"\nSTDERR:\n{result.stderr}")
    
    return result.returncode == 0

def main():
    """Run all tests for Task 14.2."""
    print("="*80)
    print("TASK 14.2: EJECUTAR SUITE COMPLETA DE TESTS")
    print("Comprehensive Test Suite Execution")
    print("="*80)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    test_results = {}
    
    # 1. Run unit tests for all services
    print("\n" + "="*80)
    print("1. UNIT TESTS - Testing individual service functionality")
    print("="*80)
    
    unit_test_files = [
        ("tests/services/test_users.py", "User Service Unit Tests"),
        ("tests/services/test_products.py", "Product Service Unit Tests"),
        ("tests/services/test_orders.py", "Order Service Unit Tests"),
        ("tests/services/test_payments.py", "Payment Service Unit Tests"),
        ("tests/services/test_notifications.py", "Notification Service Unit Tests"),
        ("tests/services/test_search.py", "Search Service Unit Tests"),
    ]
    
    for test_file, description in unit_test_files:
        if os.path.exists(test_file):
            success = run_command(f"python -m pytest {test_file} -v", description)
            test_results[description] = success
        else:
            print(f"Warning: {test_file} not found, skipping...")
            test_results[description] = False
    
    # 2. Run property-based tests
    print("\n" + "="*80)
    print("2. PROPERTY-BASED TESTS - Testing universal correctness properties")
    print("="*80)
    
    # Property tests are embedded in service tests, run with hypothesis
    success = run_command("python -m pytest tests/services/ -v -k 'property' --hypothesis-show-statistics", 
                         "Property-Based Tests")
    test_results["Property-Based Tests"] = success
    
    # 3. Run model validation tests
    print("\n" + "="*80)
    print("3. MODEL VALIDATION TESTS - Testing data model integrity")
    print("="*80)
    
    success = run_command("python -m pytest tests/test_models.py -v", "Model Validation Tests")
    test_results["Model Validation Tests"] = success
    
    # 4. Run shared component tests
    print("\n" + "="*80)
    print("4. SHARED COMPONENT TESTS - Testing shared utilities")
    print("="*80)
    
    success = run_command("python -m pytest tests/test_shared.py -v", "Shared Component Tests")
    test_results["Shared Component Tests"] = success
    
    # 5. Run persistence tests
    print("\n" + "="*80)
    print("5. PERSISTENCE TESTS - Testing database operations")
    print("="*80)
    
    success = run_command("python -m pytest tests/test_persistence.py -v", "Persistence Tests")
    test_results["Persistence Tests"] = success
    
    # 6. Run API integration tests
    print("\n" + "="*80)
    print("6. API INTEGRATION TESTS - Testing REST API endpoints")
    print("="*80)
    
    success = run_command("python -m pytest tests/test_api.py -v", "API Integration Tests")
    test_results["API Integration Tests"] = success
    
    # 7. Run complete integration tests
    print("\n" + "="*80)
    print("7. COMPLETE INTEGRATION TESTS - Testing end-to-end business flows")
    print("="*80)
    
    success = run_command("python -m pytest tests/test_integration.py -v", "Complete Integration Tests")
    test_results["Complete Integration Tests"] = success
    
    # 8. Run configuration tests
    print("\n" + "="*80)
    print("8. CONFIGURATION TESTS - Testing service configurations")
    print("="*80)
    
    success = run_command("python -m pytest tests/test_config.py -v", "Configuration Tests")
    test_results["Configuration Tests"] = success
    
    # 9. Run all tests together with coverage
    print("\n" + "="*80)
    print("9. COMPREHENSIVE TEST RUN - All tests with coverage report")
    print("="*80)
    
    success = run_command("python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term", 
                         "Complete Test Suite with Coverage")
    test_results["Complete Test Suite with Coverage"] = success
    
    # 10. Generate final report
    print("\n" + "="*80)
    print("TEST EXECUTION SUMMARY")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for success in test_results.values() if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, success in test_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test categories failed. Please review the output above.")
        print("Common issues to check:")
        print("- Missing dependencies")
        print("- Import errors")
        print("- Database connection issues")
        print("- Service configuration problems")
    else:
        print("\n🎉 All test categories passed successfully!")
        print("The marketplace platform is ready for production deployment.")
    
    # Additional information
    print("\n" + "="*80)
    print("ADDITIONAL INFORMATION")
    print("="*80)
    
    print("Coverage Report: Open htmlcov/index.html in your browser")
    print("Test Files Location: tests/")
    print("Source Code Location: src/")
    
    print("\nNext Steps:")
    if failed_tests == 0:
        print("✅ Task 14.2 Complete - All tests passing")
        print("✅ Ready to proceed to Task 15 - Final Checkpoint")
    else:
        print("❌ Fix failing tests before proceeding")
        print("❌ Review error messages and fix issues")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)