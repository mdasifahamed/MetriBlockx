from ..db.db_connection import db
import uuid


class TokenMetricsStorage:
    def __init__(self):
        self.__db = db

    async def insertTokenTransfers(self, transfers):
        if not transfers:
            return 0
        
        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s, %s)'] * len(transfers))
            values_list = []
            
            for transfer in transfers:
                values_list.extend([
                    str(uuid.uuid4()),
                    transfer['block_number'],
                    transfer['block_time_stamp'],
                    transfer['chain_id'],
                    transfer['token_address'],
                    transfer['total_amount'],
                    transfer['total_amount_human'],
                    transfer['transaction_count'],
                    transfer['transaction_hashes']
                ])
            
            await connection.execute(
                f"""INSERT INTO token_transfers
                    (id, block_number, block_time_stamp, chain_id, token_address,
                     total_amount, total_amount_human, transaction_count, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, token_address, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )
        
        return len(transfers)

    async def insertTokenCexFlows(self, cex_flows):
        if not cex_flows:
            return 0
        
        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s, %s::"FlowType", %s, %s, %s, %s)'] * len(cex_flows))
            values_list = []
            
            for flow in cex_flows:
                values_list.extend([
                    str(uuid.uuid4()),
                    flow['block_number'],
                    flow['block_time_stamp'],
                    flow['chain_id'],
                    flow['token_address'],
                    flow['cex_name'],
                    flow['flow_type'],
                    flow['total_amount'],
                    flow['total_amount_human'],
                    flow['transaction_count'],
                    flow['transaction_hashes']
                ])
            
            await connection.execute(
                f"""INSERT INTO token_cex_flows
                    (id, block_number, block_time_stamp, chain_id, token_address, cex_name,
                     flow_type, total_amount, total_amount_human, transaction_count, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, token_address, cex_name, flow_type, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )
        
        return len(cex_flows)

    async def insertTokenSupplyEvents(self, supply_events):
        if not supply_events:
            return 0
        
        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s::"TokenSupplyType", %s, %s, %s, %s)'] * len(supply_events))
            values_list = []
            
            for event in supply_events:
                values_list.extend([
                    str(uuid.uuid4()),
                    event['block_number'],
                    event['block_time_stamp'],
                    event['chain_id'],
                    event['token_address'],
                    event['supply_type'],
                    event['total_amount'],
                    event['total_amount_human'],
                    event['transaction_count'],
                    event['transaction_hashes']
                ])
            
            await connection.execute(
                f"""INSERT INTO token_supply_events
                    (id, block_number, block_time_stamp, chain_id, token_address, supply_type,
                     total_amount, total_amount_human, transaction_count, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, token_address, supply_type, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )
        
        return len(supply_events)

    async def insertTokenDepositWithdrawals(self, operations):
        if not operations:
            return 0
        
        async with self.__db.getConnection() as connection:
            values_placeholder = ', '.join(['(%s, %s, %s, %s, %s, %s::"OperationType", %s, %s, %s, %s)'] * len(operations))
            values_list = []
            
            for operation in operations:
                values_list.extend([
                    str(uuid.uuid4()),
                    operation['block_number'],
                    operation['block_time_stamp'],
                    operation['chain_id'],
                    operation['token_address'],
                    operation['operation_type'],
                    operation['total_amount'],
                    operation['total_amount_human'],
                    operation['transaction_count'],
                    operation['transaction_hashes']
                ])
            
            await connection.execute(
                f"""INSERT INTO token_deposit_withdrawals
                    (id, block_number, block_time_stamp, chain_id, token_address, operation_type,
                     total_amount, total_amount_human, transaction_count, transaction_hashes)
                    VALUES {values_placeholder}
                    ON CONFLICT (chain_id, token_address, operation_type, block_number, block_time_stamp) DO NOTHING""",
                values_list
            )
        
        return len(operations)