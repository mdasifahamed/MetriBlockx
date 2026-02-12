

-- Enable TimescaleDB extension 
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert native_transfers to hypertable (partition by blockTimeStamp)
SELECT create_hypertable('native_transfers', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert cex_flows to hypertable
SELECT create_hypertable('cex_flows', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert decoded_events to hypertable
SELECT create_hypertable('decoded_events', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert stablecoin_transfers to hypertable
SELECT create_hypertable('stablecoin_transfers', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert stablecoin_cex_flows to hypertable
SELECT create_hypertable('stablecoin_cex_flows', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert stablecoin_events_meta to hypertable
SELECT create_hypertable('stablecoin_events_meta', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert pool_swaps to hypertable
SELECT create_hypertable('pool_swaps', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert pool_liquidity to hypertable
SELECT create_hypertable('pool_liquidity', 'blockTimeStamp',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE
);

-- Convert pool_fees to hypertable
SELECT create_hypertable('pool_fees', 'blockTimeStamp',
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

-- Enable compression for older data
ALTER TABLE native_transfers SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId'
);

ALTER TABLE cex_flows SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,cexName'
);

ALTER TABLE decoded_events SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,eventName'
);

ALTER TABLE stablecoin_transfers SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,tokenAddress'
);

ALTER TABLE stablecoin_cex_flows SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,tokenAddress,cexName'
);

ALTER TABLE stablecoin_events_meta SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,tokenAddress,eventType'
);

ALTER TABLE pool_swaps SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,poolAddress'
);

ALTER TABLE pool_liquidity SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,poolAddress,liquidityType'
);

ALTER TABLE pool_fees SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'chainId,poolAddress'
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
SELECT add_compression_policy('pool_swaps', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('pool_liquidity', INTERVAL '1 days', if_not_exists => TRUE);
SELECT add_compression_policy('pool_fees', INTERVAL '1 days', if_not_exists => TRUE);

