from typing import List, Any, Dict
from decimal import Decimal
import pandas as pd
from ...cache.CacheTokenPool import TokenNPoolCache
from ...storage.PoolMetricsStorage import PoolMetricsStorage


class UniswapV2LikeMetrics:
    def __init__(self, chainId: int):
        self._chainId = chainId
        self._tokenPoolCache = TokenNPoolCache._getInstance()
        self._storage = PoolMetricsStorage()

    def _formatDecimal(self, raw_amount: int, decimals: int) -> str:
        decimal_value = Decimal(raw_amount) / Decimal(10 ** decimals)
        return f"{decimal_value:.8f}"

    def _resolvePoolDecimals(self, poolAddresses):
        pool_info = {}
        for address in poolAddresses:
            address_lower = address.lower()
            pool = self._tokenPoolCache.getPoolByAddressNChain(self._chainId, address_lower)
            if pool:
                token0_decimals = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_0_address'])
                token1_decimals = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_1_address'])
                pool_info[address_lower] = (token0_decimals, token1_decimals, pool.get('pool_symbol', 'UNKNOWN'))
        return pool_info

    async def calculatesTotalSwapAmount(self, swapEvents: List[Any]) -> Dict:
        if not swapEvents:
            return {'results': [], 'count': 0}

        events_dataframe = pd.DataFrame(swapEvents)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        for column in ['amount0In', 'amount0Out', 'amount1In', 'amount1Out']:
            event_arguments_dataframe[column] = event_arguments_dataframe[column].apply(int)

        event_arguments_dataframe['volume0'] = event_arguments_dataframe['amount0In'] + event_arguments_dataframe['amount0Out']
        event_arguments_dataframe['volume1'] = event_arguments_dataframe['amount1In'] + event_arguments_dataframe['amount1Out']

        event_arguments_dataframe[['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']] = events_dataframe[['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']].values

        pool_decimal_map = self._resolvePoolDecimals(event_arguments_dataframe['contract_address'].unique())

        event_arguments_dataframe = event_arguments_dataframe[
            event_arguments_dataframe['contract_address'].str.lower().isin(pool_decimal_map.keys())
        ]

        if event_arguments_dataframe.empty:
            return {'results': [], 'count': 0}

        event_arguments_dataframe['contract_address'] = event_arguments_dataframe['contract_address'].str.lower()

        event_arguments_dataframe['volume0_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['volume0']) / Decimal(10 ** pool_decimal_map[row['contract_address']][0]),
            axis=1
        )
        event_arguments_dataframe['volume1_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['volume1']) / Decimal(10 ** pool_decimal_map[row['contract_address']][1]),
            axis=1
        )

        grouped_swaps = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            volume0=('volume0', lambda values: sum(values)),
            volume0_decimal=('volume0_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            volume1=('volume1', lambda values: sum(values)),
            volume1_decimal=('volume1_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            swap_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_swaps.to_dict('records'):
            pool_address = grouped_row['contract_address']

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': pool_address,
                'swap_count': grouped_row['swap_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
                'volume_token_0': str(grouped_row['volume0']),
                'volume_token_0_human': f"{grouped_row['volume0_decimal']:.8f}",
                'volume_token_1': str(grouped_row['volume1']),
                'volume_token_1_human': f"{grouped_row['volume1_decimal']:.8f}",
            })

        inserted_count = await self._storage.insertPoolSwaps(results)
        return {'results': results, 'count': inserted_count}

    async def calculatesTotalLiquidityAmount(self, mintEvents: List[Any], burnEvents: List[Any]) -> Dict:
        results = []

        if mintEvents:
            add_results = await self._aggregateLiquidityPandas(mintEvents, 'ADD')
            results.extend(add_results)
        if burnEvents:
            remove_results = await self._aggregateLiquidityPandas(burnEvents, 'REMOVE')
            results.extend(remove_results)

        inserted_count = await self._storage.insertPoolLiquidity(results)
        return {'results': results, 'count': inserted_count}

    async def _aggregateLiquidityPandas(self, events: List[Any], liquidityType: str) -> List[Dict]:
        events_dataframe = pd.DataFrame(events)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        event_arguments_dataframe['amount0'] = event_arguments_dataframe['amount0'].apply(int)
        event_arguments_dataframe['amount1'] = event_arguments_dataframe['amount1'].apply(int)

        event_arguments_dataframe[['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']] = events_dataframe[['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']].values

        pool_decimal_map = self._resolvePoolDecimals(event_arguments_dataframe['contract_address'].unique())

        event_arguments_dataframe = event_arguments_dataframe[
            event_arguments_dataframe['contract_address'].str.lower().isin(pool_decimal_map.keys())
        ]

        if event_arguments_dataframe.empty:
            return []

        event_arguments_dataframe['contract_address'] = event_arguments_dataframe['contract_address'].str.lower()

        event_arguments_dataframe['amount0_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['amount0']) / Decimal(10 ** pool_decimal_map[row['contract_address']][0]),
            axis=1
        )
        event_arguments_dataframe['amount1_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['amount1']) / Decimal(10 ** pool_decimal_map[row['contract_address']][1]),
            axis=1
        )

        grouped_liquidity = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            total_amount_0=('amount0', lambda values: sum(values)),
            total_amount_0_decimal=('amount0_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            total_amount_1=('amount1', lambda values: sum(values)),
            total_amount_1_decimal=('amount1_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            transaction_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_liquidity.to_dict('records'):
            pool_address = grouped_row['contract_address']

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': pool_address,
                'liquidity_type': liquidityType,
                'transaction_count': grouped_row['transaction_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
                'amount_token_0': str(grouped_row['total_amount_0']),
                'amount_token_0_human': f"{grouped_row['total_amount_0_decimal']:.8f}",
                'amount_token_1': str(grouped_row['total_amount_1']),
                'amount_token_1_human': f"{grouped_row['total_amount_1_decimal']:.8f}",
            })

        return results

    async def calculatesReserves(self, syncEvents: List[Any]) -> Dict:
        if not syncEvents:
            return {'results': [], 'count': 0}

        events_dataframe = pd.DataFrame(syncEvents)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        event_arguments_dataframe['reserve0'] = event_arguments_dataframe['reserve0'].apply(int)
        event_arguments_dataframe['reserve1'] = event_arguments_dataframe['reserve1'].apply(int)

        event_arguments_dataframe[['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']] = events_dataframe[['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']].values

        pool_decimal_map = self._resolvePoolDecimals(event_arguments_dataframe['contract_address'].unique())

        event_arguments_dataframe = event_arguments_dataframe[
            event_arguments_dataframe['contract_address'].str.lower().isin(pool_decimal_map.keys())
        ]

        if event_arguments_dataframe.empty:
            return {'results': [], 'count': 0}

        event_arguments_dataframe['contract_address'] = event_arguments_dataframe['contract_address'].str.lower()

        grouped_reserves = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            reserve0=('reserve0', 'last'),
            reserve1=('reserve1', 'last'),
            block_time_stamp=('block_time_stamp', 'last'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_reserves.to_dict('records'):
            pool_address = grouped_row['contract_address']
            token0_decimal, token1_decimal, pool_symbol = pool_decimal_map[pool_address]

            reserve0 = grouped_row['reserve0']
            reserve1 = grouped_row['reserve1']

            reserve0_decimal = Decimal(reserve0) / Decimal(10 ** token0_decimal)
            reserve1_decimal = Decimal(reserve1) / Decimal(10 ** token1_decimal)

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': pool_address,
                'reserve_token_0': f"{reserve0_decimal:.8f}",
                'reserve_token_1': f"{reserve1_decimal:.8f}",
                'transaction_hashes': grouped_row['transaction_hashes'],
            })

        inserted_count = await self._storage.insertPoolReserves(results)
        return {'results': results, 'count': inserted_count}

    async def processAllEvents(self, eventsByName: Dict[str, List[Any]]) -> Dict[str, Any]:
        results = {}

        if eventsByName.get('Swap'):
            swap_result = await self.calculatesTotalSwapAmount(eventsByName['Swap'])
            results['swap'] = swap_result

        mint_events = eventsByName.get('Mint', [])
        burn_events = eventsByName.get('Burn', [])
        if mint_events or burn_events:
            liquidity_result = await self.calculatesTotalLiquidityAmount(mint_events, burn_events)
            results['liquidity'] = liquidity_result

        if eventsByName.get('Sync'):
            reserve_result = await self.calculatesReserves(eventsByName['Sync'])
            results['reserve'] = reserve_result

        return results