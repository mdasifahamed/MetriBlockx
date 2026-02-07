-- CreateEnum
CREATE TYPE "FlowType" AS ENUM ('INFLOW', 'OUTFLOW');

-- CreateEnum
CREATE TYPE "LiquidityType" AS ENUM ('ADD', 'REMOVE');

-- CreateTable
CREATE TABLE "chain_config" (
    "chain_id" INTEGER NOT NULL,
    "network_name" TEXT NOT NULL,
    "token_symbol" TEXT NOT NULL,

    CONSTRAINT "chain_config_pkey" PRIMARY KEY ("chain_id")
);

-- CreateTable
CREATE TABLE "tokens" (
    "id" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "token_decimal" INTEGER NOT NULL,
    "token_name" TEXT NOT NULL,
    "token_symbol" TEXT NOT NULL,

    CONSTRAINT "tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "pools" (
    "id" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "dex_name" TEXT NOT NULL,
    "dex_version" TEXT,
    "pool_address" TEXT NOT NULL,
    "pool_symbol" TEXT NOT NULL,
    "token_0_address" TEXT NOT NULL,
    "token_1_address" TEXT NOT NULL,
    "fees" INTEGER NOT NULL,

    CONSTRAINT "pools_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "native_transfers" (
    "id" TEXT NOT NULL,
    "block_hash" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "total_amount" TEXT NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "native_transfers_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "cex_flows" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "cex_name" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "flow_type" "FlowType" NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "cex_flows_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "decoded_events" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "contract_address" TEXT NOT NULL,
    "event_args" JSONB NOT NULL,
    "event_name" TEXT NOT NULL,
    "transaction_hash" TEXT NOT NULL,
    "transaction_index" INTEGER NOT NULL,

    CONSTRAINT "decoded_events_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "stablecoin_transfers" (
    "id" TEXT NOT NULL,
    "block_hash" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "stablecoin_transfers_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "stablecoin_cex_flows" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "cex_name" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "flow_type" "FlowType" NOT NULL,
    "token_address" TEXT NOT NULL,
    "total_amount" TEXT NOT NULL,
    "total_amount_human" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "stablecoin_cex_flows_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "pool_swaps" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "pool_address" TEXT NOT NULL,
    "swap_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],
    "volume_token_0" TEXT NOT NULL,
    "volume_token_0_human" TEXT NOT NULL,
    "volume_token_1" TEXT NOT NULL,
    "volume_token_1_human" TEXT NOT NULL,

    CONSTRAINT "pool_swaps_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "pool_liquidity" (
    "id" TEXT NOT NULL,
    "amount_token_0" TEXT NOT NULL,
    "amount_token_0_human" TEXT NOT NULL,
    "amount_token_1" TEXT NOT NULL,
    "amount_token_1_human" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "liquidity_type" "LiquidityType" NOT NULL,
    "pool_address" TEXT NOT NULL,
    "transaction_count" INTEGER NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "pool_liquidity_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateTable
CREATE TABLE "pool_fees" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "collect_count" INTEGER NOT NULL,
    "fees_token_0" TEXT NOT NULL,
    "fees_token_0_human" TEXT NOT NULL,
    "fees_token_1" TEXT NOT NULL,
    "fees_token_1_human" TEXT NOT NULL,
    "pool_address" TEXT NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "pool_fees_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateIndex
CREATE INDEX "tokens_token_symbol_chain_id_idx" ON "tokens"("token_symbol", "chain_id");

-- CreateIndex
CREATE UNIQUE INDEX "tokens_chain_id_token_address_key" ON "tokens"("chain_id", "token_address");

-- CreateIndex
CREATE INDEX "pools_chain_id_dex_name_idx" ON "pools"("chain_id", "dex_name");

-- CreateIndex
CREATE INDEX "pools_chain_id_token_0_address_idx" ON "pools"("chain_id", "token_0_address");

-- CreateIndex
CREATE INDEX "pools_chain_id_token_1_address_idx" ON "pools"("chain_id", "token_1_address");

-- CreateIndex
CREATE UNIQUE INDEX "pools_chain_id_pool_address_key" ON "pools"("chain_id", "pool_address");

-- CreateIndex
CREATE INDEX "native_transfers_chain_id_block_time_stamp_idx" ON "native_transfers"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "native_transfers_block_number_idx" ON "native_transfers"("block_number");

-- CreateIndex
CREATE INDEX "native_transfers_block_time_stamp_idx" ON "native_transfers"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "native_transfers_chain_id_block_number_block_time_stamp_key" ON "native_transfers"("chain_id", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "cex_flows_chain_id_block_time_stamp_idx" ON "cex_flows"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "cex_flows_cex_name_flow_type_idx" ON "cex_flows"("cex_name", "flow_type");

-- CreateIndex
CREATE INDEX "cex_flows_block_number_idx" ON "cex_flows"("block_number");

-- CreateIndex
CREATE INDEX "cex_flows_chain_id_cex_name_flow_type_idx" ON "cex_flows"("chain_id", "cex_name", "flow_type");

-- CreateIndex
CREATE INDEX "cex_flows_block_time_stamp_idx" ON "cex_flows"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "cex_flows_chain_id_cex_name_flow_type_block_number_block_ti_key" ON "cex_flows"("chain_id", "cex_name", "flow_type", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "decoded_events_chain_id_block_time_stamp_idx" ON "decoded_events"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "decoded_events_contract_address_idx" ON "decoded_events"("contract_address");

-- CreateIndex
CREATE INDEX "decoded_events_event_name_idx" ON "decoded_events"("event_name");

-- CreateIndex
CREATE INDEX "decoded_events_transaction_hash_idx" ON "decoded_events"("transaction_hash");

-- CreateIndex
CREATE INDEX "decoded_events_chain_id_contract_address_event_name_block_n_idx" ON "decoded_events"("chain_id", "contract_address", "event_name", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "decoded_events_chain_id_contract_address_event_name_block_t_idx" ON "decoded_events"("chain_id", "contract_address", "event_name", "block_time_stamp");

-- CreateIndex
CREATE INDEX "decoded_events_block_time_stamp_idx" ON "decoded_events"("block_time_stamp" DESC);

-- CreateIndex
CREATE INDEX "stablecoin_transfers_chain_id_block_time_stamp_idx" ON "stablecoin_transfers"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "stablecoin_transfers_chain_id_token_address_idx" ON "stablecoin_transfers"("chain_id", "token_address");

-- CreateIndex
CREATE INDEX "stablecoin_transfers_block_number_idx" ON "stablecoin_transfers"("block_number");

-- CreateIndex
CREATE INDEX "stablecoin_transfers_block_time_stamp_idx" ON "stablecoin_transfers"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "stablecoin_transfers_chain_id_token_address_block_number_bl_key" ON "stablecoin_transfers"("chain_id", "token_address", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "stablecoin_cex_flows_chain_id_block_time_stamp_idx" ON "stablecoin_cex_flows"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "stablecoin_cex_flows_chain_id_cex_name_flow_type_idx" ON "stablecoin_cex_flows"("chain_id", "cex_name", "flow_type");

-- CreateIndex
CREATE INDEX "stablecoin_cex_flows_chain_id_token_address_flow_type_idx" ON "stablecoin_cex_flows"("chain_id", "token_address", "flow_type");

-- CreateIndex
CREATE INDEX "stablecoin_cex_flows_block_number_idx" ON "stablecoin_cex_flows"("block_number");

-- CreateIndex
CREATE INDEX "stablecoin_cex_flows_block_time_stamp_idx" ON "stablecoin_cex_flows"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "stablecoin_cex_flows_chain_id_token_address_cex_name_flow_t_key" ON "stablecoin_cex_flows"("chain_id", "token_address", "cex_name", "flow_type", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_swaps_chain_id_block_time_stamp_idx" ON "pool_swaps"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_swaps_chain_id_pool_address_idx" ON "pool_swaps"("chain_id", "pool_address");

-- CreateIndex
CREATE INDEX "pool_swaps_block_number_idx" ON "pool_swaps"("block_number");

-- CreateIndex
CREATE INDEX "pool_swaps_block_time_stamp_idx" ON "pool_swaps"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "pool_swaps_chain_id_pool_address_block_number_block_time_st_key" ON "pool_swaps"("chain_id", "pool_address", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_liquidity_chain_id_block_time_stamp_idx" ON "pool_liquidity"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_liquidity_chain_id_pool_address_liquidity_type_idx" ON "pool_liquidity"("chain_id", "pool_address", "liquidity_type");

-- CreateIndex
CREATE INDEX "pool_liquidity_block_number_idx" ON "pool_liquidity"("block_number");

-- CreateIndex
CREATE INDEX "pool_liquidity_block_time_stamp_idx" ON "pool_liquidity"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "pool_liquidity_chain_id_pool_address_liquidity_type_block_n_key" ON "pool_liquidity"("chain_id", "pool_address", "liquidity_type", "block_number", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_fees_chain_id_block_time_stamp_idx" ON "pool_fees"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_fees_chain_id_pool_address_idx" ON "pool_fees"("chain_id", "pool_address");

-- CreateIndex
CREATE INDEX "pool_fees_block_number_idx" ON "pool_fees"("block_number");

-- CreateIndex
CREATE INDEX "pool_fees_block_time_stamp_idx" ON "pool_fees"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "pool_fees_chain_id_pool_address_block_number_block_time_sta_key" ON "pool_fees"("chain_id", "pool_address", "block_number", "block_time_stamp");

-- AddForeignKey
ALTER TABLE "tokens" ADD CONSTRAINT "tokens_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pools" ADD CONSTRAINT "pools_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pools" ADD CONSTRAINT "pools_chain_id_token_0_address_fkey" FOREIGN KEY ("chain_id", "token_0_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pools" ADD CONSTRAINT "pools_chain_id_token_1_address_fkey" FOREIGN KEY ("chain_id", "token_1_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "native_transfers" ADD CONSTRAINT "native_transfers_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cex_flows" ADD CONSTRAINT "cex_flows_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "decoded_events" ADD CONSTRAINT "decoded_events_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stablecoin_transfers" ADD CONSTRAINT "stablecoin_transfers_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stablecoin_transfers" ADD CONSTRAINT "stablecoin_transfers_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stablecoin_cex_flows" ADD CONSTRAINT "stablecoin_cex_flows_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stablecoin_cex_flows" ADD CONSTRAINT "stablecoin_cex_flows_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_swaps" ADD CONSTRAINT "pool_swaps_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_swaps" ADD CONSTRAINT "pool_swaps_chain_id_pool_address_fkey" FOREIGN KEY ("chain_id", "pool_address") REFERENCES "pools"("chain_id", "pool_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_liquidity" ADD CONSTRAINT "pool_liquidity_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_liquidity" ADD CONSTRAINT "pool_liquidity_chain_id_pool_address_fkey" FOREIGN KEY ("chain_id", "pool_address") REFERENCES "pools"("chain_id", "pool_address") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_fees" ADD CONSTRAINT "pool_fees_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_fees" ADD CONSTRAINT "pool_fees_chain_id_pool_address_fkey" FOREIGN KEY ("chain_id", "pool_address") REFERENCES "pools"("chain_id", "pool_address") ON DELETE RESTRICT ON UPDATE CASCADE;
