from typing import List,any
from decimal import Decimal
from ...cache.CacheTokenPool import TokenNPoolCache
from ...storage.PoolMetricsStorage import PoolMetricsStorage
class UniswapV2LikeMetrics:
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
                totalVolumeToken0 += int(swapData['amount0In']) + int(swapData['amount0Out'])
                totalVolumeToken1 += int(swapData['amount1In']) + int(swapData['amount1Out'])
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

    async def calculatesReserves(self,syncEvents:List[any]) -> bool:
        poolBlockSyncs = self._groupByPoolAndBlock(syncEvents)
        results = []

        for (poolAddress, blockNumber), events in poolBlockSyncs.items():
            pool = self._tokenPoolCache.getPoolByAddressNChain(self._chainId, poolAddress)
            if pool is None:
                continue

            token0Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_0_address'])
            token1Decimal = self._tokenPoolCache.getTokenDecimalByAddressNChain(self._chainId, pool['token_1_address'])

            lastEvent = events[-1]
            syncData = lastEvent['event_args']
            reserve0 = int(syncData['reserve0'])
            reserve1 = int(syncData['reserve1'])
            transactionHashes = [e['transaction_hash'] for e in events]

            results.append({
                'block_number': blockNumber,
                'block_time_stamp': lastEvent['block_time_stamp'],
                'chain_id': self._chainId,
                'pool_address': poolAddress,
                'reserve_token_0': str(Decimal(reserve0) / Decimal(10 ** token0Decimal)),
                'reserve_token_1': str(Decimal(reserve1) / Decimal(10 ** token1Decimal)),
                'transaction_hashes': transactionHashes,
            })

        return await self._storage.insertPoolReserves(results)

    def _groupByPoolAndBlock(self,swapEvents: List[any]):
        groups = {}
        for event in swapEvents:
            key = (event['contract_address'], event['block_number'])
            if key not in groups:
                groups[key] = []
            groups[key].append(event)
        return groups
    