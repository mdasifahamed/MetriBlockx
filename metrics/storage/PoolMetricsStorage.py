from ..db.db_connection import db

class PoolMetricsStorage:
    def __init__(self):
        self.__db = db

    async def insertPoolSwaps(self, swaps):
        if not swaps:
            return True
        try:
            async with self.__db.getConnection() as conn:
                await conn.executemany(
                    """INSERT INTO pool_swaps
                    (block_number, block_time_stamp, chain_id, pool_address, swap_count,
                     transaction_hashes, volume_token_0, volume_token_0_human, volume_token_1, volume_token_1_human)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chain_id, pool_address, block_number, block_time_stamp) DO NOTHING""",
                    [(s['block_number'], s['block_time_stamp'], s['chain_id'], s['pool_address'],
                      s['swap_count'], s['transaction_hashes'], s['volume_token_0'],
                      s['volume_token_0_human'], s['volume_token_1'], s['volume_token_1_human'])
                     for s in swaps]
                )
            return True
        except Exception as e:
            print(f"Error inserting pool swaps: {e}")
            return False

    async def insertPoolLiquidity(self, liquidityRecords):
        if not liquidityRecords:
            return True
        try:
            async with self.__db.getConnection() as conn:
                await conn.executemany(
                    """INSERT INTO pool_liquidity
                    (amount_token_0, amount_token_0_human, amount_token_1, amount_token_1_human,
                     block_number, block_time_stamp, chain_id, liquidity_type, pool_address,
                     transaction_count, transaction_hashes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::"LiquidityType", %s, %s, %s)
                    ON CONFLICT (chain_id, pool_address, liquidity_type, block_number, block_time_stamp) DO NOTHING""",
                    [(r['amount_token_0'], r['amount_token_0_human'], r['amount_token_1'],
                      r['amount_token_1_human'], r['block_number'], r['block_time_stamp'],
                      r['chain_id'], r['liquidity_type'], r['pool_address'],
                      r['transaction_count'], r['transaction_hashes'])
                     for r in liquidityRecords]
                )
            return True
        except Exception as e:
            print(f"Error inserting pool liquidity: {e}")
            return False

    async def insertPoolFees(self, fees):
        if not fees:
            return True
        try:
            async with self.__db.getConnection() as conn:
                await conn.executemany(
                    """INSERT INTO pool_fees
                    (block_number, block_time_stamp, chain_id, collect_count,
                     fees_token_0, fees_token_0_human, fees_token_1, fees_token_1_human,
                     pool_address, transaction_hashes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chain_id, pool_address, block_number, block_time_stamp) DO NOTHING""",
                    [(f['block_number'], f['block_time_stamp'], f['chain_id'], f['collect_count'],
                      f['fees_token_0'], f['fees_token_0_human'], f['fees_token_1'],
                      f['fees_token_1_human'], f['pool_address'], f['transaction_hashes'])
                     for f in fees]
                )
            return True
        except Exception as e:
            print(f"Error inserting pool fees: {e}")
            return False

    async def insertPoolReserves(self, reserves):
        if not reserves:
            return True
        try:
            async with self.__db.getConnection() as conn:
                await conn.executemany(
                    """INSERT INTO "pool_Reserve"
                    (block_number, block_time_stamp, chain_id, pool_address,
                     reserve_token_0, reserve_token_1, transaction_hashes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chain_id, pool_address, block_number, block_time_stamp) DO NOTHING""",
                    [(r['block_number'], r['block_time_stamp'], r['chain_id'], r['pool_address'],
                      r['reserve_token_0'], r['reserve_token_1'], r['transaction_hashes'])
                     for r in reserves]
                )
            return True
        except Exception as e:
            print(f"Error inserting pool reserves: {e}")
            return False
