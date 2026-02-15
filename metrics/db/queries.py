from .db_connection import db
from datetime import datetime
import uuid
class DBQueries:
    def __init__(self):
        self.__db=db
    async def getPools(self):
        async with self.__db.getConnection() as conn:
            cursor = await conn.execute(
        """ SELECT * 
            FROM pools
        """)
            rows = await cursor.fetchall()
            return rows if rows else []
        
    async def getTokens(self):
        async with self.__db.getConnection() as conn:
            cursor = await conn.execute(
        """ SELECT * 
            FROM tokens
        """)
            rows = await cursor.fetchall()
            return rows if rows else []
            
    async def getCexAddress(self):
        async with self.__db.getConnection() as conn:
            cursor = await conn.execute(
        """ SELECT * 
            FROM cex_addresses
        """)
            rows = await cursor.fetchall()
            return rows if rows else []
    async def getEventBlockNumbers(self,chainId: int,createdAt:str):
        async with self.__db.getConnection() as conn:
            cursor = await conn.execute(
                """ SELECT block_numbers 
                    FROM decoded_event_range 
                    WHERE chain_id = %s AND created_at = %s """,
                (chainId, createdAt)
            )
            row = await cursor.fetchone()
            return row['block_numbers'] if row else []
    async def getTransferEvents(self, tokenAddress:str, chianId,evenType:str,blockNumber: int):
            async with self.__db.getConnection() as conn:
                cursor = await conn.execute(
                    """ SELECT * 
                        FROM decoded_events
                        WHERE chain_id = %s AND contract_address = %s AND event_name = %s AND block_number = %s 
                    """,
                    (chianId,tokenAddress,evenType,blockNumber)
                )
                rows = await cursor.fetchall()
                return rows if rows else []
    async def  getStablecoinEvents():
        pass
    
    async def getWrppedTokenEvents():
        pass
    
    async def getUniswapV2Events():
        pass
    
    async def getUniSwapV3Events():
        pass

    async def getDecodedEventsByBlocks(self, chainId: int, blockNumbers: list):
        if not blockNumbers:
            return []
        
        async with self.__db.getConnection() as connection:
            block_numbers_as_bigint = [int(block_number) for block_number in blockNumbers]
            
            placeholders = ', '.join(['%s'] * len(block_numbers_as_bigint))
            query = f"""
                SELECT * 
                FROM decoded_events
                WHERE chain_id = %s AND block_number IN ({placeholders})
                ORDER BY block_number, transaction_index
            """
            
            params = [chainId] + block_numbers_as_bigint
            cursor = await connection.execute(query, params)
            rows = await cursor.fetchall()
            return rows if rows else []

    async def insertMetricsGenerated(self, chainId: int, blockNumbers: list):

    
        if not blockNumbers:
            return
    
        async with self.__db.getConnection() as connection:
            created_at = datetime.now()
            async with connection.cursor() as cursor:
                for block_number in blockNumbers:
                    await cursor.execute(
                        """ INSERT INTO metrics_generated (id, chain_id, block_number, created_at)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """,
                        (str(uuid.uuid4()), chainId, block_number, created_at)
                    )