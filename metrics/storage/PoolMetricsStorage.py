from ..db.db_connection import db
import uuid


class PoolMetricsStorage:
    def __init__(self):
        self.__db = db

    async def insertPoolSwaps(self, swaps):
        if not swaps:
            return 0

        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'] * len(swaps))
            values_list = []

            for swap in swaps:
                values_list.extend([
                    str(uuid.uuid4()),
                    swap['block_number'],
                    swap['block_time_stamp'],
                    swap['chain_id'],
                    swap['pool_address'],
                    swap['swap_count'],
                    swap['transaction_hashes'],
                    swap['volume_token_0'],
                    swap['volume_token_0_human'],
                    swap['volume_token_1'],
                    swap['volume_token_1_human']
                ])

            await connection.execute(
                f"""INSERT INTO pool_swaps
                    (id, block_number, block_time_stamp, chain_id, pool_address, swap_count,
                     transaction_hashes, volume_token_0, volume_token_0_human, volume_token_1, volume_token_1_human)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, pool_address, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )

        return len(swaps)

    async def insertPoolLiquidity(self, liquidity_records):
        if not liquidity_records:
            return 0

        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s, %s::"LiquidityType", %s, %s, %s)'] * len(liquidity_records))
            values_list = []

            for record in liquidity_records:
                values_list.extend([
                    str(uuid.uuid4()),
                    record['amount_token_0'],
                    record['amount_token_0_human'],
                    record['amount_token_1'],
                    record['amount_token_1_human'],
                    record['block_number'],
                    record['block_time_stamp'],
                    record['chain_id'],
                    record['liquidity_type'],
                    record['pool_address'],
                    record['transaction_count'],
                    record['transaction_hashes']
                ])

            await connection.execute(
                f"""INSERT INTO pool_liquidity
                    (id, amount_token_0, amount_token_0_human, amount_token_1, amount_token_1_human,
                     block_number, block_time_stamp, chain_id, liquidity_type, pool_address,
                     transaction_count, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, pool_address, liquidity_type, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )

        return len(liquidity_records)

    async def insertPoolFees(self, fees):
        if not fees:
            return 0

        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'] * len(fees))
            values_list = []

            for fee in fees:
                values_list.extend([
                    str(uuid.uuid4()),
                    fee['block_number'],
                    fee['block_time_stamp'],
                    fee['chain_id'],
                    fee['collect_count'],
                    fee['fees_token_0'],
                    fee['fees_token_0_human'],
                    fee['fees_token_1'],
                    fee['fees_token_1_human'],
                    fee['pool_address'],
                    fee['transaction_hashes']
                ])

            await connection.execute(
                f"""INSERT INTO pool_fees
                    (id, block_number, block_time_stamp, chain_id, collect_count,
                     fees_token_0, fees_token_0_human, fees_token_1, fees_token_1_human,
                     pool_address, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, pool_address, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )

        return len(fees)

    async def insertPoolReserves(self, reserves):
        if not reserves:
            return 0

        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s)'] * len(reserves))
            values_list = []

            for reserve in reserves:
                values_list.extend([
                    str(uuid.uuid4()),
                    reserve['block_number'],
                    reserve['block_time_stamp'],
                    reserve['chain_id'],
                    reserve['pool_address'],
                    reserve['reserve_token_0'],
                    reserve['reserve_token_1'],
                    reserve['transaction_hashes']
                ])

            await connection.execute(
                f"""INSERT INTO "pool_Reserve"
                    (id, block_number, block_time_stamp, chain_id, pool_address,
                     reserve_token_0, reserve_token_1, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, pool_address, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )

        return len(reserves)
