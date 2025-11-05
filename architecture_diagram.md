# Architecture Diagram

## Redshift Dynamic Data Masking Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Schema Change │    │  CloudWatch      │    │  Lambda         │
│   Detection     │───▶│  Events          │───▶│  Function       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Redshift      │◀───│  Column Scan &   │◀───│  Masking        │
│   Cluster       │    │  Pattern Match   │    │  Automation     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RLS Policies  │    │  Sensitive Data  │    │  Masking Rules  │
│   Applied       │    │  Identified      │    │  Generated      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Component Details

### 1. Schema Change Detection
- Monitors Redshift for new columns
- Triggers on DDL operations (ALTER TABLE, CREATE TABLE)

### 2. CloudWatch Events
- Captures Redshift cluster state changes
- Routes events to Lambda function

### 3. Lambda Function
- Executes masking automation
- Scans new columns for sensitive patterns
- Applies appropriate masking policies

### 4. Column Scanning
- Pattern matching against column names
- Identifies: email, phone, SSN, credit card, names, addresses

### 5. Masking Policy Application
- Creates RLS policies with masking expressions
- Applies dynamic masking based on user context

## Data Flow

1. **New Column Added** → Schema change detected
2. **Event Triggered** → CloudWatch captures change
3. **Lambda Invoked** → Automation script executes
4. **Pattern Matching** → Identifies sensitive columns
5. **Policy Creation** → RLS masking policies applied
6. **Data Protected** → Sensitive data automatically masked

## Security Benefits

- **Automatic Protection**: No manual intervention required
- **Real-time Masking**: Immediate protection for new sensitive data
- **Role-based Access**: Different masking rules per user role
- **Audit Trail**: All masking activities logged