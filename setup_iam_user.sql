-- Run this as superuser (awsuser) in Redshift to set up IAM role permissions

-- Create IAM user in Redshift
CREATE USER "IAM:redshift-masking-automation-role-sxo4h3gr" PASSWORD DISABLE;

-- Grant sys:secadmin role for masking policy creation
GRANT ROLE sys:secadmin TO "IAM:redshift-masking-automation-role-sxo4h3gr";

-- Grant basic database access
GRANT USAGE ON DATABASE dev TO "IAM:redshift-masking-automation-role-sxo4h3gr";
GRANT USAGE ON SCHEMA public TO "IAM:redshift-masking-automation-role-sxo4h3gr";

-- Grant permissions to read schema information
GRANT SELECT ON information_schema.columns TO "IAM:redshift-masking-automation-role-sxo4h3gr";
GRANT SELECT ON pg_user TO "IAM:redshift-masking-automation-role-sxo4h3gr";

-- Verify the user was created
SELECT usename, usesuper FROM pg_user WHERE usename LIKE '%redshift-masking%';