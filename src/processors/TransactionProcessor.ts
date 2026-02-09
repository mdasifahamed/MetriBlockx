import { Worker, Job } from "bullmq";
import { redisConnection, QUEUE_NAMES } from "../config/redis";
import { BlockJobData } from "./queues";
import { TransactionData } from "../core/BlockFetcher";
import { CexAddressCache } from "../cache/CexAddressCache";
import { ethers } from "ethers";
import { NativeTransferStorage } from "../storage/NativeTransferStorage";
import { CexFlowStorage } from "../storage/CexFlowStorage";
import { FlowType } from "../generated/prisma";

export interface NativeTransfer {
  from: string
  to: string
  value: string
  blockTimeStamp: number
  transactionHash: string
  transactionIndex: number
}

export interface BlockNativeTransfer {
  nativeTransfers: NativeTransfer[]
  blockNumber: bigint
  blockHash: string,
  blockParentHash: string,
  timeStamp: number
  totalAmount: string,
  chainId: number
}


export interface CEXFlowRecord {
  transactionHashes: string[]
  flowType: "inflow" | "outflow"
  totalAmount: string       // in wei
  totalAmountEth: string    // in ETH
  cexName: string           // e.g., "binance", "kucoin", "bybit"
  chainId: number           // e.g., 1 (ETH), 56 (BSC)
  blockNumber: bigint
  blockTimeStamp: number
}

// Block-level result with flat list of flows
export interface BlockCEXFlowResult {
  flows: CEXFlowRecord[]
  // Block-level totals (ALL CEX combined)
  totalInflowInSmallest: string
  totalInflowHumanNumber: string
  totalInflowCount: number
  totalOutflowInSmallest: string
  totalOutflowHumnaNumber: string
  totalOutflowCount: number
  // Block metadata
  blockNumber: bigint
  blockTimeStamp: number
  blockHash: string
  parentBlockHash: string
  chainId: number
}


interface FlowCalcResult {
  transactionHashes: string[]
  totalInSmallestNumber: string
  totalInHumanNumber: string
  count: number
}


/**
 * A class that help to determine and process the transafer ofthe native asset of specfic network
 * 1. It will have the total native transfer of block 
 * 2. It will also have the total inflow and outflow of the native asset In CEX
 */
export class TransactionProcessor {
  private worker: Worker<BlockJobData>;
  private nativeTransferStorage = new NativeTransferStorage();
  private cexFlowStorage = new CexFlowStorage();

  constructor() {
    this.worker = new Worker<BlockJobData>(
      QUEUE_NAMES.BLOCKS,
      async (job: Job<BlockJobData>) => {
        await this.process(job.data);
      },
      {
        connection: redisConnection,
        concurrency: 5,
      }
    );

    this.worker.on("completed", (job) => {
      console.log(`[TxProcessor] Block ${job.data.block.number} processed`);
    });

    this.worker.on("failed", (job, err) => {
      console.error(`[TxProcessor] Block ${job?.data.block.number} failed:`, err.message);
    });
  }

  /**
   * Process the native transfer of asset within the network and aslo seprates 
   * the inflow and out flow of the native within CEX
   * @param data  Block data contains the transaction and blokc metadata
   */
  private async process(data: BlockJobData): Promise<void> {
    const nativeEthTransfer = await this.findNativeTransfer(data)
    const cexNativeTranfer = await this.calculateBlockCEXFlows(data)


    // insert the native transfer of the asset in the db
    if (nativeEthTransfer.nativeTransfers.length > 0) {
      await this.nativeTransferStorage.insert({
        chainId: data.chainId,
        blockNumber: nativeEthTransfer.blockNumber,
        blockHash: nativeEthTransfer.blockHash,
        blockTimeStamp: new Date(nativeEthTransfer.timeStamp * 1000),
        totalAmount: nativeEthTransfer.totalAmount,
        transactionHashes: nativeEthTransfer.nativeTransfers.map(t => t.transactionHash),
      });
    }

    // insert CEX specific flow of the asset inflow /outflow
    for (const flow of cexNativeTranfer.flows) {
      await this.cexFlowStorage.insert({
        chainId: flow.chainId,
        blockNumber: flow.blockNumber,
        blockTimeStamp: new Date(flow.blockTimeStamp * 1000),
        cexName: flow.cexName,
        flowType: flow.flowType === "inflow" ? FlowType.INFLOW : FlowType.OUTFLOW,
        totalAmount: flow.totalAmount,
        totalAmountHuman: flow.totalAmountEth,
        transactionHashes: flow.transactionHashes,
        transactionCount: flow.transactionHashes.length,
      });
    }

    console.log(`[TxProcessor] Chain ${data.chainId} Block ${data.block.number}: ${data.block.transactionCount} txs`);
  }

  /**
   * Determins the cex inflow and outflow for the each CEX that we have in our list 
   * @param data blokc data
   * @returns cex flowresult
   */
  private async calculateBlockCEXFlows(data: BlockJobData): Promise<BlockCEXFlowResult> {
    const chainId = data.chainId;
    const cexCache = CexAddressCache.getInstance();
    const cexAddressSets = cexCache.getCexAddressSetsForChain(chainId);
    const allCEXAddresses = cexCache.getAllCexAddressesForChain(chainId);


    const nativeTransfers = data.block.transactions.filter(
      (trx: TransactionData) =>
        trx.input === "0x" && trx.value !== "0" && trx.to !== null
    );

    const flows: CEXFlowRecord[] = [];


    let totalInflowWei = BigInt(0);
    let totalInflowCount = 0;
    let totalOutflowWei = BigInt(0);
    let totalOutflowCount = 0;

    for (const [cexName, addressSet] of cexAddressSets) {
      const inflowData = this.calculateFlowForCEX(nativeTransfers, addressSet, allCEXAddresses, "inflow");
      const outflowData = this.calculateFlowForCEX(nativeTransfers, addressSet, allCEXAddresses, "outflow");


      if (inflowData.transactionHashes.length > 0) {
        flows.push({
          transactionHashes: inflowData.transactionHashes,
          flowType: "inflow",
          totalAmount: inflowData.totalInSmallestNumber,
          totalAmountEth: inflowData.totalInHumanNumber,
          cexName,
          chainId,
          blockNumber: BigInt(data.block.number),
          blockTimeStamp: data.block.timestamp,
        });
        totalInflowWei += BigInt(inflowData.totalInSmallestNumber);
        totalInflowCount += inflowData.count;
      }


      if (outflowData.transactionHashes.length > 0) {
        flows.push({
          transactionHashes: outflowData.transactionHashes,
          flowType: "outflow",
          totalAmount: outflowData.totalInSmallestNumber,
          totalAmountEth: outflowData.totalInHumanNumber,
          cexName,
          chainId,
          blockNumber: BigInt(data.block.number),
          blockTimeStamp: data.block.timestamp,
        });
        totalOutflowWei += BigInt(outflowData.totalInSmallestNumber);
        totalOutflowCount += outflowData.count;
      }
    }

    console.log(
      `[CEXFlows] Block ${data.block.number}: Inflow ${(Number(totalInflowWei) / 1e18).toFixed(4)} ETH (${totalInflowCount} txs), Outflow ${(Number(totalOutflowWei) / 1e18).toFixed(4)} ETH (${totalOutflowCount} txs)`
    );

    return {
      flows,
      totalInflowInSmallest: totalInflowWei.toString(),
      totalInflowHumanNumber: ethers.formatEther(totalInflowWei),
      totalInflowCount,
      totalOutflowInSmallest: totalOutflowWei.toString(),
      totalOutflowHumnaNumber: ethers.formatEther(totalOutflowWei),
      totalOutflowCount,
      blockNumber: BigInt(data.block.number),
      blockTimeStamp: data.block.timestamp,
      blockHash: data.block.hash,
      parentBlockHash: data.block.parentHash,
      chainId,
    };
  }

  /**
   * Helper function 
   * @param nativeTransfers filter native transfer transactions only
   * @param cexAddressSet  set of the cex address 
   * @param allCEXAddresses  all the cex address (e.g, binance, kuoic, etc)
   * @param flowType 
   * @returns 
   */

  private calculateFlowForCEX(
    nativeTransfers: TransactionData[],
    cexAddressSet: Set<string>,
    allCEXAddresses: Set<string>,
    flowType: "inflow" | "outflow"
  ): FlowCalcResult {
    const result: FlowCalcResult = {
      transactionHashes: [],
      totalInSmallestNumber: "0",
      totalInHumanNumber: "0",
      count: 0,
    };

    let totalWei = BigInt(0);

    for (const transfer of nativeTransfers) {
      const toLower = transfer.to!.toLowerCase();
      const fromLower = transfer.from.toLowerCase();

      const isToThisCex = cexAddressSet.has(toLower);
      const isFromThisCex = cexAddressSet.has(fromLower);
      const isToAnyCex = allCEXAddresses.has(toLower);
      const isFromAnyCex = allCEXAddresses.has(fromLower);

      let match = false;

      if (flowType === "inflow") {
        // Inflow: to is THIS CEX, from is NOT any CEX
        match = isToThisCex && !isFromAnyCex;
      } else {
        // Outflow: from is THIS CEX, to is NOT any CEX
        match = isFromThisCex && !isToAnyCex;
      }

      if (match) {
        totalWei += BigInt(transfer.value);
        result.transactionHashes.push(transfer.hash);
        result.count++;
      }
    }

    result.totalInSmallestNumber = totalWei.toString();
    result.totalInHumanNumber = (Number(totalWei) / 1e18).toFixed(8);

    return result;
  }

  /**
   * Detemines the nativetransfer transactions from the blokc levle data
   * @param data block data containing the transactiona and blokc metedata 
   * @returns native transfer object
   */
  private async findNativeTransfer(data: BlockJobData): Promise<BlockNativeTransfer> {
    const nativeTransfers: NativeTransfer[] = data.block.transactions
      .filter((trx: TransactionData) =>
        trx.input === '0x' && trx.value !== '0' && trx.to !== null
      )
      .map((trx: TransactionData) => ({
        from: trx.from,
        to: trx.to as string,
        value: trx.value,
        blockTimeStamp: data.block.timestamp,
        transactionHash: trx.hash,
        transactionIndex: trx.transactionIndex,
      }));

    const totalAmount = nativeTransfers.reduce(
      (sum, trx) => sum + BigInt(trx.value),
      BigInt(0)
    );

    return {
      nativeTransfers,
      blockNumber: BigInt(data.block.number),
      blockHash: data.block.hash,
      blockParentHash: data.block.parentHash,
      timeStamp: data.block.timestamp,
      totalAmount: totalAmount.toString(),
      chainId: data.chainId
    };
  }

  async close(): Promise<void> {
    await this.worker.close();
  }
}
