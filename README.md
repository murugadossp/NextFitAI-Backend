# NextFitAI Backend - AWS Lambda Deployment

A serverless backend for NextFitAI, an AI-powered resume coaching application built with AWS Lambda, API Gateway, DynamoDB, and S3.

## 🚀 Architecture

The application consists of three main Lambda functions:

1. **SubmitAnalysisFunction** - Handles initial resume submission
   - Validates input data
   - Stores resume and job description in S3
   - Creates tracking record in DynamoDB
   - Triggers ProcessAnalysisFunction asynchronously

2. **ProcessAnalysisFunction** - Processes the resume analysis
   - Retrieves data from S3
   - Calls AWS Bedrock Agent for AI analysis (or mock analysis)
   - Updates DynamoDB with results

3. **GetAnalysisFunction** - Retrieves analysis results and system health
   - Provides API access to analysis results
   - Handles health check monitoring
   - Formats results according to API specification

## 📋 Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Python 3.11+
- Valid AWS account with permissions for Lambda, API Gateway, DynamoDB, S3, and IAM

## 🛠️ Deployment

### 1. Clone and Setup
```bash
git clone <your-repo>
cd NextFitAI-Backend
```

### 2. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### 3. Build and Deploy
```bash
# Build the application
sam build

# Deploy to AWS
sam deploy
```

The deployment will create:
- API Gateway endpoint
- Two Lambda functions
- DynamoDB table for tracking
- S3 bucket for storing resumes/job descriptions
- IAM roles and policies

## 🔧 Configuration

### Environment Variables
The following environment variables are automatically configured:
- `TRACKING_TABLE` - DynamoDB table name
- `RAW_INPUTS_BUCKET` - S3 bucket name
- `PROCESS_FUNCTION` - ProcessAnalysis function name
- `BEDROCK_AGENT_ID` - Bedrock Agent ID (configurable)
- `BEDROCK_AGENT_ALIAS_ID` - Bedrock Agent Alias ID (configurable)

### Bedrock Agent Configuration
To enable real AI analysis instead of mock analysis:
1. Create a Bedrock Agent in AWS Console
2. Update the parameters in `samconfig.toml`:
   ```toml
   parameter_overrides = "Environment=\"prod\" BedrockAgentId=\"YOUR_AGENT_ID\" BedrockAgentAliasId=\"YOUR_ALIAS_ID\""
   ```
3. Redeploy: `sam build && sam deploy`

## 📡 API Endpoints

### POST /analyze
Submit a resume for analysis.

**Request Body:**
```json
{
  "analysis_id": "unique-uuid",
  "resume_text": "Your resume content here...",
  "job_description": "Job description content here..."
}
```

**Response:**
```json
{
  "status": "submitted",
  "analysis_id": "unique-uuid",
  "estimated_completion": "2025-06-30T01:46:10.063857"
}
```

### GET /results/{analysis_id}
Retrieve analysis results for a specific analysis.

**Response (Completed):**
```json
{
  "status": "completed",
  "results": {
    "match_score": 85,
    "missing_skills": ["Python", "AWS", "Docker"],
    "recommendations": [
      "Add quantified achievements (e.g., 'Increased efficiency by 25%')",
      "Include relevant keywords from the job description"
    ],
    "confidence_score": 92,
    "analysis_timestamp": "2025-06-29T10:35:00Z"
  }
}
```

**Response (Processing):**
```json
{
  "status": "processing",
  "message": "Analysis is currently being processed"
}
```

### GET /health
System health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-29T10:00:00Z",
  "checks": {
    "dynamodb": {"status": "healthy", "message": "Connected successfully"},
    "s3": {"status": "healthy", "message": "Bucket accessible"},
    "environment": {"status": "healthy", "message": "All required variables present"}
  }
}
```

## 🧪 Testing

### 1. Test Submit Analysis API
```bash
python tests/test_submit_analysis_api.py
```

### 2. Test Get Analysis API
```bash
python tests/test_get_analysis_api.py
```

### 3. Check Analysis Status (CLI)
```bash
# List recent analyses
python utilities/monitor_analysis_status.py

# Check specific analysis
python utilities/monitor_analysis_status.py <analysis_id>
```

### 4. Complete Test Flow
```bash
# Submit analysis
python tests/test_submit_analysis_api.py

# Test retrieval endpoints
python tests/test_get_analysis_api.py

# Monitor via CLI utility
python utilities/monitor_analysis_status.py <analysis_id_from_step_1>
```

## 💻 Frontend Integration

### For Frontend Developers

**📖 Complete Integration Guide**: [`docs/FRONTEND_API_GUIDE.md`](docs/FRONTEND_API_GUIDE.md)
- React hooks and components
- TypeScript definitions
- Error handling patterns
- Caching strategies
- Testing examples

**🧪 Interactive API Tester**: [`docs/api-test-example.html`](docs/api-test-example.html)
- Open in browser to test API endpoints
- Pre-filled with sample data
- Real-time health monitoring
- Complete workflow demonstration

### Quick Frontend Examples

**Submit Analysis (JavaScript)**:
```javascript
const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    analysis_id: crypto.randomUUID(),
    resume_text: "Your resume here...",
    job_description: "Job description here..."
  })
});
```

**Get Results (JavaScript)**:
```javascript
const response = await fetch(`https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/results/${analysisId}`);
const data = await response.json();
```

**Health Check (JavaScript)**:
```javascript
const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/health');
const health = await response.json();
```

## 📊 Monitoring

### CloudWatch Logs
- Function logs: `/aws/lambda/NextFitAI-SubmitAnalysis-prod`
- Function logs: `/aws/lambda/NextFitAI-ProcessAnalysis-prod`

### DynamoDB Table
- Table name: `NextFitAI-AnalysisTracking-prod`
- Primary key: `analysis_id`

### S3 Bucket
- Bucket name: `nextfitai-raw-inputs-<account-id>-prod`
- Structure: `raw-inputs/<analysis_id>/resume.txt` and `job_description.txt`

## 🔍 Troubleshooting

### Common Issues

1. **InvalidClientTokenId Error**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Reconfigure if needed
   aws configure
   ```

2. **Lambda Permission Errors**
   - Ensure IAM policies are correctly configured in `template.yaml`
   - Redeploy after making changes

3. **S3 Access Errors**
   - Check bucket permissions
   - Verify bucket name in environment variables

### Debugging Steps
1. Check CloudWatch logs for detailed error messages
2. Verify all resources are created in AWS Console
3. Test individual functions using AWS Console
4. Use `sam local invoke` for local testing

## 📁 Project Structure

```
NextFitAI-Backend/
├── src/                       # Lambda functions
│   ├── README.md             # Lambda functions overview
│   ├── submit_analysis/
│   │   ├── lambda_function.py
│   │   ├── requirements.txt
│   │   └── README.md         # Submit Analysis API docs
│   ├── process_analysis/
│   │   ├── lambda_function.py
│   │   ├── requirements.txt
│   │   └── README.md         # Process Analysis function docs
│   └── get_analysis/
│       ├── lambda_function.py
│       ├── requirements.txt
│       └── README.md         # Get Analysis API docs
├── tests/                     # API testing suite
│   ├── README.md             # Testing guide and documentation
│   ├── test_submit_analysis_api.py
│   ├── test_get_analysis_api.py
│   └── __init__.py
├── utilities/                 # Monitoring and utility scripts
│   ├── README.md             # Utilities documentation
│   ├── monitor_analysis_status.py
│   └── __init__.py
├── docs/                      # Frontend integration documentation
│   ├── FRONTEND_API_GUIDE.md # Complete frontend integration guide
│   └── api-test-example.html # Interactive API test page
├── design_docs/              # Architecture documentation
├── template.yaml             # SAM template
├── samconfig.toml            # SAM configuration
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🚀 Deployment Information

**Current Deployment:**
- API Gateway URL: `https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod`
- Region: `us-east-1`
- Environment: `prod`

## 🔄 Updates and Maintenance

### Making Changes
1. Modify code in `src/` directories
2. Update `template.yaml` if needed
3. Build and deploy:
   ```bash
   sam build
   sam deploy
   ```

### Monitoring Costs
- Lambda: Pay per request and execution time
- API Gateway: Pay per API call
- DynamoDB: Pay per request (on-demand billing)
- S3: Pay for storage and requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
