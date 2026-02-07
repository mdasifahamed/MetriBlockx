import { toQuantity } from "ethers";
import { RpcManager } from "./RpcManager";

export interface LogData {
  address: string;
  topics: string[];
  data: string;
  blockNumber: bigint;
  blockHash: string;
  transactionHash: string;
  transactionIndex: number;
  logIndex: number;
  removed: boolean;
}

interface RawLog {
  address: string;
  topics: string[];
  data: string;
  blockNumber: string;
  blockHash: string;
  transactionHash: string;
  transactionIndex: string;
  logIndex: string;
  removed: boolean;
}


/**
 * Base class for the fetching events data from a network for a given ste of the contract address and th block range
 */

export class EventFetcher {
  constructor(private rpc: RpcManager) { }


  /**
   * Retives Event Log data for the given block range with out filter with contract address
   * @param startBlockNumber 
   * @param endBlock 
   * @returns Logdata []
   */
  async fetchLogs(startBlockNumber: number, endBlock: number): Promise<LogData[]> {
    const hexBlockStart = toQuantity(startBlockNumber);
    const hexBlockEnd = toQuantity(endBlock);

    // RPC Call: eth_getLogs for specific block
    const logs = await this.rpc.execute<RawLog[]>("eth_getLogs", [
      {
        fromBlock: hexBlockStart,
        toBlock: hexBlockEnd,
      },
    ]);

    return logs.map((log) => ({
      address: log.address,
      topics: log.topics,
      data: log.data,
      blockNumber: BigInt(log.blockNumber),
      blockHash: log.blockHash,
      transactionHash: log.transactionHash,
      transactionIndex: parseInt(log.transactionIndex, 16),
      logIndex: parseInt(log.logIndex, 16),
      removed: log.removed,
    }));
  }

  /**
   * Retrives Event Log Data For The Given Block Range And Contract Address With Filter
   * @param startBlockNumber the number of the blokc to start
   * @param endBlock  the number of the block to end 
   * @param address the set of the contract address to fillter events only for those networks
   * @returns LogData []
   */
  async fetchLogsWithFilter(
    startBlockNumber: number,
    endBlock: number,
    address?: (string | null)[]
  ): Promise<LogData[]> {
    const hexBlockStart = toQuantity(startBlockNumber);
    const hexBlockEnd = toQuantity(endBlock);

    const filter: Record<string, unknown> = {
      fromBlock: hexBlockStart,
      toBlock: hexBlockEnd,
    };

    if (address) {
      filter.address = address;
    }

    // Rpc Call to get log log data
    const logs = await this.rpc.execute<RawLog[]>("eth_getLogs", [filter]);

    return logs.map((log) => ({
      address: log.address,
      topics: log.topics,
      data: log.data,
      blockNumber: BigInt(log.blockNumber),
      blockHash: log.blockHash,
      transactionHash: log.transactionHash,
      transactionIndex: parseInt(log.transactionIndex, 16),
      logIndex: parseInt(log.logIndex, 16),
      removed: log.removed,
    }));
  }


}
