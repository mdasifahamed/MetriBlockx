-- CreateIndex
CREATE INDEX "decoded_event_range_created_at_idx" ON "decoded_event_range"("created_at" DESC);

-- CreateIndex
CREATE INDEX "metrics_generated_created_at_idx" ON "metrics_generated"("created_at" DESC);