import asyncio
import signal
from .redisStream.ReceiveStreamEvnetBlockRangeEth import ReceiveEthEventBlockRange
from .redisStream.redisClient import redis_client
from .db.db_connection import db
from .db.queries import DBQueries
from .cache.CacheTokenPool import TokenNPoolCache
from .cache.CexAddresses import CEXAddressCache


async def main():
    receiveEthStream = ReceiveEthEventBlockRange()
    loop = asyncio.get_running_loop()
    main_task = asyncio.current_task()
    queries = DBQueries()
    tokenNPoolCache = TokenNPoolCache()._getInstance()
    cexAddressCache = CEXAddressCache()._getInstance()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, main_task.cancel)

    try:
        await db.connect()
        pools = await queries.getPools()
        tokens = await queries.getTokens()
        cexAddresses = await queries.getCexAddress()
        tokenNPoolCache.load(tokens,pools)
        cexAddressCache.load(cexAddresses=cexAddressCache)
        # await receiveEthStream.receviveMessage()
    except asyncio.CancelledError:
        print("Shutting down...")
    except Exception as e:
        print(f"Unexpected Error Occurred {e}")
        raise e
    finally:
        await db.disConnect()
        await redis_client.disconnect()
        

if __name__ == "__main__":
    asyncio.run(main())