-- Development database initialization script
-- This script sets up additional development-specific configurations

-- Enable useful extensions for development
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create additional development schemas if needed
-- CREATE SCHEMA IF NOT EXISTS dev_testing;

-- Set up development-specific configurations
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';
ALTER SYSTEM SET log_min_duration_statement = 0;

-- Reload configuration
SELECT pg_reload_conf();

-- Create development user with limited privileges (optional)
-- DO $$
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dev_user') THEN
--         CREATE ROLE dev_user WITH LOGIN PASSWORD 'dev_password';
--         GRANT CONNECT ON DATABASE chatbot_db_dev TO dev_user;
--         GRANT USAGE ON SCHEMA public TO dev_user;
--         GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dev_user;
--         GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dev_user;
--     END IF;
-- END
-- $$;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Development database initialized successfully';
END
$$;