import { prisma } from "./DatabaseClient";
import { Prisma } from "../generated/prisma";

export interface DecodedEventInput {
  chainId: number;
  blockNumber: bigint;
  blockTimeStamp: Date;
  contractAddress: string;
  transactionHash: string;
  transactionIndex: number;
  eventName: string;
  eventArgs: Prisma.InputJsonValue;
}

export interface EventBlockRange {
  chainId: number;
  blockNumbers: bigint[]
  createdAt: Date
}

/**
 * A class responsible for the storing decodedevents
 */
export class DecodedEventStorage {
  async insert(data: DecodedEventInput): Promise<void> {
    await prisma.decodedEvent.create({ data });

  }
  async insertDecodedEventBlockRange(data: EventBlockRange): Promise<void> {
    await prisma.decodedEventRange.create({ data })
  }

  async insertBatch(records: DecodedEventInput[]): Promise<void> {
    if (records.length === 0) return;
    await prisma.decodedEvent.createMany({ data: records });

  }
}
