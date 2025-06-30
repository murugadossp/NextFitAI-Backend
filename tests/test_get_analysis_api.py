import requests
import json
import uuid
import time

# Replace with your deployed API Gateway URL
API_GATEWAY_URL = "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod"

def test_health_endpoint():
    """Test the GET /health endpoint"""
    print(f"Testing GET {API_GATEWAY_URL}/health")
    
    try:
        response = requests.get(f"{API_GATEWAY_URL}/health")
        print("Response Status Code:", response.status_code)
        print("Response Body:", json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ Health check passed - System is healthy")
                return True
            else:
                print("⚠️ Health check shows system issues")
                return False
        else:
            print("❌ Health check failed with non-200 status")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed with error: {e}")
        return False

def test_get_results_endpoint_not_found():
    """Test GET /results/{analysis_id} with non-existent ID"""
    fake_analysis_id = str(uuid.uuid4())
    print(f"\nTesting GET {API_GATEWAY_URL}/results/{fake_analysis_id} (should return 404)")
    
    try:
        response = requests.get(f"{API_GATEWAY_URL}/results/{fake_analysis_id}")
        print("Response Status Code:", response.status_code)
        print("Response Body:", json.dumps(response.json(), indent=2))
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent analysis")
            return True
        else:
            print("❌ Expected 404 but got different status")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed with error: {e}")
        return False

def test_get_results_endpoint_with_real_analysis():
    """Test GET /results/{analysis_id} with a real analysis ID"""
    print(f"\nTesting GET /results endpoint with real analysis...")
    
    # First, submit a new analysis to get a real ID
    analysis_id = str(uuid.uuid4())
    resume_text = "Jane Smith, Senior Software Engineer with 7 years of experience in Python, AWS, and microservices. Led teams of 5+ developers and improved system performance by 40%."
    job_description = "Seeking a Senior Software Engineer with strong Python and AWS experience. Leadership experience and performance optimization skills preferred."

    submit_payload = {
        "analysis_id": analysis_id,
        "resume_text": resume_text,
        "job_description": job_description
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Submit analysis
        print(f"Submitting analysis with ID: {analysis_id}")
        submit_response = requests.post(f"{API_GATEWAY_URL}/analyze", headers=headers, data=json.dumps(submit_payload))
        
        if submit_response.status_code != 202:
            print(f"❌ Failed to submit analysis: {submit_response.status_code}")
            return False
        
        print("✅ Analysis submitted successfully")
        
        # Wait a moment for processing
        print("Waiting 5 seconds for processing...")
        time.sleep(5)
        
        # Now test the GET endpoint
        print(f"Testing GET {API_GATEWAY_URL}/results/{analysis_id}")
        response = requests.get(f"{API_GATEWAY_URL}/results/{analysis_id}")
        print("Response Status Code:", response.status_code)
        print("Response Body:", json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status == 'completed':
                results = data.get('results', {})
                required_fields = ['match_score', 'missing_skills', 'recommendations', 'confidence_score', 'analysis_timestamp']
                
                missing_fields = [field for field in required_fields if field not in results]
                if missing_fields:
                    print(f"❌ Missing required fields in results: {missing_fields}")
                    return False
                
                print("✅ Analysis completed with all required fields")
                print(f"   Match Score: {results['match_score']}")
                print(f"   Missing Skills: {results['missing_skills']}")
                print(f"   Confidence Score: {results['confidence_score']}")
                return True
                
            elif status in ['processing', 'submitted']:
                print("✅ Analysis is still processing (this is expected)")
                return True
                
            elif status == 'failed':
                print("⚠️ Analysis failed - check logs for details")
                return False
                
            else:
                print(f"❌ Unknown status: {status}")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed with error: {e}")
        return False

def test_invalid_routes():
    """Test invalid routes to ensure proper error handling"""
    print(f"\nTesting invalid routes...")
    
    invalid_routes = [
        "/results",  # Missing analysis_id
        "/results/",  # Empty analysis_id
        "/invalid-route",  # Non-existent route
    ]
    
    for route in invalid_routes:
        try:
            print(f"Testing {API_GATEWAY_URL}{route}")
            response = requests.get(f"{API_GATEWAY_URL}{route}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [400, 404]:
                print(f"  ✅ Correctly handled invalid route")
            else:
                print(f"  ⚠️ Unexpected status for invalid route")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("NextFitAI GET Analysis API Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Get Results - Not Found", test_get_results_endpoint_not_found),
        ("Get Results - Real Analysis", test_get_results_endpoint_with_real_analysis),
        ("Invalid Routes", test_invalid_routes),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed - check the output above for details")

if __name__ == "__main__":
    run_all_tests()
