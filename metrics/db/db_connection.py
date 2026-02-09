import os
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

load_dotenv()


class DBConnectionPool:
    def __init__(self,dbUrl:str):
        self.__dbUrl = dbUrl
        self.__pool = AsyncConnectionPool(
            self.__dbUrl,
            max_size=10,
            min_size=5,
            open=False,
            kwargs={"row_factory":dict_row},
            timeout=30,
            max_idle=600,
            check=AsyncConnectionPool.check_connection,
            reconnect_timeout=180
        )
        
    async def connect(self):
        return await self.__pool.open()
    
    async def disConnect(self):
        return await self.__pool.close()
    
    def getConnection(self):
        return self.__pool.connection()


db = DBConnectionPool(os.getenv("DATABASE_URL"))