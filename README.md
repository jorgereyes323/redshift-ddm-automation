# Redshift Dynamic Data Masking Automation

Automated solution for detecting and masking sensitive data in Amazon Redshift using Dynamic Data Masking (DDM) policies.

## Features

- **Automatic Detection**: Identifies sensitive columns using pattern matching
- **Dynamic Masking**: Creates and applies DDM masking policies automatically
- **Superuser Execution**: Automatically executes SQL commands using awsuser superuser
- **Role-based Masking**: Different masking levels for public, analyst, and admin roles
- **Event-Driven**: Can be triggered manually or via events
- **Configurable**: Easy to add new sensitivity patterns and masking rules

## Supported Data Types

| Type | Pattern | Masking Example |
|------|---------|-----------------|
| Email | `*email*`, `*mail*` | `user@*****.com` |
| Phone | `*phone*`, `*mobile*` | `**********` |
| SSN | `*ssn*`, `*social*` | `***-**-1234` |
| Credit Card | `*card*`, `*cc*` | `****-****-****-1234` |
| Name | `*name*`, `*first*` | `J*****` |
| Address | `*address*`, `*addr*` | `***MASKED***` |

## Quick Start

1. **Setup IAM Permissions**:
   - Add the IAM policy from `iam-policy-instructions.md` to your Lambda role
   - This allows the Lambda to use awsuser superuser for DDM policy creation

2. **Deploy Lambda Function**:
   ```bash
   # Deploy using AWS CLI or console
   # Upload lambda_function.py and redshift_masking_automation.py
   ```

3. **Test Lambda Function**:
   ```json
   {
     "cluster_identifier": "daab-redshift-cluster-jr-bedrock",
     "database": "dev",
     "schema": "public"
   }
   ```

4. **Manual Execution**:
   ```python
   from redshift_masking_automation import RedshiftMaskingAutomator
   
   automator = RedshiftMaskingAutomator('your-cluster')
   result = automator.apply_automated_masking('your-database')
   ```

## Files

- `redshift_masking_automation.py` - Core DDM automation logic
- `lambda_function.py` - AWS Lambda function with automatic SQL execution
- `iam-policy-instructions.md` - Required IAM policy setup
- `run_this_first.sql` - Redshift user setup (if needed)
- `setup_iam_user.sql` - Alternative IAM user setup
- `requirements.txt` - Python dependencies
- `test_automation.py` - Test suite
- `notebook_setup.sql` - SQL setup script from Redshift notebook

## IAM Requirements

The Lambda execution role needs:
```json
{
    "Effect": "Allow",
    "Action": "redshift:GetClusterCredentials",
    "Resource": "arn:aws:redshift:us-east-1:442483223120:*"
}
```

See `iam-policy-instructions.md` for detailed setup instructions.

## How It Works

1. **Lambda Triggered**: Function receives cluster/database parameters
2. **Column Scanning**: Scans information_schema for sensitive column patterns
3. **Policy Generation**: Creates DDM policies for each role (public, analyst, admin)
4. **Automatic Execution**: Executes SQL commands using awsuser superuser
5. **Response**: Returns success status with created policies count

## Architecture

See `architecture_diagram.md` for visual representation of the solution flow.