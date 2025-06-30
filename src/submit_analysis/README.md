# Submit Analysis API

## Route
**POST** `/analyze`

## Purpose
Initial ingestion and processing kickoff for resume analysis requests. This function handles the first step of the resume analysis workflow.

## API Endpoint
```
POST https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze
```

## Input Schema
```json
{
  "analysis_id": "string (UUID)",
  "resume_text": "string (required)",
  "job_description": "string (required)"
}
```

### Input Parameters
- **analysis_id**: Unique identifier for the analysis request (UUID format)
- **resume_text**: Complete resume content as plain text
- **job_description**: Job description to match against the resume

### Input Validation
- Both `resume_text` and `job_description` are required
- Empty strings will result in 400 Bad Request
- Maximum recommended length: 10,000 characters each

## Output Schema
```json
{
  "status": "submitted",
  "analysis_id": "string (UUID)",
  "estimated_completion": "string (ISO 8601 timestamp)"
}
```

### Response Fields
- **status**: Always "submitted" for successful requests
- **analysis_id**: Echo of the input analysis_id
- **estimated_completion**: Estimated completion time (typically 30 seconds from submission)

## HTTP Status Codes
- **202 Accepted**: Analysis successfully submitted for processing
- **400 Bad Request**: Missing or invalid input parameters
- **500 Internal Server Error**: Server-side processing error

## Error Response Format
```json
{
  "error": "Error description string"
}
```

## Process Flow
1. **Input Validation**: Validates required fields
2. **S3 Storage**: Stores resume and job description in separate S3 objects
   - `raw-inputs/{analysis_id}/resume.txt`
   - `raw-inputs/{analysis_id}/job_description.txt`
3. **DynamoDB Tracking**: Creates tracking record with status "SUBMITTED"
4. **Async Processing**: Triggers ProcessAnalysisFunction asynchronously
5. **Response**: Returns 202 with tracking information

## Environment Variables Used
- `RAW_INPUTS_BUCKET`: S3 bucket for storing input files
- `TRACKING_TABLE`: DynamoDB table for analysis tracking
- `PROCESS_FUNCTION`: Name of the ProcessAnalysis function to invoke

## IAM Permissions Required
- S3: `s3:PutObject` on the raw inputs bucket
- DynamoDB: `dynamodb:PutItem` on the tracking table
- Lambda: `lambda:InvokeFunction` on the ProcessAnalysis function

## Example Usage

### cURL
```bash
curl -X POST https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
    "resume_text": "John Doe, Software Engineer...",
    "job_description": "Seeking a Software Engineer..."
  }'
```

### Python
```python
import requests
import json
import uuid

response = requests.post(
    "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "analysis_id": str(uuid.uuid4()),
        "resume_text": "Your resume content here...",
        "job_description": "Job description here..."
    })
)
```

## Monitoring & Debugging
- **CloudWatch Logs**: `/aws/lambda/NextFitAI-SubmitAnalysis-prod`
- **DynamoDB**: Check `NextFitAI-AnalysisTracking-prod` table for tracking records
- **S3**: Verify files are created in `nextfitai-raw-inputs-*-prod` bucket

## Related Functions
- **ProcessAnalysisFunction**: Invoked asynchronously to process the analysis
- **Monitor Utility**: Use `utilities/monitor_analysis_status.py` to check progress
