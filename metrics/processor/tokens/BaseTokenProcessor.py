from typing import List, Any, Protocol
from decimal import Decimal
from abc import ABC, abstractmethod
from ...cache.CacheTokenPool import TokenNPoolCache
from ...cache.CexAddresses import CEXAddressCache


class BaseTokenProcessor(ABC):

    
    def __init__(self, chainId: int):
        self._chainId = chainId
        self._cexAddresses = CEXAddressCache()._getInstance()
        self._cexAddressCache = CEXAddressCache()._getInstance().getAllCexByChainId(self._chainId)
        self._tokenCache = TokenNPoolCache()._getInstance().tokens_by_chain(self._chainId)
    
    @abstractmethod
    def calculateTotalTransferNative(self, transferEvent: List[Any]) -> str:
        # calculate token transfer between only wallet to wallet not the within the CEx wallet
        pass
    
    @abstractmethod
    def calculateTotalCeXFlow(self, transferEvents: List[Any]) -> str:
        # calculate flow between walet and cex condition internal transfer between the cex wallet it self is avoied only cex-> eoa and eoa->
        pass
    
    @abstractmethod
    def calculateTotalMintAmount(self, mintEvents: List[Any]) -> str:
        # Calculate total minted amount of the token
        pass
    
    @abstractmethod
    def calculateTotalBurnAmount(self, burnEvents: List[Any]) -> str:
        # Calculate total minted amount of the token
        pass
    
    def _is_cex_address(self, address: str) -> bool:
        """Check if address belongs to a CEX"""
        return False if self._cexAddresses.getCexNameByAddressNChain(self._chainId,address) is None else True
    