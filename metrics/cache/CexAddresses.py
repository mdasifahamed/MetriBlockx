from typing import List, Dict, Optional


class CEXAddressCache:
    _instance = None
    
    def __init__(self):
        self.cexAddress_by_chain = {}
    
    @classmethod    
    def _getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def load(self, cexAddresses: List[Dict]):
        for cexAddress in cexAddresses:
            chain_id = cexAddress['chain_id']
            if chain_id not in self.cexAddress_by_chain:
                self.cexAddress_by_chain[chain_id] = {}
            address_lower = cexAddress['address'].lower()
            self.cexAddress_by_chain[chain_id][address_lower] = cexAddress
                
    def getAllCexByChainId(self, chainId: int) -> Optional[Dict]:
        return self.cexAddress_by_chain.get(chainId)
    
    def getCexByAddressNChain(self, chainId: int, address: str) -> Optional[Dict]:
        cexAddress = self.cexAddress_by_chain.get(chainId)
        if cexAddress is None:
            return None
        return cexAddress.get(address.lower())
    
    def getCexNameByAddressNChain(self, chainId: int, address: str) -> Optional[str]:
        cexAddress = self.cexAddress_by_chain.get(chainId)
        if cexAddress is None:
            return None
        entry = cexAddress.get(address.lower())
        if entry is None:
            return None
        return entry['cex_name']
