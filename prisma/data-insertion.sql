-- Token Infomation Insertion


INSERT INTO tokens (id,chain_id, token_address, token_name, token_symbol, token_decimal)
VALUES
(gen_random_uuid(),1,'0xdac17f958d2ee523a2206206994597c13d831ec7','Tether USD','USDT',6),
(gen_random_uuid(),56,'0x55d398326f99059ff775485246999027b3197955','Tether USD','USDT',6),
(gen_random_uuid(),137,'0xc2132d05d31c914a87c6611c10748aeb04b58e8f','Tether USD','USDT',6),
(gen_random_uuid(),1,'0xb8c77482e45f1f44de1745f52c74426c631bdd52','Wrapped BNB','WBNB',18),
(gen_random_uuid(),137,'0x3ba4c387f786bfee076a58914f5bd38d668b42c3','Wrapped BNB','WBNB',18),
(gen_random_uuid(),56,'0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c','Wrapped BNB','WBNB',18),
(gen_random_uuid(),1,'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','USD C','USDC',6),
(gen_random_uuid(),137,'0x3c499c542cef5e3811e1192ce70d8cc03d5c3359','USD C','USDC',6),
(gen_random_uuid(),56,'0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d','USD C','USDC',6),
(gen_random_uuid(),1,'0x8965349fb649a33a30cbfda057d8ec2c48abe2a2','Wrapped BTC','BTC',8),
(gen_random_uuid(),56,'0x0555e30da8f98308edb960aa94c0db47230d2b9c','Wrapped BTC','BTC',8),
(gen_random_uuid(),137,'0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6','Wrapped BTC','BTC',8),
(gen_random_uuid(),1,'0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2','Wrapped ETH','WETH',18),
(gen_random_uuid(),56,'0x2170ed0880ac9a755fd29b2688956bd959f933f8','Wrapped ETH','WETH',18),
(gen_random_uuid(),137,'0x7ceb23fd6bc0add59e62ac25578270cff1b9f619','Wrapped ETH','WETH',18),
(gen_random_uuid(),1,'0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0','Wrapped POL','WPOL',18),
(gen_random_uuid(),137,'0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270','Wrapped POL','WPOL',18),
(gen_random_uuid(),56,'0xc836d8dc361e44dbe64c4862d55ba041f88dd39','Wrapped POL','WPOL',18),
(gen_random_uuid(),1,'0x45804880de22913dafe09f4980848ece6ecbaf78','Paxos Gold','PAXG',18),
(gen_random_uuid(),137,'0x553d3d295e0f695b9228246232edf400ed3560b5','Paxos Gold','PAXG',18),
(gen_random_uuid(),56,'0x7950865a9140cb519342433146ed5b40c6f210f7','Paxos Gold','PAXG',18),
(gen_random_uuid(),1,'0x2260fac5e5542a773aa44fbcfedf7c193bc2c599','Wrapped BTC','WBTC',8)
ON CONFLICT (chain_id, token_address) 
DO NOTHING;
COMMIT;




-- Pool Information Insertion 
INSERT INTO pools (id,chain_id, pool_address, token_0_address, token_1_address, pool_symbol, dex_name, dex_version, fees)

VALUES (
    gen_random_uuid(),
    1,                             
    '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640', 
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',           
    'WETH/USDC',                   
    'uniswap',                      
    'v3',                           
    500      
),
(
    gen_random_uuid(),
    137,                             
    '0xa4d8c89f0c20efbe54cba9e7e7a7e509056228d9', 
    '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
    '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619',           
    'WETH/USDC',                   
    'uniswap',                      
    'v3',                           
    500         
),
(
    gen_random_uuid(),
    56,
    '0x17507bef4c3abC1bc715be723ee1baf571256e05',
    '0x2170ed0880ac9a755fd29b2688956bd959f933f8',
    '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
    'WETH/USDC',                   
    'uniswap',                      
    'v3',
    3000 

),
(
    gen_random_uuid(),
    1,
    '0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    '0xdac17f958d2ee523a2206206994597c13d831ec7',
    'WETH/USDT',                   
    'uniswap',                      
    'v2',
    3000 
),
(
    gen_random_uuid(),
    137,
    '0x4ccd010148379ea531d6c587cfdd60180196f9b1',
    '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619',
    '0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
    'WETH/USDT',                   
    'uniswap',                      
    'v3',
    3000 

),

(
    gen_random_uuid(),
    56,
    '0xde67d05242b18af00b28678db34feec883cc9cd6',
    '0x2170ed0880ac9a755fd29b2688956bd959f933f8',
    '0x55d398326f99059ff775485246999027b3197955',
    'WETH/USDT',                   
    'uniswap',                      
    'v3',
    3000 

),
(
    gen_random_uuid(),
    1,
    '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    'WETH/USDC',                   
    'uniswap',                      
    'v3',
    3000
),
(
    gen_random_uuid(),
    1,
    '0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    'WETH/USDC',                   
    'uniswap',                      
    'v2',
    3000
),

(
    gen_random_uuid(),
    1,
    '0x11b815efb8f581194ae79006d24e0d814b7697f6',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    '0xdac17f958d2ee523a2206206994597c13d831ec7',
    'WETH/USDT',                   
    'uniswap',                      
    'v3',
    500
),

(
    gen_random_uuid(),
    1,
    '0x9db9e0e53058c89e5b94e29621a205198648425b',
    '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    '0xdac17f958d2ee523a2206206994597c13d831ec7',
    'WBTC/USDT',                   
    'uniswap',                      
    'v3',
    3000
),

(
    gen_random_uuid(),
    1,
    '0x56534741cd8b152df6d48adf7ac51f75169a83b2',
    '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    '0xdac17f958d2ee523a2206206994597c13d831ec7',
    'WBTC/USDT',                   
    'uniswap',                      
    'v3',
    500
),

(
    gen_random_uuid(),
    1,
    '0x99ac8ca7087fa4a2a1fb6357269965a2014abc35',
    '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    'WBTC/USDC',                   
    'uniswap',                      
    'v3',
    3000
),

(
    gen_random_uuid(),
    137,
    '0xb6e57ed85c4c9dbfef2a68711e9d6f36c56e0fcb',
    '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270',
    '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
    'WPOL/USDC',                   
    'uniswap',                      
    'v3',
    500
),

(
    gen_random_uuid(),
    137,
    '0x2db87c4831b2fec2e35591221455834193b50d1b',
    '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270',
    '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
    'WPOL/USDC',                   
    'uniswap',                      
    'v3',
    3000
),

(
    gen_random_uuid(),
    137,
    '0x781067ef296e5c4a4203f81c593274824b7c185d',
    '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270',
    '0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
    'WPOL/USDT',                   
    'uniswap',                      
    'v3',
    3000
),

(
    gen_random_uuid(),
    56,
    '0x6fe9e9de56356f7edbfcbb29fab7cd69471a4869',
    '0x55d398326f99059ff775485246999027b3197955',
    '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
    'WBNB/USDT',                   
    'uniswap',                      
    'v3',
    500
),

(
    gen_random_uuid(),
    56,
    '0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4',
    '0x55d398326f99059ff775485246999027b3197955',
    '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
    'WBNB/USDT',                   
    'uniswap',                      
    'v3',
    100
),

(
    gen_random_uuid(),
    56,
    '0x8a1ed8e124fdfbd534bf48baf732e26db9cc0cf4',
    '0x55d398326f99059ff775485246999027b3197955',
    '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
    'WBNB/USDT',                   
    'uniswap',                      
    'v2',
    3000
),

(
    gen_random_uuid(),
    56,
    '0x4141325bac36affe9db165e854982230a14e6d48',
    '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
    '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
    'WBNB/USDC',                   
    'uniswap',                      
    'v3',
    100
)
ON CONFLICT (chain_id, pool_address)
DO NOTHING;
COMMIT;