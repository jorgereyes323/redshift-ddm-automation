-- MUST RUN THIS FIRST as superuser (awsuser) in Redshift Query Editor

CREATE USER "IAM:redshift-masking-automation-role-sxo4h3gr" PASSWORD DISABLE;
GRANT ROLE sys:secadmin TO "IAM:redshift-masking-automation-role-sxo4h3gr";
GRANT USAGE ON DATABASE dev TO "IAM:redshift-masking-automation-role-sxo4h3gr";
GRANT USAGE ON SCHEMA public TO "IAM:redshift-masking-automation-role-sxo4h3gr";
GRANT SELECT ON information_schema.columns TO "IAM:redshift-masking-automation-role-sxo4h3gr";
GRANT SELECT ON pg_user TO "IAM:redshift-masking-automation-role-sxo4h3gr";