import json
import boto3
from redshift_masking_automation import RedshiftMaskingAutomator

def lambda_handler(event, context):
    """Lambda function to trigger masking when schema changes detected"""
    
    print(f"Received event: {json.dumps(event)}")
    
    # Extract cluster info from event
    cluster_identifier = event.get('cluster_identifier', 'daab-redshift-cluster-jr-bedrock')
    database = event.get('database', 'dev')
    schema = event.get('schema', 'public')
    
    if not cluster_identifier or not database:
        missing = []
        if not cluster_identifier:
            missing.append('cluster_identifier')
        if not database:
            missing.append('database')
        
        return {
            'statusCode': 400,
            'body': json.dumps(f'Missing required parameters: {", ".join(missing)}')
        }
    
    try:
        # Initialize automator
        automator = RedshiftMaskingAutomator(cluster_identifier)
        
        # Apply masking policies
        result = automator.apply_automated_masking(database, schema)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }