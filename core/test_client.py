import os
import requests
import json
import time
import sys
from typing import Dict, Any, List

# =============================================
# CRITICAL FIX: Add parent directory to path
# =============================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load .env from parent directory
from dotenv import load_dotenv
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path, override=True)

# Configuration for the FastAPI service
API_BASE_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{API_BASE_URL}/chat"
HEALTH_URL = f"{API_BASE_URL}/health"

# --- Environment Debugging ---
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"✅ DEBUG: GEMINI_API_KEY loaded from {env_path}")
    print(f"   Key preview: {gemini_key[:10]}...")
else:
    print(f"❌ DEBUG: GEMINI_API_KEY not found in {env_path}")

# --- Comprehensive Aadhaar-focused Test Queries ---
test_queries: List[Dict[str, Any]] = [
    {
        "query": "How to link mobile number with Aadhaar? What is the complete process?",
        "expected_action": "respond",
        "description": "Aadhaar: Comprehensive mobile linking process"
    },
    {
        "query": "What documents are required for Aadhaar enrollment?",
        "expected_action": "respond", 
        "description": "Aadhaar: Document requirements for enrollment"
    },
    {
        "query": "How to update address in Aadhaar card? Step by step process",
        "expected_action": "respond",
        "description": "Aadhaar: Address update procedure"
    },
    {
        "query": "Aadhaar enrollment form fields and how to fill them correctly",
        "expected_action": "form_assistance",
        "description": "Aadhaar: Form field assistance"
    },
    {
        "query": "Where is the nearest Aadhaar enrollment center in my area?",
        "expected_action": "location_service",
        "description": "Aadhaar: Location service request"
    },
    {
        "query": "How to correct name spelling in Aadhaar card?",
        "expected_action": "respond",
        "description": "Aadhaar: Name correction process"
    },
    {
        "query": "What is the process for Aadhaar biometric update?",
        "expected_action": "respond",
        "description": "Aadhaar: Biometric update procedure"
    },
    {
        "query": "How to fill Aadhaar update form for date of birth correction?",
        "expected_action": "form_assistance",
        "description": "Aadhaar: Form assistance for DOB correction"
    },
    {
        "query": "What to do if Aadhaar card is lost? How to get duplicate?",
        "expected_action": "respond",
        "description": "Aadhaar: Duplicate card process"
    },
    {
        "query": "Aadhaar card download process without enrollment number",
        "expected_action": "respond",
        "description": "Aadhaar: e-Aadhaar download help"
    },
    {
        "query": "How to check Aadhaar status after enrollment?",
        "expected_action": "respond",
        "description": "Aadhaar: Application status check"
    },
    {
        "query": "Aadhaar PVC card application process and requirements",
        "expected_action": "respond",
        "description": "Aadhaar: PVC card application"
    }
]

def check_server_health():
    """Comprehensive health check"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server Status: {health_data.get('status')}")
            print(f"   LLM Ready: {health_data.get('llm_initialized')}")
            print(f"   LLM Working: {health_data.get('llm_available', False)}")
            print(f"   Capabilities: {health_data.get('capabilities', 'Unknown')}")
            return True
        return False
    except Exception as e:
        print(f"❌ Server unavailable: {e}")
        return False

def run_test(query_data: Dict[str, Any], test_number: int):
    """Comprehensive test execution"""
    print(f"\n--- TEST {test_number}: {query_data['description']} ---")
    print(f"Query: {query_data['query']}")
    
    payload = {"message": query_data['query'], "context": {}}

    try:
        start_time = time.time()
        response = requests.post(CHAT_URL, json=payload, timeout=20)  # Increased timeout for comprehensive responses
        response_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
        chat_response = response.json()
        
        print(f"✅ Response ({response_time:.1f}s):")
        print(f"   Action: {chat_response.get('action')}")
        
        response_text = chat_response.get('response', '')
        if response_text:
            # Show more of the response to see comprehensive answers
            preview = response_text[:150] + "..." if len(response_text) > 150 else response_text
            print(f"   Answer Preview: {preview}")
        
        # Show sources if available
        sources = chat_response.get('sources', [])
        if sources:
            print(f"   Sources: {len(sources)} documents referenced")
        
        # Check response quality indicators
        response_length = len(response_text)
        has_bullet_points = '•' in response_text or '-' in response_text
        print(f"   Quality: {response_length} chars, Bullet points: {'✅' if has_bullet_points else '❌'}")
        
        action_match = chat_response.get('action') == query_data['expected_action']
        print(f"   Status: {'✅ PASS' if action_match else '❌ FAIL'}")
        
        return action_match
        
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Comprehensive Aadhaar responses might take longer")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Comprehensive Aadhaar Chat Service Test")
    print(f"📡 API: {API_BASE_URL}")
    print("🎯 Testing enhanced comprehensive Aadhaar responses with temperature 0.3")
    print(f"📚 Testing {len(test_queries)} comprehensive Aadhaar queries...")
    
    time.sleep(1)
    
    if not check_server_health():
        print("❌ Server health check failed. Make sure the server is running.")
        return
    
    passed = 0
    for i, test in enumerate(test_queries, 1):
        if run_test(test, i):
            passed += 1
        time.sleep(2)  # Increased delay for rate limiting with comprehensive responses
    
    print(f"\n📊 Comprehensive Aadhaar Test Results: {passed}/{len(test_queries)} passed")
    print(f"💡 Features tested: Natural responses, comprehensive document search, detailed Aadhaar answers")
    print(f"🎯 Focus: Aadhaar enrollment, updates, forms, documents, locations, and procedures")

if __name__ == "__main__":
    main()