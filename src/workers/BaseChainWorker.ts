import { ChainConfig } from "../config/chains";
import { RpcManager } from "../core/RpcManager";
import { BlockFetcher, BlockData } from "../core/BlockFetcher";
import { EventFetcher, LogData } from "../core/EventFetcher";
import { blockQueue, eventQueue } from "../processors/queues";

/**
 * Base worker class for the each network
 */
export abstract class BaseChainWorker {
  protected rpc: RpcManager;
  protected blockFetcher: BlockFetcher;
  protected eventFetcher: EventFetcher;
  protected isRunning = false;

  // Separate progress tracking for each phase
  protected eventBlock = 0;
  protected blockBlock = 0;
  protected targetBlock = 0;

  constructor(protected config: ChainConfig, targetBlock: number) {
    this.rpc = new RpcManager(config.rpcEndpoints, config.name, targetBlock);
    this.blockFetcher = new BlockFetcher(this.rpc);
    this.eventFetcher = new EventFetcher(this.rpc);
    this.targetBlock = targetBlock;
  }

  async start(fromBlock?: number): Promise<void> {
    this.isRunning = true;
    const startBlock = fromBlock ?? this.targetBlock;

    this.eventBlock = startBlock;
    this.blockBlock = startBlock;

    console.log(`\n========================================`);
    console.log(`[${this.config.name}] Worker Started (Dual-Phase)`);
    console.log(`[${this.config.name}] Chain ID: ${this.config.id}`);
    console.log(`[${this.config.name}] Starting from block: ${startBlock}`);
    console.log(`[${this.config.name}] Target block: ${this.targetBlock}`);
    console.log(`[${this.config.name}] Event batch size: ${this.config.blockThresholdForTheEvents}`);
    console.log(`[${this.config.name}] Target addresses: ${this.config.targetAddresses.length}`);
    console.log(`========================================\n`);

    // Run both phases concurrently
    await Promise.all([
      this.runEventPhase(),
      this.runBlockPhase()
    ]);
  }

  /**
   * Start the receieving the events from the networks
   */
  private async runEventPhase(): Promise<void> {
    console.log(`[${this.config.name}] Event phase started`);

    while (this.isRunning && this.eventBlock <= this.targetBlock) {
      try {
        const batchEnd = Math.min(
          this.eventBlock + this.config.blockThresholdForTheEvents - 1,
          this.targetBlock
        );


        const logs = await this.eventFetcher.fetchLogsWithFilter(
          this.eventBlock,
          batchEnd,
          this.config.targetAddresses.length > 0 ? this.config.targetAddresses : undefined
        );


        // Process events (chain-specific)
        await this.onEventsProcessed(logs);

        this.eventBlock = batchEnd + 1;
      } catch (error) {
        console.error(
          `[${this.config.name}] Event phase error at block ${this.eventBlock}:`,
          error instanceof Error ? error.message : error
        );
        await this.sleep(15000);
      }
    }

    console.log(`[${this.config.name}] Event phase completed at block ${this.eventBlock - 1}`);
  }

  private async runBlockPhase(): Promise<void> {
    console.log(`[${this.config.name}] Block phase started`);

    while (this.isRunning && this.blockBlock <= this.targetBlock) {
      try {
        const block = await this.blockFetcher.fetchBlock(this.blockBlock);
        await this.onBlockProcessed(block);

        this.blockBlock++;
        await this.sleep(this.config.blockTime);
      } catch (error) {
        console.error(
          `[${this.config.name}] Block phase error at block ${this.blockBlock}:`,
          error instanceof Error ? error.message : error
        );
        await this.sleep(15000);
      }
    }

    console.log(`[${this.config.name}] Block phase completed at block ${this.blockBlock - 1}`);
  }


  /**
   * The function the processes the block level transactions  the push it to the bull job
   * @param block BlokcData with trasnactions set
   */

  protected async onBlockProcessed(block: BlockData): Promise<void> {
    await blockQueue.add(`block-${block.number}`, {
      chainId: this.config.id,
      block,
    });
  }

  /**
   * push ;ogdata to the bullq job for the further processing
   * @param logs 
   */
  protected async onEventsProcessed(logs: LogData[]): Promise<void> {
    // Get unique block numbers from logs
    const uniqueBlocks = [...new Set(logs.map(log => log.blockNumber))];

    // Fetch timestamps for each unique block
    const blockTimestamps: Record<string, number> = {};
    for (const blockNum of uniqueBlocks) {
      const block = await this.blockFetcher.fetchBlock(Number(blockNum));
      blockTimestamps[blockNum.toString()] = block.timestamp;
    }

    await eventQueue.add(`events-${this.eventBlock}`, {
      chainId: this.config.id,
      fromBlock: this.eventBlock,
      toBlock: Math.min(this.eventBlock + this.config.blockThresholdForTheEvents - 1, this.targetBlock),
      logs: logs.map(l => ({ ...l, blockNumber: l.blockNumber.toString() })),
      blockTimestamps,
      blockNumbers: uniqueBlocks.map(b => b.toString())
    } as any);
  }

  stop(): void {
    this.isRunning = false;
    console.log(`\n[${this.config.name}] Worker stopping...`);
    console.log(`[${this.config.name}] Event phase at block: ${this.eventBlock}`);
    console.log(`[${this.config.name}] Block phase at block: ${this.blockBlock}`);
  }

  getStatus(): { chain: string; running: boolean; eventBlock: number; blockBlock: number } {
    return {
      chain: this.config.name,
      running: this.isRunning,
      eventBlock: this.eventBlock,
      blockBlock: this.blockBlock,
    };
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
