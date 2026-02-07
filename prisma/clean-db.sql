

-- Drops all tables, migrations, and enum types


-- Drop all the tables
DROP TABLE IF EXISTS pool_fees CASCADE;
DROP TABLE IF EXISTS pool_liquidity CASCADE;
DROP TABLE IF EXISTS pool_swaps CASCADE;
DROP TABLE IF EXISTS stablecoin_cex_flows CASCADE;
DROP TABLE IF EXISTS stablecoin_transfers CASCADE;
DROP TABLE IF EXISTS decoded_events CASCADE;
DROP TABLE IF EXISTS cex_flows CASCADE;
DROP TABLE IF EXISTS native_transfers CASCADE;

-- Drop reference tables
DROP TABLE IF EXISTS pools CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS chain_config CASCADE;

-- Drop Prisma migrations table
DROP TABLE IF EXISTS _prisma_migrations CASCADE;

-- Drop enum types
DROP TYPE IF EXISTS "FlowType" CASCADE;
DROP TYPE IF EXISTS "LiquidityType" CASCADE;

-- Done
SELECT 'Database cleaned successfully!' AS status;
