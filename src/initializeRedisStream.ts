import { BlockRangeEventStreamCreator } from "./stream/BlockRangeEventStream";

const blockEventsStreamCreator = new BlockRangeEventStreamCreator()


async function main() {
    await blockEventsStreamCreator.initStream()
}

main().catch((err) => {
    if (err) {
        console.log(err)
        process.exit(1)
    }
})