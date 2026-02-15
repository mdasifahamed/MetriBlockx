from typing import List, Dict, Any
from .tokens.BaseTokenProcessor import BaseTokenProcessor
from .tokens.UsdtProcessor import UsdtProcessor
from .tokens.WbtcProcessor import WbtcProcessor
from .pools.UniSwapV2Like import UniswapV2LikeMetrics
from .pools.UniswapV3Like import UniswapV3LikeMetrics
from ..cache.CacheTokenPool import TokenNPoolCache
from .tokens.BaseWrappedTokenProcessor import WrappedAssetProcessor


class EvmProcessor:
    
    def __init__(self, chainId: int):
        self._chainId = chainId
        self._cache = TokenNPoolCache._getInstance()
    
    async def processAllEvents(self, eventsByContract: Dict[str, Dict[str, List[Any]]]) -> Dict:
        results = {'tokens': {}, 'pools': {}}
        
        token_cache = self._cache.getAllTokenByChainId(self._chainId)
        pool_cache = self._cache.getAllPoolsByChainId(self._chainId)
        
        for address, eventsByName in eventsByContract.items():
            addr = address.lower()
            
            if token_cache and addr in token_cache:
                processor = self._getTokenProcessor(addr, token_cache)
                results['tokens'][addr] = await processor.processAllEvents(eventsByName)
            
            elif pool_cache and addr in pool_cache:
                processor = self._getPoolProcessor(addr, pool_cache)
                results['pools'][addr] = await processor.processAllEvents(eventsByName)
        
        return results
    
    def _getTokenProcessor(self, tokenAddress: str, token_cache: Dict) -> BaseTokenProcessor:
        token = token_cache.get(tokenAddress)
        token_type = token.get('token_type', 'ERC20')
        token_symbol = token.get('token_symbol', '').upper()
        
        if token_type == 'WRAPPED' or token_symbol in ['WETH', 'WBNB', 'WPOL']:
            return WrappedAssetProcessor(self._chainId)
        
        if token_symbol == 'USDT':
            return UsdtProcessor(self._chainId)
        if token_symbol == 'WBTC':
            return WbtcProcessor(self._chainId)
        
        return BaseTokenProcessor(self._chainId)
    
    def _getPoolProcessor(self, poolAddress: str, pool_cache: Dict):
        pool = pool_cache.get(poolAddress)
        dex_version = (pool.get('dex_version') or 'v2').lower()
        
        if dex_version == 'v3':
            return UniswapV3LikeMetrics(self._chainId)
        return UniswapV2LikeMetrics(self._chainId)


def groupEventsByContract(events: List[Any]) -> Dict[str, Dict[str, List[Any]]]:
    grouped = {}
    
    for event in events:
        addr = event.get('contract_address', '').lower()
        name = event.get('event_name', '')
        
        if addr not in grouped:
            grouped[addr] = {}
        if name not in grouped[addr]:
            grouped[addr][name] = []
        
        grouped[addr][name].append(event)
    
    return grouped