import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from metrics.db.db_connection import db
from metrics.research.test.prices import fetch_all_daily_prices, fetch_all_hourly_prices
from metrics.research.test.queries import (
    get_all_pools_metadata_query,
    get_all_tokens_metadata_query,
    get_pool_fees_aggregation_query,
    get_pool_liquidity_aggregation_query,
    get_pool_reserves_daily_query,
    get_pool_swaps_aggregation_query,
    get_token_cex_flows_aggregation_query,
    get_token_supply_events_aggregation_query,
    get_token_transfers_aggregation_query,
)


CHAIN_NAMES: Dict[int, str] = {
    1: 'Ethereum',
    56: 'BNB Chain',
    137: 'Polygon',
}

AGGREGATION_DATE_STRINGS: List[str] = ['2026-02-10', '2026-02-11', '2026-02-12']

STABLE_TOKEN_TYPE = 'STABLE'
MINT_SUPPLY_TYPES = {'ISSUE'}
BURN_SUPPLY_TYPES = {'BURN'}

OUTPUT_DIRECTORY = Path(__file__).parent / 'output'
OUTPUT_V2_DIRECTORY = Path(__file__).parent / 'output_v2_raw'
OUTPUT_V3_DIRECTORY = Path(__file__).parent / 'output_v3_hourly'

DAILY_BUCKET_KEY_FORMAT = '%Y-%m-%d'
HOURLY_BUCKET_KEY_FORMAT = '%Y-%m-%d %H:%M:%S'


def serialize_array_for_csv(array_value) -> str:
    if array_value is None:
        return '[]'
    return json.dumps(list(array_value))


def combine_arrays_from_series(array_series: pd.Series) -> list:
    combined: list = []
    for array_value in array_series:
        if array_value is not None and isinstance(array_value, (list, tuple)):
            combined.extend(array_value)
    return combined


def combine_block_numbers_from_series(block_number_series: pd.Series) -> list:
    combined = combine_arrays_from_series(block_number_series)
    return sorted(set(combined))


async def execute_query_as_dataframe(query: str) -> pd.DataFrame:
    async with db.getConnection() as conn:
        cur = await conn.execute(query)
        rows = await cur.fetchall()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def build_pool_metadata_lookup(
    pools_dataframe: pd.DataFrame,
    tokens_dataframe: pd.DataFrame,
) -> Dict:
    token_type_by_key: Dict = {}
    token_symbol_by_key: Dict = {}

    for _, row in tokens_dataframe.iterrows():
        key = (int(row['chain_id']), str(row['token_address']).lower())
        token_type_by_key[key] = str(row['token_type'])
        token_symbol_by_key[key] = str(row['token_symbol'])

    out: Dict = {}

    for _, row in pools_dataframe.iterrows():
        cid = int(row['chain_id'])
        pool_key = (cid, str(row['pool_address']).lower())
        t0_key = (cid, str(row['token_0_address']).lower())
        t1_key = (cid, str(row['token_1_address']).lower())

        t0_type = token_type_by_key.get(t0_key, 'UNKNOWN')
        t1_type = token_type_by_key.get(t1_key, 'UNKNOWN')
        t0_sym = token_symbol_by_key.get(t0_key, 'UNKNOWN')
        t1_sym = token_symbol_by_key.get(t1_key, 'UNKNOWN')

        if t0_type == STABLE_TOKEN_TYPE:
            stable_pos = 0
        elif t1_type == STABLE_TOKEN_TYPE:
            stable_pos = 1
        else:
            stable_pos = None

        out[pool_key] = {
            'pool_symbol': str(row['pool_symbol']),
            'dex_name': str(row['dex_name']),
            'dex_version': str(row['dex_version']),
            'fee_tier': int(row['fees']) if row['fees'] is not None else 0,
            'token_0_symbol': t0_sym,
            'token_1_symbol': t1_sym,
            'token_0_type': t0_type,
            'token_1_type': t1_type,
            'stable_token_position': stable_pos,
        }

    return out


def build_token_metadata_lookup(tokens_dataframe: pd.DataFrame) -> Dict:
    out: Dict = {}
    for _, row in tokens_dataframe.iterrows():
        key = (int(row['chain_id']), str(row['token_address']).lower())
        out[key] = {
            'token_symbol': str(row['token_symbol']),
            'token_type': str(row['token_type']),
            'token_decimal': int(row['token_decimal']),
        }
    return out


def get_date_string_from_bucket(time_bucket_value) -> str:
    return pd.Timestamp(time_bucket_value).strftime('%Y-%m-%d')


def compute_pool_usd_value(
    row: pd.Series,
    pool_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    token_0_amount_column: str,
    token_1_amount_column: str,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> float:
    pool_key = (int(row['chain_id']), str(row['pool_address']).lower())
    meta = pool_metadata_lookup.get(pool_key)
    if meta is None:
        return 0.0

    bucket_key = pd.Timestamp(row['time_bucket']).strftime(bucket_key_format)
    prices_bucket = prices.get(bucket_key, {})
    stable_pos = meta['stable_token_position']

    if stable_pos == 0:
        return float(row[token_0_amount_column])
    if stable_pos == 1:
        return float(row[token_1_amount_column])
    p0 = prices_bucket.get(meta['token_0_symbol'], 0.0)
    p1 = prices_bucket.get(meta['token_1_symbol'], 0.0)
    return float(row[token_0_amount_column]) * p0 + float(row[token_1_amount_column]) * p1


def compute_token_usd_value(
    row: pd.Series,
    token_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    amount_column: str,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> float:
    key = (int(row['chain_id']), str(row['token_address']).lower())
    meta = token_metadata_lookup.get(key)
    if meta is None:
        return 0.0

    amt = float(row[amount_column])
    if meta['token_type'] == STABLE_TOKEN_TYPE:
        return amt

    bucket_key = pd.Timestamp(row['time_bucket']).strftime(bucket_key_format)
    return amt * prices.get(bucket_key, {}).get(meta['token_symbol'], 0.0)


def compute_reserve_usd_value(
    row: pd.Series,
    pool_metadata_lookup: Dict,
    daily_prices: Dict[str, Dict[str, float]],
    reserve_column: str,
    token_position: int,
) -> float:
    pool_key = (int(row['chain_id']), str(row['pool_address']).lower())
    meta = pool_metadata_lookup.get(pool_key, {})
    sym = meta.get(f'token_{token_position}_symbol', '')
    date_key = get_date_string_from_bucket(row['time_bucket'])
    price = daily_prices.get(date_key, {}).get(sym, 0.0)
    return float(row[reserve_column]) * price


def _pool_key(row) -> tuple:
    return (int(row['chain_id']), str(row['pool_address']).lower())


def _token_key(row) -> tuple:
    return (int(row['chain_id']), str(row['token_address']).lower())


def _format_time_column(df: pd.DataFrame, time_granularity: str, time_column_name: str) -> pd.DataFrame:
    if time_granularity == 'day':
        return format_bucket_as_date_string(df, time_column_name)
    return format_bucket_as_datetime_string(df, time_column_name)


def enrich_dataframe_with_pool_metadata(
    dataframe: pd.DataFrame,
    pool_metadata_lookup: Dict,
) -> pd.DataFrame:
    out = dataframe.copy()
    for col, meta_key in [
        ('pool_symbol', 'pool_symbol'), ('dex_name', 'dex_name'), ('dex_version', 'dex_version'),
        ('fee_tier', 'fee_tier'), ('token_0_symbol', 'token_0_symbol'), ('token_1_symbol', 'token_1_symbol'),
    ]:
        default = 0 if col == 'fee_tier' else 'UNKNOWN'
        out[col] = out.apply(
            lambda r, mk=meta_key, d=default: pool_metadata_lookup.get(_pool_key(r), {}).get(mk, d),
            axis=1,
        )
    return out


def enrich_dataframe_with_token_metadata(
    dataframe: pd.DataFrame,
    token_metadata_lookup: Dict,
) -> pd.DataFrame:
    out = dataframe.copy()
    out['token_symbol'] = out.apply(
        lambda r: token_metadata_lookup.get(_token_key(r), {}).get('token_symbol', 'UNKNOWN'),
        axis=1,
    )
    out['token_type'] = out.apply(
        lambda r: token_metadata_lookup.get(_token_key(r), {}).get('token_type', 'UNKNOWN'),
        axis=1,
    )
    return out


def add_chain_name_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    out = dataframe.copy()
    out['chain_name'] = out['chain_id'].apply(
        lambda cid: CHAIN_NAMES.get(int(cid), f'Chain-{cid}')
    )
    return out


def format_bucket_as_date_string(dataframe: pd.DataFrame, output_column_name: str) -> pd.DataFrame:
    out = dataframe.copy()
    out[output_column_name] = out['time_bucket'].apply(
        lambda b: pd.Timestamp(b).strftime('%Y-%m-%d')
    )
    return out


def format_bucket_as_datetime_string(dataframe: pd.DataFrame, output_column_name: str) -> pd.DataFrame:
    out = dataframe.copy()
    out[output_column_name] = out['time_bucket'].apply(
        lambda b: pd.Timestamp(b).strftime('%Y-%m-%d %H:%M:%S')
    )
    return out


def apply_array_serialization(dataframe: pd.DataFrame) -> pd.DataFrame:
    out = dataframe.copy()
    out['block_numbers'] = out['block_numbers'].apply(serialize_array_for_csv)
    out['transaction_hashes'] = out['transaction_hashes'].apply(serialize_array_for_csv)
    return out


def export_dataframe_to_csv(dataframe: pd.DataFrame, filename: str, output_dir: Path) -> None:
    path = output_dir / filename
    dataframe.to_csv(path, index=False)


def pivot_add_remove(
    enriched: pd.DataFrame,
    group_columns: List[str],
    amount_column: str,
    added_col_name: str,
    removed_col_name: str,
    net_col_name: str,
) -> pd.DataFrame:
    add = enriched[enriched['liquidity_type'] == 'ADD'].copy()
    rem = enriched[enriched['liquidity_type'] == 'REMOVE'].copy()

    add_agg = add.groupby(group_columns, as_index=False).agg(
        **{added_col_name: (amount_column, 'sum')},
        block_numbers_add=('block_numbers', combine_block_numbers_from_series),
        transaction_count_add=('transaction_count', 'sum'),
        transaction_hashes_add=('transaction_hashes', combine_arrays_from_series),
    )
    rem_agg = rem.groupby(group_columns, as_index=False).agg(
        **{removed_col_name: (amount_column, 'sum')},
        block_numbers_remove=('block_numbers', combine_block_numbers_from_series),
        transaction_count_remove=('transaction_count', 'sum'),
        transaction_hashes_remove=('transaction_hashes', combine_arrays_from_series),
    )

    pv = add_agg.merge(rem_agg, on=group_columns, how='outer')
    for c in ['block_numbers_add', 'block_numbers_remove', 'transaction_hashes_add', 'transaction_hashes_remove']:
        pv[c] = pv[c].apply(lambda x: x if isinstance(x, list) else [])
    pv['transaction_count_add'] = pv['transaction_count_add'].fillna(0).astype(int)
    pv['transaction_count_remove'] = pv['transaction_count_remove'].fillna(0).astype(int)
    pv[added_col_name] = pv[added_col_name].fillna(0)
    pv[removed_col_name] = pv[removed_col_name].fillna(0)
    pv[net_col_name] = pv[added_col_name] - pv[removed_col_name]

    pv['block_numbers'] = pv.apply(
        lambda r: sorted(set(r['block_numbers_add'] + r['block_numbers_remove'])), axis=1
    )
    pv['transaction_count'] = pv['transaction_count_add'] + pv['transaction_count_remove']
    pv['transaction_hashes'] = pv.apply(
        lambda r: r['transaction_hashes_add'] + r['transaction_hashes_remove'], axis=1
    )
    return pv


def pivot_inflow_outflow(
    enriched: pd.DataFrame,
    group_columns: List[str],
    amount_column: str,
) -> pd.DataFrame:
    amt_col = 'amount_usd' if amount_column == 'amount_usd' else amount_column
    inf = enriched[enriched['flow_type'] == 'INFLOW'].copy()
    outf = enriched[enriched['flow_type'] == 'OUTFLOW'].copy()

    inf_agg = inf.groupby(group_columns, as_index=False).agg(
        INFLOW=(amt_col, 'sum'),
        block_numbers_inflow=('block_numbers', combine_block_numbers_from_series),
        transaction_count_inflow=('transaction_count', 'sum'),
        transaction_hashes_inflow=('transaction_hashes', combine_arrays_from_series),
    )
    outf_agg = outf.groupby(group_columns, as_index=False).agg(
        OUTFLOW=(amt_col, 'sum'),
        block_numbers_outflow=('block_numbers', combine_block_numbers_from_series),
        transaction_count_outflow=('transaction_count', 'sum'),
        transaction_hashes_outflow=('transaction_hashes', combine_arrays_from_series),
    )

    pv = inf_agg.merge(outf_agg, on=group_columns, how='outer')
    for c in ['block_numbers_inflow', 'block_numbers_outflow', 'transaction_hashes_inflow', 'transaction_hashes_outflow']:
        pv[c] = pv[c].apply(lambda x: x if isinstance(x, list) else [])
    pv['transaction_count_inflow'] = pv['transaction_count_inflow'].fillna(0).astype(int)
    pv['transaction_count_outflow'] = pv['transaction_count_outflow'].fillna(0).astype(int)
    pv['INFLOW'] = pv['INFLOW'].fillna(0)
    pv['OUTFLOW'] = pv['OUTFLOW'].fillna(0)
    pv['net_flow_usd'] = pv['INFLOW'] - pv['OUTFLOW']

    pv['block_numbers'] = pv.apply(
        lambda r: sorted(set(r['block_numbers_inflow'] + r['block_numbers_outflow'])), axis=1
    )
    pv['transaction_count'] = pv['transaction_count_inflow'] + pv['transaction_count_outflow']
    pv['transaction_hashes'] = pv.apply(
        lambda r: r['transaction_hashes_inflow'] + r['transaction_hashes_outflow'], axis=1
    )
    return pv


# V1 — USD with daily (or hourly for V3) prices

async def build_dex_swap_volume_csvs(
    pool_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    output_dir: Path,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '01', 'block_hour'),
        ('day', '02', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_pool_swaps_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        fmt = bucket_key_format if time_granularity == 'hour' else DAILY_BUCKET_KEY_FORMAT
        enriched['volume_usd'] = enriched.apply(
            lambda r: compute_pool_usd_value(
                r, pool_metadata_lookup, prices,
                'volume_token_0_total', 'volume_token_1_total',
                bucket_key_format=fmt,
            ),
            axis=1,
        )
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        cols = [
            'chain_id', 'chain_name', time_column_name,
            'pool_symbol', 'dex_name', 'dex_version', 'fee_tier',
            'volume_usd', 'total_swap_count',
            'block_numbers', 'transaction_count', 'transaction_hashes',
        ]
        out_df = enriched[cols].rename(columns={'total_swap_count': 'swap_count'}).copy()
        out_df['volume_usd'] = out_df['volume_usd'].round(2)
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_dex_swap_volume_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)
        results[f'{file_number}_daily' if time_granularity == 'day' else f'{file_number}_hourly'] = out_df
    return results


async def build_dex_liquidity_csvs(
    pool_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    output_dir: Path,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '03', 'block_hour'),
        ('day', '04', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_pool_liquidity_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        fmt = bucket_key_format if time_granularity == 'hour' else DAILY_BUCKET_KEY_FORMAT
        enriched['amount_usd'] = enriched.apply(
            lambda r: compute_pool_usd_value(
                r, pool_metadata_lookup, prices,
                'amount_token_0_total', 'amount_token_1_total',
                bucket_key_format=fmt,
            ),
            axis=1,
        )
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        grp = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'dex_name']
        pv = pivot_add_remove(enriched, grp, 'amount_usd', 'liquidity_added_usd', 'liquidity_removed_usd', 'net_liquidity_usd')
        pv['liquidity_added_usd'] = pv['liquidity_added_usd'].round(2)
        pv['liquidity_removed_usd'] = pv['liquidity_removed_usd'].round(2)
        pv['net_liquidity_usd'] = pv['net_liquidity_usd'].round(2)

        cols = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'dex_name',
                'liquidity_added_usd', 'liquidity_removed_usd', 'net_liquidity_usd',
                'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = pv[cols].copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_dex_liquidity_{"daily" if time_granularity == "day" else "hourly"}_net.csv', output_dir)
        results[f'{file_number}'] = out_df
    return results


async def build_dex_fees_csvs(
    pool_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    output_dir: Path,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '05', 'block_hour'),
        ('day', '06', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_pool_fees_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        fmt = bucket_key_format if time_granularity == 'hour' else DAILY_BUCKET_KEY_FORMAT
        enriched['fees_usd'] = enriched.apply(
            lambda r: compute_pool_usd_value(
                r, pool_metadata_lookup, prices,
                'fees_token_0_total', 'fees_token_1_total',
                bucket_key_format=fmt,
            ),
            axis=1,
        )
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        cols = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'fee_tier', 'dex_name',
                'fees_usd', 'total_collect_count', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = enriched[cols].rename(columns={'total_collect_count': 'collect_count'}).copy()
        out_df['fees_usd'] = out_df['fees_usd'].round(2)
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_dex_fees_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)
        results[f'{file_number}'] = out_df
    return results


async def build_cex_flows_csvs(
    token_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    output_dir: Path,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '07', 'block_hour'),
        ('day', '08', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_cex_flows_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        fmt = bucket_key_format if time_granularity == 'hour' else DAILY_BUCKET_KEY_FORMAT
        enriched['amount_usd'] = enriched.apply(
            lambda r: compute_token_usd_value(r, token_metadata_lookup, prices, 'total_amount_sum', bucket_key_format=fmt),
            axis=1,
        )
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        grp = ['chain_id', 'chain_name', time_column_name, 'cex_name']
        pv = pivot_inflow_outflow(enriched, grp, 'amount_usd')
        pv['INFLOW'] = pv['INFLOW'].round(2)
        pv['OUTFLOW'] = pv['OUTFLOW'].round(2)
        pv['net_flow_usd'] = pv['net_flow_usd'].round(2)

        cols = ['chain_id', 'chain_name', time_column_name, 'cex_name',
                'INFLOW', 'OUTFLOW', 'net_flow_usd', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = pv[cols].copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_cex_flows_{"daily" if time_granularity == "day" else "hourly"}_net.csv', output_dir)
        results[f'{file_number}'] = out_df
    return results


async def build_stablecoin_transfer_csvs(
    token_metadata_lookup: Dict,
    output_dir: Path,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '09', 'block_hour'),
        ('day', '10', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_transfers_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        stable = enriched[enriched['token_type'] == STABLE_TOKEN_TYPE].copy()
        if stable.empty:
            continue

        stable['total_amount_usd'] = stable['total_amount_sum'].astype(float).round(2)
        stable = _format_time_column(stable, time_granularity, time_column_name)

        cols = ['chain_id', 'chain_name', time_column_name, 'token_symbol', 'total_amount_usd', 'total_transaction_count',
                'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = stable[cols].rename(columns={'total_transaction_count': 'transfer_count'}).copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_stablecoin_transfer_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)
        results[f'{file_number}'] = out_df
    return results


async def build_stablecoin_cex_flows_csvs(
    token_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    output_dir: Path,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '11', 'block_hour'),
        ('day', '12', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_cex_flows_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        stable = enriched[enriched['token_type'] == STABLE_TOKEN_TYPE].copy()
        if stable.empty:
            continue

        stable = add_chain_name_column(stable)
        stable['amount_usd'] = stable['total_amount_sum'].astype(float)
        stable = _format_time_column(stable, time_granularity, time_column_name)

        grp = ['chain_id', 'chain_name', time_column_name, 'cex_name', 'token_symbol']
        pv = pivot_inflow_outflow(stable, grp, 'amount_usd')
        pv['INFLOW'] = pv['INFLOW'].round(2)
        pv['OUTFLOW'] = pv['OUTFLOW'].round(2)
        pv['net_flow_usd'] = pv['net_flow_usd'].round(2)

        cols = ['chain_id', 'chain_name', time_column_name, 'cex_name', 'token_symbol',
                'INFLOW', 'OUTFLOW', 'net_flow_usd', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = pv[cols].copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_stablecoin_cex_flows_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)
        results[f'{file_number}'] = out_df
    return results


async def build_token_supply_events_csvs(
    token_metadata_lookup: Dict,
    prices: Dict[str, Dict[str, float]],
    output_dir: Path,
    bucket_key_format: str = DAILY_BUCKET_KEY_FORMAT,
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    for time_granularity, file_number, time_column_name in [
        ('hour', '13', 'block_hour'),
        ('day', '14', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_supply_events_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        fmt = bucket_key_format if time_granularity == 'hour' else DAILY_BUCKET_KEY_FORMAT
        enriched['total_amount_usd'] = enriched.apply(
            lambda r: compute_token_usd_value(r, token_metadata_lookup, prices, 'total_amount_sum', bucket_key_format=fmt),
            axis=1,
        )
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        cols = ['chain_id', 'chain_name', time_column_name, 'token_symbol', 'token_type', 'supply_type',
                'total_amount_usd', 'total_transaction_count', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = enriched[cols].rename(columns={'total_transaction_count': 'event_count'}).copy()
        out_df['total_amount_usd'] = out_df['total_amount_usd'].round(2)
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_token_supply_events_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)
        results[f'{file_number}'] = out_df
    return results


async def build_pool_reserves_daily_csv(
    pool_metadata_lookup: Dict,
    daily_prices: Dict[str, Dict[str, float]],
    output_dir: Path,
) -> Optional[pd.DataFrame]:
    raw = await execute_query_as_dataframe(get_pool_reserves_daily_query())
    if raw.empty:
        return None

    enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
    enriched = add_chain_name_column(enriched)
    enriched['reserve_token_0_usd'] = enriched.apply(
        lambda r: compute_reserve_usd_value(r, pool_metadata_lookup, daily_prices, 'reserve_token_0_last', 0),
        axis=1,
    )
    enriched['reserve_token_1_usd'] = enriched.apply(
        lambda r: compute_reserve_usd_value(r, pool_metadata_lookup, daily_prices, 'reserve_token_1_last', 1),
        axis=1,
    )
    enriched = format_bucket_as_date_string(enriched, 'block_date')
    enriched['total_reserve_usd'] = (enriched['reserve_token_0_usd'] + enriched['reserve_token_1_usd']).round(2)
    enriched['reserve_token_0_usd'] = enriched['reserve_token_0_usd'].round(2)
    enriched['reserve_token_1_usd'] = enriched['reserve_token_1_usd'].round(2)

    cols = ['chain_id', 'chain_name', 'block_date', 'pool_symbol', 'dex_name',
            'reserve_token_0_last', 'reserve_token_0_usd', 'reserve_token_1_last', 'reserve_token_1_usd',
            'total_reserve_usd', 'block_numbers', 'transaction_count', 'transaction_hashes']
    out_df = enriched[cols].copy()
    out_df = apply_array_serialization(out_df)
    export_dataframe_to_csv(out_df, '15_pool_reserves_daily.csv', output_dir)
    return out_df


# V2 — raw token amounts, no USD

async def build_dex_swap_volume_raw_csvs(
    pool_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '01', 'block_hour'),
        ('day', '02', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_pool_swaps_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        enriched = _format_time_column(enriched, time_granularity, time_column_name)
        enriched['volume_token_0_human'] = enriched['volume_token_0_total'].astype(float).round(8)
        enriched['volume_token_1_human'] = enriched['volume_token_1_total'].astype(float).round(8)

        cols = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'dex_name', 'dex_version', 'fee_tier',
                'token_0_symbol', 'volume_token_0_human', 'token_1_symbol', 'volume_token_1_human',
                'total_swap_count', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = enriched[cols].rename(columns={'total_swap_count': 'swap_count'}).copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_dex_swap_volume_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)


async def build_dex_liquidity_raw_csvs(
    pool_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '03', 'block_hour'),
        ('day', '04', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_pool_liquidity_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        enriched['amount_token_0_total'] = enriched['amount_token_0_total'].astype(float)
        enriched['amount_token_1_total'] = enriched['amount_token_1_total'].astype(float)
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        grp = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'dex_name', 'token_0_symbol', 'token_1_symbol']
        pv0 = pivot_add_remove(enriched, grp, 'amount_token_0_total', 'token_0_added', 'token_0_removed', 'net_token_0')
        pv1 = pivot_add_remove(enriched, grp, 'amount_token_1_total', 'token_1_added', 'token_1_removed', 'net_token_1')
        pv = pv0.merge(pv1[grp + ['token_1_added', 'token_1_removed', 'net_token_1']], on=grp, how='outer')

        for c in ['token_0_added', 'token_0_removed', 'net_token_0', 'token_1_added', 'token_1_removed', 'net_token_1']:
            pv[c] = pv[c].fillna(0).round(8)

        cols = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'dex_name',
                'token_0_symbol', 'token_0_added', 'token_0_removed', 'net_token_0',
                'token_1_symbol', 'token_1_added', 'token_1_removed', 'net_token_1',
                'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = pv[cols].copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_dex_liquidity_{"daily" if time_granularity == "day" else "hourly"}_net.csv', output_dir)


async def build_dex_fees_raw_csvs(
    pool_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '05', 'block_hour'),
        ('day', '06', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_pool_fees_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        enriched = _format_time_column(enriched, time_granularity, time_column_name)
        enriched['fees_token_0_human'] = enriched['fees_token_0_total'].astype(float).round(8)
        enriched['fees_token_1_human'] = enriched['fees_token_1_total'].astype(float).round(8)

        cols = ['chain_id', 'chain_name', time_column_name, 'pool_symbol', 'fee_tier', 'dex_name',
                'token_0_symbol', 'fees_token_0_human', 'token_1_symbol', 'fees_token_1_human',
                'total_collect_count', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = enriched[cols].rename(columns={'total_collect_count': 'collect_count'}).copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_dex_fees_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)


async def build_cex_flows_raw_csvs(
    token_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '07', 'block_hour'),
        ('day', '08', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_cex_flows_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        enriched['total_amount_sum'] = enriched['total_amount_sum'].astype(float)
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        grp = ['chain_id', 'chain_name', time_column_name, 'cex_name', 'token_symbol']
        inf = enriched[enriched['flow_type'] == 'INFLOW'].copy()
        outf = enriched[enriched['flow_type'] == 'OUTFLOW'].copy()
        inf_agg = inf.groupby(grp, as_index=False).agg(
            inflow_amount=('total_amount_sum', 'sum'),
            block_numbers_inflow=('block_numbers', combine_block_numbers_from_series),
            transaction_count_inflow=('transaction_count', 'sum'),
            transaction_hashes_inflow=('transaction_hashes', combine_arrays_from_series),
        )
        outf_agg = outf.groupby(grp, as_index=False).agg(
            outflow_amount=('total_amount_sum', 'sum'),
            block_numbers_outflow=('block_numbers', combine_block_numbers_from_series),
            transaction_count_outflow=('transaction_count', 'sum'),
            transaction_hashes_outflow=('transaction_hashes', combine_arrays_from_series),
        )
        pv = inf_agg.merge(outf_agg, on=grp, how='outer')
        for c in ['block_numbers_inflow', 'block_numbers_outflow', 'transaction_hashes_inflow', 'transaction_hashes_outflow']:
            pv[c] = pv[c].apply(lambda x: x if isinstance(x, list) else [])
        pv['transaction_count_inflow'] = pv['transaction_count_inflow'].fillna(0).astype(int)
        pv['transaction_count_outflow'] = pv['transaction_count_outflow'].fillna(0).astype(int)
        pv['inflow_amount'] = pv['inflow_amount'].fillna(0).round(8)
        pv['outflow_amount'] = pv['outflow_amount'].fillna(0).round(8)
        pv['net_amount'] = (pv['inflow_amount'] - pv['outflow_amount']).round(8)
        pv['block_numbers'] = pv.apply(lambda r: sorted(set(r['block_numbers_inflow'] + r['block_numbers_outflow'])), axis=1)
        pv['transaction_count'] = pv['transaction_count_inflow'] + pv['transaction_count_outflow']
        pv['transaction_hashes'] = pv.apply(lambda r: r['transaction_hashes_inflow'] + r['transaction_hashes_outflow'], axis=1)

        cols = ['chain_id', 'chain_name', time_column_name, 'cex_name', 'token_symbol',
                'inflow_amount', 'outflow_amount', 'net_amount', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = pv[cols].copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_cex_flows_{"daily" if time_granularity == "day" else "hourly"}_net.csv', output_dir)


async def build_stablecoin_transfer_raw_csvs(
    token_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '09', 'block_hour'),
        ('day', '10', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_transfers_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        stable = enriched[enriched['token_type'] == STABLE_TOKEN_TYPE].copy()
        if stable.empty:
            continue

        stable['total_amount_human'] = stable['total_amount_sum'].astype(float).round(8)
        stable = _format_time_column(stable, time_granularity, time_column_name)

        cols = ['chain_id', 'chain_name', time_column_name, 'token_symbol', 'total_amount_human', 'total_transaction_count',
                'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = stable[cols].rename(columns={'total_transaction_count': 'transfer_count'}).copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_stablecoin_transfer_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)


async def build_stablecoin_cex_flows_raw_csvs(
    token_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '11', 'block_hour'),
        ('day', '12', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_cex_flows_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        stable = enriched[enriched['token_type'] == STABLE_TOKEN_TYPE].copy()
        if stable.empty:
            continue

        stable = add_chain_name_column(stable)
        stable['total_amount_sum'] = stable['total_amount_sum'].astype(float)
        stable = _format_time_column(stable, time_granularity, time_column_name)

        grp = ['chain_id', 'chain_name', time_column_name, 'cex_name', 'token_symbol']
        inf = stable[stable['flow_type'] == 'INFLOW'].copy()
        outf = stable[stable['flow_type'] == 'OUTFLOW'].copy()
        inf_agg = inf.groupby(grp, as_index=False).agg(
            inflow_amount=('total_amount_sum', 'sum'),
            block_numbers_inflow=('block_numbers', combine_block_numbers_from_series),
            transaction_count_inflow=('transaction_count', 'sum'),
            transaction_hashes_inflow=('transaction_hashes', combine_arrays_from_series),
        )
        outf_agg = outf.groupby(grp, as_index=False).agg(
            outflow_amount=('total_amount_sum', 'sum'),
            block_numbers_outflow=('block_numbers', combine_block_numbers_from_series),
            transaction_count_outflow=('transaction_count', 'sum'),
            transaction_hashes_outflow=('transaction_hashes', combine_arrays_from_series),
        )
        pv = inf_agg.merge(outf_agg, on=grp, how='outer')
        for c in ['block_numbers_inflow', 'block_numbers_outflow', 'transaction_hashes_inflow', 'transaction_hashes_outflow']:
            pv[c] = pv[c].apply(lambda x: x if isinstance(x, list) else [])
        pv['transaction_count_inflow'] = pv['transaction_count_inflow'].fillna(0).astype(int)
        pv['transaction_count_outflow'] = pv['transaction_count_outflow'].fillna(0).astype(int)
        pv['inflow_amount'] = pv['inflow_amount'].fillna(0).round(8)
        pv['outflow_amount'] = pv['outflow_amount'].fillna(0).round(8)
        pv['net_amount'] = (pv['inflow_amount'] - pv['outflow_amount']).round(8)
        pv['block_numbers'] = pv.apply(lambda r: sorted(set(r['block_numbers_inflow'] + r['block_numbers_outflow'])), axis=1)
        pv['transaction_count'] = pv['transaction_count_inflow'] + pv['transaction_count_outflow']
        pv['transaction_hashes'] = pv.apply(lambda r: r['transaction_hashes_inflow'] + r['transaction_hashes_outflow'], axis=1)

        cols = ['chain_id', 'chain_name', time_column_name, 'cex_name', 'token_symbol',
                'inflow_amount', 'outflow_amount', 'net_amount', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = pv[cols].copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_stablecoin_cex_flows_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)


async def build_token_supply_events_raw_csvs(
    token_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    for time_granularity, file_number, time_column_name in [
        ('hour', '13', 'block_hour'),
        ('day', '14', 'block_date'),
    ]:
        raw = await execute_query_as_dataframe(get_token_supply_events_aggregation_query(time_granularity))
        if raw.empty:
            continue

        enriched = enrich_dataframe_with_token_metadata(raw, token_metadata_lookup)
        enriched = add_chain_name_column(enriched)
        enriched['total_amount_human'] = enriched['total_amount_sum'].astype(float).round(8)
        enriched = _format_time_column(enriched, time_granularity, time_column_name)

        cols = ['chain_id', 'chain_name', time_column_name, 'token_symbol', 'token_type', 'supply_type',
                'total_amount_human', 'total_transaction_count', 'block_numbers', 'transaction_count', 'transaction_hashes']
        out_df = enriched[cols].rename(columns={'total_transaction_count': 'event_count'}).copy()
        out_df = apply_array_serialization(out_df)
        export_dataframe_to_csv(out_df, f'{file_number}_token_supply_events_{"daily" if time_granularity == "day" else "hourly"}.csv', output_dir)


async def build_pool_reserves_raw_csv(
    pool_metadata_lookup: Dict,
    output_dir: Path,
) -> None:
    raw = await execute_query_as_dataframe(get_pool_reserves_daily_query())
    if raw.empty:
        return

    enriched = enrich_dataframe_with_pool_metadata(raw, pool_metadata_lookup)
    enriched = add_chain_name_column(enriched)
    enriched = format_bucket_as_date_string(enriched, 'block_date')
    enriched['reserve_token_0_last'] = enriched['reserve_token_0_last'].astype(float).round(8)
    enriched['reserve_token_1_last'] = enriched['reserve_token_1_last'].astype(float).round(8)

    cols = ['chain_id', 'chain_name', 'block_date', 'pool_symbol', 'dex_name',
            'token_0_symbol', 'reserve_token_0_last', 'token_1_symbol', 'reserve_token_1_last',
            'block_numbers', 'transaction_count', 'transaction_hashes']
    out_df = enriched[cols].copy()
    out_df = apply_array_serialization(out_df)
    export_dataframe_to_csv(out_df, '15_pool_reserves_daily.csv', output_dir)


# Master summary and cross-chain (V1)

def build_master_summary_daily_dataframe(
    daily_swap_volume_dataframe: Optional[pd.DataFrame],
    daily_fees_dataframe: Optional[pd.DataFrame],
    daily_liquidity_dataframe: Optional[pd.DataFrame],
    daily_stablecoin_transfer_dataframe: Optional[pd.DataFrame],
    daily_cex_flows_dataframe: Optional[pd.DataFrame],
    daily_supply_events_dataframe: Optional[pd.DataFrame],
) -> pd.DataFrame:
    summary_rows = []

    for date_string in AGGREGATION_DATE_STRINGS:
        for chain_id, chain_name in CHAIN_NAMES.items():

            def sum_column_for_chain_date(
                dataframe: Optional[pd.DataFrame],
                date_column: str,
                amount_column: str,
                filter_column: Optional[str] = None,
                filter_values: Optional[set] = None,
            ) -> float:
                if dataframe is None or dataframe.empty:
                    return 0.0
                mask = (
                    (dataframe[date_column] == date_string)
                    & (dataframe['chain_id'] == chain_id)
                )
                if filter_column and filter_values:
                    mask &= dataframe[filter_column].isin(filter_values)
                filtered = dataframe[mask]
                if filtered.empty:
                    return 0.0
                return float(filtered[amount_column].sum())

            dex_volume_usd = sum_column_for_chain_date(
                daily_swap_volume_dataframe, 'block_date', 'volume_usd'
            )
            dex_fees_usd = sum_column_for_chain_date(
                daily_fees_dataframe, 'block_date', 'fees_usd'
            )
            liquidity_added_usd = sum_column_for_chain_date(
                daily_liquidity_dataframe, 'block_date', 'liquidity_added_usd'
            )
            liquidity_removed_usd = sum_column_for_chain_date(
                daily_liquidity_dataframe, 'block_date', 'liquidity_removed_usd'
            )
            liquidity_added_removed_usd = liquidity_added_usd + liquidity_removed_usd

            stablecoin_transfer_volume_usd = sum_column_for_chain_date(
                daily_stablecoin_transfer_dataframe, 'block_date', 'total_amount_usd'
            )

            cex_inflow_usd = sum_column_for_chain_date(
                daily_cex_flows_dataframe, 'block_date', 'INFLOW'
            )
            cex_outflow_usd = sum_column_for_chain_date(
                daily_cex_flows_dataframe, 'block_date', 'OUTFLOW'
            )
            net_cex_flow_usd = cex_inflow_usd - cex_outflow_usd

            token_mint_usd = sum_column_for_chain_date(
                daily_supply_events_dataframe, 'block_date', 'total_amount_usd',
                'supply_type', MINT_SUPPLY_TYPES,
            )
            token_burn_usd = sum_column_for_chain_date(
                daily_supply_events_dataframe, 'block_date', 'total_amount_usd',
                'supply_type', BURN_SUPPLY_TYPES,
            )
            net_supply_change_usd = token_mint_usd - token_burn_usd

            summary_rows.append({
                'chain_id': chain_id,
                'chain_name': chain_name,
                'block_date': date_string,
                'dex_volume_usd': round(dex_volume_usd, 2),
                'dex_fees_usd': round(dex_fees_usd, 2),
                'liquidity_added_removed_usd': round(liquidity_added_removed_usd, 2),
                'stablecoin_transfer_volume_usd': round(stablecoin_transfer_volume_usd, 2),
                'cex_inflow_usd': round(cex_inflow_usd, 2),
                'cex_outflow_usd': round(cex_outflow_usd, 2),
                'net_cex_flow_usd': round(net_cex_flow_usd, 2),
                'token_mint_usd': round(token_mint_usd, 2),
                'token_burn_usd': round(token_burn_usd, 2),
                'net_supply_change_usd': round(net_supply_change_usd, 2),
            })

    return pd.DataFrame(summary_rows)


def build_cross_chain_comparison_dataframe(master_summary_dataframe: pd.DataFrame) -> pd.DataFrame:
    if master_summary_dataframe.empty:
        return pd.DataFrame()
    num_cols = ['dex_volume_usd', 'dex_fees_usd', 'stablecoin_transfer_volume_usd', 'net_cex_flow_usd', 'net_supply_change_usd']
    out = master_summary_dataframe.groupby('block_date', as_index=False)[num_cols].sum()
    for c in num_cols:
        out[c] = out[c].round(2)
    return out


async def main() -> None:
    for directory in [OUTPUT_DIRECTORY, OUTPUT_V2_DIRECTORY, OUTPUT_V3_DIRECTORY]:
        directory.mkdir(parents=True, exist_ok=True)

    await db.connect()

    try:
        pools_df = await execute_query_as_dataframe(get_all_pools_metadata_query())
        tokens_df = await execute_query_as_dataframe(get_all_tokens_metadata_query())
        if pools_df.empty or tokens_df.empty:
            return

        pool_metadata_lookup = build_pool_metadata_lookup(pools_df, tokens_df)
        token_metadata_lookup = build_token_metadata_lookup(tokens_df)

        daily_prices = await fetch_all_daily_prices(AGGREGATION_DATE_STRINGS)
        hourly_prices = await fetch_all_hourly_prices(AGGREGATION_DATE_STRINGS)

        swap_results = await build_dex_swap_volume_csvs(pool_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)
        liquidity_results = await build_dex_liquidity_csvs(pool_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)
        fees_results = await build_dex_fees_csvs(pool_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)
        cex_flow_results = await build_cex_flows_csvs(token_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)
        stablecoin_transfer_results = await build_stablecoin_transfer_csvs(token_metadata_lookup, OUTPUT_DIRECTORY)
        await build_stablecoin_cex_flows_csvs(token_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)
        supply_event_results = await build_token_supply_events_csvs(token_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)
        await build_pool_reserves_daily_csv(pool_metadata_lookup, daily_prices, OUTPUT_DIRECTORY)

        master_summary_dataframe = build_master_summary_daily_dataframe(
            daily_swap_volume_dataframe=swap_results.get('02_daily'),
            daily_fees_dataframe=fees_results.get('06'),
            daily_liquidity_dataframe=liquidity_results.get('04'),
            daily_stablecoin_transfer_dataframe=stablecoin_transfer_results.get('10'),
            daily_cex_flows_dataframe=cex_flow_results.get('08'),
            daily_supply_events_dataframe=supply_event_results.get('14'),
        )
        export_dataframe_to_csv(master_summary_dataframe, '16_MASTER_SUMMARY_DAILY.csv', OUTPUT_DIRECTORY)
        cross_chain_dataframe = build_cross_chain_comparison_dataframe(master_summary_dataframe)
        export_dataframe_to_csv(cross_chain_dataframe, '17_cross_chain_comparison_daily.csv', OUTPUT_DIRECTORY)

        await build_dex_swap_volume_raw_csvs(pool_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_dex_liquidity_raw_csvs(pool_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_dex_fees_raw_csvs(pool_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_cex_flows_raw_csvs(token_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_stablecoin_transfer_raw_csvs(token_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_stablecoin_cex_flows_raw_csvs(token_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_token_supply_events_raw_csvs(token_metadata_lookup, OUTPUT_V2_DIRECTORY)
        await build_pool_reserves_raw_csv(pool_metadata_lookup, OUTPUT_V2_DIRECTORY)

        await build_dex_swap_volume_csvs(
            pool_metadata_lookup, hourly_prices, OUTPUT_V3_DIRECTORY,
            bucket_key_format=HOURLY_BUCKET_KEY_FORMAT,
        )
        await build_dex_liquidity_csvs(
            pool_metadata_lookup, hourly_prices, OUTPUT_V3_DIRECTORY,
            bucket_key_format=HOURLY_BUCKET_KEY_FORMAT,
        )
        await build_dex_fees_csvs(
            pool_metadata_lookup, hourly_prices, OUTPUT_V3_DIRECTORY,
            bucket_key_format=HOURLY_BUCKET_KEY_FORMAT,
        )
        await build_cex_flows_csvs(
            token_metadata_lookup, hourly_prices, OUTPUT_V3_DIRECTORY,
            bucket_key_format=HOURLY_BUCKET_KEY_FORMAT,
        )
        await build_stablecoin_transfer_csvs(
            token_metadata_lookup, OUTPUT_V3_DIRECTORY
        )
        await build_stablecoin_cex_flows_csvs(
            token_metadata_lookup, hourly_prices, OUTPUT_V3_DIRECTORY,
            bucket_key_format=HOURLY_BUCKET_KEY_FORMAT,
        )
        await build_token_supply_events_csvs(
            token_metadata_lookup, hourly_prices, OUTPUT_V3_DIRECTORY,
            bucket_key_format=HOURLY_BUCKET_KEY_FORMAT,
        )
        await build_pool_reserves_daily_csv(pool_metadata_lookup, daily_prices, OUTPUT_V3_DIRECTORY)

    finally:
        await db.disConnect()
        print('Done.')


if __name__ == '__main__':
    asyncio.run(main())
