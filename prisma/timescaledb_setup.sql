-- Enable TimescaleDB extension 
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert native_transfers to hypertable (partition by blockTimeStamp)
SELECT create_hypertable('native_transfers', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert cex_flows to hypertable
SELECT create_hypertable('cex_flows', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert decoded_events to hypertable
SELECT create_hypertable('decoded_events', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert stablecoin_transfers to hypertable
SELECT create_hypertable('stablecoin_transfers', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert stablecoin_cex_flows to hypertable
SELECT create_hypertable('stablecoin_cex_flows', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert stablecoin_events_meta to hypertable
SELECT create_hypertable('stablecoin_events_meta', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert pool_swaps to hypertable
SELECT create_hypertable('pool_swaps', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert pool_liquidity to hypertable
SELECT create_hypertable('pool_liquidity', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert pool_fees to hypertable
SELECT create_hypertable('pool_fees', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert deceoded_event_range to hypertable
SELECT create_hypertable('deceoded_event_range', 'created_at',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert metrics_generated to hypertable
SELECT create_hypertable('metrics_generated', 'created_at',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert token_transfers to hypertable
SELECT create_hypertable('token_transfers', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert token_cex_flows to hypertable
SELECT create_hypertable('token_cex_flows', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert token_supply_events to hypertable
SELECT create_hypertable('token_supply_events', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert token_deposit_withdrawals to hypertable
SELECT create_hypertable('token_deposit_withdrawals', 'block_time_stamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Enable compression for older data
ALTER TABLE native_transfers SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id'
);

ALTER TABLE cex_flows SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,cex_name'
);

ALTER TABLE decoded_events SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,event_name'
);

ALTER TABLE stablecoin_transfers SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,token_address'
);

ALTER TABLE stablecoin_cex_flows SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,token_address,cex_name'
);

ALTER TABLE stablecoin_events_meta SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,token_address,event_type'
);

ALTER TABLE token_supply SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,token_address,token_supply_type'
);

ALTER TABLE pool_swaps SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,pool_address'
);

ALTER TABLE pool_liquidity SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,pool_address,liquidity_type'
);

ALTER TABLE pool_fees SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chain_id,pool_address'
);
ALTER TABLE deceoded_event_range SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'created_at,chain_id'
);

-- compression policy (compress data older than 1 days)
SELECT add_compression_policy('native_transfers', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('cex_flows', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('decoded_events', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('stablecoin_transfers', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('stablecoin_cex_flows', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('stablecoin_events_meta', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('token_supply', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('pool_swaps', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('pool_liquidity', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('pool_fees', INTERVAL '1 days', if_not_exists => TRUE);

SELECT add_compression_policy('token_transfers', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('token_cex_flows', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('token_supply_events', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('token_deposit_withdrawals', INTERVAL '1 days', if_not_exists => TRUE);

