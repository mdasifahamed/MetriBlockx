from typing import List,any
from decimal import Decimal
from ...cache.CacheTokenPool import TokenNPoolCache
from ...storage.PoolMetricsStorage import PoolMetricsStorage
class UniswapV3LikeMetrics:
    def __init__(self,chainId:int):
        self._chainId = chainId
        self._tokenPoolCache = TokenNPoolCache._getInstance()
        self._storage = PoolMetricsStorage()

    async def calculatesTotalSwapAmount(self,swapEvents:List[any]) -> bool:
        poolBlockSwaps = self._groupByPoolAndBlock(swapEvents)
        results = []

        for (poolAddress, blockNumber), events in poolBlockSwaps.items():
            pool = self._tokenPoolCache.getPoolByAddressNChain(self._chainId, poolAddress)
            if pool is None:
                continue

            token0Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_0_address'])
            token1Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_1_address'])

            totalVolumeToken0 = 0
            totalVolumeToken1 = 0
            transactionHashes = []

            for event in events:
                swapData = event['event_args']
                totalVolumeToken0 += abs(int(swapData['amount0']))
                totalVolumeToken1 += abs(int(swapData['amount1']))
                transactionHashes.append(event['transaction_hash'])

            results.append({
                'block_number': blockNumber,
                'block_time_stamp': events[0]['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': poolAddress,
                'swap_count': len(events),
                'transaction_hashes': transactionHashes,
                'volume_token_0': str(totalVolumeToken0),
                'volume_token_0_human': str(Decimal(totalVolumeToken0) / Decimal(10 ** token0Decimal)),
                'volume_token_1': str(totalVolumeToken1),
                'volume_token_1_human': str(Decimal(totalVolumeToken1) / Decimal(10 ** token1Decimal)),
            })

        return await self._storage.insertPoolSwaps(results)

    async def calculatesTotalLiquidityAmount(self,mintEvents:List[any],burnEvents:List[any]) -> bool:
        addGroups = self._groupByPoolAndBlock(mintEvents)
        removeGroups = self._groupByPoolAndBlock(burnEvents)
        results = []

        for (poolAddress, blockNumber), events in addGroups.items():
            result = self._aggregateLiquidity(poolAddress, blockNumber, events, 'ADD')
            if result:
                results.append(result)

        for (poolAddress, blockNumber), events in removeGroups.items():
            result = self._aggregateLiquidity(poolAddress, blockNumber, events, 'REMOVE')
            if result:
                results.append(result)

        return await self._storage.insertPoolLiquidity(results)

    async def calculatesTotalFees(self,collectEvents:List[any]) -> bool:
        poolBlockCollects = self._groupByPoolAndBlock(collectEvents)
        results = []

        for (poolAddress, blockNumber), events in poolBlockCollects.items():
            pool = self._tokenPoolCache.getPoolByAddressNChain(self._chainId, poolAddress)
            if pool is None:
                continue

            token0Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_0_address'])
            token1Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_1_address'])

            totalFeesToken0 = 0
            totalFeesToken1 = 0
            transactionHashes = []

            for event in events:
                args = event['event_args']
                totalFeesToken0 += int(args['amount0'])
                totalFeesToken1 += int(args['amount1'])
                transactionHashes.append(event['transaction_hash'])

            results.append({
                'block_number': blockNumber,
                'block_time_stamp': events[0]['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': poolAddress,
                'collect_count': len(events),
                'transaction_hashes': transactionHashes,
                'fees_token_0': str(totalFeesToken0),
                'fees_token_0_human': str(Decimal(totalFeesToken0) / Decimal(10 ** token0Decimal)),
                'fees_token_1': str(totalFeesToken1),
                'fees_token_1_human': str(Decimal(totalFeesToken1) / Decimal(10 ** token1Decimal)),
            })

        return await self._storage.insertPoolFees(results)

    def _aggregateLiquidity(self,poolAddress:str,blockNumber:int,events:List[any],liquidityType:str):
        pool = self._tokenPoolCache.getPoolByAddressNChain(self._chainId, poolAddress)
        if pool is None:
            return None

        token0Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_0_address'])
        token1Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_1_address'])

        totalAmountToken0 = 0
        totalAmountToken1 = 0
        transactionHashes = []

        for event in events:
            args = event['event_args']
            totalAmountToken0 += int(args['amount0'])
            totalAmountToken1 += int(args['amount1'])
            transactionHashes.append(event['transaction_hash'])

        return {
            'block_number': blockNumber,
            'block_time_stamp': events[0]['block_time_stamp'],
            'chain_id': self._chainId,
            'pool_address': poolAddress,
            'liquidity_type': liquidityType,
            'transaction_count': len(events),
            'transaction_hashes': transactionHashes,
            'amount_token_0': str(totalAmountToken0),
            'amount_token_0_human': str(Decimal(totalAmountToken0) / Decimal(10 ** token0Decimal)),
            'amount_token_1': str(totalAmountToken1),
            'amount_token_1_human': str(Decimal(totalAmountToken1) / Decimal(10 ** token1Decimal)),
        }

    def _groupByPoolAndBlock(self,events: List[any]):
        groups = {}
        for event in events:
            key = (event['contract_address'], event['block_number'])
            if key not in groups:
                groups[key] = []
            groups[key].append(event)
        return groups
