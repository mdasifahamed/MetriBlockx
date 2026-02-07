import { PrismaClient } from "../src/generated/prisma";

const prisma = new PrismaClient();

const chainConfigs = [
  { chainId: 1, networkName: "Ethereum Mainnet", tokenSymbol: "ETH" },
  { chainId: 137, networkName: "Polygon", tokenSymbol: "MATIC" },
  { chainId: 42161, networkName: "Arbitrum One", tokenSymbol: "ETH" },
  { chainId: 10, networkName: "Optimism", tokenSymbol: "ETH" },
  { chainId: 8453, networkName: "Base", tokenSymbol: "ETH" },
  { chainId: 56, networkName: "BNB Smart Chain", tokenSymbol: "BNB" },
  { chainId: 43114, networkName: "Avalanche C-Chain", tokenSymbol: "AVAX" },
];

async function main() {
  console.log("Initial Chain Config");

  for (const config of chainConfigs) {
    await prisma.chainConfig.upsert({
      where: { chainId: config.chainId },
      update: {
        networkName: config.networkName,
        tokenSymbol: config.tokenSymbol,
      },
      create: config,
    });
    console.log(`${config.networkName} (chainId: ${config.chainId})`);
  }

  console.log("\nChain Config Is Done");
}

main()
  .catch((e) => {
    console.error("Initial Chain Config:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
