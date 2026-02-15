from .BaseTokenProcessor import BaseTokenProcessor
from typing import List,Any,Dict
import pandas as pd

class WbtcProcessor(BaseTokenProcessor):
    async def calculateTotalBurnAmount(self, reddemEvents: List[Any]) -> Dict:
        return await self._calculateSupplyAmount(reddemEvents, fieldName='value', supplyType='BURN')

