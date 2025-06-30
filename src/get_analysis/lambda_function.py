import json
import boto3
import os
import re
from datetime import datetime
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle DynamoDB Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """
    Handle GET requests for analysis results and health checks
    Routes:
    - GET /results/{analysis_id} - Get analysis results
    - GET /health - Health check endpoint
    """
    try:
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        
        # Add CORS headers to all responses
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
        
        if method == 'GET':
            if path.startswith('/results/'):
                return handle_get_results(event, context, cors_headers)
            elif path == '/health':
                return handle_health_check(event, context, cors_headers)
        
        # Handle unsupported routes
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Route not found'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

def handle_get_results(event, context, cors_headers):
    """
    Handle GET /results/{analysis_id}
    Returns analysis results in the specified format
    """
    try:
        # Extract analysis_id from path
        path_parameters = event.get('pathParameters', {})
        analysis_id = path_parameters.get('analysis_id') if path_parameters else None
        
        if not analysis_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'analysis_id is required'})
            }
        
        # Query DynamoDB for the analysis
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['TRACKING_TABLE'])
        
        response = table.get_item(
            Key={'analysis_id': analysis_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Analysis not found'})
            }
        
        item = response['Item']
        status = item.get('status', 'unknown')
        
        # Handle different status states
        if status == 'SUBMITTED':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'processing',
                    'message': 'Analysis is queued for processing'
                })
            }
        
        elif status == 'PROCESSING':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'processing',
                    'message': 'Analysis is currently being processed'
                })
            }
        
        elif status == 'FAILED':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'failed',
                    'error': item.get('error_message', 'Analysis failed'),
                    'timestamp': item.get('completion_timestamp', item.get('timestamp'))
                })
            }
        
        elif status == 'COMPLETED':
            # Process completed analysis
            analysis_result = item.get('analysis_result', {})
            
            # Extract and format the results
            formatted_results = format_analysis_results(analysis_result)
            
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'completed',
                    'results': formatted_results
                }, cls=DecimalEncoder)
            }
        
        else:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'unknown',
                    'message': f'Unknown status: {status}'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': f'Failed to retrieve analysis: {str(e)}'})
        }

def handle_health_check(event, context, cors_headers):
    """
    Handle GET /health
    Returns system health status
    """
    try:
        # Perform basic health checks
        health_status = perform_health_checks()
        
        if health_status['healthy']:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'checks': health_status['checks']
                })
            }
        else:
            return {
                'statusCode': 503,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'checks': health_status['checks']
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
        }

def format_analysis_results(analysis_result):
    """
    Format the stored analysis result to match the API specification
    """
    match_score = analysis_result.get('match_score', 0)
    analysis_text = analysis_result.get('analysis', '')
    timestamp = analysis_result.get('timestamp', datetime.now().isoformat())
    is_mock = analysis_result.get('is_mock', False)
    
    # Extract missing skills from analysis text
    missing_skills = extract_missing_skills(analysis_text)
    
    # Extract recommendations from analysis text
    recommendations = extract_recommendations(analysis_text)
    
    # Calculate confidence score
    confidence_score = calculate_confidence_score(analysis_result, match_score, is_mock)
    
    return {
        'match_score': match_score,
        'missing_skills': missing_skills,
        'recommendations': recommendations,
        'confidence_score': confidence_score,
        'analysis_timestamp': timestamp
    }

def extract_missing_skills(analysis_text):
    """
    Extract missing skills from the analysis text
    """
    missing_skills = []
    
    # Look for common skill patterns in the analysis
    skill_patterns = [
        r'missing[:\s]+([^.]+)',
        r'lacks?[:\s]+([^.]+)',
        r'should add[:\s]+([^.]+)',
        r'needs?[:\s]+([^.]+)',
        r'consider adding[:\s]+([^.]+)'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, analysis_text, re.IGNORECASE)
        for match in matches:
            # Clean up the match and extract individual skills
            skills = [skill.strip().strip('"\'') for skill in match.split(',')]
            missing_skills.extend(skills)
    
    # Common technical skills to look for
    common_skills = ['Python', 'AWS', 'Docker', 'Kubernetes', 'React', 'Node.js', 'SQL', 'Git', 'CI/CD', 'Agile']
    
    # If no specific missing skills found, infer from common skills not mentioned
    if not missing_skills and 'mock' in analysis_text.lower():
        # For mock analysis, suggest some common skills
        missing_skills = ['Python', 'AWS', 'Docker']
    
    # Remove duplicates and limit to reasonable number
    missing_skills = list(set(missing_skills))[:5]
    
    return missing_skills

def extract_recommendations(analysis_text):
    """
    Extract recommendations from the analysis text
    """
    recommendations = []
    
    # Look for recommendation patterns
    rec_patterns = [
        r'recommend[a-z]*[:\s]+([^.]+)',
        r'suggest[a-z]*[:\s]+([^.]+)',
        r'should[:\s]+([^.]+)',
        r'consider[:\s]+([^.]+)',
        r'improve[a-z]*[:\s]+([^.]+)'
    ]
    
    for pattern in rec_patterns:
        matches = re.findall(pattern, analysis_text, re.IGNORECASE)
        for match in matches:
            recommendation = match.strip().strip('"\'')
            if len(recommendation) > 10:  # Filter out very short matches
                recommendations.append(recommendation)
    
    # If no specific recommendations found, provide default ones
    if not recommendations:
        recommendations = [
            "Add quantified achievements (e.g., 'Increased efficiency by 25%')",
            "Include relevant keywords from the job description",
            "Highlight specific technical skills and experience",
            "Use action verbs to describe accomplishments",
            "Tailor resume content to match job requirements"
        ]
    
    # Limit to reasonable number
    return recommendations[:5]

def calculate_confidence_score(analysis_result, match_score, is_mock):
    """
    Calculate confidence score based on various factors
    """
    base_confidence = 70
    
    # Adjust based on match score
    if match_score >= 80:
        base_confidence += 20
    elif match_score >= 60:
        base_confidence += 10
    elif match_score >= 40:
        base_confidence += 5
    else:
        base_confidence -= 10
    
    # Reduce confidence for mock analysis
    if is_mock:
        base_confidence -= 30
    
    # Adjust based on analysis quality (length and detail)
    analysis_text = analysis_result.get('analysis', '')
    if len(analysis_text) > 500:
        base_confidence += 10
    elif len(analysis_text) < 100:
        base_confidence -= 15
    
    # Ensure confidence is within reasonable bounds
    confidence_score = max(10, min(95, base_confidence))
    
    return confidence_score

def perform_health_checks():
    """
    Perform basic health checks on system components
    """
    checks = {}
    overall_healthy = True
    
    # Check DynamoDB connectivity
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['TRACKING_TABLE'])
        # Simple operation to test connectivity
        table.meta.client.describe_table(TableName=os.environ['TRACKING_TABLE'])
        checks['dynamodb'] = {'status': 'healthy', 'message': 'Connected successfully'}
    except Exception as e:
        checks['dynamodb'] = {'status': 'unhealthy', 'message': str(e)}
        overall_healthy = False
    
    # Check S3 connectivity
    try:
        s3_client = boto3.client('s3')
        bucket_name = os.environ['RAW_INPUTS_BUCKET']
        s3_client.head_bucket(Bucket=bucket_name)
        checks['s3'] = {'status': 'healthy', 'message': 'Bucket accessible'}
    except Exception as e:
        checks['s3'] = {'status': 'unhealthy', 'message': str(e)}
        overall_healthy = False
    
    # Check environment variables
    required_env_vars = ['TRACKING_TABLE', 'RAW_INPUTS_BUCKET']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        checks['environment'] = {
            'status': 'unhealthy', 
            'message': f'Missing environment variables: {", ".join(missing_vars)}'
        }
        overall_healthy = False
    else:
        checks['environment'] = {'status': 'healthy', 'message': 'All required variables present'}
    
    return {
        'healthy': overall_healthy,
        'checks': checks
    }
