# AWS Console Testing Guide - Redshift DDM Automation

## Prerequisites
- AWS Account with Redshift access
- Redshift cluster running
- IAM permissions for Lambda, CloudWatch Events, and Redshift Data API

## Step 1: Setup Redshift Environment

### 1.1 Connect to Redshift Query Editor
1. Go to AWS Console → Amazon Redshift
2. Click "Query data" → "Query in query editor v2"
3. Connect to your cluster

### 1.2 Run Initial Setup
Execute the following SQL in Query Editor:

```sql
-- Create customer table
CREATE TABLE customer (
    customer_id INT,
    e_mail TEXT,
    SSN TEXT
);

-- Insert test data
INSERT INTO customer VALUES
(100,'customer1@abc.com', '111-11-1111'),
(101,'customer2@xyz.com', '222-22-2222'),
(102,'customer3@abcxyz.com', '333-33-3333');

-- Create users and roles
CREATE USER analyst_user WITH PASSWORD '1234Test!';
CREATE USER admin_user WITH PASSWORD '1234Test!';
CREATE USER regular_user WITH PASSWORD '1234Test!';
CREATE ROLE analyst_role;
CREATE ROLE admin_role;

-- Grant roles
GRANT ROLE analyst_role TO analyst_user;
GRANT ROLE admin_role TO admin_user;
GRANT SELECT ON customer TO PUBLIC;
```

## Step 2: Deploy Lambda Function

### 2.1 Create Lambda Function
1. Go to AWS Console → Lambda
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: `redshift-masking-automation`
5. Runtime: Python 3.9
6. Click "Create function"

### 2.2 Upload Code
1. In Lambda console, go to "Code" tab
2. Delete default code
3. Copy and paste content from `lambda_trigger.py`
4. Create new file `redshift_masking_automation.py`
5. Copy and paste content from `redshift_masking_automation.py`
6. Click "Deploy"

### 2.3 Configure Environment Variables
1. Go to "Configuration" → "Environment variables"
2. Add:
   - `CLUSTER_IDENTIFIER`: your-cluster-name
   - `DATABASE_NAME`: your-database-name

### 2.4 Update IAM Role
1. Go to "Configuration" → "Permissions"
2. Click on execution role
3. Add policy with Redshift Data API permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "redshift-data:*",
                "redshift:DescribeClusters"
            ],
            "Resource": "*"
        }
    ]
}
```

## Step 3: Test Automation Detection

### 3.1 Manual Lambda Test
1. In Lambda console, click "Test"
2. Create new test event:
```json
{
    "cluster_identifier": "your-cluster-name",
    "database": "your-database-name",
    "schema": "public"
}
```
3. Click "Test"
4. Check execution results for detected sensitive columns

### 3.2 Verify Detection Results
Expected output should show:
```json
{
    "customer": [
        {"column": "e_mail", "type": "email"},
        {"column": "SSN", "type": "ssn"}
    ]
}
```

## Step 4: Add New Sensitive Column

### 4.1 Add Phone Column
In Redshift Query Editor:
```sql
ALTER TABLE customer ADD COLUMN phone_number TEXT;
UPDATE customer SET phone_number = '555-123-4567' WHERE customer_id = 100;
UPDATE customer SET phone_number = '555-987-6543' WHERE customer_id = 101;
```

### 4.2 Trigger Automation
1. Run Lambda test again
2. Verify `phone_number` is detected as sensitive

## Step 5: Test Masking Policies

### 5.1 Create Manual Masking Policies
In Redshift Query Editor:
```sql
-- Create masking function
CREATE OR REPLACE FUNCTION REDACT_SSN (ssn TEXT)
RETURNS TEXT IMMUTABLE
AS $$
    import re
    vSSN = ''.join(re.findall(r'\d+',ssn ))
    if len(vSSN)==9:
        rtn_val = 'xxx-xx-' + vSSN[5:9]
    else:
        rtn_val='invalid ssn'
    return rtn_val
$$ LANGUAGE plpythonu;

-- Create masking policies
CREATE MASKING POLICY mask_ssn_full
WITH (SSN VARCHAR(256))
USING ('XXX-XX-XXXX'::text);

ATTACH MASKING POLICY mask_ssn_full
ON customer(SSN)
TO PUBLIC;

CREATE MASKING POLICY ssn_partial_mask
WITH (SSN VARCHAR(256))
USING (REDACT_SSN(SSN));

ATTACH MASKING POLICY ssn_partial_mask
ON customer(SSN)
TO ROLE analyst_role
PRIORITY 10;
```

### 5.2 Test Masking
```sql
-- Test as regular user (should see XXX-XX-XXXX)
SET SESSION AUTHORIZATION regular_user;
SELECT * FROM customer LIMIT 1;

-- Test as analyst (should see xxx-xx-1111)
SET SESSION AUTHORIZATION analyst_user;
SELECT * FROM customer LIMIT 1;

-- Reset
SET SESSION AUTHORIZATION default;
```

## Step 6: Setup CloudWatch Events (Optional)

### 6.1 Create EventBridge Rule
1. Go to AWS Console → EventBridge
2. Click "Create rule"
3. Name: `redshift-schema-changes`
4. Event pattern:
```json
{
    "source": ["aws.redshift"],
    "detail-type": ["Redshift Cluster State Change"]
}
```
5. Target: Lambda function `redshift-masking-automation`

## Step 7: Verify System Views

### 7.1 Check Masking Policies
```sql
-- View all masking policies
SELECT * FROM svv_masking_policy;

-- View attached policies
SELECT * FROM svv_attached_masking_policy;
```

## Expected Results

1. **Detection**: Automation identifies `e_mail`, `SSN`, and `phone_number` as sensitive
2. **Masking**: Different users see different levels of data masking
3. **Automation**: New sensitive columns trigger automatic policy creation

## Troubleshooting

- **Lambda timeout**: Increase timeout in Configuration → General configuration
- **Permission errors**: Check IAM roles have Redshift Data API access
- **Query failures**: Verify cluster is running and accessible
- **Masking not working**: Check policy priorities and user roles