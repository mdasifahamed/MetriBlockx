-- CreateTable
CREATE TABLE "pool_Reserve" (
    "id" TEXT NOT NULL,
    "block_number" BIGINT NOT NULL,
    "block_time_stamp" TIMESTAMP(3) NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "reserve_token_0" TEXT NOT NULL,
    "reserve_token_1" TEXT NOT NULL,
    "pool_address" TEXT NOT NULL,
    "transaction_hashes" TEXT[],

    CONSTRAINT "pool_Reserve_pkey" PRIMARY KEY ("id","block_time_stamp")
);

-- CreateIndex
CREATE INDEX "pool_Reserve_chain_id_block_time_stamp_idx" ON "pool_Reserve"("chain_id", "block_time_stamp");

-- CreateIndex
CREATE INDEX "pool_Reserve_chain_id_pool_address_idx" ON "pool_Reserve"("chain_id", "pool_address");

-- CreateIndex
CREATE INDEX "pool_Reserve_block_number_idx" ON "pool_Reserve"("block_number");

-- CreateIndex
CREATE INDEX "pool_Reserve_block_time_stamp_idx" ON "pool_Reserve"("block_time_stamp" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "pool_Reserve_chain_id_pool_address_block_number_block_time__key" ON "pool_Reserve"("chain_id", "pool_address", "block_number", "block_time_stamp");

-- AddForeignKey
ALTER TABLE "pool_Reserve" ADD CONSTRAINT "pool_Reserve_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pool_Reserve" ADD CONSTRAINT "pool_Reserve_chain_id_pool_address_fkey" FOREIGN KEY ("chain_id", "pool_address") REFERENCES "pools"("chain_id", "pool_address") ON DELETE RESTRICT ON UPDATE CASCADE;
