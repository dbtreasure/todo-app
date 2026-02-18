-- PostgreSQL: Create a read-only role for Claude Code database access.
-- Run this as a database administrator.

-- Create the role
CREATE ROLE claude_readonly WITH LOGIN PASSWORD 'change-this-password';

-- Grant connect privilege
GRANT CONNECT ON DATABASE todoDb TO claude_readonly;

-- Grant usage on the public schema
GRANT USAGE ON SCHEMA public TO claude_readonly;

-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_readonly;

-- Grant SELECT on all existing sequences
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO claude_readonly;

-- Automatically grant SELECT on any new tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO claude_readonly;

-- Verify: list grants for the role
-- \du claude_readonly
-- \dp

-- Connection string for .env:
-- DATABASE_URL=postgresql://claude_readonly:change-this-password@localhost:5432/todoDb
