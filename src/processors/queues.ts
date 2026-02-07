import { Queue } from "bullmq";
import { redisConnection, QUEUE_NAMES } from "../config/redis";
import { BlockData } from "../core/BlockFetcher";
import { LogData } from "../core/EventFetcher";

// Block Job data types
export interface BlockJobData {
  chainId: number;
  block: BlockData;
}


// Event Job data types
export interface EventJobData {
  chainId: number;
  fromBlock: number;
  toBlock: number;
  logs: LogData[];
  blockTimestamps: Record<string, number>; // blockNumber.toString() -> timestamp
  blockNumbers: bigint[]

}

// Event data after extraction from log
export interface EventData {
  logIndex: number;
  topics: string[];
  data: string;
  address: string;
}

// Transaction with its associated events
export interface GroupedTransaction {
  blockHash: string;
  blockNumber: bigint;
  blockTimestamp: number;
  removed: boolean;
  transactionHash: string;
  transactionIndex: number;
  events: EventData[];
}

// Job data for grouped event processing
export interface GroupedEventJobData {
  chainId: number;
  fromBlock: number;
  toBlock: number;
  single: GroupedTransaction[];  // Transactions with 1 event
  multi: GroupedTransaction[];   // Transactions with multiple events
  blockNumbers: bigint[]
}

// Queues (producers push here)
export const blockQueue = new Queue<BlockJobData>(QUEUE_NAMES.BLOCKS, {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 5,
    backoff: { type: "exponential", delay: 10000 },
    removeOnComplete: 50,
    removeOnFail: 1000,
  },
});

export const eventQueue = new Queue<EventJobData>(QUEUE_NAMES.EVENTS, {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: "exponential", delay: 10000 },
    removeOnComplete: 50,
    removeOnFail: 1000,
  },
});

export const groupedEventQueue = new Queue<GroupedEventJobData>(QUEUE_NAMES.GROUPED_EVENTS, {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: "exponential", delay: 10000 },
    removeOnComplete: 50,
    removeOnFail: 1000,
  },
});

