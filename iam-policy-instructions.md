# IAM Policy Setup Instructions

## Required IAM Policy for Lambda Role

Add this policy to the Lambda execution role `redshift-masking-automation-role-sxo4h3gr`:

### Option 1: Specific Resources
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "redshift:GetClusterCredentials",
            "Resource": [
                "arn:aws:redshift:us-east-1:442483223120:dbuser:daab-redshift-cluster-jr-bedrock/awsuser",
                "arn:aws:redshift:us-east-1:442483223120:cluster:daab-redshift-cluster-jr-bedrock",
                "arn:aws:redshift:us-east-1:442483223120:dbname:daab-redshift-cluster-jr-bedrock/dev"
            ]
        }
    ]
}
```

### Option 2: Wildcard (Recommended)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "redshift:GetClusterCredentials",
            "Resource": "arn:aws:redshift:us-east-1:442483223120:*"
        }
    ]
}
```

## Steps to Add Policy

1. Go to AWS Console → IAM → Roles
2. Search for: `redshift-masking-automation-role-sxo4h3gr`
3. Click "Add permissions" → "Create inline policy"
4. Click "JSON" tab and paste one of the policies above
5. Name: `RedshiftSuperuserAccess`
6. Click "Create policy"

## Test
After adding the policy, test the Lambda function. It should now automatically execute SQL commands using the awsuser superuser account.