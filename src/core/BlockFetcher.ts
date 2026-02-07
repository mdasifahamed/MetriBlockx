import { toBigInt, toQuantity } from "ethers";
import { RpcManager } from "./RpcManager";

export interface TransactionData {
  hash: string;
  from: string;
  to: string | null;
  value: string; // converted from hex to biginit string
  gasPrice: string | null;  // converted from hex to biginit string or (null for EIP-1559)
  maxFeePerGas: string | null; // converted from hex to biginit string or (null for EIP-1559)
  maxPriorityFeePerGas: string | null; // converted from hex to biginit string or (null for EIP-1559)
  gas: string; // converted from hex to biginit string
  nonce: string; // converted from hex to biginit string
  input: string; // hex calldata
  transactionIndex: number; //converted from hex to biginit string
}

export interface BlockData {
  number: number;
  hash: string;
  parentHash: string;
  timestamp: number;
  gasUsed: string; // hex
  gasLimit: string; // hex
  baseFeePerGas: string | null; // hex 
  transactions: TransactionData[]; // set of raw transaction receipts for a block
  transactionCount: number;
}

interface RawTransaction {
  hash: string;
  from: string;
  to: string | null;
  value: string;
  gasPrice?: string;
  maxFeePerGas?: string;
  maxPriorityFeePerGas?: string;
  gas: string;
  nonce: string;
  input: string;
  transactionIndex: string;
}

interface RawBlock {
  number: string;
  hash: string;
  parentHash: string;
  timestamp: string;
  gasUsed: string;
  gasLimit: string;
  baseFeePerGas?: string;
  transactions: RawTransaction[];
}



/**
 * Base block fetcher class that handles block fecthing from the rpc 
 * handles only block data 
 */
export class BlockFetcher {
  constructor(private rpc: RpcManager) { }

  /**
   * retirves block data blokc from an from network for a given blkc number 
   * @param blockNumber number of the blokc that we from where we want get the blokc level data
   * @returns BlocData object that contarct transation set of that block and blokc details
   */
  async fetchBlock(blockNumber: number): Promise<BlockData> {
    const hexBlock = toQuantity(blockNumber);

    // RPC Call: eth_getBlockByNumber with full transactions
    const block = await this.rpc.execute<RawBlock>("eth_getBlockByNumber", [
      hexBlock,
      true, // include full transaction objects
    ]);

    if (!block) {
      throw new Error(`Block ${blockNumber} not found`);
    }

    return {
      number: parseInt(block.number, 16),
      hash: block.hash,
      parentHash: block.parentHash,
      timestamp: parseInt(block.timestamp, 16),
      gasUsed: block.gasUsed,
      gasLimit: block.gasLimit,
      baseFeePerGas: block.baseFeePerGas || null,
      transactions: block.transactions.map((tx) => ({
        hash: tx.hash,
        from: tx.from,
        to: tx.to,
        value: toBigInt(tx.value).toString(),
        gasPrice: tx.gasPrice ? toBigInt(tx.gasPrice).toString() : null,
        maxFeePerGas: tx.maxFeePerGas ? toBigInt(tx.maxFeePerGas).toString() : null,
        maxPriorityFeePerGas: tx.maxPriorityFeePerGas ? toBigInt(tx.maxPriorityFeePerGas).toString() : null,
        gas: toBigInt(tx.gas).toString(),
        nonce: toBigInt(tx.nonce).toString(),
        input: tx.input,
        transactionIndex: parseInt(tx.transactionIndex, 16),
      })),
      transactionCount: block.transactions.length,
    };
  }


}
