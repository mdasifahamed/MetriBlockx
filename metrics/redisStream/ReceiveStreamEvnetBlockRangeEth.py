import asyncio
import json
import time
from typing import Any, Dict
from redis.asyncio import Redis
from .redisClient import get_redis

class ReceiveEthEventBlockRange:
    def __init__(self):
        self.ethStream = 'eth_stream'
        self.ethGroup = 'eth_group'
        self.ethWorker = 'eth_Worker'
        
    
    async def __redisClient(self)-> Redis:
        try:
            return await get_redis()
        except Exception as e:
            print(f"Falied to get Redis Client {str(e)}")
            raise e
        
        
    async def receviveMessage(self):
        redisClient = await self.__redisClient()
        while True:
            notifications = await redisClient.xreadgroup(
                self.ethGroup,
                self.ethWorker,
                streams={self.ethStream:'>'},
                count=1,
                block=5000
                )
            
            if not notifications:
                continue
            stream_name, notificationList = notifications[0]
            notificationId, notificationFileds = notificationList[0]
            
            notification_id = notificationId
            notification_fields = {key.decode():value for key, value in notificationFileds.item}
            notification_data =  json.load(notification_fields['data'])
            
            # DB callls 
            # metrics genertion (total swaps, transfers, last swap price, total voulme, value in and out, fees collected, stable coins transfer)
            # metrics string
            # blokc tracking updated 
            # ack back. 
            