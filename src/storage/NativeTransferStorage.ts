import { prisma } from "./DatabaseClient";

export interface NativeTransferInput {
  chainId: number;
  blockNumber: bigint;
  blockHash: string;
  blockTimeStamp: Date;
  totalAmount: string;
  transactionHashes: string[];
}

/**
 * Handles Native Transfer Storage
 */
export class NativeTransferStorage {
  async insert(data: NativeTransferInput): Promise<void> {
    await prisma.nativeTransfer.upsert({
      where: {
        chainId_blockNumber_blockTimeStamp: {
          chainId: data.chainId,
          blockNumber: data.blockNumber,
          blockTimeStamp: data.blockTimeStamp,
        },
      },
      update: {
        totalAmount: data.totalAmount,
        transactionHashes: data.transactionHashes,
      },
      create: data,
    });

  }

  async insertBatch(records: NativeTransferInput[]): Promise<void> {
    if (records.length === 0) return;

    const operations = records.map((data) =>
      prisma.nativeTransfer.upsert({
        where: {
          chainId_blockNumber_blockTimeStamp: {
            chainId: data.chainId,
            blockNumber: data.blockNumber,
            blockTimeStamp: data.blockTimeStamp,
          },
        },
        update: {
          totalAmount: data.totalAmount,
          transactionHashes: data.transactionHashes,
        },
        create: data,
      })
    );

    await prisma.$transaction(operations);

  }
}
