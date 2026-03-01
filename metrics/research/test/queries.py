AGGREGATION_START_DATE = '2026-02-10'
AGGREGATION_END_DATE_EXCLUSIVE = '2026-02-13'


def get_pool_swaps_aggregation_query(time_granularity: str) -> str:
    return f"""
    WITH by_bucket AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id,
            pool_address,
            SUM(CAST(volume_token_0_human AS NUMERIC)) as volume_token_0_total,
            SUM(CAST(volume_token_1_human AS NUMERIC)) as volume_token_1_total,
            SUM(swap_count) as total_swap_count,
            ARRAY_AGG(DISTINCT block_number ORDER BY block_number) as block_numbers
        FROM pool_swaps
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}'
          AND block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
        GROUP BY DATE_TRUNC('{time_granularity}', block_time_stamp), chain_id, pool_address
    ),
    -- unnest so we can count txs per bucket
    txs AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id,
            pool_address,
            UNNEST(transaction_hashes) as single_transaction_hash
        FROM pool_swaps
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}'
          AND block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ),
    txs_agg AS (
        SELECT time_bucket, chain_id, pool_address,
            COUNT(single_transaction_hash) as transaction_count,
            ARRAY_AGG(single_transaction_hash) as transaction_hashes
        FROM txs
        GROUP BY time_bucket, chain_id, pool_address
    )
    SELECT b.time_bucket, b.chain_id, b.pool_address,
        b.volume_token_0_total, b.volume_token_1_total, b.total_swap_count,
        b.block_numbers, t.transaction_count, t.transaction_hashes
    FROM by_bucket b
    JOIN txs_agg t ON b.time_bucket = t.time_bucket AND b.chain_id = t.chain_id AND b.pool_address = t.pool_address
    ORDER BY b.time_bucket, b.chain_id
    """


def get_pool_liquidity_aggregation_query(time_granularity: str) -> str:
    return f"""
    WITH aggregated_metrics AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, pool_address, liquidity_type,
            SUM(CAST(amount_token_0_human AS NUMERIC)) as amount_token_0_total,
            SUM(CAST(amount_token_1_human AS NUMERIC)) as amount_token_1_total,
            SUM(transaction_count) as total_transaction_count,
            ARRAY_AGG(DISTINCT block_number ORDER BY block_number) as block_numbers
        FROM pool_liquidity
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' AND block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
        GROUP BY DATE_TRUNC('{time_granularity}', block_time_stamp), chain_id, pool_address, liquidity_type
    ),
    unnested_hashes AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, pool_address, liquidity_type,
            UNNEST(transaction_hashes) as single_transaction_hash
        FROM pool_liquidity
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' AND block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ),
    aggregated_hashes AS (
        SELECT time_bucket, chain_id, pool_address, liquidity_type,
            COUNT(single_transaction_hash) as transaction_count,
            ARRAY_AGG(single_transaction_hash) as transaction_hashes
        FROM unnested_hashes
        GROUP BY time_bucket, chain_id, pool_address, liquidity_type
    )
    SELECT am.time_bucket, am.chain_id, am.pool_address, am.liquidity_type,
        am.amount_token_0_total, am.amount_token_1_total, am.total_transaction_count,
        am.block_numbers, ah.transaction_count, ah.transaction_hashes
    FROM aggregated_metrics am
    JOIN aggregated_hashes ah ON am.time_bucket = ah.time_bucket AND am.chain_id = ah.chain_id
        AND am.pool_address = ah.pool_address AND am.liquidity_type = ah.liquidity_type
    ORDER BY am.time_bucket, am.chain_id
    """


def get_pool_fees_aggregation_query(time_granularity: str) -> str:
    return f"""
    WITH m AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, pool_address,
            SUM(CAST(fees_token_0_human AS NUMERIC)) as fees_token_0_total,
            SUM(CAST(fees_token_1_human AS NUMERIC)) as fees_token_1_total,
            SUM(collect_count) as total_collect_count,
            ARRAY_AGG(DISTINCT block_number ORDER BY block_number) as block_numbers
        FROM pool_fees
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
        GROUP BY DATE_TRUNC('{time_granularity}', block_time_stamp), chain_id, pool_address
    ),
    h AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, pool_address,
            UNNEST(transaction_hashes) as single_transaction_hash
        FROM pool_fees
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ),
    h_agg AS (
        SELECT time_bucket, chain_id, pool_address,
            COUNT(single_transaction_hash) as transaction_count,
            ARRAY_AGG(single_transaction_hash) as transaction_hashes
        FROM h
        GROUP BY time_bucket, chain_id, pool_address
    )
    SELECT m.time_bucket, m.chain_id, m.pool_address,
        m.fees_token_0_total, m.fees_token_1_total, m.total_collect_count,
        m.block_numbers, h_agg.transaction_count, h_agg.transaction_hashes
    FROM m
    JOIN h_agg ON m.time_bucket = h_agg.time_bucket AND m.chain_id = h_agg.chain_id AND m.pool_address = h_agg.pool_address
    ORDER BY m.time_bucket, m.chain_id
    """


def get_pool_reserves_daily_query() -> str:
    # latest reserve per pool per day
    return f"""
    SELECT DISTINCT ON (DATE_TRUNC('day', block_time_stamp), chain_id, pool_address)
        DATE_TRUNC('day', block_time_stamp) as time_bucket,
        chain_id, pool_address,
        CAST(reserve_token_0 AS NUMERIC) as reserve_token_0_last,
        CAST(reserve_token_1 AS NUMERIC) as reserve_token_1_last,
        ARRAY[block_number] as block_numbers,
        ARRAY_LENGTH(transaction_hashes, 1) as transaction_count,
        transaction_hashes
    FROM "pool_Reserve"
    WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ORDER BY DATE_TRUNC('day', block_time_stamp), chain_id, pool_address, block_time_stamp DESC
    """


def get_token_cex_flows_aggregation_query(time_granularity: str) -> str:
    return f"""
    WITH by_bucket AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, token_address, cex_name, flow_type,
            SUM(CAST(total_amount_human AS NUMERIC)) as total_amount_sum,
            SUM(transaction_count) as total_transaction_count,
            ARRAY_AGG(DISTINCT block_number ORDER BY block_number) as block_numbers
        FROM token_cex_flows
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
        GROUP BY DATE_TRUNC('{time_granularity}', block_time_stamp), chain_id, token_address, cex_name, flow_type
    ),
    txs AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, token_address, cex_name, flow_type,
            UNNEST(transaction_hashes) as single_transaction_hash
        FROM token_cex_flows
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ),
    txs_agg AS (
        SELECT time_bucket, chain_id, token_address, cex_name, flow_type,
            COUNT(single_transaction_hash) as transaction_count,
            ARRAY_AGG(single_transaction_hash) as transaction_hashes
        FROM txs
        GROUP BY time_bucket, chain_id, token_address, cex_name, flow_type
    )
    SELECT b.time_bucket, b.chain_id, b.token_address, b.cex_name, b.flow_type,
        b.total_amount_sum, b.total_transaction_count, b.block_numbers,
        t.transaction_count, t.transaction_hashes
    FROM by_bucket b
    JOIN txs_agg t ON b.time_bucket = t.time_bucket AND b.chain_id = t.chain_id
        AND b.token_address = t.token_address AND b.cex_name = t.cex_name AND b.flow_type = t.flow_type
    ORDER BY b.time_bucket, b.chain_id
    """


def get_token_transfers_aggregation_query(time_granularity: str) -> str:
    return f"""
    WITH m AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, token_address,
            SUM(CAST(total_amount_human AS NUMERIC)) as total_amount_sum,
            SUM(transaction_count) as total_transaction_count,
            ARRAY_AGG(DISTINCT block_number ORDER BY block_number) as block_numbers
        FROM token_transfers
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
        GROUP BY DATE_TRUNC('{time_granularity}', block_time_stamp), chain_id, token_address
    ),
    txs AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, token_address,
            UNNEST(transaction_hashes) as single_transaction_hash
        FROM token_transfers
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ),
    txs_agg AS (
        SELECT time_bucket, chain_id, token_address,
            COUNT(single_transaction_hash) as transaction_count,
            ARRAY_AGG(single_transaction_hash) as transaction_hashes
        FROM txs
        GROUP BY time_bucket, chain_id, token_address
    )
    SELECT m.time_bucket, m.chain_id, m.token_address,
        m.total_amount_sum, m.total_transaction_count, m.block_numbers,
        txs_agg.transaction_count, txs_agg.transaction_hashes
    FROM m
    JOIN txs_agg ON m.time_bucket = txs_agg.time_bucket AND m.chain_id = txs_agg.chain_id AND m.token_address = txs_agg.token_address
    ORDER BY m.time_bucket, m.chain_id
    """


def get_token_supply_events_aggregation_query(time_granularity: str) -> str:
    return f"""
    WITH by_bucket AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, token_address, supply_type,
            SUM(CAST(total_amount_human AS NUMERIC)) as total_amount_sum,
            SUM(transaction_count) as total_transaction_count,
            ARRAY_AGG(DISTINCT block_number ORDER BY block_number) as block_numbers
        FROM token_supply_events
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
        GROUP BY DATE_TRUNC('{time_granularity}', block_time_stamp), chain_id, token_address, supply_type
    ),
    txs AS (
        SELECT
            DATE_TRUNC('{time_granularity}', block_time_stamp) as time_bucket,
            chain_id, token_address, supply_type,
            UNNEST(transaction_hashes) as single_transaction_hash
        FROM token_supply_events
        WHERE block_time_stamp >= '{AGGREGATION_START_DATE}' and block_time_stamp < '{AGGREGATION_END_DATE_EXCLUSIVE}'
    ),
    txs_agg AS (
        SELECT time_bucket, chain_id, token_address, supply_type,
            COUNT(single_transaction_hash) as transaction_count,
            ARRAY_AGG(single_transaction_hash) as transaction_hashes
        FROM txs
        GROUP BY time_bucket, chain_id, token_address, supply_type
    )
    SELECT b.time_bucket, b.chain_id, b.token_address, b.supply_type,
        b.total_amount_sum, b.total_transaction_count, b.block_numbers,
        t.transaction_count, t.transaction_hashes
    FROM by_bucket b
    JOIN txs_agg t ON b.time_bucket = t.time_bucket AND b.chain_id = t.chain_id
        AND b.token_address = t.token_address AND b.supply_type = t.supply_type
    ORDER BY b.time_bucket, b.chain_id
    """


def get_all_pools_metadata_query() -> str:
    return """
    SELECT pool_address, chain_id, token_0_address, token_1_address,
           pool_symbol, dex_name, dex_version, fees
    FROM pools
    """


def get_all_tokens_metadata_query() -> str:
    return """
    SELECT token_address, chain_id, token_symbol, token_type, token_decimal
    FROM tokens
    """
