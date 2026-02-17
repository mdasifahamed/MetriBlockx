import { redisConnection } from "../config/redis";

export interface BlockRangeNotification {
    chainId: number
    createdAt: Date
}


interface StreamConfig {
    streamName: string
    group: string
}

export class SendEventBlockRange {
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
     * Send event to appropriate Redis stream based on chain ID
     * @param data Block range notification with chainId
     * @returns Message ID if successful, undefined if failed
     */
    async sendEventBlockRange(data: BlockRangeNotification): Promise<string | null | undefined> {
        let streamConfig: StreamConfig | null = null;
        let chainName = '';
        switch (data.chainId) {
            case 1:
                streamConfig = this.ethStreamConfig;
                chainName = 'Ethereum';
                break;
            case 56:
                streamConfig = this.bnbStreamConfig;
                chainName = 'BNB';
                break;
            case 137:
                streamConfig = this.polStreamConfig;
                chainName = 'Polygon';
                break;
            default:
                console.error(`✗ Unsupported chainId: ${data.chainId}`);
                return undefined;
        }

        return this.sendToStream(streamConfig, data, chainName);
    }

    /**
     * Internal method to send data to a specific stream with production configurations
     * @param streamConfig Stream configuration
     * @param data Notification data to send
     * @param chainName Human-readable chain name for logging
     */
    private async sendToStream(
        streamConfig: StreamConfig,
        data: BlockRangeNotification,
        chainName: string
    ): Promise<string | null | undefined> {
        try {
            // XADD parameters:
            // - streamConfig.streamName: Redis stream key
            // - "MAXLEN": Trim stream to max size (20K messages)
            // - "data": Field name
            // - JSON.stringify(data): Field value
            const messageId = await redisConnection.xadd(
                streamConfig.streamName,
                "MAXLEN",
                "~",
                "20000",
                "*",
                'data',
                JSON.stringify(data)
            );

            console.log(`[${chainName}] Event sent to stream '${streamConfig.streamName}' - Message ID: ${messageId}`);
            return messageId;
        } catch (err: any) {
            console.error(
                `[${chainName}] Failed to send event to stream '${streamConfig.streamName}':`,
                err.message
            );
            throw err;
        }
    }
}