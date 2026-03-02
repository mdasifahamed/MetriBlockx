<div align="center">

<h1>MetriBlockx</h1>

[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)](.)
[![Data](https://img.shields.io/badge/Data-Pure%20On--Chain-1d4ed8?style=flat-square)](.)
[![Chains](https://img.shields.io/badge/Chains-EVM%20%E2%80%94%20Extensible-7c3aed?style=flat-square)](.)
[![Validation](https://img.shields.io/badge/Validated-Feb%2010%E2%80%9312%2C%202026-0891b2?style=flat-square)](.)

<br>

**Block-level on-chain analytics — every metric is traceable to a block and a transaction hash, every CEX flow is traceable to a publicly audited wallet address.**

<br>

<a href="https://metriblokcx-frontend-init.vercel.app/" target="_blank">
  <img src="https://img.shields.io/badge/Live%20Dashboard-Open%20%E2%86%92-0ea5e9?style=for-the-badge" alt="Live Dashboard">
</a>

<sub>Interactive dashboard powered by data from all blocks indexed across Feb 10–12, 2026 — Ethereum and Polygon only.</sub>

</div>

---

## The Problem

> Most blockchain data platforms mix CEX (centralized exchange) off-chain data with on-chain metrics. Their sources are opaque — you cannot verify whether a number came from a DEX event, a CEX API, or a price oracle. **MetriBlockx is built differently.**

| | MetriBlockx | Typical Providers |
|---|---|---|
| Data source | **Direct RPC → chain state** | Often mixed with CEX or API data |
| Verifiability | **Every row includes block numbers and transaction hashes** | Opaque, unauditable |
| CEX data | **Tracked separately, clearly labeled** | Blended into on-chain metrics |
| Pipeline | **Open and reproducible** | Closed and proprietary |

---

## CEX Flow Tracking — via Officially Published Wallet Addresses

> MetriBlockx tracks CEX on-chain activity using **wallet addresses that exchanges themselves publish** in their proof-of-reserve reports and audit disclosures — available publicly on their official websites. CEX flow data here is not estimated or inferred. It is read directly from the chain using auditor-verified addresses.

This is a deliberate design decision. Very few analytics platforms do this.

Most tools either ignore CEX on-chain flows entirely or rely on heuristic address labelling that cannot be independently verified. MetriBlockx uses the same source of truth that regulators and independent auditors reference.

**What this enables:**

- `per stablecoin` — USDT and USDC flows tracked separately, not aggregated
- `per exchange` — see which CEX is seeing inflows vs outflows at any point
- `per chain` — Ethereum and Polygon reported independently, never merged
- `hourly + daily` — time-series granularity, not just snapshots
- `block references` — every flow row cites the block numbers it came from

---

## What MetriBlockx Indexes

MetriBlockx is designed as a chain-agnostic indexing and metrics layer. It currently targets EVM-compatible networks, with the architecture designed to extend to non-EVM chains.

- **DEX swap volume** — per pool, per hour and day, denominated in USD
- **Liquidity add/remove flows** — net LP position change per pool over time
- **DEX fee collection** — fees earned per pool, broken out from volume
- **Pool reserves** — token balances and total value locked (TVL) snapshots
- **Stablecoin transfer volume** — on-chain movement of USDT and USDC
- **Token supply events** — mint and burn events per token, with amounts
- **CEX inflow and outflow** — via published wallet addresses, per exchange and stablecoin
- **Cross-chain summary** — unified daily view across all indexed chains in one dataset

---

## Proof of Concept — Validation Run (Feb 10–12, 2026)

> The following reflects the **initial validation run** — chosen to prove the system works on high-volume, real mainnet data. The pipeline is built to extend to any EVM chain and any token or pool configuration. **This is not the final scope.**

### Why Ethereum and Polygon?

Ethereum and Polygon were selected because both have deep Uniswap V2/V3 liquidity, high daily transaction volume, and established stablecoin activity. The goal was to stress-test the full pipeline — indexer, decoder, metrics engine, and CEX flow tracker — under real mainnet conditions, and confirm that block-level aggregation with verification works in practice, not just in theory.

### Networks

| Chain | Chain ID | Role in Validation |
|---|---|---|
| Ethereum | 1 | Primary — highest DEX volume and stablecoin activity |
| Polygon | 137 | Secondary — high throughput and native token pool coverage |

### Tokens Covered

High-volume stablecoins and wrapped assets, selected to maximize signal density and validate CEX flow tracking across multiple asset types:

`USDT` &nbsp; `USDC` &nbsp; `WETH` &nbsp; `WBTC` &nbsp; `WBNB` &nbsp; `WPOL / MATIC` &nbsp; `PAXG`

### DEX Pools Covered

Pools selected from the highest-volume Uniswap V2 and V3 pairs on both networks.

**Ethereum — Uniswap:**

| Pool Pair | Version | Fee Tier |
|---|---|---|
| USDC / WETH | V2 | — |
| WETH / USDT | V2 | — |
| USDC / WETH | V3 | 0.05% |
| USDC / WETH | V3 | 0.30% |
| WBTC / USDT | V3 | 0.30% |
| WBTC / USDC | V3 | 0.30% |
| WBTC / USDT | V3 | 0.05% |
| WETH / USDT | V3 | 0.05% |

**Polygon — Uniswap:**

| Pool Pair | Version | Fee Tier |
|---|---|---|
| WETH / USDT | V3 | 0.30% |
| USDC / WETH | V3 | — |
| WPOL / USDC | V3 | 0.05% |
| WPOL / USDT | V3 | 0.30% |
| WPOL / USDC | V3 | 0.30% |

---

## Research Output

The datasets in [`metrics/research/test/output/`](metrics/research/test/output/) were generated to answer a direct question:

<br>
<div align="center">

*Can block-level on-chain data — decoded and aggregated with full transaction-level traceability — produce clean, usable analytics metrics without any external data enrichment?*

</div>
<br>

The Feb 10–12, 2026 validation run on Ethereum and Polygon answers: **yes.**

Every output dataset includes:

- `block_numbers` — the specific blocks that contributed to each metric row
- `transaction_hashes` — individual transactions behind each number, where applicable
- `chain_id` and `chain_name` — explicit chain attribution on every row
- Hourly and daily granularity available across all datasets

**17 datasets generated from the validation run:**

| # | Dataset | Granularity | What It Shows |
|---|---|---|---|
| 01 | DEX Swap Volume | Hourly | Trading volume per pool per hour, in USD |
| 02 | DEX Swap Volume | Daily | Daily aggregation of swap volume per pool |
| 03 | DEX Liquidity Net | Hourly | Liquidity added vs removed, net LP flow |
| 04 | DEX Liquidity Net | Daily | Daily LP flow per pool |
| 05 | DEX Fees | Hourly | Fee revenue collected per pool per hour |
| 06 | DEX Fees | Daily | Daily fee revenue per pool |
| 07 | CEX Flows | Hourly | Total CEX inflow vs outflow per exchange |
| 08 | CEX Flows | Daily | Daily CEX flow totals |
| 09 | Stablecoin Transfers | Hourly | USDT and USDC on-chain transfer volume |
| 10 | Stablecoin Transfers | Daily | Daily stablecoin transfer volume |
| 11 | Stablecoin CEX Flows | Hourly | CEX inflow/outflow broken down by stablecoin and exchange |
| 12 | Stablecoin CEX Flows | Daily | Daily per-stablecoin CEX flows |
| 13 | Token Supply Events | Hourly | Mint and burn events per token per hour |
| 14 | Token Supply Events | Daily | Daily supply event totals |
| 15 | Pool Reserves | Daily | End-of-day token balances and USD TVL per pool |
| 16 | Master Daily Summary | Daily | All metrics consolidated — one row per chain per day |
| 17 | Cross-Chain Comparison | Daily | Ethereum vs Polygon side-by-side across all metrics |

[View all datasets →](metrics/research/test/output/)

---

## Live Dashboard

An interactive dashboard powered by data from **all blocks indexed across Feb 10–12, 2026 — Ethereum and Polygon only**. It covers hourly and daily views, pool-level breakdowns, CEX inflow/outflow by exchange, stablecoin transfer volume, and token supply events — sourced entirely from on-chain data.

<a href="https://metriblokcx-frontend-init.vercel.app/" target="_blank"><strong>Open MetriBlockx Dashboard →</strong></a>

---

## Roadmap

- [x] EVM event and block indexer — Ethereum, Polygon, BNB Chain
- [x] DEX metrics: swap volume, liquidity, fees, pool reserves — Uniswap V2 and V3
- [x] CEX flow tracking via officially published wallet addresses — per exchange, per stablecoin, per chain
- [x] Token supply tracking: mint and burn events
- [x] Hourly and daily time-series aggregation with block-level traceability
- [x] Validation run: Ethereum and Polygon, Feb 10–12, 2026
- [x] Research dashboard for validation output
- [ ] Public analytics dashboard (Next.js — in progress)
- [ ] Extended EVM chain support (Arbitrum, Base, Optimism, Avalanche)
- [ ] Non-EVM chain support
- [ ] Public query API for historical data
- [ ] Cross-chain capital flow correlation analytics
- [ ] Anomaly detection for unusual on-chain activity

---

*MetriBlockx — pure on-chain, always verifiable.*
