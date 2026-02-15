from typing import List, Any, Dict
from decimal import Decimal
import pandas as pd
from ...cache.CacheTokenPool import TokenNPoolCache
from ...storage.PoolMetricsStorage import PoolMetricsStorage


class UniswapV3LikeMetrics:
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

        event_arguments_dataframe['amount0'] = event_arguments_dataframe['amount0'].apply(lambda value: abs(int(value)))
        event_arguments_dataframe['amount1'] = event_arguments_dataframe['amount1'].apply(lambda value: abs(int(value)))

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        pool_decimal_map = self._resolvePoolDecimals(event_arguments_dataframe['contract_address'].unique())

        event_arguments_dataframe = event_arguments_dataframe[
            event_arguments_dataframe['contract_address'].str.lower().isin(pool_decimal_map.keys())
        ]

        if event_arguments_dataframe.empty:
            return {'results': [], 'count': 0}

        event_arguments_dataframe['contract_address'] = event_arguments_dataframe['contract_address'].str.lower()

        event_arguments_dataframe['amount0_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['amount0']) / Decimal(10 ** pool_decimal_map[row['contract_address']][0]),
            axis=1
        )
        event_arguments_dataframe['amount1_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['amount1']) / Decimal(10 ** pool_decimal_map[row['contract_address']][1]),
            axis=1
        )

        grouped_swaps = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            volume0=('amount0', lambda values: sum(values)),
            volume0_decimal=('amount0_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            volume1=('amount1', lambda values: sum(values)),
            volume1_decimal=('amount1_decimal', lambda decimals: sum(decimals, Decimal('0'))),
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
        all_liquidity_results = []

        if mintEvents:
            liquidity_additions = await self._aggregateLiquidityPandas(mintEvents, 'ADD')
            all_liquidity_results.extend(liquidity_additions)

        if burnEvents:
            liquidity_removals = await self._aggregateLiquidityPandas(burnEvents, 'REMOVE')
            all_liquidity_results.extend(liquidity_removals)

        inserted_count = await self._storage.insertPoolLiquidity(all_liquidity_results)
        return {'results': all_liquidity_results, 'count': inserted_count}

    async def calculatesTotalFees(self, collectEvents: List[Any]) -> Dict:
        if not collectEvents:
            return {'results': [], 'count': 0}

        events_dataframe = pd.DataFrame(collectEvents)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        event_arguments_dataframe['amount0'] = event_arguments_dataframe['amount0'].apply(int)
        event_arguments_dataframe['amount1'] = event_arguments_dataframe['amount1'].apply(int)

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        pool_decimal_map = self._resolvePoolDecimals(
            event_arguments_dataframe['contract_address'].unique()
        )

        event_arguments_dataframe = event_arguments_dataframe[
            event_arguments_dataframe['contract_address'].str.lower().isin(pool_decimal_map.keys())
        ]

        if event_arguments_dataframe.empty:
            return {'results': [], 'count': 0}

        event_arguments_dataframe['contract_address'] = event_arguments_dataframe['contract_address'].str.lower()

        event_arguments_dataframe['amount0_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['amount0']) / Decimal(10 ** pool_decimal_map[row['contract_address']][0]),
            axis=1
        )
        event_arguments_dataframe['amount1_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['amount1']) / Decimal(10 ** pool_decimal_map[row['contract_address']][1]),
            axis=1
        )

        grouped_fees = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            total_fees_0=('amount0', lambda values: sum(values)),
            total_fees_0_decimal=('amount0_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            total_fees_1=('amount1', lambda values: sum(values)),
            total_fees_1_decimal=('amount1_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            collect_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        fee_results = []
        for grouped_row in grouped_fees.to_dict('records'):
            pool_address = grouped_row['contract_address']

            fee_results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': pool_address,
                'collect_count': grouped_row['collect_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
                'fees_token_0': str(grouped_row['total_fees_0']),
                'fees_token_0_human': f"{grouped_row['total_fees_0_decimal']:.8f}",
                'fees_token_1': str(grouped_row['total_fees_1']),
                'fees_token_1_human': f"{grouped_row['total_fees_1_decimal']:.8f}",
            })

        inserted_count = await self._storage.insertPoolFees(fee_results)
        return {'results': fee_results, 'count': inserted_count}

    async def _aggregateLiquidityPandas(self, events: List[Any], liquidityType: str) -> List[Dict]:
        events_dataframe = pd.DataFrame(events)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        event_arguments_dataframe['amount0'] = event_arguments_dataframe['amount0'].apply(int)
        event_arguments_dataframe['amount1'] = event_arguments_dataframe['amount1'].apply(int)

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        pool_decimal_map = self._resolvePoolDecimals(
            event_arguments_dataframe['contract_address'].unique()
        )

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

        liquidity_results = []
        for grouped_row in grouped_liquidity.to_dict('records'):
            pool_address = grouped_row['contract_address']

            liquidity_results.append({
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

        return liquidity_results

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

        if eventsByName.get('Collect'):
            fees_result = await self.calculatesTotalFees(eventsByName['Collect'])
            results['fees'] = fees_result

        return results