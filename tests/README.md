# API Testing Suite

## Overview
This directory contains all test files for the NextFitAI backend API endpoints. Tests are designed to validate functionality, error handling, and integration between components.

## Available Tests

### test_submit_analysis_api.py
**Purpose**: Test the POST /analyze endpoint functionality
**Usage**: `python tests/test_submit_analysis_api.py`

**What it tests**:
- API endpoint availability and response time
- Request/response format validation
- Success scenario with valid input
- Error handling for invalid requests
- CORS headers and HTTP status codes

**Test Data Used**:
- Sample resume: "John Doe, Software Engineer with 5 years of experience in Python and AWS..."
- Sample job description: "Seeking a Software Engineer with strong Python and AWS experience..."
- Generated UUID for analysis_id

## Running Tests

### Individual Test
```bash
# Test the submit analysis API
python tests/test_submit_analysis_api.py
```

### Future: All Tests
```bash
# When more tests are added, use pytest
python -m pytest tests/ -v
```

## Test Configuration

### API Endpoint
Tests use the deployed API Gateway URL:
```
https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod
```

### Test Data
All tests use mock data that doesn't contain real personal information:
- Generic resume content with common skills
- Generic job descriptions
- Randomly generated UUIDs for analysis IDs

## Expected Test Results

### Successful Test Run
```
Testing POST https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze
Response Status Code: 202
Response Body: {'status': 'submitted', 'analysis_id': '...', 'estimated_completion': '...'}
Successfully submitted analysis with ID: <uuid>
```

### Test Failure Indicators
- HTTP status codes other than 202
- Missing required response fields
- Network connectivity issues
- Authentication/authorization errors

## Test Dependencies

### Required Python Packages
- `requests`: For HTTP API calls
- `json`: For JSON data handling
- `uuid`: For generating unique analysis IDs

### AWS Resources Required
- Deployed API Gateway endpoint
- Lambda functions (SubmitAnalysis, ProcessAnalysis)
- DynamoDB table for tracking
- S3 bucket for file storage

## Adding New Tests

### Test File Naming Convention
- `test_<endpoint_name>_api.py` for API endpoint tests
- `test_<function_name>_lambda.py` for direct Lambda function tests
- `test_integration_<scenario>.py` for integration tests

### Test Structure Template
```python
import requests
import json
import uuid

def test_endpoint_name():
    """Test description"""
    # Arrange
    api_url = "https://your-api-gateway-url.com/endpoint"
    payload = {...}
    
    # Act
    response = requests.post(api_url, json=payload)
    
    # Assert
    assert response.status_code == expected_code
    assert response.json().get('field') == expected_value
    
if __name__ == "__main__":
    test_endpoint_name()
```

## Future Test Plans

### Planned Test Files
- `test_get_analysis_status_api.py` - Test status retrieval endpoint (when added)
- `test_integration_full_workflow.py` - End-to-end workflow testing
- `test_error_scenarios.py` - Comprehensive error handling tests
- `test_performance.py` - Load and performance testing

### Test Scenarios to Cover
- **Happy Path**: Valid requests with expected responses
- **Error Handling**: Invalid inputs, missing fields, malformed JSON
- **Edge Cases**: Very long text, special characters, empty strings
- **Performance**: Response times, concurrent requests
- **Security**: Input validation, injection attempts

## Monitoring Test Results

### Manual Verification
After running tests, verify results using:
```bash
# Check if analysis was processed
python utilities/monitor_analysis_status.py <analysis_id>
```

### Automated Verification
Future tests should include:
- Automatic status checking after submission
- Result validation against expected patterns
- Cleanup of test data after completion

## Troubleshooting

### Common Issues
1. **Network Errors**: Check internet connectivity and API Gateway URL
2. **403 Forbidden**: Verify API Gateway permissions and CORS settings
3. **500 Internal Server Error**: Check Lambda function logs in CloudWatch
4. **Timeout**: Increase request timeout or check Lambda function performance

### Debug Steps
1. Check API Gateway URL is correct and accessible
2. Verify request format matches API specification
3. Check CloudWatch logs for Lambda function errors
4. Validate AWS resources are properly deployed
5. Test with curl or Postman for comparison

## Best Practices

### Test Data Management
- Use realistic but generic test data
- Avoid real personal information
- Generate unique IDs for each test run
- Clean up test data when possible

### Test Reliability
- Include proper error handling in tests
- Use assertions to validate all important response fields
- Add timeouts to prevent hanging tests
- Log detailed information for debugging failures
