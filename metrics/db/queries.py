from .db_connection import db
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
