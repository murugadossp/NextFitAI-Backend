# NextFitAI Backend - AWS Lambda Deployment

A serverless backend for NextFitAI, an AI-powered resume coaching application built with AWS Lambda, API Gateway, DynamoDB, and S3.

## 🚀 Architecture

The application consists of two main Lambda functions:

1. **SubmitAnalysisFunction** - Handles initial resume submission
   - Validates input data
   - Stores resume and job description in S3
   - Creates tracking record in DynamoDB
   - Triggers ProcessAnalysisFunction asynchronously

2. **ProcessAnalysisFunction** - Processes the resume analysis
   - Retrieves data from S3
   - Calls AWS Bedrock Agent for AI analysis (or mock analysis)
   - Updates DynamoDB with results

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

## 🧪 Testing

### 1. Test API Endpoint
```bash
python test_api.py
```

### 2. Check Analysis Status
```bash
# List recent analyses
python check_analysis_status.py

# Check specific analysis
python check_analysis_status.py <analysis_id>
```

### 3. Example Test Flow
```bash
# Submit analysis
python test_api.py

# Wait a few seconds, then check status
python check_analysis_status.py <analysis_id_from_previous_step>
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
├── src/
│   ├── submit_analysis/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── process_analysis/
│       ├── lambda_function.py
│       └── requirements.txt
├── template.yaml              # SAM template
├── samconfig.toml             # SAM configuration
├── test_api.py               # API testing script
├── check_analysis_status.py  # Status checking script
└── README.md                 # This file
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
