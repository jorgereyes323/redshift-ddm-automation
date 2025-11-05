# Redshift Dynamic Data Masking Automation

Automated solution for detecting and masking sensitive data in Amazon Redshift when new columns are added.

## Features

- **Automatic Detection**: Identifies sensitive columns using pattern matching
- **Dynamic Masking**: Applies RLS policies with masking expressions
- **Event-Driven**: Triggers on schema changes via CloudWatch Events
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

1. **Deploy Infrastructure**:
   ```bash
   ./deploy.sh your-cluster-name your-database-name
   ```

2. **Manual Execution**:
   ```python
   from redshift_masking_automation import RedshiftMaskingAutomator
   
   automator = RedshiftMaskingAutomator('your-cluster')
   result = automator.apply_automated_masking('your-database')
   ```

## Files

- `redshift_masking_automation.py` - Core automation logic
- `lambda_trigger.py` - AWS Lambda function
- `cloudformation_template.yaml` - Infrastructure template
- `deploy.sh` - Deployment script
- `requirements.txt` - Python dependencies

## Architecture

See `architecture_diagram.md` for visual representation of the solution flow.