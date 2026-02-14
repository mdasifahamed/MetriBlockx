-- CreateEnum
CREATE TYPE "TokenSupplyType" AS ENUM ('ISSUE', 'BURN');

-- CreateEnum
CREATE TYPE "TokenType" AS ENUM ('STABLE', 'WRAPPED', 'RWA', 'ERC20');

-- AlterTable
ALTER TABLE "tokens" ADD COLUMN     "token_type" "TokenType" NOT NULL DEFAULT 'ERC20';

-- CreateTable
CREATE TABLE "token_supply" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "token_supply_type" TEXT NOT NULL,
    "amount" TEXT NOT NULL,
    "transaction_hash" TEXT NOT NULL,

    CONSTRAINT "token_supply_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateIndex
CREATE INDEX "token_supply_chain_id_block_time_stamp_idx" ON "token_supply"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_supply_chain_id_token_address_token_supply_type_idx" ON "token_supply"("chain_id", "token_address", "token_supply_type");

-- CreateIndex
CREATE INDEX "token_supply_block_number_idx" ON "token_supply"("block_number");

-- CreateIndex
CREATE INDEX "token_supply_block_time_stamp_idx" ON "token_supply"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "token_supply_chain_id_token_address_token_supply_type_trans_key" ON "token_supply"("chain_id", "token_address", "token_supply_type", "transaction_hash", "block_time_stamp");

-- AddForeignKey
ALTER TABLE "token_supply" ADD CONSTRAINT "token_supply_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_supply" ADD CONSTRAINT "token_supply_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;
