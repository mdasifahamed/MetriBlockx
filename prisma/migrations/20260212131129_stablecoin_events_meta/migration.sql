-- CreateTable
CREATE TABLE "stablecoin_events_meta" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "token_address" TEXT NOT NULL,
    "event_type" TEXT NOT NULL,
    "event_data" JSONB NOT NULL,
    "transaction_hash" TEXT NOT NULL,

    CONSTRAINT "stablecoin_events_meta_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateIndex
CREATE INDEX "stablecoin_events_meta_chain_id_block_time_stamp_idx" ON "stablecoin_events_meta"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "stablecoin_events_meta_chain_id_token_address_event_type_idx" ON "stablecoin_events_meta"("chain_id", "token_address", "event_type");

-- CreateIndex
CREATE INDEX "stablecoin_events_meta_block_number_idx" ON "stablecoin_events_meta"("block_number");

-- CreateIndex
CREATE INDEX "stablecoin_events_meta_block_time_stamp_idx" ON "stablecoin_events_meta"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "stablecoin_events_meta_chain_id_token_address_event_type_tr_key" ON "stablecoin_events_meta"("chain_id", "token_address", "event_type", "transaction_hash", "block_time_stamp");

-- AddForeignKey
ALTER TABLE "stablecoin_events_meta" ADD CONSTRAINT "stablecoin_events_meta_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stablecoin_events_meta" ADD CONSTRAINT "stablecoin_events_meta_chain_id_token_address_fkey" FOREIGN KEY ("chain_id", "token_address") REFERENCES "tokens"("chain_id", "token_address") ON DELETE RESTRICT ON UPDATE CASCADE;
