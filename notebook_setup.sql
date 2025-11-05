-- DDM Test Setup from Notebook
-- This SQL script recreates the notebook environment for testing

-- 1. Create customer table
DROP TABLE IF EXISTS public.customer;

CREATE TABLE customer (
    customer_id INT,
    e_mail TEXT,
    SSN TEXT
);

-- 2. Insert test data
INSERT INTO customer VALUES
(100,'customer1@abc.com', '111-11-1111'),
(101,'customer2@xyz.com', '222-22-2222'),
(102,'customer3@abcxyz.com', '333-33-3333'),
(103,'customer4@abc123.com', '444-44-4444'),
(104,'customer5@axyz.com', '555-55-5555'),
(105,'customer6@abc.com', '666-66-6666'),
(106,'customer7abc.com', '666-66-6666');

-- 3. Create users
CREATE USER analyst_user WITH PASSWORD '1234Test!';
CREATE USER admin_user WITH PASSWORD '1234Test!';
CREATE USER regular_user WITH PASSWORD '1234Test!';

-- 4. Create roles
CREATE ROLE analyst_role;
CREATE ROLE admin_role;

-- 5. Grant roles to users
GRANT ROLE analyst_role TO analyst_user;
GRANT ROLE admin_role TO admin_user;

-- 6. Grant table permissions
GRANT SELECT ON customer TO PUBLIC;

-- 7. Create masking function
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

-- 8. Create masking policies
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

CREATE MASKING POLICY raw_ssn
WITH (SSN varchar(256))
USING (SSN);

ATTACH MASKING POLICY raw_ssn
ON customer(SSN)
TO ROLE admin_role
PRIORITY 20;