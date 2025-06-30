# Lambda Functions

## Overview
This directory contains all AWS Lambda functions for the NextFitAI backend serverless architecture.

## Functions

### submit_analysis/
- **Purpose**: Handles initial resume submission requests
- **Route**: POST /analyze
- **Trigger**: API Gateway
- **Runtime**: Python 3.11

### process_analysis/
- **Purpose**: Processes resume analysis using AWS Bedrock Agent
- **Trigger**: Asynchronous invocation from SubmitAnalysisFunction
- **Runtime**: Python 3.11

## Environment Variables

All Lambda functions have access to these environment variables:

- `TRACKING_TABLE`: DynamoDB table name for analysis tracking
- `RAW_INPUTS_BUCKET`: S3 bucket name for storing raw inputs
- `BEDROCK_REGION`: AWS region for Bedrock services
- `PROCESS_FUNCTION`: Name of the ProcessAnalysis function (SubmitAnalysis only)
- `BEDROCK_AGENT_ID`: Bedrock Agent ID for AI analysis (ProcessAnalysis only)
- `BEDROCK_AGENT_ALIAS_ID`: Bedrock Agent Alias ID (ProcessAnalysis only)

## Architecture Flow

1. **Client** → POST /analyze → **SubmitAnalysisFunction**
2. **SubmitAnalysisFunction** → Store in S3 & DynamoDB → Invoke **ProcessAnalysisFunction**
3. **ProcessAnalysisFunction** → Retrieve from S3 → Call Bedrock Agent → Update DynamoDB

## Deployment

Functions are deployed using AWS SAM:
```bash
sam build
sam deploy
```

## Monitoring

- CloudWatch Logs: `/aws/lambda/NextFitAI-SubmitAnalysis-prod`
- CloudWatch Logs: `/aws/lambda/NextFitAI-ProcessAnalysis-prod`
- DynamoDB Table: `NextFitAI-AnalysisTracking-prod`
- S3 Bucket: `nextfitai-raw-inputs-<account-id>-prod`
