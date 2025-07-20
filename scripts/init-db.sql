-- ABOUTME: Database initialization script for PostgreSQL
-- ABOUTME: Creates necessary extensions and initial schema setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create database if it doesn't exist (this runs after database creation)
-- The main database is created by POSTGRES_DB environment variable

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON DATABASE snowflake_mcp TO snowflake_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO snowflake_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO snowflake_user;
