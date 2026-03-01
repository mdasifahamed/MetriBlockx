import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional


COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'
DEFILLAMA_BASE_URL = 'https://coins.llama.fi'
DEXSCREENER_BASE_URL = 'https://api.dexscreener.com/latest'

COINGECKO_RATE_LIMIT_DELAY_SECONDS = 1.5

COINGECKO_TOKEN_IDS: Dict[str, str] = {
    'WETH': 'ethereum',
    'WBTC': 'wrapped-bitcoin',
    'WBNB': 'wbnb',
    'WPOL': 'matic-network',
    'PAXG': 'pax-gold',
    'USDC': 'usd-coin',
    'USDT': 'tether',
}

DEFILLAMA_COIN_KEYS: Dict[str, str] = {
    'WETH': 'coingecko:ethereum',
    'WBTC': 'coingecko:wrapped-bitcoin',
    'WBNB': 'coingecko:wbnb',
    'WPOL': 'coingecko:matic-network',
    'PAXG': 'coingecko:pax-gold',
    'USDC': 'coingecko:usd-coin',
    'USDT': 'coingecko:tether',
}

DEXSCREENER_TOKEN_ADDRESSES: Dict[str, str] = {
    'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    'WPOL': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
    'PAXG': '0x45804880De22913dAFE09f4980848ECE6EcbAf78',
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
}

STABLECOIN_SYMBOLS = {'USDC', 'USDT'}
ALL_TOKEN_SYMBOLS: List[str] = list(COINGECKO_TOKEN_IDS.keys())


async def fetch_price_from_coingecko(
    http_session: aiohttp.ClientSession,
    token_symbol: str,
    date_string: str,
) -> Optional[float]:
    coin_id = COINGECKO_TOKEN_IDS[token_symbol]
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    date_param = dt.strftime('%d-%m-%Y')
    url = f'{COINGECKO_BASE_URL}/coins/{coin_id}/history'
    params = {'date': date_param, 'localization': 'false'}
    try:
        async with http_session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            market = data.get('market_data', {})
            prices = market.get('current_price', {})
            usd = prices.get('usd')
            return float(usd) if usd is not None else None
    except Exception:
        return None


async def fetch_price_from_defillama(
    http_session: aiohttp.ClientSession,
    token_symbol: str,
    date_string: str,
) -> Optional[float]:
    coin_key = DEFILLAMA_COIN_KEYS[token_symbol]
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    ts = int(dt.replace(hour=12, tzinfo=timezone.utc).timestamp())
    url = f'{DEFILLAMA_BASE_URL}/prices/historical/{ts}/{coin_key}'
    try:
        async with http_session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            coins = data.get('coins', {})
            token = coins.get(coin_key, {})
            p = token.get('price')
            return float(p) if p is not None else None
    except Exception:
        return None


async def fetch_price_from_dexscreener(
    http_session: aiohttp.ClientSession,
    token_symbol: str,
) -> Optional[float]:
    addr = DEXSCREENER_TOKEN_ADDRESSES[token_symbol]
    url = f'{DEXSCREENER_BASE_URL}/dex/tokens/{addr}'
    try:
        async with http_session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            pairs = data.get('pairs') or []
            if not pairs:
                return None
            # pick most liquid pair for price
            by_liq = sorted(
                pairs,
                key=lambda p: float((p.get('liquidity') or {}).get('usd', 0) or 0),
                reverse=True,
            )
            top = by_liq[0]
            price_str = top.get('priceUsd')
            return float(price_str) if price_str is not None else None
    except Exception:
        return None


async def compute_mean_price_for_token_on_date(
    http_session: aiohttp.ClientSession,
    token_symbol: str,
    date_string: str,
    dexscreener_prices_cache: Dict[str, Optional[float]],
) -> float:
    if token_symbol in STABLECOIN_SYMBOLS:
        return 1.0

    prices: List[float] = []
    cg = await fetch_price_from_coingecko(http_session, token_symbol, date_string)
    await asyncio.sleep(COINGECKO_RATE_LIMIT_DELAY_SECONDS)
    if cg is not None:
        prices.append(cg)

    dl = await fetch_price_from_defillama(http_session, token_symbol, date_string)
    if dl is not None:
        prices.append(dl)

    dx = dexscreener_prices_cache.get(token_symbol)
    if dx is not None:
        prices.append(dx)

    if not prices:
        return 0.0
    return sum(prices) / len(prices)


async def fetch_hourly_prices_from_coingecko(
    http_session: aiohttp.ClientSession,
    token_symbol: str,
) -> Dict[str, float]:
    coin_id = COINGECKO_TOKEN_IDS[token_symbol]
    url = f'{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart'
    params = {'vs_currency': 'usd', 'days': '4', 'interval': 'hourly'}
    try:
        async with http_session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                return {}
            data = await resp.json()
            points = data.get('prices', [])
            out: Dict[str, float] = {}
            for ts_ms, price in points:
                dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
                key = dt.strftime('%Y-%m-%d %H:%M:%S')
                out[key] = float(price)
            return out
    except Exception:
        return {}


async def fetch_hourly_prices_from_defillama_batch(
    http_session: aiohttp.ClientSession,
    unix_timestamp: int,
) -> Dict[str, float]:
    non_stable = [s for s in ALL_TOKEN_SYMBOLS if s not in STABLECOIN_SYMBOLS]
    coin_keys = ','.join(DEFILLAMA_COIN_KEYS[s] for s in non_stable)
    url = f'{DEFILLAMA_BASE_URL}/prices/historical/{unix_timestamp}/{coin_keys}'
    try:
        async with http_session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return {}
            data = await resp.json()
            coins = data.get('coins', {})
            out: Dict[str, float] = {}
            for symbol in non_stable:
                key = DEFILLAMA_COIN_KEYS[symbol]
                token = coins.get(key, {})
                p = token.get('price')
                if p is not None:
                    out[symbol] = float(p)
            return out
    except Exception:
        return {}


async def fetch_all_hourly_prices(date_strings: List[str]) -> Dict[str, Dict[str, float]]:
    from datetime import timedelta

    start = datetime.strptime(date_strings[0], '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end = datetime.strptime(date_strings[-1], '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1)

    buckets: List[datetime] = []
    cur = start
    while cur < end:
        buckets.append(cur)
        cur += timedelta(hours=1)

    hourly: Dict[str, Dict[str, float]] = {
        b.strftime('%Y-%m-%d %H:%M:%S'): {} for b in buckets
    }

    async with aiohttp.ClientSession() as session:
        cg_by_symbol: Dict[str, Dict[str, float]] = {}
        for symbol in ALL_TOKEN_SYMBOLS:
            if symbol in STABLECOIN_SYMBOLS:
                continue
            print(f'  CoinGecko hourly chart for {symbol}...')
            cg_by_symbol[symbol] = await fetch_hourly_prices_from_coingecko(session, symbol)
            await asyncio.sleep(COINGECKO_RATE_LIMIT_DELAY_SECONDS)

        for bucket_dt in buckets:
            bucket_key = bucket_dt.strftime('%Y-%m-%d %H:%M:%S')
            ts = int(bucket_dt.timestamp())
            dl_prices = await fetch_hourly_prices_from_defillama_batch(session, ts)

            for symbol in ALL_TOKEN_SYMBOLS:
                if symbol in STABLECOIN_SYMBOLS:
                    hourly[bucket_key][symbol] = 1.0
                    continue
                available: List[float] = []
                cg_prices = cg_by_symbol.get(symbol, {})
                if cg_prices.get(bucket_key) is not None:
                    available.append(cg_prices[bucket_key])
                if dl_prices.get(symbol) is not None:
                    available.append(dl_prices[symbol])
                hourly[bucket_key][symbol] = sum(available) / len(available) if available else 0.0

    return hourly


async def fetch_all_daily_prices(date_strings: List[str]) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}

    async with aiohttp.ClientSession() as session:
        dx_cache: Dict[str, Optional[float]] = {}
        print('Fetching DexScreener current prices (used as third price source)...')
        for symbol in ALL_TOKEN_SYMBOLS:
            if symbol not in STABLECOIN_SYMBOLS:
                dx_cache[symbol] = await fetch_price_from_dexscreener(session, symbol)
                print(f'  DexScreener {symbol}: {dx_cache[symbol]}')

        for date_string in date_strings:
            print(f'Fetching historical prices for {date_string}...')
            by_token: Dict[str, float] = {}
            for symbol in ALL_TOKEN_SYMBOLS:
                mean_price = await compute_mean_price_for_token_on_date(
                    session, symbol, date_string, dx_cache,
                )
                by_token[symbol] = mean_price
                print(f'  {symbol} on {date_string}: ${mean_price:.4f} (mean of available sources)')
            result[date_string] = by_token

    return result
