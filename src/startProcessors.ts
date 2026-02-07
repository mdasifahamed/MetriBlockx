import { TransactionProcessor } from "./processors/TransactionProcessor";
import { EventProcessor } from "./processors/EventProcessor";
import { GroupedEventProcessor } from "./processors/GroupedEventProcessor";

const txProcessor = new TransactionProcessor();
const eventProcessor = new EventProcessor();
const groupedEventProcessor = new GroupedEventProcessor();

console.log("Processors started. Waiting for jobs...\n");

process.on("SIGINT", async () => {
  console.log("\nShutting down processors...");
  await txProcessor.close();
  await eventProcessor.close();
  await groupedEventProcessor.close();
  console.log("Processors stopped. Goodbye!");
  process.exit(0);
});

process.on("SIGTERM", async () => {
  await txProcessor.close();
  await eventProcessor.close();
  await groupedEventProcessor.close();
  process.exit(0);
});
