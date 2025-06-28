-- ABOUTME: Database initialization script for Snowflake MCP Lambda production deployment
-- ABOUTME: Creates necessary extensions, users, and basic security configurations

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create application database if it doesn't exist
-- Note: This is handled by POSTGRES_DB environment variable

-- Create read-only user for monitoring
CREATE USER readonly_user WITH PASSWORD 'readonly_password_change_me';
GRANT CONNECT ON DATABASE snowflake_mcp TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;

-- Create monitoring views
CREATE OR REPLACE VIEW pg_stat_activity_custom AS
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    waiting,
    LEFT(query, 100) as query_snippet
FROM pg_stat_activity
WHERE state != 'idle';

-- Grant access to monitoring views
GRANT SELECT ON pg_stat_activity_custom TO readonly_user;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully at %', NOW();
END $$;
