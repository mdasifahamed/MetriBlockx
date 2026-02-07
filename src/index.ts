import { CHAINS, getChainConfig } from "./config/chains";
import { EthereumWorker } from "./workers/EthereumWorker";
import { PolygonWorker } from "./workers/PolygonWorker";
import { BnbWorker } from "./workers/BnbWorker";
import { BaseChainWorker } from "./workers/BaseChainWorker";

// Store active workers for graceful shutdown
const activeWorkers: BaseChainWorker[] = [];

function createWorker(chainName: string, targetBlock: number): BaseChainWorker {
  switch (chainName) {
    case "ethereum":
      return new EthereumWorker(targetBlock);
    case "polygon":
      return new PolygonWorker(targetBlock);
    case "bnb":
      return new BnbWorker(targetBlock);
    default:
      throw new Error(
        `Unknown chain: ${chainName}. Available chains: ${Object.keys(CHAINS).join(", ")}`
      );
  }
}

async function main(): Promise<void> {
  // Parse command line arguments
  const chainArg = process.argv.find((arg) => arg.startsWith("--chain="));
  const blockArg = process.argv.find((arg) => arg.startsWith("--block="));
  const targetBlockArg = process.argv.find((arg) => arg.startsWith("--targetBlock="));

  const chain = chainArg?.split("=")[1] ?? "ethereum";
  const blockStr = blockArg?.split("=")[1];
  const targetBlockStr = targetBlockArg?.split("=")[1]
  const startBlock = blockStr ? parseInt(blockStr, 10) : undefined;
  const targetBlock = targetBlockStr ? parseInt(targetBlockStr, 10) : undefined;

  console.log("Data Fetcher Started");



  console.log(`Starting worker for: ${chain}`);
  if (!targetBlock) {
    throw Error(`Target Block Is Required For The ${chain}`)
  }
  const worker = createWorker(chain, targetBlock);
  activeWorkers.push(worker);

  await worker.start(startBlock);

}

// Graceful shutdown handler
function shutdown(): void {

  console.log(" Shutting down workers");


  activeWorkers.forEach((worker) => {
    const status = worker.getStatus();
    console.log(`[${status.chain}] Event phase at: ${status.eventBlock} | Block phase at: ${status.blockBlock}`);
    worker.stop();
  });

  // Give workers time to clean up
  setTimeout(() => {
    console.log("\nAll workers stopped. Goodbye!");
    process.exit(0);
  }, 1000);
}

// Handle termination signals
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

// Handle uncaught errors
process.on("uncaughtException", (error) => {
  console.error("Uncaught exception:", error);
  shutdown();
});

process.on("unhandledRejection", (reason) => {
  console.error("Unhandled rejection:", reason);
  shutdown();
});

// Start the process
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
