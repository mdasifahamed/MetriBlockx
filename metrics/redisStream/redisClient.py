import os
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
load_dotenv()

class RedisConnection:
    _lock = asyncio.Lock() 
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis: Redis = None
            self._initialized = False
            
            
    async def connect(self) -> Redis:

        async with self._lock:
            if self.redis is None:
                try:
                    self.redis = await Redis.from_url(
                        self.redis_url,
                        encoding='utf-8',
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_keepalive=True,
                        max_connections=10,  # Connection pool size
                        retry_on_timeout=True,
                    )
                    
                    # Test connection
                    await self.redis.ping()
                    self._initialized = True
                    
                except Exception as err:
                    print(f"Failed to connect to Redis: {str(err)}")
                    self.redis = None
                    raise

        return self.redis
    
    async def disconnect(self) -> None:
        if self.redis:
            try:
                await self.redis.close()
                print("Redis connection closed")
                self.redis = None
                self._initialized = False
            except Exception as err:
                print(f"Error closing Redis connection: {str(err)}")
                
    async def get_client(self) -> Redis:
        if self.redis is None:
            await self.connect()
        return self.redis

redis_client = RedisConnection()
async def get_redis() -> Redis:
    return await redis_client.get_client()


