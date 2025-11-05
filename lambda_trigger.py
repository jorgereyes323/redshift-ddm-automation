import json
import boto3
from redshift_masking_automation import RedshiftMaskingAutomator

def lambda_handler(event, context):
    """Lambda function to trigger masking when schema changes detected"""
    
    # Extract cluster info from event
    cluster_identifier = event.get('cluster_identifier')
    database = event.get('database')
    schema = event.get('schema', 'public')
    
    if not cluster_identifier or not database:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required parameters')
        }
    
    try:
        # Initialize automator
        automator = RedshiftMaskingAutomator(cluster_identifier)
        
        # Apply masking policies
        sensitive_columns = automator.apply_automated_masking(database, schema)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Masking policies applied successfully',
                'sensitive_columns': sensitive_columns
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }