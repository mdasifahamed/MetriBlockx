import { PrismaClient } from "../src/generated/prisma";

const prisma = new PrismaClient();

async function setupHypertables() {
  console.log("Setting up TimescaleDB hypertables\n");

  try {
    await prisma.$executeRawUnsafe(`CREATE EXTENSION IF NOT EXISTS timescaledb`);
    console.log("OK: TimescaleDB extension enabled");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('native_transfers', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: native_transfers hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('cex_flows', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: cex_flows hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('decoded_events', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: decoded_events hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('stablecoin_transfers', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: stablecoin_transfers hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('stablecoin_cex_flows', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: stablecoin_cex_flows hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('stablecoin_events_meta', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: stablecoin_events_meta hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('token_supply', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: token_supply hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('pool_swaps', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: pool_swaps hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('pool_liquidity', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: pool_liquidity hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('pool_fees', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: pool_fees hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('decoded_event_range', 'created_at', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: decoded_event_range hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('metrics_generated', 'created_at', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: metrics_generated hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('token_transfers', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: token_transfers hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('token_cex_flows', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: token_cex_flows hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('token_supply_events', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: token_supply_events hypertable");

    await prisma.$executeRawUnsafe(`SELECT create_hypertable('token_deposit_withdrawals', 'block_time_stamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)`);
    console.log("OK: token_deposit_withdrawals hypertable");

    await prisma.$executeRawUnsafe(`ALTER TABLE native_transfers SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id')`);
    console.log("OK: native_transfers compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE cex_flows SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,cex_name')`);
    console.log("OK: cex_flows compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE decoded_events SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,event_name')`);
    console.log("OK: decoded_events compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE stablecoin_transfers SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address')`);
    console.log("OK: stablecoin_transfers compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE stablecoin_cex_flows SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address,cex_name')`);
    console.log("OK: stablecoin_cex_flows compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE stablecoin_events_meta SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address,event_type')`);
    console.log("OK: stablecoin_events_meta compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE token_supply SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address,token_supply_type')`);
    console.log("OK: token_supply compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE pool_swaps SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,pool_address')`);
    console.log("OK: pool_swaps compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE pool_liquidity SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,pool_address,liquidity_type')`);
    console.log("OK: pool_liquidity compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE pool_fees SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,pool_address')`);
    console.log("OK: pool_fees compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE decoded_event_range SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,created_at')`);
    console.log("OK: decoded_event_range compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE metrics_generated SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,created_at')`);
    console.log("OK: metrics_generated compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE token_transfers SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address')`);
    console.log("OK: token_transfers compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE token_cex_flows SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address,cex_name')`);
    console.log("OK: token_cex_flows compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE token_supply_events SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address')`);
    console.log("OK: token_supply_events compression");

    await prisma.$executeRawUnsafe(`ALTER TABLE token_deposit_withdrawals SET (timescaledb.compress, timescaledb.compress_segmentby = 'chain_id,token_address')`);
    console.log("OK: token_deposit_withdrawals compression");

    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('native_transfers', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('cex_flows', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('decoded_events', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('stablecoin_transfers', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('stablecoin_cex_flows', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('stablecoin_events_meta', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('token_supply', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('pool_swaps', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('pool_liquidity', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('pool_fees', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('decoded_event_range', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('metrics_generated', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('token_transfers', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('token_cex_flows', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('token_supply_events', INTERVAL '1 days', if_not_exists => TRUE)`);
    await prisma.$executeRawUnsafe(`SELECT add_compression_policy('token_deposit_withdrawals', INTERVAL '1 days', if_not_exists => TRUE)`);

    console.log("OK: compression policies added");

    console.log("\nHypertables setup completed!");
  } catch (error) {
    console.error("Error setting up hypertables:", error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

setupHypertables();