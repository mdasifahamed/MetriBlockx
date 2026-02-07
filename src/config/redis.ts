import { Redis } from "ioredis";
import 'dotenv/config';  // Auto-loads .env
import dotenv from 'dotenv';
dotenv.config();
/**
 * Creates redis connecstion to use bullMQ dor the worker queues
 */


export const redisConnection = new Redis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null, // to run bullmq it is required here to keeep it null
});



/**
 * Names ofthe queues is being used
 */
export const QUEUE_NAMES = {
  BLOCKS: "block-processing",
  EVENTS: "event-processing",
  GROUPED_EVENTS: "grouped-event-processing",
} as const;
