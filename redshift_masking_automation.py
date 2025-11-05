import boto3
import json
import re
from typing import Dict, List

class RedshiftMaskingAutomator:
    def __init__(self, cluster_identifier: str, region: str = 'us-east-1'):
        self.cluster_identifier = cluster_identifier
        self.redshift_data = boto3.client('redshift-data', region_name=region)
        
        self.sensitive_patterns = {
            'email': r'.*email.*|.*mail.*',
            'phone': r'.*phone.*|.*mobile.*|.*tel.*',
            'ssn': r'.*ssn.*|.*social.*security.*',
            'credit_card': r'.*card.*|.*cc.*|.*credit.*',
            'name': r'.*name.*|.*first.*|.*last.*',
            'address': r'.*address.*|.*addr.*|.*street.*'
        }
        
        self.masking_policies = {
            'email': "REGEXP_REPLACE({column}, '@.*', '@*****.com')",
            'phone': "REGEXP_REPLACE({column}, '.', '*')",
            'ssn': "CONCAT('***-**-', RIGHT({column}, 4))",
            'credit_card': "CONCAT('****-****-****-', RIGHT({column}, 4))",
            'name': "CONCAT(LEFT({column}, 1), REPEAT('*', LENGTH({column})-1))",
            'address': "'***MASKED***'"
        }

    def scan_new_columns(self, database: str, schema: str = 'public') -> Dict[str, List[str]]:
        """Scan for new columns and identify sensitive ones"""
        query = f"""
        SELECT table_name, column_name
        FROM information_schema.columns 
        WHERE table_schema = '{schema}'
        """
        
        response = self.redshift_data.execute_statement(
            ClusterIdentifier=self.cluster_identifier,
            Database=database,
            Sql=query
        )
        
        self._wait_for_query(response['Id'])
        result = self.redshift_data.get_statement_result(Id=response['Id'])
        
        sensitive_columns = {}
        for record in result['Records']:
            table_name = record[0]['stringValue']
            column_name = record[1]['stringValue']
            
            for sensitivity_type, pattern in self.sensitive_patterns.items():
                if re.match(pattern, column_name.lower()):
                    if table_name not in sensitive_columns:
                        sensitive_columns[table_name] = []
                    sensitive_columns[table_name].append({
                        'column': column_name,
                        'type': sensitivity_type
                    })
                    break
        
        return sensitive_columns

    def create_masking_policy(self, database: str, table_name: str, column_name: str, sensitivity_type: str, schema: str = 'public'):
        """Create masking policy for a specific column"""
        policy_name = f"mask_{table_name}_{column_name}"
        masking_expr = self.masking_policies[sensitivity_type].format(column=column_name)
        
        # Create masking policy
        policy_sql = f"""
        CREATE MASKING POLICY {policy_name} 
        WITH (column_name = '{column_name}') 
        USING ({masking_expr})
        """
        
        try:
            response = self.redshift_data.execute_statement(
                ClusterIdentifier=self.cluster_identifier,
                Database=database,
                Sql=policy_sql
            )
            self._wait_for_query(response['Id'])
            print(f"Created masking policy: {policy_name}")
            return policy_name
        except Exception as e:
            print(f"Error creating policy {policy_name}: {e}")
            return None

    def attach_policy_to_users(self, database: str, policy_name: str, table_name: str, column_name: str, users: List[str], schema: str = 'public'):
        """Attach masking policy to specific users"""
        for user in users:
            attach_sql = f"""
            ATTACH MASKING POLICY {policy_name} 
            ON {schema}.{table_name}({column_name}) 
            TO USER {user}
            """
            
            try:
                response = self.redshift_data.execute_statement(
                    ClusterIdentifier=self.cluster_identifier,
                    Database=database,
                    Sql=attach_sql
                )
                self._wait_for_query(response['Id'])
                print(f"Attached policy {policy_name} to user {user}")
            except Exception as e:
                print(f"Error attaching policy to user {user}: {e}")

    def get_database_users(self, database: str) -> List[str]:
        """Get list of database users"""
        query = "SELECT usename FROM pg_user WHERE usename != 'rdsdb'"
        
        try:
            response = self.redshift_data.execute_statement(
                ClusterIdentifier=self.cluster_identifier,
                Database=database,
                Sql=query
            )
            self._wait_for_query(response['Id'])
            result = self.redshift_data.get_statement_result(Id=response['Id'])
            
            users = [record[0]['stringValue'] for record in result['Records']]
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def apply_automated_masking(self, database: str, schema: str = 'public', target_users: List[str] = None):
        """Main automation method"""
        sensitive_columns = self.scan_new_columns(database, schema)
        
        # Get users if not provided
        if target_users is None:
            target_users = self.get_database_users(database)
        
        for table_name, columns in sensitive_columns.items():
            for col_info in columns:
                policy_name = self.create_masking_policy(
                    database, table_name, 
                    col_info['column'], col_info['type'], schema
                )
                
                if policy_name and target_users:
                    self.attach_policy_to_users(
                        database, policy_name, table_name, 
                        col_info['column'], target_users, schema
                    )
        
        return sensitive_columns

    def _wait_for_query(self, query_id: str, max_wait_time: int = 30):
        """Wait for query completion with timeout"""
        import time
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            response = self.redshift_data.describe_statement(Id=query_id)
            if response['Status'] == 'FINISHED':
                break
            elif response['Status'] == 'FAILED':
                raise Exception(f"Query failed: {response.get('Error')}")
            time.sleep(0.5)  # Reduced sleep time
        else:
            raise Exception(f"Query timed out after {max_wait_time} seconds")

if __name__ == "__main__":
    automator = RedshiftMaskingAutomator('your-cluster')
    result = automator.apply_automated_masking('your-database')
    print(json.dumps(result, indent=2))