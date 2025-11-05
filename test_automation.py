import boto3
import json
from redshift_masking_automation import RedshiftMaskingAutomator

class DDMTestAutomation:
    def __init__(self, cluster_identifier: str, database: str, region: str = 'us-east-1'):
        self.cluster_identifier = cluster_identifier
        self.database = database
        self.redshift_data = boto3.client('redshift-data', region_name=region)
        self.automator = RedshiftMaskingAutomator(cluster_identifier, region)

    def setup_test_environment(self):
        """Setup test tables and users from notebook"""
        setup_queries = [
            # Create customer table
            """
            CREATE TABLE IF NOT EXISTS customer (
                customer_id INT,
                e_mail TEXT,
                SSN TEXT
            )
            """,
            
            # Insert test data
            """
            INSERT INTO customer VALUES
            (100,'customer1@abc.com', '111-11-1111'),
            (101,'customer2@xyz.com', '222-22-2222'),
            (102,'customer3@abcxyz.com', '333-33-3333'),
            (103,'customer4@abc123.com', '444-44-4444'),
            (104,'customer5@axyz.com', '555-55-5555'),
            (105,'customer6@abc.com', '666-66-6666'),
            (106,'customer7abc.com', '666-66-6666')
            """,
            
            # Create users and roles
            "CREATE USER IF NOT EXISTS analyst_user WITH PASSWORD '1234Test!'",
            "CREATE USER IF NOT EXISTS admin_user WITH PASSWORD '1234Test!'",
            "CREATE USER IF NOT EXISTS regular_user WITH PASSWORD '1234Test!'",
            "CREATE ROLE IF NOT EXISTS analyst_role",
            "CREATE ROLE IF NOT EXISTS admin_role",
            
            # Grant roles
            "GRANT ROLE analyst_role TO analyst_user",
            "GRANT ROLE admin_role TO admin_user",
            "GRANT SELECT ON customer TO PUBLIC"
        ]
        
        for query in setup_queries:
            try:
                response = self.redshift_data.execute_statement(
                    ClusterIdentifier=self.cluster_identifier,
                    Database=self.database,
                    Sql=query
                )
                self.automator._wait_for_query(response['Id'])
                print(f"✓ Executed: {query[:50]}...")
            except Exception as e:
                print(f"✗ Error: {query[:50]}... - {e}")

    def create_masking_function(self):
        """Create the SSN masking function from notebook"""
        function_sql = """
        CREATE OR REPLACE FUNCTION REDACT_SSN (ssn TEXT)
        RETURNS TEXT IMMUTABLE
        AS $$
            import re
            vSSN = ''.join(re.findall(r'\\d+',ssn ))
            if len(vSSN)==9:
                rtn_val = 'xxx-xx-' + vSSN[5:9]
            else:
                rtn_val='invalid ssn'
            return rtn_val
        $$ LANGUAGE plpythonu
        """
        
        try:
            response = self.redshift_data.execute_statement(
                ClusterIdentifier=self.cluster_identifier,
                Database=self.database,
                Sql=function_sql
            )
            self.automator._wait_for_query(response['Id'])
            print("✓ Created REDACT_SSN function")
        except Exception as e:
            print(f"✗ Error creating function: {e}")

    def test_automation_detection(self):
        """Test if automation detects sensitive columns"""
        print("\n=== Testing Automation Detection ===")
        
        # Run automation
        sensitive_columns = self.automator.scan_new_columns(self.database)
        
        print(f"Detected sensitive columns: {json.dumps(sensitive_columns, indent=2)}")
        
        # Verify expected columns are detected
        expected_columns = ['e_mail', 'SSN']
        detected = sensitive_columns.get('customer', [])
        detected_names = [col['column'] for col in detected]
        
        for expected in expected_columns:
            if expected in detected_names:
                print(f"✓ Correctly detected: {expected}")
            else:
                print(f"✗ Missed detection: {expected}")

    def create_manual_masking_policies(self):
        """Create masking policies from notebook for comparison"""
        policies = [
            """
            CREATE MASKING POLICY mask_ssn_full
            WITH (SSN VARCHAR(256))
            USING ('XXX-XX-XXXX'::text)
            """,
            
            """
            ATTACH MASKING POLICY mask_ssn_full
            ON customer(SSN)
            TO PUBLIC
            """,
            
            """
            CREATE MASKING POLICY ssn_partial_mask
            WITH (SSN VARCHAR(256))
            USING (REDACT_SSN(SSN))
            """,
            
            """
            ATTACH MASKING POLICY ssn_partial_mask
            ON customer(SSN)
            TO ROLE analyst_role
            PRIORITY 10
            """,
            
            """
            CREATE MASKING POLICY raw_ssn
            WITH (SSN varchar(256))
            USING (SSN)
            """,
            
            """
            ATTACH MASKING POLICY raw_ssn
            ON customer(SSN)
            TO ROLE admin_role
            PRIORITY 20
            """
        ]
        
        print("\n=== Creating Manual Masking Policies ===")
        for policy in policies:
            try:
                response = self.redshift_data.execute_statement(
                    ClusterIdentifier=self.cluster_identifier,
                    Database=self.database,
                    Sql=policy
                )
                self.automator._wait_for_query(response['Id'])
                print(f"✓ Created policy: {policy.split()[2] if len(policy.split()) > 2 else 'policy'}")
            except Exception as e:
                print(f"✗ Error: {e}")

    def test_masking_effectiveness(self):
        """Test masking policies work correctly"""
        print("\n=== Testing Masking Effectiveness ===")
        
        test_queries = [
            ("Public user", "SET SESSION AUTHORIZATION regular_user; SELECT * FROM customer LIMIT 1"),
            ("Analyst user", "SET SESSION AUTHORIZATION analyst_user; SELECT * FROM customer LIMIT 1"),
            ("Admin user", "SET SESSION AUTHORIZATION admin_user; SELECT * FROM customer LIMIT 1"),
            ("Reset", "SET SESSION AUTHORIZATION default")
        ]
        
        for user_type, query in test_queries:
            try:
                response = self.redshift_data.execute_statement(
                    ClusterIdentifier=self.cluster_identifier,
                    Database=self.database,
                    Sql=query
                )
                self.automator._wait_for_query(response['Id'])
                
                if "SELECT" in query:
                    result = self.redshift_data.get_statement_result(Id=response['Id'])
                    print(f"✓ {user_type}: Query executed successfully")
                    if result.get('Records'):
                        ssn_value = result['Records'][0][2]['stringValue'] if len(result['Records'][0]) > 2 else 'N/A'
                        print(f"  SSN shown as: {ssn_value}")
                else:
                    print(f"✓ {user_type}: Session set")
                    
            except Exception as e:
                print(f"✗ {user_type}: {e}")

    def run_full_test(self):
        """Run complete test suite"""
        print("Starting DDM Automation Test Suite")
        print("=" * 50)
        
        self.setup_test_environment()
        self.create_masking_function()
        self.test_automation_detection()
        self.create_manual_masking_policies()
        self.test_masking_effectiveness()
        
        print("\n" + "=" * 50)
        print("Test Suite Complete")

if __name__ == "__main__":
    # Configure your cluster details
    tester = DDMTestAutomation(
        cluster_identifier='your-redshift-cluster',
        database='your-database'
    )
    
    tester.run_full_test()