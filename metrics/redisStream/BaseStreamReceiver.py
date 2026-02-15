import json
from typing import Dict
from redis.asyncio import Redis
from .redisClient import get_redis
from ..db.queries import DBQueries
from ..processor.EvmProcessor import EvmProcessor, groupEventsByContract


class BaseStreamReceiver:
    def __init__(self, chainId: int, streamName: str, groupName: str, workerName: str):
        self._chainId = chainId
        self._streamName = streamName
        self._groupName = groupName
        self._workerName = workerName
        self._chainName = {1: 'Ethereum', 56: 'BNB', 137: 'Polygon'}.get(chainId, f'Chain-{chainId}')
        self._queries = DBQueries()
        self._evmProcessor = EvmProcessor(chainId)

    async def _getRedisClient(self) -> Redis:
        return await get_redis()

    async def receiveMessages(self):
        redis_client = await self._getRedisClient()
        print(f"{self._chainName} Stream receiver started")

        while True:
            notifications = await redis_client.xreadgroup(
                self._groupName,
                self._workerName,
                streams={self._streamName: '>'},
                count=3,
                block=5000
            )

            if not notifications:
                continue

            stream_name, notification_list = notifications[0]

            for notification_id, notification_fields in notification_list:
                try:
                    await self._processNotification(redis_client, notification_id, notification_fields)
                except Exception as error:
                    print(f"{self._chainName} Error: {str(error)}")

    async def _processNotification(self, redis_client: Redis, notification_id: str, notification_fields: Dict):
        data_key = b'data' if b'data' in notification_fields else 'data'
        raw_data = notification_fields[data_key]
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8')
        notification_data = json.loads(raw_data)

        block_numbers = await self._queries.getEventBlockNumbers(
            notification_data['chainId'],
            notification_data['createdAt']
        )

        if not block_numbers:
            await redis_client.xack(self._streamName, self._groupName, notification_id)
            return

        decoded_events = await self._queries.getDecodedEventsByBlocks(self._chainId, block_numbers)

        if not decoded_events:
            await redis_client.xack(self._streamName, self._groupName, notification_id)
            return

        events_grouped_by_contract = groupEventsByContract(decoded_events)
        processing_results = await self._evmProcessor.processAllEvents(events_grouped_by_contract)
        pool_count = len(processing_results.get('pools', {}))
        asset_count = len(processing_results.get('tokens', {}))

        print(f"{self._chainName} Blocks {min(block_numbers)}-{max(block_numbers)} | Events: {len(decoded_events)} | Pools: {pool_count} | Assets: {asset_count}")

        await self._queries.insertMetricsGenerated(self._chainId, block_numbers)
        await redis_client.xack(self._streamName, self._groupName, notification_id)


class EthereumStreamReceiver(BaseStreamReceiver):
    def __init__(self):
        super().__init__(1, 'eth_stream', 'eth_group', 'eth_worker')


class BnbStreamReceiver(BaseStreamReceiver):
    def __init__(self):
        super().__init__(56, 'bnb_stream', 'bnb_group', 'bnb_worker')


class PolygonStreamReceiver(BaseStreamReceiver):
    def __init__(self):
        super().__init__(137, 'pol_stream', 'pol_group', 'pol_worker')