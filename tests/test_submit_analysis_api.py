import requests
import json
import uuid

# Replace with your deployed API Gateway URL
API_GATEWAY_URL = "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod"

def test_analyze_endpoint():
    print(f"Testing POST {API_GATEWAY_URL}/analyze")
    analysis_id = str(uuid.uuid4())
    resume_text = "John Doe, Software Engineer with 5 years of experience in Python and AWS. Developed scalable microservices."
    job_description = "Seeking a Software Engineer with strong Python and AWS experience. Knowledge of microservices architecture is a plus."

    payload = {
        "analysis_id": analysis_id,
        "resume_text": resume_text,
        "job_description": job_description
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{API_GATEWAY_URL}/analyze", headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        print("Response Status Code:", response.status_code)
        print("Response Body:", response.json())
        if response.status_code == 202 and response.json().get("status") == "submitted":
            print(f"Successfully submitted analysis with ID: {analysis_id}")
        else:
            print("Analysis submission failed or returned unexpected status.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Error Response Body:", e.response.text)

if __name__ == "__main__":
    test_analyze_endpoint()
