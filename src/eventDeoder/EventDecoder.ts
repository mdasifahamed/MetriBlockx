import { ethers } from "ethers";
import * as fs from "fs";
import * as path from "path";

export interface DecodedEventResult {
    contractAddress: string;
    chainId: number;
    blockNumber: bigint;
    blockTimeStamp: number;
    transactionHash: string;
    transactionIndex: number;
    eventName: string;
    eventArg: string;
}

export interface RawEvent {
    address: string;
    blockNumber: bigint;
    data: string;
    topics: string[];
    transactionHash: string;
    transactionIndex: number;
}

interface EventConfig {
    abi: string[];
    signature?: string;
    tokens?: string[];
}



/**
 * A single class that will handle the event data decoding based on the eventaatribute config we have in `eventAttributes.json` file
 */
export class EventDecoder {
    private interfaces: Map<string, { iface: ethers.Interface; eventName: string }>;

    constructor() {
        this.interfaces = new Map();
        this.loadEventConfigs();
    }

    /**
     * Load the event attribute configuration required to decode the event efficiently.
     */
    private loadEventConfigs(): void {
        const configPath = path.join(__dirname, "../config/eventAttributes.json");
        const configData = fs.readFileSync(configPath, "utf-8");
        const eventAttributes: Record<string, EventConfig> = JSON.parse(configData);

        // Create an event interface map with its signature configuration for faster
        // look while decoding 
        for (const [signature, config] of Object.entries(eventAttributes)) {
            try {
                const iface = new ethers.Interface(config.abi);
                const fragment = iface.fragments[0];
                if (fragment && fragment.type === "event") {
                    const eventFragment = fragment as ethers.EventFragment;
                    this.interfaces.set(signature, {
                        iface,
                        eventName: eventFragment.name
                    });
                }
            } catch {
                console.warn(`Failed to parse ABI for signature: ${signature}`);
            }
        }
    }
    /**
     * This function consumes raw event data and process the event data for the further processing
     * @param events Raw event data 
     * @param chainId network id 
     * @param blockTimeStamp block timestamp of of evnet log data
     * @returns DecodedEventResult[]
     */

    decodeEvents(
        events: RawEvent[],
        chainId: number,
        blockTimeStamp: number
    ): DecodedEventResult[] {
        const results: DecodedEventResult[] = [];

        for (const event of events) {
            const signature = event.topics[0];
            if (!signature) continue;

            const config = this.interfaces.get(signature);
            if (!config) continue;

            try {
                const parsed = config.iface.parseLog({
                    topics: event.topics,
                    data: event.data
                });
                if (!parsed) continue;

                results.push({
                    contractAddress: event.address,
                    chainId,
                    blockNumber: event.blockNumber,
                    blockTimeStamp,
                    transactionHash: event.transactionHash,
                    transactionIndex: event.transactionIndex,
                    eventName: parsed.name,
                    eventArg: JSON.stringify(
                        parsed.args.toObject(),
                        (_, v) => (typeof v === "bigint" ? v.toString() : v)
                    )
                });
            } catch {
                // Skip events that don't match ABI structure (e.g., ERC-721 vs ERC-20)
            }
        }

        return results;
    }
}
