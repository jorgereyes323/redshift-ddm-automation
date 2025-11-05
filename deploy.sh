#!/bin/bash

# Deploy Redshift Masking Automation

CLUSTER_IDENTIFIER=$1
DATABASE_NAME=$2

if [ -z "$CLUSTER_IDENTIFIER" ] || [ -z "$DATABASE_NAME" ]; then
    echo "Usage: ./deploy.sh <cluster-identifier> <database-name>"
    exit 1
fi

# Package Lambda function
zip -r masking-lambda.zip redshift_masking_automation.py lambda_trigger.py

# Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file cloudformation_template.yaml \
    --stack-name redshift-masking-automation \
    --parameter-overrides \
        RedshiftClusterIdentifier=$CLUSTER_IDENTIFIER \
        DatabaseName=$DATABASE_NAME \
    --capabilities CAPABILITY_IAM

# Update Lambda function code
aws lambda update-function-code \
    --function-name redshift-masking-automation \
    --zip-file fileb://masking-lambda.zip

echo "Deployment complete!"