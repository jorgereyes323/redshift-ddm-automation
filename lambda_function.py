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
        
        # Get SQL commands and sensitive columns
        result = automator.apply_automated_masking(database, schema)
        
        if 'sql_commands' in result:
            # Execute SQL commands as superuser
            redshift_data = boto3.client('redshift-data')
            executed_commands = []
            
            for sql_command in result['sql_commands']:
                try:
                    response = redshift_data.execute_statement(
                        ClusterIdentifier=cluster_identifier,
                        Database=database,
                        DbUser='awsuser',
                        Sql=sql_command
                    )
                    
                    # Wait for completion
                    automator._wait_for_query(response['Id'])
                    executed_commands.append(sql_command)
                    
                except Exception as e:
                    print(f"Error executing SQL: {e}")
                    return {
                        'statusCode': 500,
                        'body': json.dumps({
                            'message': f'Error executing SQL: {str(e)}',
                            'executed_commands': executed_commands,
                            'failed_command': sql_command
                        })
                    }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Masking policies created and applied successfully',
                    'sensitive_columns': result['sensitive_columns'],
                    'executed_commands': len(executed_commands)
                })
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }