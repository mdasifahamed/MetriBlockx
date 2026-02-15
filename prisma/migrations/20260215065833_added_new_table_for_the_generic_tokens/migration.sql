-- CreateEnum
CREATE TYPE "OperationType" AS ENUM ('DEPOSIT', 'WITHDRAWAL');

-- CreateTable
CREATE TABLE "token_transfers" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "token_transfers_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "token_cex_flows" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "cex_name" TEXT NOT NULL,
    "flow_type" "FlowType" NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "token_cex_flows_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "token_supply_events" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "supply_type" "TokenSupplyType" NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "token_supply_events_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "token_deposit_withdrawals" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "operation_type" "OperationType" NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "token_deposit_withdrawals_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateIndex
CREATE INDEX "token_transfers_chain_id_block_time_stamp_idx" ON "token_transfers"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_transfers_chain_id_token_address_idx" ON "token_transfers"("chain_id", "token_address");

-- CreateIndex
CREATE INDEX "token_transfers_block_number_idx" ON "token_transfers"("block_number");

-- CreateIndex
CREATE INDEX "token_transfers_block_time_stamp_idx" ON "token_transfers"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "token_transfers_chain_id_token_address_block_number_block_t_key" ON "token_transfers"("chain_id", "token_address", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_cex_flows_chain_id_block_time_stamp_idx" ON "token_cex_flows"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_cex_flows_chain_id_token_address_flow_type_idx" ON "token_cex_flows"("chain_id", "token_address", "flow_type");

-- CreateIndex
CREATE INDEX "token_cex_flows_chain_id_cex_name_flow_type_idx" ON "token_cex_flows"("chain_id", "cex_name", "flow_type");

-- CreateIndex
CREATE INDEX "token_cex_flows_block_number_idx" ON "token_cex_flows"("block_number");

-- CreateIndex
CREATE INDEX "token_cex_flows_block_time_stamp_idx" ON "token_cex_flows"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "token_cex_flows_chain_id_token_address_cex_name_flow_type_b_key" ON "token_cex_flows"("chain_id", "token_address", "cex_name", "flow_type", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_supply_events_chain_id_block_time_stamp_idx" ON "token_supply_events"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_supply_events_chain_id_token_address_supply_type_idx" ON "token_supply_events"("chain_id", "token_address", "supply_type");

-- CreateIndex
CREATE INDEX "token_supply_events_block_number_idx" ON "token_supply_events"("block_number");

-- CreateIndex
CREATE INDEX "token_supply_events_supply_type_idx" ON "token_supply_events"("supply_type");

-- CreateIndex
CREATE INDEX "token_supply_events_block_time_stamp_idx" ON "token_supply_events"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "token_supply_events_chain_id_token_address_supply_type_bloc_key" ON "token_supply_events"("chain_id", "token_address", "supply_type", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_deposit_withdrawals_chain_id_block_time_stamp_idx" ON "token_deposit_withdrawals"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "token_deposit_withdrawals_chain_id_token_address_operation__idx" ON "token_deposit_withdrawals"("chain_id", "token_address", "operation_type");

-- CreateIndex
CREATE INDEX "token_deposit_withdrawals_block_number_idx" ON "token_deposit_withdrawals"("block_number");

-- CreateIndex
CREATE INDEX "token_deposit_withdrawals_block_time_stamp_idx" ON "token_deposit_withdrawals"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "token_deposit_withdrawals_chain_id_token_address_operation__key" ON "token_deposit_withdrawals"("chain_id", "token_address", "operation_type", "block_number", "block_time_stamp");

-- AddForeignKey
ALTER TABLE "token_transfers" ADD CONSTRAINT "token_transfers_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_transfers" ADD CONSTRAINT "token_transfers_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_cex_flows" ADD CONSTRAINT "token_cex_flows_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_cex_flows" ADD CONSTRAINT "token_cex_flows_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_supply_events" ADD CONSTRAINT "token_supply_events_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_supply_events" ADD CONSTRAINT "token_supply_events_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_deposit_withdrawals" ADD CONSTRAINT "token_deposit_withdrawals_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "token_deposit_withdrawals" ADD CONSTRAINT "token_deposit_withdrawals_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;
