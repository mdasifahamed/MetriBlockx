/*
  Warnings:

  - A unique constraint covering the columns `[chain_id,cex_name]` on the table `cex_addresses` will be added. If there are existing duplicate values, this will fail.

*/
-- DropIndex
DROP INDEX "cex_addresses_chain_id_address_key";

-- CreateIndex
CREATE UNIQUE INDEX "cex_addresses_chain_id_cex_name_key" ON "cex_addresses"("chain_id", "cex_name");
