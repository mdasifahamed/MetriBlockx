from .BaseTokenProcessor import BaseTokenProcessor
from typing import List, Any, Dict


class UsdtProcessor(BaseTokenProcessor):
    async def calculateTotalMintAmount(self, issueEvents: List[Any]) -> Dict:
        return await self._calculateSupplyAmount(issueEvents, fieldName='amount', supplyType='ISSUE')

    async def calculateTotalBurnAmount(self, redeemEvents: List[Any]) -> Dict:
        return await self._calculateSupplyAmount(redeemEvents, fieldName='amount', supplyType='BURN')

