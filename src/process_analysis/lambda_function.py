import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Purpose: Process the resume analysis using Bedrock Agent
    - Retrieve resume and job description from S3
    - Call Bedrock Agent for analysis
    - Update DynamoDB with results
    """
    try:
        analysis_id = event['analysis_id']
        
        # Get S3 and DynamoDB clients
        s3_client = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['TRACKING_TABLE'])
        bucket_name = os.environ['RAW_INPUTS_BUCKET']
        
        # Update status to PROCESSING
        table.update_item(
            Key={'analysis_id': analysis_id},
            UpdateExpression='SET #status = :status, processing_timestamp = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'PROCESSING',
                ':timestamp': datetime.now().isoformat()
            }
        )
        
        # Retrieve resume and job description from S3
        try:
            resume_response = s3_client.get_object(
                Bucket=bucket_name,
                Key=f"raw-inputs/{analysis_id}/resume.txt"
            )
            resume_text = resume_response['Body'].read().decode('utf-8')
            
            jd_response = s3_client.get_object(
                Bucket=bucket_name,
                Key=f"raw-inputs/{analysis_id}/job_description.txt"
            )
            job_description = jd_response['Body'].read().decode('utf-8')
            
        except Exception as e:
            # Update status to FAILED
            table.update_item(
                Key={'analysis_id': analysis_id},
                UpdateExpression='SET #status = :status, error_message = :error, completion_timestamp = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'FAILED',
                    ':error': f"Failed to retrieve input files: {str(e)}",
                    ':timestamp': datetime.now().isoformat()
                }
            )
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Failed to retrieve input files: {str(e)}'})
            }
        
        # Process with Bedrock Agent (if agent IDs are not placeholders)
        bedrock_agent_id = os.environ.get('BEDROCK_AGENT_ID', 'PLACEHOLDER_AGENT_ID')
        bedrock_agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
        
        if bedrock_agent_id != 'PLACEHOLDER_AGENT_ID' and bedrock_agent_alias_id != 'TSTALIASID':
            try:
                analysis_result = invoke_bedrock_agent(
                    resume_text, 
                    job_description, 
                    bedrock_agent_id, 
                    bedrock_agent_alias_id
                )
            except Exception as e:
                # Update status to FAILED
                table.update_item(
                    Key={'analysis_id': analysis_id},
                    UpdateExpression='SET #status = :status, error_message = :error, completion_timestamp = :timestamp',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'FAILED',
                        ':error': f"Bedrock Agent error: {str(e)}",
                        ':timestamp': datetime.now().isoformat()
                    }
                )
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f'Bedrock Agent error: {str(e)}'})
                }
        else:
            # Mock analysis for testing when Bedrock Agent is not configured
            analysis_result = generate_mock_analysis(resume_text, job_description)
        
        # Update DynamoDB with results
        table.update_item(
            Key={'analysis_id': analysis_id},
            UpdateExpression='SET #status = :status, analysis_result = :result, completion_timestamp = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'COMPLETED',
                ':result': analysis_result,
                ':timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'completed',
                'analysis_id': analysis_id,
                'result': analysis_result
            })
        }
        
    except Exception as e:
        # Update status to FAILED if possible
        try:
            table.update_item(
                Key={'analysis_id': analysis_id},
                UpdateExpression='SET #status = :status, error_message = :error, completion_timestamp = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'FAILED',
                    ':error': str(e),
                    ':timestamp': datetime.now().isoformat()
                }
            )
        except:
            pass  # If we can't update the table, at least return the error
            
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def invoke_bedrock_agent(resume_text, job_description, agent_id, agent_alias_id):
    """
    Invoke Bedrock Agent for resume analysis
    """
    bedrock_agent_client = boto3.client('bedrock-agent-runtime')
    
    prompt = f"""
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
    """
    
    response = bedrock_agent_client.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=f"session-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        inputText=prompt
    )
    
    # Process the response
    result = ""
    for event in response['completion']:
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                result += chunk['bytes'].decode('utf-8')
    
    return {
        'match_score': extract_match_score(result),
        'analysis': result,
        'timestamp': datetime.now().isoformat()
    }

def generate_mock_analysis(resume_text, job_description):
    """
    Generate a mock analysis for testing purposes when Bedrock Agent is not configured
    """
    # Simple keyword matching for mock score
    resume_words = set(resume_text.lower().split())
    jd_words = set(job_description.lower().split())
    common_words = resume_words.intersection(jd_words)
    mock_score = min(100, len(common_words) * 5)  # Simple scoring
    
    return {
        'match_score': mock_score,
        'analysis': f"""
        MOCK ANALYSIS (Bedrock Agent not configured):
        
        Match Score: {mock_score}/100
        
        Key Strengths:
        - Found {len(common_words)} matching keywords between resume and job description
        - Resume demonstrates relevant experience
        
        Areas for Improvement:
        - Configure Bedrock Agent for detailed AI-powered analysis
        - Update BedrockAgentId and BedrockAgentAliasId parameters
        
        Recommendations:
        - This is a mock analysis. Configure AWS Bedrock Agent for real AI-powered resume coaching.
        - Common keywords found: {', '.join(list(common_words)[:10])}
        """,
        'timestamp': datetime.now().isoformat(),
        'is_mock': True
    }

def extract_match_score(analysis_text):
    """
    Extract match score from analysis text
    """
    import re
    
    # Look for patterns like "Match score: 85" or "Score: 85/100"
    patterns = [
        r'match score[:\s]+(\d+)',
        r'score[:\s]+(\d+)',
        r'(\d+)/100',
        r'(\d+)%'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis_text.lower())
        if match:
            return int(match.group(1))
    
    return 75  # Default score if not found
