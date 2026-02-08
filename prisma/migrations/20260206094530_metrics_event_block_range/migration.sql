-- CreateTable
CREATE TABLE "decoded_event_range" (
    "id" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "block_numbers" BIGINT[],
    "created_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "decoded_event_range_pkey" PRIMARY KEY ("id","created_at")
);

-- CreateTable
CREATE TABLE "metrics_generated" (
    "id" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "block_number" BIGINT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "metrics_generated_pkey" PRIMARY KEY ("id","created_at")
);

-- CreateIndex
CREATE INDEX "decoded_event_range_id_chain_id_idx" ON "decoded_event_range"("id", "chain_id");

-- CreateIndex
CREATE INDEX "decoded_event_range_chain_id_idx" ON "decoded_event_range"("chain_id");

-- CreateIndex
CREATE INDEX "decoded_event_range_chain_id_created_at_idx" ON "decoded_event_range"("chain_id", "created_at");

-- CreateIndex
CREATE INDEX "metrics_generated_id_chain_id_idx" ON "metrics_generated"("id", "chain_id");

-- CreateIndex
CREATE INDEX "metrics_generated_chain_id_created_at_idx" ON "metrics_generated"("chain_id", "created_at");

-- AddForeignKey
ALTER TABLE "decoded_event_range" ADD CONSTRAINT "decoded_event_range_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "metrics_generated" ADD CONSTRAINT "metrics_generated_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;