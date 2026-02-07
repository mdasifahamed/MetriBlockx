import { prisma } from "./DatabaseClient";
import { FlowType } from "../generated/prisma";

export interface CexFlowInput {
  chainId: number;
  blockNumber: bigint;
  blockTimeStamp: Date;
  cexName: string;
  flowType: FlowType;
  totalAmount: string;
  totalAmountHuman: string;
  transactionHashes: string[];
  transactionCount: number;
}

/**
 * A class that handles the storing the CEX transfer data
 * 
 */
export class CexFlowStorage {
  /**
   * Insert an single transaction
   * @param data single cex flow
   */
  async insert(data: CexFlowInput): Promise<void> {
    await prisma.cexFlow.upsert({
      where: {
        chainId_cexName_flowType_blockNumber_blockTimeStamp: {
          chainId: data.chainId,
          cexName: data.cexName,
          flowType: data.flowType,
          blockNumber: data.blockNumber,
          blockTimeStamp: data.blockTimeStamp,
        },
      },
      update: {
        totalAmount: data.totalAmount,
        totalAmountHuman: data.totalAmountHuman,
        transactionHashes: data.transactionHashes,
        transactionCount: data.transactionCount,
      },
      create: data,
    });

  }

  /**
   * bacth inser function 
   * @param records array of cex flow
   * @returns 
   */
  async insertBatch(records: CexFlowInput[]): Promise<void> {
    if (records.length === 0) return;

    const operations = records.map((data) =>
      prisma.cexFlow.upsert({
        where: {
          chainId_cexName_flowType_blockNumber_blockTimeStamp: {
            chainId: data.chainId,
            cexName: data.cexName,
            flowType: data.flowType,
            blockNumber: data.blockNumber,
            blockTimeStamp: data.blockTimeStamp,
          },
        },
        update: {
          totalAmount: data.totalAmount,
          totalAmountHuman: data.totalAmountHuman,
          transactionHashes: data.transactionHashes,
          transactionCount: data.transactionCount,
        },
        create: data,
      })
    );

    await prisma.$transaction(operations);
    await prisma.$disconnect()
  }
}
