from typing import List, Dict


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
            self.tokens_by_chain[chain_id][token['token_address']] = token
        
        for pool in pools:
            chain_id = pool['chain_id']
            if chain_id not in self.pools_by_chain:
                self.pools_by_chain[chain_id] = {}
            self.pools_by_chain[chain_id][pool['pool_address']] = pool
                
    def getAllTokenByChainId(self, chainId: int):
        return self.tokens_by_chain.get(chainId)
    
    def getAllPoolsByChainId(self, chainId: int):
        return self.pools_by_chain.get(chainId)
    
    def getTokenByAddressNChain(self, chainId: int, address: str):

        tokens = self.tokens_by_chain.get(chainId)
        assert tokens is not None, f"Chain {chainId} not found in cache" 
        token = tokens.get(address)
        assert token is not None, f"Token {address} not found on chain {chainId}" 
        return token
    
    def getPoolByAddressNChain(self, chainId: int, address: str):

        pools = self.pools_by_chain.get(chainId)
        assert pools is not None, f"Chain {chainId} not found in cache"  
        pool = pools.get(address)
        assert pool is not None, f"Pool {address} not found on chain {chainId}"  
        return pool
    
    def getTokenDecimalByAddressNChain(self, chainId: int, address: str):
        """Get token decimal - ASSUMES valid chainId and address"""
        token = self.getTokenByAddressNChain(chainId, address)
        return token['token_decimal']
    
    def getPoolTypeByAddressNChainId(self, chainId: int, address: str):
        """Get pool type - ASSUMES valid chainId and address"""
        pool = self.getPoolByAddressNChain(chainId, address)
        return pool['dex_version']