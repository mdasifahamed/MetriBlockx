from typing import List, Any, Dict
from eth_utils import from_wei_decimals
from decimal import Decimal
import pandas as pd
from ...cache.CacheTokenPool import TokenNPoolCache
from ...cache.CexAddresses import CEXAddressCache
from ...storage.TokenMetricsStorage import TokenMetricsStorage

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class BaseTokenProcessor:

    def __init__(self, chainId: int):
        self._chainId = chainId
        self._tokenPoolCache = TokenNPoolCache._getInstance()
        self._cexCache = CEXAddressCache._getInstance()
        self._storage = TokenMetricsStorage()

    def _getTokenCache(self):
        return self._tokenPoolCache.getAllTokenByChainId(self._chainId)

    def _getCexAddressCache(self):
        return self._cexCache.getAllCexByChainId(self._chainId)

    def _toHumanReadable(self, rawAmount: int, tokenDecimal: int) -> str:
        human_readable_value = Decimal(rawAmount) / Decimal(10 ** tokenDecimal)
        return f"{human_readable_value:.8f}"

    async def calculateTotalTransferNative(self, transferEvents: List[Any]) -> Dict:
        if not transferEvents:
            return {'results': [], 'count': 0}

        token_cache = self._getTokenCache()
        cex_address_cache = self._getCexAddressCache()

        events_dataframe = pd.DataFrame(transferEvents)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        event_arguments_dataframe['from'] = event_arguments_dataframe['from'].str.lower()
        event_arguments_dataframe['to'] = event_arguments_dataframe['to'].str.lower()
        event_arguments_dataframe['value'] = event_arguments_dataframe['value'].apply(int)

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        token_decimal_map = {}
        for contract_address in events_dataframe['contract_address'].unique():
            token_address_lower = contract_address.lower()
            token_info = token_cache.get(token_address_lower) if token_cache else None
            token_decimal_map[contract_address] = token_info['token_decimal'] if token_info else 18

        event_arguments_dataframe['value_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['value']) / Decimal(10 ** token_decimal_map.get(row['contract_address'], 18)),
            axis=1
        )

        cex_addresses_set = set(cex_address_cache) if cex_address_cache else set()

        is_zero_address = (event_arguments_dataframe['from'] == ZERO_ADDRESS) | (event_arguments_dataframe['to'] == ZERO_ADDRESS)
        is_cex_address = event_arguments_dataframe['from'].isin(cex_addresses_set) | event_arguments_dataframe['to'].isin(cex_addresses_set)
        valid_native_transfers_mask = ~is_zero_address & ~is_cex_address

        event_arguments_dataframe['is_valid_native'] = valid_native_transfers_mask

        valid_transfers_dataframe = event_arguments_dataframe[event_arguments_dataframe['is_valid_native']]

        if valid_transfers_dataframe.empty:
            return {'results': [], 'count': 0}

        grouped_transfers = valid_transfers_dataframe.groupby(['contract_address', 'block_number']).agg(
            total_amount=('value', lambda values: sum(values)),
            total_amount_decimal=('value_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            transaction_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_transfers.to_dict('records'):
            token_address = grouped_row['contract_address'].lower()

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'token_address': token_address,
                'total_amount': str(grouped_row['total_amount']),
                'total_amount_human': f"{grouped_row['total_amount_decimal']:.8f}",
                'transaction_count': grouped_row['transaction_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
            })

        inserted_count = await self._storage.insertTokenTransfers(results)
        return {'results': results, 'count': inserted_count}

    async def calculateTotalCeXFlow(self, transferEvents: List[Any]) -> Dict:
        if not transferEvents:
            return {'results': [], 'count': 0}

        token_cache = self._getTokenCache()
        cex_address_cache = self._getCexAddressCache()

        events_dataframe = pd.DataFrame(transferEvents)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        event_arguments_dataframe['from'] = event_arguments_dataframe['from'].str.lower()
        event_arguments_dataframe['to'] = event_arguments_dataframe['to'].str.lower()
        event_arguments_dataframe['value'] = event_arguments_dataframe['value'].apply(int)

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        token_decimal_map = {}
        for contract_address in events_dataframe['contract_address'].unique():
            token_address_lower = contract_address.lower()
            token_info = token_cache.get(token_address_lower) if token_cache else None
            token_decimal_map[contract_address] = token_info['token_decimal'] if token_info else 18

        event_arguments_dataframe['value_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row['value']) / Decimal(10 ** token_decimal_map.get(row['contract_address'], 18)),
            axis=1
        )

        cex_addresses_cache = cex_address_cache if cex_address_cache else {}
        cex_addresses_set = set(cex_addresses_cache)

        from_is_cex = event_arguments_dataframe['from'].isin(cex_addresses_set)
        to_is_cex = event_arguments_dataframe['to'].isin(cex_addresses_set)
        valid_cex_flow_mask = from_is_cex != to_is_cex

        event_arguments_dataframe['cex_address'] = None
        event_arguments_dataframe.loc[valid_cex_flow_mask & to_is_cex, 'cex_address'] = event_arguments_dataframe.loc[valid_cex_flow_mask & to_is_cex, 'to']
        event_arguments_dataframe.loc[valid_cex_flow_mask & from_is_cex, 'cex_address'] = event_arguments_dataframe.loc[valid_cex_flow_mask & from_is_cex, 'from']

        event_arguments_dataframe['flow_type'] = None
        event_arguments_dataframe.loc[valid_cex_flow_mask & to_is_cex, 'flow_type'] = 'INFLOW'
        event_arguments_dataframe.loc[valid_cex_flow_mask & from_is_cex, 'flow_type'] = 'OUTFLOW'

        event_arguments_dataframe['cex_name'] = event_arguments_dataframe['cex_address'].map(
            lambda address: cex_addresses_cache[address]['cex_name'] if address and address in cex_addresses_cache else None
        )

        valid_cex_flows_dataframe = event_arguments_dataframe[valid_cex_flow_mask]

        if valid_cex_flows_dataframe.empty:
            return {'results': [], 'count': 0}

        grouped_cex_flows = valid_cex_flows_dataframe.groupby(['contract_address', 'block_number', 'flow_type', 'cex_name']).agg(
            total_amount=('value', lambda values: sum(values)),
            total_amount_decimal=('value_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            transaction_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_cex_flows.to_dict('records'):
            token_address = grouped_row['contract_address'].lower()

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'token_address': token_address,
                'cex_name': grouped_row['cex_name'],
                'flow_type': grouped_row['flow_type'],
                'total_amount': str(grouped_row['total_amount']),
                'total_amount_human': f"{grouped_row['total_amount_decimal']:.8f}",
                'transaction_count': grouped_row['transaction_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
            })

        inserted_count = await self._storage.insertTokenCexFlows(results)
        return {'results': results, 'count': inserted_count}

    async def _calculateSupplyAmount(self, events: List[Any], fieldName: str, supplyType: str) -> Dict:
        if not events:
            return {'results': [], 'count': 0}

        token_cache = self._getTokenCache()

        events_dataframe = pd.DataFrame(events)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        if fieldName not in event_arguments_dataframe.columns:
            return {'results': [], 'count': 0}

        event_arguments_dataframe[fieldName] = event_arguments_dataframe[fieldName].apply(int)

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        token_decimal_map = {}
        for contract_address in events_dataframe['contract_address'].unique():
            token_address_lower = contract_address.lower()
            token_info = token_cache.get(token_address_lower) if token_cache else None
            token_decimal_map[contract_address] = token_info['token_decimal'] if token_info else 18

        event_arguments_dataframe['value_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row[fieldName]) / Decimal(10 ** token_decimal_map.get(row['contract_address'], 18)),
            axis=1
        )

        grouped_events = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            total_amount=(fieldName, lambda values: sum(values)),
            total_amount_decimal=('value_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            transaction_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_events.to_dict('records'):
            token_address = grouped_row['contract_address'].lower()

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'token_address': token_address,
                'supply_type': supplyType,
                'total_amount': str(grouped_row['total_amount']),
                'total_amount_human': f"{grouped_row['total_amount_decimal']:.8f}",
                'transaction_count': grouped_row['transaction_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
            })

        inserted_count = await self._storage.insertTokenSupplyEvents(results)
        return {'results': results, 'count': inserted_count}

    async def _calculateDepositWithdrawal(self, events: List[Any], fieldName: str, operationType: str) -> Dict:
        if not events:
            return {'results': [], 'count': 0}

        token_cache = self._getTokenCache()

        events_dataframe = pd.DataFrame(events)
        event_arguments_dataframe = pd.json_normalize(events_dataframe['event_args'])

        if fieldName not in event_arguments_dataframe.columns:
            return {'results': [], 'count': 0}

        event_arguments_dataframe[fieldName] = event_arguments_dataframe[fieldName].apply(int)

        metadata_columns = ['contract_address', 'block_number', 'block_time_stamp', 'transaction_hash']
        event_arguments_dataframe[metadata_columns] = events_dataframe[metadata_columns].values

        token_decimal_map = {}
        for contract_address in events_dataframe['contract_address'].unique():
            token_address_lower = contract_address.lower()
            token_info = token_cache.get(token_address_lower) if token_cache else None
            token_decimal_map[contract_address] = token_info['token_decimal'] if token_info else 18

        event_arguments_dataframe['value_decimal'] = event_arguments_dataframe.apply(
            lambda row: Decimal(row[fieldName]) / Decimal(10 ** token_decimal_map.get(row['contract_address'], 18)),
            axis=1
        )

        grouped_events = event_arguments_dataframe.groupby(['contract_address', 'block_number']).agg(
            total_amount=(fieldName, lambda values: sum(values)),
            total_amount_decimal=('value_decimal', lambda decimals: sum(decimals, Decimal('0'))),
            block_time_stamp=('block_time_stamp', 'first'),
            transaction_count=('transaction_hash', 'count'),
            transaction_hashes=('transaction_hash', list),
        ).reset_index()

        results = []
        for grouped_row in grouped_events.to_dict('records'):
            token_address = grouped_row['contract_address'].lower()

            results.append({
                'block_number': grouped_row['block_number'],
                'block_time_stamp': grouped_row['block_time_stamp'],
                'chain_id': self._chainId,
                'token_address': token_address,
                'operation_type': operationType,
                'total_amount': str(grouped_row['total_amount']),
                'total_amount_human': f"{grouped_row['total_amount_decimal']:.8f}",
                'transaction_count': grouped_row['transaction_count'],
                'transaction_hashes': grouped_row['transaction_hashes'],
            })

        inserted_count = await self._storage.insertTokenDepositWithdrawals(results)
        return {'results': results, 'count': inserted_count}

    async def calculateTotalMintAmount(self, mintEvents: List[Any]) -> Dict:
        return await self._calculateSupplyAmount(mintEvents, fieldName='amount', supplyType='ISSUE')

    async def calculateTotalBurnAmount(self, burnEvents: List[Any]) -> Dict:
        return await self._calculateSupplyAmount(burnEvents, fieldName='amount', supplyType='BURN')

    async def calculateTotalDepositAmount(self, depositEvents: List[Any]) -> Dict:
        return await self._calculateDepositWithdrawal(depositEvents, fieldName='wad', operationType='DEPOSIT')

    async def calculateTotalWithdrawalAmount(self, withdrawalEvents: List[Any]) -> Dict:
        return await self._calculateDepositWithdrawal(withdrawalEvents, fieldName='wad', operationType='WITHDRAWAL')

    async def processAllEvents(self, eventsByName: Dict[str, List[Any]]) -> Dict[str, Any]:
        results = {}

        if eventsByName.get('Transfer'):
            results['transfer'] = await self.calculateTotalTransferNative(eventsByName['Transfer'])
            results['cex_flow'] = await self.calculateTotalCeXFlow(eventsByName['Transfer'])

        mint_events = eventsByName.get('Mint') or eventsByName.get('Issue')
        if mint_events:
            results['mint'] = await self.calculateTotalMintAmount(mint_events)

        burn_events = eventsByName.get('Burn') or eventsByName.get('Redeem')
        if burn_events:
            results['burn'] = await self.calculateTotalBurnAmount(burn_events)

        if eventsByName.get('Deposit'):
            results['deposit'] = await self.calculateTotalDepositAmount(eventsByName['Deposit'])

        if eventsByName.get('Withdrawal'):
            results['withdrawal'] = await self.calculateTotalWithdrawalAmount(eventsByName['Withdrawal'])

        return results
