# Monitoring & Utility Scripts

## Overview
This directory contains monitoring and utility scripts for the NextFitAI backend. These tools help with operational monitoring, debugging, and maintenance tasks.

## Available Utilities

### monitor_analysis_status.py
**Purpose**: Monitor and check the status of resume analysis requests
**Type**: Monitoring/Debugging Tool

#### Usage
```bash
# List recent analyses (default: 5 most recent)
python utilities/monitor_analysis_status.py

# Check specific analysis by ID
python utilities/monitor_analysis_status.py <analysis_id>
```

#### What it does
- **Direct DynamoDB Access**: Queries the tracking table directly
- **Status Monitoring**: Shows current status (SUBMITTED, PROCESSING, COMPLETED, FAILED)
- **Timeline Tracking**: Displays timestamps for each stage
- **Result Display**: Shows analysis results including match scores and feedback
- **Error Reporting**: Displays error messages for failed analyses

#### Output Examples

**List Recent Analyses:**
```
Recent 5 analyses:
- e204a2f3-7dd0-4554-b4f6-5f89d39f34cc: COMPLETED (2025-06-30T01:47:03.557427)
- 6651d8b7-b3bf-47b0-b365-2f528483ce23: COMPLETED (2025-06-30T01:45:39.946391)
- abc123def-4567-89ab-cdef-123456789012: FAILED (2025-06-29T15:30:22.123456)
```

**Specific Analysis Details:**
```
Analysis ID: e204a2f3-7dd0-4554-b4f6-5f89d39f34cc
Status: COMPLETED
Submitted: 2025-06-30T01:47:03.557427
Processing Started: 2025-06-30T01:47:03.705831
Completed: 2025-06-30T01:47:03.820980

Analysis Result:
Match Score: 30
Analysis: MOCK ANALYSIS (Bedrock Agent not configured):
        Match Score: 30/100
        Key Strengths: Found 6 matching keywords...
Note: This is a mock analysis (Bedrock Agent not configured)
```

#### Requirements
- **AWS Credentials**: Must be configured with access to DynamoDB
- **DynamoDB Access**: Read permissions on `NextFitAI-AnalysisTracking-prod` table
- **Python Packages**: `boto3` (included in requirements)

#### Use Cases
- **Development**: Check if submitted analyses are processing correctly
- **Debugging**: Identify failed analyses and error messages
- **Operations**: Monitor system health and processing times
- **Customer Support**: Check status of specific user requests

## Future Utilities (Planned)

### cleanup_old_analyses.py
**Purpose**: Clean up old analysis data to manage storage costs
**Features**:
- Remove analyses older than specified days
- Clean up corresponding S3 files
- Maintain audit trail of deletions

### bulk_test_data.py
**Purpose**: Generate bulk test data for performance testing
**Features**:
- Create multiple test analyses
- Simulate various resume/job description combinations
- Load testing data generation

### performance_monitor.py
**Purpose**: Monitor system performance metrics
**Features**:
- Track average processing times
- Monitor error rates
- Generate performance reports

### data_migration.py
**Purpose**: Handle data migrations and schema updates
**Features**:
- Migrate data between DynamoDB table versions
- Update data formats when schema changes
- Backup and restore capabilities

## Common Usage Patterns

### Development Workflow
```bash
# 1. Submit test analysis
python tests/test_submit_analysis_api.py

# 2. Monitor processing (wait a few seconds)
python utilities/monitor_analysis_status.py

# 3. Check specific result
python utilities/monitor_analysis_status.py <analysis_id_from_step_1>
```

### Debugging Failed Analyses
```bash
# 1. List recent analyses to find failures
python utilities/monitor_analysis_status.py

# 2. Check specific failed analysis
python utilities/monitor_analysis_status.py <failed_analysis_id>

# 3. Check CloudWatch logs for detailed errors
# (Use AWS Console or AWS CLI)
```

### Operational Monitoring
```bash
# Regular health check - run every few minutes
python utilities/monitor_analysis_status.py

# Look for:
# - Recent FAILED statuses
# - Analyses stuck in PROCESSING
# - Unusual processing times
```

## Configuration

### AWS Region
The utilities are configured for `us-east-1` region. To use in different regions:
1. Update the `region_name` parameter in the utility scripts
2. Or set the `AWS_DEFAULT_REGION` environment variable

### DynamoDB Table Name
Currently hardcoded to `NextFitAI-AnalysisTracking-prod`. For different environments:
1. Update the table name in the utility scripts
2. Or add environment variable support

## Error Handling

### Common Errors and Solutions

**1. AWS Credentials Not Found**
```
Error: Unable to locate credentials
```
**Solution**: Configure AWS credentials using `aws configure`

**2. DynamoDB Access Denied**
```
Error: User is not authorized to perform: dynamodb:Scan
```
**Solution**: Ensure your AWS user/role has DynamoDB read permissions

**3. Table Not Found**
```
Error: Requested resource not found
```
**Solution**: Verify the DynamoDB table exists and the name is correct

**4. Network/Connection Issues**
```
Error: Unable to connect to DynamoDB
```
**Solution**: Check internet connectivity and AWS service status

## Best Practices

### Security
- Use IAM roles with minimal required permissions
- Avoid hardcoding credentials in scripts
- Use AWS profiles for different environments

### Performance
- Use pagination for large result sets
- Implement caching for frequently accessed data
- Add rate limiting to avoid throttling

### Monitoring
- Log utility usage for audit trails
- Set up alerts for critical failures
- Monitor utility execution times

### Maintenance
- Regularly update utility scripts
- Test utilities after AWS resource changes
- Document any custom modifications

## Integration with Other Tools

### CloudWatch Integration
```bash
# View Lambda logs
aws logs tail /aws/lambda/NextFitAI-SubmitAnalysis-prod --follow

# View specific log group
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/NextFitAI"
```

### AWS CLI Integration
```bash
# Direct DynamoDB query
aws dynamodb scan --table-name NextFitAI-AnalysisTracking-prod --max-items 5

# S3 bucket contents
aws s3 ls s3://nextfitai-raw-inputs-898240539132-prod/raw-inputs/
```

### Automation Integration
The utilities can be integrated into:
- CI/CD pipelines for automated testing
- Monitoring systems for health checks
- Scheduled tasks for maintenance operations
- Alert systems for failure notifications
