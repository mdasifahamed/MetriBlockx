import dotenv from 'dotenv';
dotenv.config();
export interface ChainConfig {
  id: number;
  name: string;
  symbol: string;
  rpcEndpoints: string[];
  blockTime: number; // block timestamp 
  startBlock?: number;
  blockThresholdForTheEvents: number; // we need these for the histrorical event data fecthing because rpc provider limits this
  targetAddresses: string[]; // contract addresses to filter events
}

export const CHAINS: Record<string, ChainConfig> = {
  ethereum: {
    id: 1,
    name: "Ethereum",
    symbol: "ETH",
    rpcEndpoints: [
      process.env.ETH_RPC_1 || "",
      process.env.ETH_RPC_2 || "",
      process.env.ETH_RPC_3 || "",
    ],
    blockTime: 25, // kept it generaic for the historical data.can be tuned according to the network for the blokc creation time
    blockThresholdForTheEvents: 5, // kept it generic for the so that it can adjust amon the rpc providers
    targetAddresses: [
      "0xdac17f958d2ee523a2206206994597c13d831ec7", //usdt
      "0xb8c77482e45f1f44de1745f52c74426c631bdd52", //wbnb
      "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", //usdc
      "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", //wbtc
      "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", //weth
      "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", //WPOL
      "0x45804880De22913dAFE09f4980848ECE6EcbAf78", //paxos gold
      "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc", //usdc/WETH v2
      "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852", // weth/usdt v2 
      "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", //usdc/weth v3 500
      "0x9db9e0e53058c89e5b94e29621a205198648425b", // wbtc/usdt v3 3000
      "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35",  // wbtc/usdc v3 3000
      "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8", //usdc/weth v3 3000
      "0x56534741cd8b152df6d48adf7ac51f75169a83b2", // wbtc/usdt v3 500
      "0x11b815efb8f581194ae79006d24e0d814b7697f6"  //weth/usdt v3 500 
    ], // add contract addresses to filter events
  },
  polygon: {
    id: 137,
    name: "Polygon",
    symbol: "MATIC",
    rpcEndpoints: [
      process.env.POLYGON_RPC_1 || "",
      process.env.POLYGON_RPC_2 || "",
      process.env.POLYGON_RPC_3 || "",
    ],
    blockTime: 250, // kept it generaic for the historical data.can be tuned according to the network for the blokc creation time
    blockThresholdForTheEvents: 5, // kept it generic for the so that it can adjust amon the rpc providers
    targetAddresses: [
      '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359', //usdc
      '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619', // weth
      '0xc2132d05d31c914a87c6611c10748aeb04b58e8f', // usdt 
      '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6', // wbtc
      '0x3ba4c387f786bfee076a58914f5bd38d668b42c3', //wbnb
      '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270', //wpol
      '0x553d3d295e0f695b9228246232edf400ed3560b5', //Paxos Gold
      '0x4ccd010148379ea531d6c587cfdd60180196f9b1', // weth/usdt v3 3000 
      '0xa4d8c89f0c20efbe54cba9e7e7a7e509056228d9', // USDC/WETH
      '0xb6e57ed85c4c9dbfef2a68711e9d6f36c56e0fcb', //WPOL/usdc v3 500
      '0x781067ef296e5c4a4203f81c593274824b7c185d', //WPOL/usdt v3 300
      '0x2db87c4831b2fec2e35591221455834193b50d1b', // WPOL/USDC v3 3000 
    ], // add contract addresses to filter events
  },
  bnb: {
    id: 56,
    name: "BNB Chain",
    symbol: "BNB",
    rpcEndpoints: [
      process.env.BNB_RPC_1 || "",
      process.env.BNB_RPC_2 || "",
      process.env.BNB_RPC_3 || "",
    ],
    blockTime: 250, // kept it generaic for the historical data.can be tuned according to the network for the blokc creation time
    blockThresholdForTheEvents: 5, // kept it generic for the so that it can adjust amon the rpc providers
    targetAddresses: [
      '0x0555e30da8f98308edb960aa94c0db47230d2b9c', // WBCT
      '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', // usdc
      '0x55d398326f99059ff775485246999027b3197955', // usdt
      '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c', // WBNB
      '0x2170ed0880ac9a755fd29b2688956bd959f933f8', //WETH
      '0x7950865a9140cb519342433146ed5b40c6f210f7', // PAXGOLD
      '0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4', // usdt/wbnb v3 100
      '0x6fe9e9de56356f7edbfcbb29fab7cd69471a4869', // usdt/wbnb v3 3000
      '0x4141325bac36affe9db165e854982230a14e6d48', // usdc/wbnb v3 100
      '0x17507bef4c3abC1bc715be723ee1baf571256e05', // weth/usdc v3 3000
      '0xde67d05242b18af00b28678db34feec883cc9cd6', // weth/usdt v3 3000
      '0x8a1ed8e124fdfbd534bf48baf732e26db9cc0cf4', //usdt/wbnb v2 3000
    ], // add contract addresses to filter events
  },
};

// Helper to get chain config
export function getChainConfig(chainName: string): ChainConfig {
  const config = CHAINS[chainName];
  if (!config) {
    throw new Error(`Unknown chain: ${chainName}. Available: ${Object.keys(CHAINS).join(", ")}`);
  }
  return config;
}
