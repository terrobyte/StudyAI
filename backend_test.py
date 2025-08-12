#!/usr/bin/env python3
"""
Backend Testing Suite for Educational Study App
Tests AI Integration, Chat API, Session Management, and University Resources
"""

import requests
import json
import time
import uuid
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://scholarly-ref-app.preview.emergentagent.com/api"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_results = []
        self.session_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_api_health(self):
        """Test basic API health endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "Educational Study App API" in data.get("message", ""):
                    self.log_test("API Health Check", True, "API is responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_session_creation(self):
        """Test session creation endpoint"""
        try:
            response = self.session.post(f"{BASE_URL}/sessions")
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "created_at" in data:
                    self.session_id = data["id"]
                    self.log_test("Session Creation", True, f"Session created with ID: {self.session_id}")
                    return True
                else:
                    self.log_test("Session Creation", False, f"Invalid session response: {data}")
                    return False
            else:
                self.log_test("Session Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Session Creation", False, f"Error: {str(e)}")
            return False
    
    def test_chat_mathematics(self):
        """Test chat with mathematics query - should use GPT-4o"""
        if not self.session_id:
            self.log_test("Mathematics Chat", False, "No session ID available")
            return False
            
        try:
            payload = {
                "message": "Explain calculus derivatives for Year 12 students with practical examples",
                "session_id": self.session_id
            }
            
            response = self.session.post(f"{BASE_URL}/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["ai_response", "subject", "ai_model_used", "sources"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Mathematics Chat", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check subject detection
                if data["subject"] != "mathematics":
                    self.log_test("Mathematics Chat", False, f"Wrong subject detected: {data['subject']}, expected: mathematics")
                    return False
                
                # Check AI model
                if "gpt-4o" not in data["ai_model_used"].lower():
                    self.log_test("Mathematics Chat", False, f"Wrong AI model: {data['ai_model_used']}, expected GPT-4o")
                    return False
                
                # Check sources
                if not data["sources"] or len(data["sources"]) == 0:
                    self.log_test("Mathematics Chat", False, "No university sources provided")
                    return False
                
                # Check response quality
                if len(data["ai_response"]) < 50:
                    self.log_test("Mathematics Chat", False, "AI response too short")
                    return False
                
                self.log_test("Mathematics Chat", True, 
                            f"Subject: {data['subject']}, Model: {data['ai_model_used']}, Sources: {len(data['sources'])}")
                return True
            else:
                self.log_test("Mathematics Chat", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Mathematics Chat", False, f"Error: {str(e)}")
            return False
    
    def test_chat_photography(self):
        """Test chat with photography query - should use Claude Sonnet 4"""
        if not self.session_id:
            self.log_test("Photography Chat", False, "No session ID available")
            return False
            
        try:
            payload = {
                "message": "What are the key principles of composition in photography for portrait work?",
                "session_id": self.session_id
            }
            
            response = self.session.post(f"{BASE_URL}/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                
                # Check subject detection
                if data["subject"] != "photography":
                    self.log_test("Photography Chat", False, f"Wrong subject detected: {data['subject']}, expected: photography")
                    return False
                
                # Check AI model
                if "claude-sonnet-4" not in data["ai_model_used"].lower():
                    self.log_test("Photography Chat", False, f"Wrong AI model: {data['ai_model_used']}, expected Claude Sonnet 4")
                    return False
                
                # Check sources
                if not data["sources"] or len(data["sources"]) == 0:
                    self.log_test("Photography Chat", False, "No university sources provided")
                    return False
                
                self.log_test("Photography Chat", True, 
                            f"Subject: {data['subject']}, Model: {data['ai_model_used']}, Sources: {len(data['sources'])}")
                return True
            else:
                self.log_test("Photography Chat", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Photography Chat", False, f"Error: {str(e)}")
            return False
    
    def test_chat_film_directing(self):
        """Test chat with film directing query - should use Gemini 2.0 Flash"""
        if not self.session_id:
            self.log_test("Film Directing Chat", False, "No session ID available")
            return False
            
        try:
            payload = {
                "message": "How do directors create visual storytelling in cinema through camera angles and movement?",
                "session_id": self.session_id
            }
            
            response = self.session.post(f"{BASE_URL}/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                
                # Check subject detection
                if data["subject"] != "film_directing":
                    self.log_test("Film Directing Chat", False, f"Wrong subject detected: {data['subject']}, expected: film_directing")
                    return False
                
                # Check AI model
                if "gemini-2.0-flash" not in data["ai_model_used"].lower():
                    self.log_test("Film Directing Chat", False, f"Wrong AI model: {data['ai_model_used']}, expected Gemini 2.0 Flash")
                    return False
                
                # Check sources
                if not data["sources"] or len(data["sources"]) == 0:
                    self.log_test("Film Directing Chat", False, "No university sources provided")
                    return False
                
                self.log_test("Film Directing Chat", True, 
                            f"Subject: {data['subject']}, Model: {data['ai_model_used']}, Sources: {len(data['sources'])}")
                return True
            else:
                self.log_test("Film Directing Chat", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Film Directing Chat", False, f"Error: {str(e)}")
            return False
    
    def test_university_resources(self):
        """Test university resources endpoints for all subjects"""
        subjects = ["mathematics", "photography", "film_directing"]
        all_passed = True
        
        for subject in subjects:
            try:
                response = self.session.get(f"{BASE_URL}/resources/{subject}")
                if response.status_code == 200:
                    data = response.json()
                    
                    if not isinstance(data, list) or len(data) == 0:
                        self.log_test(f"Resources - {subject}", False, "No resources returned")
                        all_passed = False
                        continue
                    
                    # Check resource structure
                    required_fields = ["name", "url", "department", "subject"]
                    for resource in data[:3]:  # Check first 3 resources
                        missing_fields = [field for field in required_fields if field not in resource]
                        if missing_fields:
                            self.log_test(f"Resources - {subject}", False, f"Missing fields in resource: {missing_fields}")
                            all_passed = False
                            break
                    else:
                        self.log_test(f"Resources - {subject}", True, f"Found {len(data)} university resources")
                else:
                    self.log_test(f"Resources - {subject}", False, f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Resources - {subject}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_session_messages(self):
        """Test retrieving session messages"""
        if not self.session_id:
            self.log_test("Session Messages", False, "No session ID available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/sessions/{self.session_id}/messages")
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Session Messages", False, "Response is not a list")
                    return False
                
                # We should have messages from previous chat tests
                if len(data) == 0:
                    self.log_test("Session Messages", False, "No messages found in session")
                    return False
                
                # Check message structure
                for message in data:
                    required_fields = ["user_message", "ai_response", "subject", "ai_model_used"]
                    missing_fields = [field for field in required_fields if field not in message]
                    if missing_fields:
                        self.log_test("Session Messages", False, f"Missing fields in message: {missing_fields}")
                        return False
                
                self.log_test("Session Messages", True, f"Retrieved {len(data)} messages from session")
                return True
            else:
                self.log_test("Session Messages", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Session Messages", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Backend Testing Suite for Educational Study App")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("API Health Check", self.test_api_health),
            ("Session Creation", self.test_session_creation),
            ("Mathematics Chat (GPT-4o)", self.test_chat_mathematics),
            ("Photography Chat (Claude Sonnet 4)", self.test_chat_photography),
            ("Film Directing Chat (Gemini 2.0)", self.test_chat_film_directing),
            ("University Resources", self.test_university_resources),
            ("Session Messages Retrieval", self.test_session_messages)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Check details above.")
            return False
    
    def get_summary(self):
        """Get a summary of test results"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "details": self.test_results
        }
        
        return summary

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Print detailed summary
    summary = tester.get_summary()
    print(f"\n📈 Final Summary:")
    print(f"   Success Rate: {summary['success_rate']}")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    
    exit(0 if success else 1)