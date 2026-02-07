import { PrismaClient } from "../src/generated/prisma";

const prisma = new PrismaClient();

async function cleanDatabase() {
  console.log("Cleaning database...\n");

  try {
    // Drop all tables
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS pool_fees CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS pool_liquidity CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS pool_swaps CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS stablecoin_cex_flows CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS stablecoin_transfers CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS decoded_events CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS cex_flows CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS native_transfers CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS pools CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS tokens CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS chain_config CASCADE`);

    // Drop Prisma migrations table
    await prisma.$executeRawUnsafe(`DROP TABLE IF EXISTS _prisma_migrations CASCADE`);

    // Drop enum types
    await prisma.$executeRawUnsafe(`DROP TYPE IF EXISTS "FlowType" CASCADE`);
    await prisma.$executeRawUnsafe(`DROP TYPE IF EXISTS "LiquidityType" CASCADE`);

    console.log("Database cleaned successfully!");
  } catch (error) {
    console.error("Error cleaning database:", error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

cleanDatabase();
