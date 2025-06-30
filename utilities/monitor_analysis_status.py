import boto3
import json
from datetime import datetime

def check_analysis_status(analysis_id):
    """
    Check the status of an analysis by querying DynamoDB directly
    """
    try:
        # Initialize DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('NextFitAI-AnalysisTracking-prod')
        
        # Get the analysis record
        response = table.get_item(
            Key={'analysis_id': analysis_id}
        )
        
        if 'Item' in response:
            item = response['Item']
            print(f"Analysis ID: {analysis_id}")
            print(f"Status: {item.get('status', 'Unknown')}")
            print(f"Submitted: {item.get('timestamp', 'Unknown')}")
            
            if 'processing_timestamp' in item:
                print(f"Processing Started: {item['processing_timestamp']}")
            
            if 'completion_timestamp' in item:
                print(f"Completed: {item['completion_timestamp']}")
            
            if 'error_message' in item:
                print(f"Error: {item['error_message']}")
            
            if 'analysis_result' in item:
                result = item['analysis_result']
                print(f"\nAnalysis Result:")
                print(f"Match Score: {result.get('match_score', 'N/A')}")
                print(f"Analysis: {result.get('analysis', 'N/A')}")
                if result.get('is_mock'):
                    print("Note: This is a mock analysis (Bedrock Agent not configured)")
            
            return item
        else:
            print(f"No analysis found with ID: {analysis_id}")
            return None
            
    except Exception as e:
        print(f"Error checking analysis status: {str(e)}")
        return None

def list_recent_analyses(limit=5):
    """
    List recent analyses from DynamoDB
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('NextFitAI-AnalysisTracking-prod')
        
        # Scan the table (note: in production, you'd want to use a GSI with timestamp)
        response = table.scan(
            Limit=limit
        )
        
        if 'Items' in response and response['Items']:
            print(f"Recent {len(response['Items'])} analyses:")
            for item in response['Items']:
                print(f"- {item['analysis_id']}: {item.get('status', 'Unknown')} ({item.get('timestamp', 'Unknown')})")
            return response['Items']
        else:
            print("No analyses found")
            return []
            
    except Exception as e:
        print(f"Error listing analyses: {str(e)}")
        return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Check specific analysis ID
        analysis_id = sys.argv[1]
        check_analysis_status(analysis_id)
    else:
        # List recent analyses
        print("Recent analyses:")
        analyses = list_recent_analyses()
        
        if analyses:
            print("\nTo check a specific analysis, run:")
            print("python check_analysis_status.py <analysis_id>")
