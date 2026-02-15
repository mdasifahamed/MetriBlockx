from typing import List, Dict, Optional


class TokenNPoolCache:
    _instance = None
    
    def __init__(self):
        self.pools_by_chain = {}
        self.tokens_by_chain = {}
    
    @classmethod    
    def _getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def load(self, tokens: List[Dict], pools: List[Dict]):
        for token in tokens:
            chain_id = token['chain_id']
            if chain_id not in self.tokens_by_chain:
                self.tokens_by_chain[chain_id] = {}
            token_address_lower = token['token_address'].lower()
            self.tokens_by_chain[chain_id][token_address_lower] = token
        
        for pool in pools:
            chain_id = pool['chain_id']
            if chain_id not in self.pools_by_chain:
                self.pools_by_chain[chain_id] = {}
            pool_address_lower = pool['pool_address'].lower()
            self.pools_by_chain[chain_id][pool_address_lower] = pool
                
    def getAllTokenByChainId(self, chainId: int) -> Optional[Dict]:
        return self.tokens_by_chain.get(chainId)
    
    def getAllPoolsByChainId(self, chainId: int) -> Optional[Dict]:
        return self.pools_by_chain.get(chainId)
    
    def getTokenByAddressNChain(self, chainId: int, address: str) -> Optional[Dict]:
        tokens = self.tokens_by_chain.get(chainId)
        if tokens is None:
            return None
        return tokens.get(address.lower())
    
    def getPoolByAddressNChain(self, chainId: int, address: str) -> Optional[Dict]:
        pools = self.pools_by_chain.get(chainId)
        if pools is None:
            return None
        return pools.get(address.lower())
    
    def getTokenDecimalByAddressNChain(self, chainId: int, address: str) -> Optional[int]:
        token = self.getTokenByAddressNChain(chainId, address)
        if token is None:
            return None
        return token['token_decimal']
    
    def getPoolTypeByAddressNChainId(self, chainId: int, address: str) -> Optional[str]:
        pool = self.getPoolByAddressNChain(chainId, address)
        if pool is None:
            return None
        return pool['dex_version']