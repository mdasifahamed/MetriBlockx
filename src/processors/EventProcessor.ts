import { Worker, Job } from "bullmq";
import { redisConnection, QUEUE_NAMES } from "../config/redis";
import { EventJobData, GroupedTransaction, EventData, groupedEventQueue } from "./queues";



/**
 * Worker Class to process The events retiuved from the block 
 * which meands whne the evnet are being reviced to this it process/decode them
 */
export class EventProcessor {
  private worker: Worker<EventJobData>;

  constructor() {
    this.worker = new Worker<EventJobData>(
      QUEUE_NAMES.EVENTS, // name of the worker
      async (job: Job<EventJobData>) => {
        await this.process(job.data);
      },
      {
        connection: redisConnection,
        concurrency: 5,
      }
    ); // worker initiations

    this.worker.on("completed", (job) => {
      console.log(
        `[EventProcessor] Batch ${job.data.fromBlock}-${job.data.toBlock} processed`
      );
    });

    this.worker.on("failed", (job, err) => {
      console.error(`[EventProcessor] Batch failed:`, err.message);
    });
  }


  /**
   * It Actualty grouped groupd the events into groups
   * The reason behind this architecture whe use the eth_getLogs, it return events as single ojects of  arrary
   * While a transaction can emits sigle and multiple event to have propoer calaulation and iolsated calualtion we have goupped the transactions and events
   * @param data 
   */

  private async process(data: EventJobData): Promise<void> {
    const { chainId, fromBlock, toBlock, blockTimestamps } = data;
    const logs = data.logs.map((l: any) => ({ ...l, blockNumber: BigInt(l.blockNumber) }));
    const blockNumbers = data.blockNumbers.map((b: any) => BigInt(b));

    console.log(
      `[EventProcessor] Chain ${chainId} Blocks ${fromBlock}-${toBlock}: ${logs.length} logs`
    );

    // Group logs by transaction
    const txMap = new Map<string, GroupedTransaction>();

    for (const log of logs) {
      const txHash = log.transactionHash;

      if (!txMap.has(txHash)) {
        txMap.set(txHash, {
          blockHash: log.blockHash,
          blockNumber: log.blockNumber,
          blockTimestamp: blockTimestamps[log.blockNumber.toString()] || 0,
          removed: log.removed,
          transactionHash: txHash,
          transactionIndex: log.transactionIndex,
          events: [],
        });
      }

      const eventData: EventData = {
        logIndex: log.logIndex,
        topics: log.topics,
        data: log.data,
        address: log.address,
      };

      txMap.get(txHash)!.events.push(eventData);
    }

    // Separate into single and multi-event transactions
    const single: GroupedTransaction[] = [];
    const multi: GroupedTransaction[] = [];

    for (const tx of txMap.values()) {
      if (tx.events.length === 1) {
        single.push(tx);
      } else {
        multi.push(tx);
      }
    }
    // Push to grouped event queue for further processing
    if (single.length > 0 || multi.length > 0) {
      await groupedEventQueue.add(`grouped-${fromBlock}-${toBlock}`, {
        chainId,
        fromBlock,
        toBlock,
        single: single.map(tx => ({ ...tx, blockNumber: tx.blockNumber.toString() })),
        multi: multi.map(tx => ({ ...tx, blockNumber: tx.blockNumber.toString() })),
        blockNumbers: blockNumbers.map(b => b.toString())
      } as any);
    }
  }

  async close(): Promise<void> {
    await this.worker.close();
  }
}
