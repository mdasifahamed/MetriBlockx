import { getChainConfig } from "../config/chains";
import { BaseChainWorker } from "./BaseChainWorker";
import { BlockData } from "../core/BlockFetcher";
import { LogData } from "../core/EventFetcher";

/**
 * Extends The Base Worker Responsible for the Polygon network
 */
export class PolygonWorker extends BaseChainWorker {
  constructor(protected targeBlock: number) {
    super(getChainConfig("polygon"), targeBlock);
  }

  protected logBlock(block: BlockData, fetchTimeMs: number): void {
    const timestamp = new Date(block.timestamp * 1000).toISOString();
    console.log(`\n[POLYGON] Block #${block.number}`);
    console.log(`  Hash: ${block.hash}`);
    console.log(`  Time: ${timestamp}`);
    console.log(`  Fetch Time: ${fetchTimeMs}ms`);
  }

  protected logEventBatch(fromBlock: number, toBlock: number, logs: LogData[], fetchTimeMs: number): void {
    console.log(`[POLYGON] Events ${fromBlock}-${toBlock} | Count: ${logs.length} | ${fetchTimeMs}ms`);
  }
}
