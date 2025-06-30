# Get Analysis API

## Overview
This Lambda function handles GET requests for retrieving analysis results and system health checks. It provides two main endpoints for the NextFitAI backend.

## API Endpoints

### GET /results/{analysis_id}
**Purpose**: Retrieve analysis results for a specific analysis ID

#### Route
```
GET /results/{analysis_id}
```

#### Path Parameters
- **analysis_id** (required): UUID of the analysis to retrieve

#### Response Formats

**Completed Analysis (200 OK):**
```json
{
  "status": "completed",
  "results": {
    "match_score": 85,
    "missing_skills": ["Python", "AWS", "Docker"],
    "recommendations": [
      "Add quantified achievements (e.g., 'Increased efficiency by 25%')",
      "Include relevant keywords from the job description",
      "Highlight specific technical skills and experience"
    ],
    "confidence_score": 92,
    "analysis_timestamp": "2025-06-29T10:35:00Z"
  }
}
```

**Processing Analysis (200 OK):**
```json
{
  "status": "processing",
  "message": "Analysis is currently being processed"
}
```

**Failed Analysis (200 OK):**
```json
{
  "status": "failed",
  "error": "Error description",
  "timestamp": "2025-06-29T10:35:00Z"
}
```

**Analysis Not Found (404 Not Found):**
```json
{
  "error": "Analysis not found"
}
```

#### Status Values
- **completed**: Analysis finished successfully with results
- **processing**: Analysis is queued or currently being processed
- **failed**: Analysis encountered an error

#### Results Object Fields
- **match_score**: Numerical score (0-100) indicating resume-job match
- **missing_skills**: Array of skills that could improve the match
- **recommendations**: Array of specific improvement suggestions
- **confidence_score**: Confidence level (0-100) in the analysis quality
- **analysis_timestamp**: ISO 8601 timestamp of when analysis completed

### GET /health
**Purpose**: System health check endpoint for monitoring

#### Route
```
GET /health
```

#### Response Formats

**Healthy System (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-29T10:00:00Z",
  "checks": {
    "dynamodb": {
      "status": "healthy",
      "message": "Connected successfully"
    },
    "s3": {
      "status": "healthy",
      "message": "Bucket accessible"
    },
    "environment": {
      "status": "healthy",
      "message": "All required variables present"
    }
  }
}
```

**Unhealthy System (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-06-29T10:00:00Z",
  "checks": {
    "dynamodb": {
      "status": "unhealthy",
      "message": "Connection timeout"
    },
    "s3": {
      "status": "healthy",
      "message": "Bucket accessible"
    },
    "environment": {
      "status": "healthy",
      "message": "All required variables present"
    }
  }
}
```

## Implementation Details

### Data Processing
The function transforms stored DynamoDB analysis results into the API specification format:

1. **Missing Skills Extraction**: Uses regex patterns to identify missing skills from analysis text
2. **Recommendations Parsing**: Extracts actionable recommendations from analysis content
3. **Confidence Scoring**: Calculates confidence based on match score, analysis quality, and type (mock vs real)

### Health Checks
The health endpoint performs the following checks:
- **DynamoDB**: Verifies table connectivity and accessibility
- **S3**: Confirms bucket exists and is accessible
- **Environment**: Validates required environment variables are present

### Error Handling
- Comprehensive error handling for all failure scenarios
- Proper HTTP status codes for different error types
- CORS headers included in all responses
- Detailed error messages for debugging

## Environment Variables

### Required
- `TRACKING_TABLE`: DynamoDB table name for analysis tracking
- `RAW_INPUTS_BUCKET`: S3 bucket name for storing input files

### Inherited from Globals
- `BEDROCK_REGION`: AWS region for Bedrock services

## IAM Permissions

### Required Policies
- **DynamoDBReadPolicy**: Read access to the analysis tracking table
- **S3ReadPolicy**: Read access to the raw inputs bucket (for health checks)

### Specific Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:DescribeTable"
      ],
      "Resource": "arn:aws:dynamodb:region:account:table/NextFitAI-AnalysisTracking-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:HeadBucket"
      ],
      "Resource": "arn:aws:s3:::nextfitai-raw-inputs-*"
    }
  ]
}
```

## Usage Examples

### cURL Examples

**Get Analysis Results:**
```bash
curl -X GET https://your-api-gateway-url.com/prod/results/123e4567-e89b-12d3-a456-426614174000
```

**Health Check:**
```bash
curl -X GET https://your-api-gateway-url.com/prod/health
```

### Python Examples

**Get Analysis Results:**
```python
import requests

analysis_id = "123e4567-e89b-12d3-a456-426614174000"
response = requests.get(f"https://your-api-gateway-url.com/prod/results/{analysis_id}")

if response.status_code == 200:
    data = response.json()
    if data['status'] == 'completed':
        print(f"Match Score: {data['results']['match_score']}")
        print(f"Missing Skills: {data['results']['missing_skills']}")
    else:
        print(f"Status: {data['status']}")
else:
    print(f"Error: {response.status_code}")
```

**Health Check:**
```python
import requests

response = requests.get("https://your-api-gateway-url.com/prod/health")
data = response.json()

print(f"System Status: {data['status']}")
if data['status'] != 'healthy':
    for check_name, check_result in data['checks'].items():
        if check_result['status'] != 'healthy':
            print(f"Issue with {check_name}: {check_result['message']}")
```

### JavaScript/Frontend Examples

**Get Analysis Results:**
```javascript
async function getAnalysisResults(analysisId) {
  try {
    const response = await fetch(`/api/results/${analysisId}`);
    const data = await response.json();
    
    if (data.status === 'completed') {
      return {
        matchScore: data.results.match_score,
        missingSkills: data.results.missing_skills,
        recommendations: data.results.recommendations,
        confidence: data.results.confidence_score
      };
    } else {
      return { status: data.status, message: data.message };
    }
  } catch (error) {
    console.error('Error fetching analysis:', error);
    return { error: 'Failed to fetch analysis' };
  }
}
```

## Monitoring & Debugging

### CloudWatch Logs
- **Log Group**: `/aws/lambda/NextFitAI-GetAnalysis-prod`
- **Key Metrics**: Response times, error rates, health check failures

### Common Issues

1. **Analysis Not Found (404)**
   - Verify analysis_id is correct
   - Check if analysis was successfully submitted
   - Confirm DynamoDB table contains the record

2. **Health Check Failures (503)**
   - Check DynamoDB table permissions and connectivity
   - Verify S3 bucket exists and is accessible
   - Confirm environment variables are properly set

3. **Timeout Errors**
   - Monitor Lambda execution duration
   - Check DynamoDB and S3 response times
   - Consider increasing Lambda timeout if needed

### Performance Optimization
- **Cold Start**: ~2-5 seconds for first invocation
- **Warm Execution**: ~100-500ms for subsequent calls
- **Health Check**: Optimized for fast response (~200ms)

## Integration with Frontend

### Polling Pattern
```javascript
async function pollAnalysisResults(analysisId, maxAttempts = 30) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const result = await getAnalysisResults(analysisId);
    
    if (result.status === 'completed' || result.status === 'failed') {
      return result;
    }
    
    // Wait 2 seconds before next poll
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error('Analysis timeout - please try again');
}
```

### Error Handling
```javascript
function handleAnalysisError(error) {
  if (error.status === 404) {
    return 'Analysis not found. Please submit a new analysis.';
  } else if (error.status === 503) {
    return 'System temporarily unavailable. Please try again later.';
  } else {
    return 'An unexpected error occurred. Please contact support.';
  }
}
```

## Related Components
- **SubmitAnalysisFunction**: Creates analyses that this function retrieves
- **ProcessAnalysisFunction**: Processes analyses and stores results
- **Monitor Utility**: `utilities/monitor_analysis_status.py` provides similar functionality via CLI
