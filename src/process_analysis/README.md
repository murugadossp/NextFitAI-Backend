# Process Analysis Function

## Purpose
Processes resume analysis using AWS Bedrock Agent (or mock analysis when not configured). This function is invoked asynchronously by the SubmitAnalysisFunction.

## Trigger
- **Type**: Asynchronous Lambda invocation
- **Invoked by**: SubmitAnalysisFunction
- **Runtime**: Python 3.11

## Input Schema
```json
{
  "analysis_id": "string (UUID)"
}
```

### Input Parameters
- **analysis_id**: Unique identifier for the analysis to process

## Output Schema
```json
{
  "statusCode": 200,
  "body": {
    "status": "completed",
    "analysis_id": "string (UUID)",
    "result": {
      "match_score": "number (0-100)",
      "analysis": "string (detailed analysis)",
      "timestamp": "string (ISO 8601)",
      "is_mock": "boolean (optional)"
    }
  }
}
```

## Process Flow
1. **Status Update**: Updates DynamoDB status to "PROCESSING"
2. **Data Retrieval**: Retrieves resume and job description from S3
3. **AI Analysis**: 
   - If Bedrock Agent configured: Calls AWS Bedrock Agent
   - If not configured: Generates mock analysis with keyword matching
4. **Result Storage**: Updates DynamoDB with analysis results and status "COMPLETED"
5. **Error Handling**: Updates status to "FAILED" if any step fails

## Analysis Types

### Real AI Analysis (Bedrock Agent)
When `BEDROCK_AGENT_ID` and `BEDROCK_AGENT_ALIAS_ID` are properly configured:
- Uses AWS Bedrock Agent for sophisticated AI analysis
- Provides detailed feedback on resume-job match
- Includes specific recommendations and improvements

### Mock Analysis (Fallback)
When Bedrock Agent is not configured:
- Performs simple keyword matching between resume and job description
- Calculates basic match score based on common keywords
- Provides placeholder analysis with configuration instructions

## Environment Variables Used
- `TRACKING_TABLE`: DynamoDB table for analysis tracking
- `RAW_INPUTS_BUCKET`: S3 bucket containing input files
- `BEDROCK_AGENT_ID`: Bedrock Agent ID (optional, defaults to placeholder)
- `BEDROCK_AGENT_ALIAS_ID`: Bedrock Agent Alias ID (optional, defaults to placeholder)

## IAM Permissions Required
- S3: `s3:GetObject` on the raw inputs bucket
- DynamoDB: `dynamodb:UpdateItem` on the tracking table
- Bedrock: `bedrock:InvokeAgent` (when using real AI analysis)

## DynamoDB Status Tracking

The function updates the analysis record through these states:

1. **SUBMITTED** → **PROCESSING** (when function starts)
2. **PROCESSING** → **COMPLETED** (successful analysis)
3. **PROCESSING** → **FAILED** (error occurred)

### DynamoDB Record Structure
```json
{
  "analysis_id": "uuid",
  "status": "COMPLETED",
  "timestamp": "2025-06-30T01:45:39.946391",
  "processing_timestamp": "2025-06-30T01:45:41.460594",
  "completion_timestamp": "2025-06-30T01:45:41.595008",
  "resume_s3_path": "raw-inputs/{analysis_id}/resume.txt",
  "jd_s3_path": "raw-inputs/{analysis_id}/job_description.txt",
  "analysis_result": {
    "match_score": 85,
    "analysis": "Detailed analysis text...",
    "timestamp": "2025-06-30T01:45:41.595008",
    "is_mock": false
  }
}
```

## Error Handling

### Common Error Scenarios
1. **S3 Access Errors**: Input files not found or access denied
2. **Bedrock Errors**: Agent not found or access denied
3. **DynamoDB Errors**: Table access issues

### Error Response Format
```json
{
  "statusCode": 500,
  "body": {
    "error": "Error description"
  }
}
```

## Bedrock Agent Configuration

### Setting Up Real AI Analysis
1. Create a Bedrock Agent in AWS Console
2. Configure the agent for resume analysis tasks
3. Update deployment parameters:
   ```toml
   parameter_overrides = "BedrockAgentId=\"YOUR_AGENT_ID\" BedrockAgentAliasId=\"YOUR_ALIAS_ID\""
   ```
4. Redeploy: `sam build && sam deploy`

### Bedrock Agent Prompt Template
The function sends this prompt structure to Bedrock:
```
Please analyze the following resume against the job description and provide detailed feedback:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide:
1. Match score (0-100)
2. Key strengths that align with the job
3. Areas for improvement
4. Missing skills or qualifications
5. Specific recommendations for improvement
```

## Mock Analysis Details

When Bedrock is not configured, the function provides:
- **Keyword Matching**: Finds common words between resume and job description
- **Basic Scoring**: Score = min(100, common_keywords_count * 5)
- **Helpful Feedback**: Instructions on configuring real AI analysis
- **Development Mode**: Clearly marked as mock analysis

## Monitoring & Debugging
- **CloudWatch Logs**: `/aws/lambda/NextFitAI-ProcessAnalysis-prod`
- **DynamoDB**: Monitor status changes in `NextFitAI-AnalysisTracking-prod`
- **S3**: Verify input files exist in `nextfitai-raw-inputs-*-prod`
- **Bedrock**: Check agent availability and permissions

## Performance Characteristics
- **Timeout**: 900 seconds (15 minutes)
- **Memory**: 1024 MB
- **Typical Execution**: 1-3 seconds for mock analysis, 10-30 seconds for Bedrock
- **Cold Start**: Additional 2-5 seconds for first invocation

## Related Components
- **SubmitAnalysisFunction**: Invokes this function asynchronously
- **Monitor Utility**: Use `utilities/monitor_analysis_status.py` to check results
- **DynamoDB Table**: Stores all analysis results and status updates
