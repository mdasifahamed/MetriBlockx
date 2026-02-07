import { redisConnection } from "../config/redis";

interface StreamConfig {
    streamName: string
    group: string
}


export class BlockRangeEventStreamCreator {
    private ethStreamConfig: StreamConfig = {
        streamName: 'eth_stream',
        group: 'eth_group'
    }
    private bnbStreamConfig: StreamConfig = {
        streamName: 'bnb_stream',
        group: 'bnb_group'
    }
    private polStreamConfig: StreamConfig = {
        streamName: 'pol_stream',
        group: 'pol_group'
    }

    /**
     * Initialize a Redis consumer group with BUSYGROUP error handling and ENTRIESREAD tracking
     * @param streamName - Name of the Redis stream
     * @param groupName - Name of the consumer group
     */
    private async initConsumerGroup(streamName: string, groupName: string): Promise<void> {
        try {
            const streamLength = await redisConnection.xlen(streamName);
            await redisConnection.xgroup(
                "CREATE",
                streamName,
                groupName,
                "$",  // Start from latest entry (new messages only)
                "MKSTREAM",
                "ENTRIESREAD",
                streamLength
            );

            console.log(`✓ Consumer group '${groupName}' created for stream '${streamName}' (ENTRIESREAD: ${streamLength})`);
        } catch (err: any) {
            if (err.message && err.message.includes("BUSYGROUP")) {
                console.log(`Consumer group '${groupName}' already exists for stream '${streamName}' - skipping creation`);
            } else {
                console.error(`Failed to create consumer group '${groupName}' for stream '${streamName}':`, err.message);
                throw err;
            }
        }
    }

    async initStream(): Promise<void> {
        console.log("Initializing Redis streams for MetricBlockx...");

        const initResults = await Promise.allSettled([
            this.initConsumerGroup(this.ethStreamConfig.streamName, this.ethStreamConfig.group),
            this.initConsumerGroup(this.bnbStreamConfig.streamName, this.bnbStreamConfig.group),
            this.initConsumerGroup(this.polStreamConfig.streamName, this.polStreamConfig.group)
        ]);
        initResults.forEach((result, index) => {
            const chains = ['ETH', 'BNB', 'POL'];
            if (result.status === 'rejected') {
                console.error(`✗ ${chains[index]} stream initialization failed:`, result.reason);
            }
        });

        console.log("Stream initialization completed MetricBlockx...");
    }
}