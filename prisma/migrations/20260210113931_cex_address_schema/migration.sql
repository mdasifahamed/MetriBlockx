-- CreateTable
CREATE TABLE "cex_addresses" (
    "id" TEXT NOT NULL,
    "chain_id" INTEGER NOT NULL,
    "cex_name" TEXT NOT NULL,
    "address" TEXT NOT NULL,

    CONSTRAINT "cex_addresses_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "cex_addresses_chain_id_cex_name_idx" ON "cex_addresses"("chain_id", "cex_name");

-- CreateIndex
CREATE INDEX "cex_addresses_chain_id_address_cex_name_idx" ON "cex_addresses"("chain_id", "address", "cex_name");

-- CreateIndex
CREATE INDEX "cex_addresses_chain_id_idx" ON "cex_addresses"("chain_id");

-- CreateIndex
CREATE UNIQUE INDEX "cex_addresses_chain_id_cex_name_key" ON "cex_addresses"("chain_id", "cex_name");

-- AddForeignKey
ALTER TABLE "cex_addresses" ADD CONSTRAINT "cex_addresses_chain_id_fkey" FOREIGN KEY ("chain_id") REFERENCES "chain_config"("chain_id") ON DELETE RESTRICT ON UPDATE CASCADE;
