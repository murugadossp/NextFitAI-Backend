import json
import boto3
import uuid
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Purpose: Initial ingestion and processing kickoff
    - Validate input data
    - Store resume/JD in S3
    - Create DynamoDB tracking record
    - Trigger ProcessAnalysisLambda asynchronously
    """
    try:
        body = json.loads(event['body'])
        analysis_id = body['analysis_id']
        resume_text = body['resume_text']
        job_description = body['job_description']

        # Input validation
        if not resume_text or not job_description:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Resume and job description are required'})
            }

        # Store in S3
        s3_client = boto3.client('s3')
        bucket_name = os.environ['RAW_INPUTS_BUCKET']

        # Store resume
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"raw-inputs/{analysis_id}/resume.txt",
            Body=resume_text.encode('utf-8'),
            ContentType='text/plain'
        )

        # Store job description
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"raw-inputs/{analysis_id}/job_description.txt",
            Body=job_description.encode('utf-8'),
            ContentType='text/plain'
        )

        # Track in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['TRACKING_TABLE'])
        table.put_item(
            Item={
                'analysis_id': analysis_id,
                'status': 'SUBMITTED',
                'timestamp': datetime.now().isoformat(),
                'resume_s3_path': f"raw-inputs/{analysis_id}/resume.txt",
                'jd_s3_path': f"raw-inputs/{analysis_id}/job_description.txt"
            }
        )

        # Trigger processing asynchronously
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
            FunctionName=os.environ['PROCESS_FUNCTION'],
            InvocationType='Event',
            Payload=json.dumps({'analysis_id': analysis_id})
        )

        return {
            'statusCode': 202,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'status': 'submitted',
                'analysis_id': analysis_id,
                'estimated_completion': get_estimated_completion()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_estimated_completion():
    """Estimate completion time (30 seconds from now)"""
    return (datetime.now() + timedelta(seconds=30)).isoformat()
