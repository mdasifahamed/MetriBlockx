import asyncio
import signal
from .redisStream.BaseStreamReceiver import EthereumStreamReceiver, BnbStreamReceiver, PolygonStreamReceiver
from .redisStream.redisClient import redis_client
from .db.db_connection import db
from .db.queries import DBQueries
from .cache.CacheTokenPool import TokenNPoolCache
from .cache.CexAddresses import CEXAddressCache


async def main():
    ethereum_stream_receiver = EthereumStreamReceiver()
    bnb_stream_receiver = BnbStreamReceiver()
    polygon_stream_receiver = PolygonStreamReceiver()

    loop = asyncio.get_running_loop()
    main_task = asyncio.current_task()
    queries = DBQueries()
    token_and_pool_cache = TokenNPoolCache()._getInstance()
    cex_address_cache = CEXAddressCache()._getInstance()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, main_task.cancel)

    try:
        await db.connect()
        pools = await queries.getPools()
        tokens = await queries.getTokens()
        cex_addresses = await queries.getCexAddress()
        token_and_pool_cache.load(tokens, pools)
        cex_address_cache.load(cexAddresses=cex_addresses)

        print("Starting stream receivers for all chains...")

        await asyncio.gather(
            ethereum_stream_receiver.receiveMessages(),
            bnb_stream_receiver.receiveMessages(),
            polygon_stream_receiver.receiveMessages()
        )
    except asyncio.CancelledError:
        print("Shutting down...")
    except Exception as error:
        print(f"Unexpected Error Occurred: {error}")
        raise error
    finally:
        await db.disConnect()
        await redis_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())