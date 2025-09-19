#!/usr/bin/env python3
"""
Manual testing script for AI Agent Dashboard
Tests all critical functionality systematically
"""

import requests
import json
import time
from datetime import datetime

class AgentDashboardTester:
    def __init__(self):
        self.base_url = "http://localhost:3002"
        self.agent_api_url = "https://dynamous-agent-api-woeg.onrender.com"
        self.supabase_url = "https://lgveqfnpkxvzbnnwuled.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxndmVxZm5wa3h2emJubnd1bGVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTQxNjYsImV4cCI6MjA3MDgzMDE2Nn0.g56kDPUokoJpWY7vXd3GTMXpOc4WFOU0hDVWfGMZtO8"
        self.test_results = {}
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_results[test_name] = {
            "status": status,
            "details": details,
            "timestamp": timestamp
        }
        print(f"[{timestamp}] {test_name}: {'✅ PASS' if status else '❌ FAIL'}")
        if details:
            print(f"  Details: {details}")
        print()

    def test_application_accessibility(self):
        """Test if the application is accessible"""
        try:
            response = requests.get(self.base_url, allow_redirects=False, timeout=10)
            if response.status_code == 307 and 'auth/login' in response.headers.get('location', ''):
                self.log_test("Application Accessibility", True, "App redirects to login as expected")
                return True
            else:
                self.log_test("Application Accessibility", False, f"Unexpected response: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Application Accessibility", False, f"Connection failed: {str(e)}")
            return False

    def test_login_page_loads(self):
        """Test if login page loads correctly"""
        try:
            response = requests.get(f"{self.base_url}/auth/login", timeout=10)
            if response.status_code == 200 and 'login' in response.text.lower():
                self.log_test("Login Page Loads", True, "Login page loads with form")
                return True
            else:
                self.log_test("Login Page Loads", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Login Page Loads", False, f"Error: {str(e)}")
            return False

    def test_supabase_database_connection(self):
        """Test Supabase database connectivity"""
        try:
            headers = {"apikey": self.supabase_key}
            
            # Test documents table
            response = requests.get(
                f"{self.supabase_url}/rest/v1/documents?select=id,title&limit=5", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                documents = response.json()
                self.log_test("Supabase Database Connection", True, f"Found {len(documents)} documents")
                return True
            else:
                self.log_test("Supabase Database Connection", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Supabase Database Connection", False, f"Error: {str(e)}")
            return False

    def test_rag_documents_exist(self):
        """Test if RAG documents exist in database"""
        try:
            headers = {"apikey": self.supabase_key}
            
            # Search for Seminole Collective documents
            response = requests.get(
                f"{self.supabase_url}/rest/v1/documents?select=id,title,content&title=ilike.*seminole*", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                documents = response.json()
                if len(documents) > 0:
                    # Check if we have recent documents
                    has_content = any(doc.get('content') and len(doc['content']) > 100 for doc in documents)
                    self.log_test("RAG Documents Exist", has_content, 
                                f"Found {len(documents)} Seminole documents with content")
                    return has_content
                else:
                    self.log_test("RAG Documents Exist", False, "No Seminole documents found")
                    return False
            else:
                self.log_test("RAG Documents Exist", False, f"Query failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("RAG Documents Exist", False, f"Error: {str(e)}")
            return False

    def test_agent_api_health(self):
        """Test Agent API health"""
        try:
            response = requests.get(f"{self.agent_api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                all_healthy = health_data.get('status') == 'healthy'
                services = health_data.get('services', {})
                
                service_status = []
                for service, status in services.items():
                    service_status.append(f"{service}: {'✅' if status else '❌'}")
                
                self.log_test("Agent API Health", all_healthy, 
                            f"Services: {', '.join(service_status)}")
                return all_healthy
            else:
                self.log_test("Agent API Health", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Agent API Health", False, f"Error: {str(e)}")
            return False

    def test_user_profiles_table(self):
        """Test user profiles table exists"""
        try:
            headers = {"apikey": self.supabase_key}
            response = requests.get(
                f"{self.supabase_url}/rest/v1/user_profiles?select=id&limit=1", 
                headers=headers, 
                timeout=10
            )
            
            success = response.status_code in [200, 404]  # 404 means table exists but no data
            self.log_test("User Profiles Table", success, 
                        f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("User Profiles Table", False, f"Error: {str(e)}")
            return False

    def test_conversations_table(self):
        """Test conversations table exists"""
        try:
            headers = {"apikey": self.supabase_key}
            response = requests.get(
                f"{self.supabase_url}/rest/v1/conversations?select=id&limit=1", 
                headers=headers, 
                timeout=10
            )
            
            success = response.status_code in [200, 404]
            self.log_test("Conversations Table", success, 
                        f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Conversations Table", False, f"Error: {str(e)}")
            return False

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("AI AGENT DASHBOARD - COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical Issues
        critical_failures = []
        if not self.test_results.get("Application Accessibility", {}).get("status"):
            critical_failures.append("❌ CRITICAL: Application not accessible")
        if not self.test_results.get("Supabase Database Connection", {}).get("status"):
            critical_failures.append("❌ CRITICAL: Database connection failed")
        if not self.test_results.get("Agent API Health", {}).get("status"):
            critical_failures.append("❌ CRITICAL: Agent API unhealthy")
        if not self.test_results.get("RAG Documents Exist", {}).get("status"):
            critical_failures.append("❌ CRITICAL: No RAG documents found")
            
        if critical_failures:
            print("CRITICAL ISSUES:")
            for issue in critical_failures:
                print(f"  {issue}")
            print()
        
        # Detailed Results
        print("DETAILED TEST RESULTS:")
        print("-" * 40)
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] else "❌"
            print(f"{status_icon} {test_name}")
            if result['details']:
                print(f"    {result['details']}")
        print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        print("-" * 20)
        if failed_tests == 0:
            print("✅ All tests passed! System appears to be working correctly.")
            print("✅ Proceed with browser-based testing for full validation.")
        else:
            print("❌ Fix critical issues before proceeding with UI testing.")
            if not self.test_results.get("RAG Documents Exist", {}).get("status"):
                print("  • Run RAG pipeline to process documents")
            if not self.test_results.get("Agent API Health", {}).get("status"):
                print("  • Check Agent API configuration and connections")
        
        return passed_tests == total_tests

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("Starting comprehensive AI Agent Dashboard testing...\n")
        
        # Core Infrastructure Tests
        self.test_application_accessibility()
        self.test_login_page_loads()
        self.test_supabase_database_connection()
        self.test_agent_api_health()
        
        # Database Schema Tests  
        self.test_user_profiles_table()
        self.test_conversations_table()
        
        # RAG Functionality Tests
        self.test_rag_documents_exist()
        
        # Generate final report
        return self.generate_report()

if __name__ == "__main__":
    tester = AgentDashboardTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - System ready for browser testing!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Fix issues before proceeding")