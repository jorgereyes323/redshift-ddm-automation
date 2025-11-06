# Architecture Diagram

## Redshift DDM Automation Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Manual/Event │    │  Lambda Function │    │  IAM Role with  │
│   Trigger       │───▶│  Invocation      │───▶│  Superuser      │
└─────────────────┘    └──────────────────┘    │  Permissions    │
                                               └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Redshift      │◀───│  Column Scan &   │◀───│  DDM Automation │
│   Cluster       │    │  Pattern Match   │    │  Engine         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DDM Policies  │    │  Sensitive Data  │    │  SQL Commands   │
│   Created &     │    │  Identified      │    │  Auto-Executed  │
│   Applied       │    │                  │    │  as awsuser     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Component Details

### 1. Lambda Function Trigger
- Manual invocation or event-driven
- Receives cluster, database, and schema parameters
- Uses IAM role with superuser permissions

### 2. DDM Automation Engine
- Scans information_schema.columns for sensitive patterns
- Generates DDM policies for multiple roles
- Automatically executes SQL using awsuser superuser

### 3. Column Pattern Matching
- Regex patterns for: email, phone, SSN, credit card, names, addresses
- Configurable sensitivity detection rules
- Supports custom pattern addition

### 4. Role-Based Masking
- **Public**: Full masking (***MASKED***)
- **Analyst Role**: Partial masking (partial visibility)
- **Admin Role**: No masking (full access)

### 5. Automatic SQL Execution
- Creates DDM policies using CREATE MASKING POLICY
- Attaches policies using ATTACH MASKING POLICY
- Executes as awsuser with superuser privileges

## Data Flow

1. **Lambda Invoked** → Function receives parameters
2. **Column Scanning** → Queries information_schema for columns
3. **Pattern Matching** → Identifies sensitive columns by name patterns
4. **Policy Generation** → Creates DDM SQL commands for each role
5. **Automatic Execution** → Executes SQL as awsuser superuser
6. **Policy Application** → DDM policies created and attached
7. **Response** → Returns success with policy count

## Security Benefits

- **Automatic DDM**: Creates masking policies without manual SQL execution
- **Role-based Masking**: Different protection levels per user role
- **Superuser Execution**: Uses awsuser for privileged operations
- **Pattern-based Detection**: Automatically identifies sensitive data
- **Immediate Protection**: Policies applied instantly upon detection
- **Audit Trail**: All operations logged in Lambda CloudWatch logs

## Prerequisites

- Lambda execution role with `redshift:GetClusterCredentials` permission
- Redshift cluster with awsuser superuser account
- Python 3.9+ runtime environment