#!/usr/bin/env python3
"""
On-Chain DeFi Analytics Dashboard Generator

Research project: Cross-chain DeFi market microstructure analysis
Reads 17 on-chain CSV datasets and produces a self-contained interactive
HTML dashboard using Plotly.js + Bootstrap 5.

Run:  python generate_dashboard.py
Output: dashboard.html  (open in any browser, no server needed)
"""

import json
import math
import os
from datetime import datetime

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))

FILEMAP = {
    "f01": "01_dex_swap_volume_hourly.csv",
    "f02": "02_dex_swap_volume_daily.csv",
    "f03": "03_dex_liquidity_hourly_net.csv",
    "f04": "04_dex_liquidity_daily_net.csv",
    "f05": "05_dex_fees_hourly.csv",
    "f06": "06_dex_fees_daily.csv",
    "f07": "07_cex_flows_hourly_net.csv",
    "f08": "08_cex_flows_daily_net.csv",
    "f09": "09_stablecoin_transfer_hourly.csv",
    "f10": "10_stablecoin_transfer_daily.csv",
    "f11": "11_stablecoin_cex_flows_hourly.csv",
    "f12": "12_stablecoin_cex_flows_daily.csv",
    "f13": "13_token_supply_events_hourly.csv",
    "f14": "14_token_supply_events_daily.csv",
    "f15": "15_pool_reserves_daily.csv",
    "f16": "16_MASTER_SUMMARY_DAILY.csv",
    "f17": "17_cross_chain_comparison_daily.csv",
}


def read_csv(fname):
    df = pd.read_csv(os.path.join(BASE, fname))
    for col in ["block_numbers", "transaction_hashes"]:
        if col in df.columns:
            df.drop(columns=col, inplace=True)
    return df


print("Loading 17 CSV files...")
DFS = {k: read_csv(v) for k, v in FILEMAP.items()}
print(f"  Loaded: {', '.join(f'{k}({len(v)}rows)' for k,v in DFS.items())}")

# ── KPIs from master summary ──────────────────────────────────────────────────
m = DFS["f16"]
KPIS = {
    "dex_vol":    float(m["dex_volume_usd"].sum()),
    "dex_fees":   float(m["dex_fees_usd"].sum()),
    "stable_vol": float(m["stablecoin_transfer_volume_usd"].sum()),
    "net_cex":    float(m["net_cex_flow_usd"].sum()),
    "net_supply": float(m["net_supply_change_usd"].sum()),
}

# ── Serialize data (pandas handles NaN → null) ────────────────────────────────
ALL_DATA = {}
for k, df in DFS.items():
    ALL_DATA[k] = json.loads(df.to_json(orient="records"))

DATA_JSON  = json.dumps(ALL_DATA)
KPIS_JSON  = json.dumps(KPIS)
GEN_TIME   = datetime.now().strftime("%B %d, %Y · %H:%M")


def fmt_usd(v):
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e12:
        return f"{sign}${v/1e12:.2f}T"
    if v >= 1e9:
        return f"{sign}${v/1e9:.2f}B"
    if v >= 1e6:
        return f"{sign}${v/1e6:.2f}M"
    if v >= 1e3:
        return f"{sign}${v/1e3:.1f}K"
    return f"{sign}${v:.2f}"


KPI_DEX_VOL = fmt_usd(KPIS["dex_vol"])
KPI_FEES    = fmt_usd(KPIS["dex_fees"])
KPI_STABLE  = fmt_usd(KPIS["stable_vol"])
KPI_CEX     = fmt_usd(KPIS["net_cex"])
KPI_SUPPLY  = fmt_usd(KPIS["net_supply"])

CEX_SIGN  = "text-success" if KPIS["net_cex"] >= 0 else "text-danger"
SUP_SIGN  = "text-success" if KPIS["net_supply"] >= 0 else "text-danger"

# ── HTML template (placeholders replaced at bottom) ──────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>On-Chain DeFi Analytics Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>
<style>
  :root {
    --bg:      #0d1117;
    --card-bg: #161b22;
    --border:  #30363d;
    --text:    #c9d1d9;
    --muted:   #8b949e;
    --blue:    #58a6ff;
    --green:   #3fb950;
    --red:     #f85149;
    --yellow:  #d29922;
    --purple:  #bc8cff;
    --orange:  #f0883e;
    --teal:    #39d353;
  }
  * { box-sizing: border-box; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; min-height: 100vh; }
  a { color: var(--blue); }

  /* ── Header ── */
  .dash-header { background: linear-gradient(135deg,#0d1117 0%,#161b22 100%); border-bottom: 1px solid var(--border); padding: 20px 28px 16px; }
  .dash-header h1 { font-size: 1.4rem; font-weight: 700; color: #fff; margin: 0; }
  .dash-header .subtitle { color: var(--muted); font-size: .82rem; margin-top: 4px; }
  .badge-chain { background: #21262d; border: 1px solid var(--border); color: var(--blue); font-size: .7rem; padding: 2px 7px; border-radius: 20px; margin-right: 4px; }

  /* ── Filter bar ── */
  .filter-bar { background: #161b22; border-bottom: 1px solid var(--border); padding: 10px 28px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
  .filter-bar label { font-size: .72rem; color: var(--muted); margin-bottom: 2px; display: block; }
  .filter-bar select { background: #0d1117; color: var(--text); border: 1px solid var(--border); border-radius: 6px; font-size: .8rem; padding: 4px 8px; min-width: 130px; cursor: pointer; }
  .filter-bar select:focus { outline: none; border-color: var(--blue); }
  .filter-bar .filter-group { display: flex; flex-direction: column; }
  .filter-reset { background: transparent; border: 1px solid var(--border); color: var(--muted); border-radius: 6px; font-size: .75rem; padding: 4px 12px; cursor: pointer; margin-top: 14px; transition: all .15s; }
  .filter-reset:hover { border-color: var(--red); color: var(--red); }

  /* ── KPI Cards ── */
  .kpi-row { display: flex; gap: 14px; flex-wrap: wrap; padding: 18px 28px 0; }
  .kpi-card { flex: 1; min-width: 170px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; }
  .kpi-card .kpi-label { font-size: .72rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
  .kpi-card .kpi-value { font-size: 1.5rem; font-weight: 700; color: #fff; line-height: 1; }
  .kpi-card .kpi-sub { font-size: .72rem; color: var(--muted); margin-top: 4px; }
  .kpi-card .kpi-icon { font-size: 1.3rem; float: right; margin-top: -4px; opacity: .7; }

  /* ── Tabs ── */
  .nav-wrapper { padding: 16px 28px 0; }
  .nav-tabs { border-bottom: 1px solid var(--border); gap: 2px; }
  .nav-tabs .nav-link { background: transparent; border: none; border-bottom: 2px solid transparent; color: var(--muted); font-size: .82rem; padding: 8px 14px; border-radius: 0; transition: color .15s; }
  .nav-tabs .nav-link:hover { color: var(--text); }
  .nav-tabs .nav-link.active { color: var(--blue); border-bottom-color: var(--blue); background: transparent; }
  .tab-content { padding: 20px 28px 30px; }

  /* ── Charts ── */
  .chart-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 18px; }
  .chart-card .chart-title { font-size: .83rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
  .chart-card .chart-subtitle { font-size: .72rem; color: var(--muted); margin-bottom: 12px; }
  .chart-div { width: 100%; }
  .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; }
  @media (max-width: 900px) { .row-2, .row-3 { grid-template-columns: 1fr; } }

  /* ── Section headers ── */
  .section-header { font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 16px; }

  /* ── Footer ── */
  .dash-footer { background: #161b22; border-top: 1px solid var(--border); padding: 24px 28px; margin-top: 10px; }
  .dash-footer h6 { color: var(--text); font-size: .82rem; font-weight: 600; margin-bottom: 10px; }
  .dash-footer p { color: var(--muted); font-size: .75rem; margin-bottom: 6px; line-height: 1.6; }
  .skill-tag { display: inline-block; background: #21262d; border: 1px solid var(--border); color: var(--blue); font-size: .68rem; padding: 2px 8px; border-radius: 20px; margin: 2px; }
  .text-success { color: var(--green) !important; }
  .text-danger  { color: var(--red) !important; }
  .spinner-border { color: var(--muted); }
</style>
</head>
<body>

<!-- ═══════════════════════ HEADER ═══════════════════════ -->
<div class="dash-header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
    <div>
      <h1><i class="bi bi-graph-up-arrow" style="color:var(--blue);margin-right:8px;"></i>On-Chain DeFi Analytics Dashboard</h1>
      <div class="subtitle">
        Multi-chain market microstructure research &nbsp;·&nbsp; 17 on-chain datasets &nbsp;·&nbsp; Feb 10–12, 2026
        &nbsp;&nbsp;
        <span class="badge-chain">Ethereum</span>
        <span class="badge-chain">BNB Chain</span>
        <span class="badge-chain">Polygon</span>
      </div>
    </div>
    <div style="text-align:right;font-size:.72rem;color:var(--muted);">
      Generated: %%GEN_TIME%%<br>
      <span style="color:var(--blue);">DEX · CEX · Stablecoin · Token Supply · Cross-chain</span>
    </div>
  </div>
</div>

<!-- ═══════════════════════ FILTER BAR ═══════════════════════ -->
<div class="filter-bar">
  <div class="filter-group">
    <label>Chain</label>
    <select id="filterChain" class="filter-select" onchange="onFilterChange()">
      <option value="All">All Chains</option>
      <option value="Ethereum">Ethereum</option>
      <option value="BNB Chain">BNB Chain</option>
      <option value="Polygon">Polygon</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Pool</label>
    <select id="filterPool" class="filter-select" onchange="onFilterChange()">
      <option value="All">All Pools</option>
      <option value="WETH/USDC">WETH/USDC</option>
      <option value="WETH/USDT">WETH/USDT</option>
      <option value="WBTC/USDC">WBTC/USDC</option>
      <option value="WBTC/USDT">WBTC/USDT</option>
      <option value="WPOL/USDC">WPOL/USDC</option>
      <option value="WPOL/USDT">WPOL/USDT</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Exchange (CEX)</label>
    <select id="filterCEX" class="filter-select" onchange="onFilterChange()">
      <option value="All">All Exchanges</option>
      <option value="binance">Binance</option>
      <option value="bybit">Bybit</option>
      <option value="kucoin">KuCoin</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Stablecoin</label>
    <select id="filterToken" class="filter-select" onchange="onFilterChange()">
      <option value="All">USDC + USDT</option>
      <option value="USDC">USDC</option>
      <option value="USDT">USDT</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Granularity</label>
    <select id="filterGran" class="filter-select" onchange="onFilterChange()">
      <option value="daily">Daily</option>
      <option value="hourly">Hourly</option>
    </select>
  </div>
  <div class="filter-group">
    <label>DEX Version</label>
    <select id="filterDexVer" class="filter-select" onchange="onFilterChange()">
      <option value="All">v2 + v3</option>
      <option value="v2">v2</option>
      <option value="v3">v3</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Fee Tier</label>
    <select id="filterFeeTier" class="filter-select" onchange="onFilterChange()">
      <option value="All">All Tiers</option>
      <option value="500">0.05% (500)</option>
      <option value="3000">0.30% (3000)</option>
    </select>
  </div>
  <button class="filter-reset" onclick="resetFilters()"><i class="bi bi-arrow-counterclockwise"></i> Reset</button>
</div>

<!-- ═══════════════════════ KPI CARDS ═══════════════════════ -->
<div class="kpi-row">
  <div class="kpi-card">
    <i class="bi bi-arrow-left-right kpi-icon" style="color:var(--blue);"></i>
    <div class="kpi-label">Total DEX Volume</div>
    <div class="kpi-value" id="kpiDexVol">%%KPI_DEX_VOL%%</div>
    <div class="kpi-sub">Uniswap v2 + v3 · All chains</div>
  </div>
  <div class="kpi-card">
    <i class="bi bi-currency-dollar kpi-icon" style="color:var(--yellow);"></i>
    <div class="kpi-label">Total DEX Fees</div>
    <div class="kpi-value" id="kpiFees">%%KPI_FEES%%</div>
    <div class="kpi-sub">Protocol revenue collected</div>
  </div>
  <div class="kpi-card">
    <i class="bi bi-bank kpi-icon" style="color:var(--purple);"></i>
    <div class="kpi-label">Stablecoin Volume</div>
    <div class="kpi-value" id="kpiStable">%%KPI_STABLE%%</div>
    <div class="kpi-sub">USDC + USDT on-chain transfers</div>
  </div>
  <div class="kpi-card">
    <i class="bi bi-building kpi-icon" style="color:var(--orange);"></i>
    <div class="kpi-label">Net CEX Flow</div>
    <div class="kpi-value %%CEX_SIGN%%" id="kpiCex">%%KPI_CEX%%</div>
    <div class="kpi-sub">Inflow minus outflow · All CEXes</div>
  </div>
  <div class="kpi-card">
    <i class="bi bi-layers kpi-icon" style="color:var(--teal);"></i>
    <div class="kpi-label">Net Supply Change</div>
    <div class="kpi-value %%SUP_SIGN%%" id="kpiSupply">%%KPI_SUPPLY%%</div>
    <div class="kpi-sub">Token mint events (ISSUE)</div>
  </div>
</div>

<!-- ═══════════════════════ TABS ═══════════════════════ -->
<div class="nav-wrapper">
  <ul class="nav nav-tabs" id="mainTabs">
    <li class="nav-item"><button class="nav-link active" data-tab="overview"  onclick="switchTab(this,'overview')"><i class="bi bi-grid-1x2"></i> Overview</button></li>
    <li class="nav-item"><button class="nav-link"        data-tab="dex"       onclick="switchTab(this,'dex')"><i class="bi bi-arrow-left-right"></i> DEX Activity</button></li>
    <li class="nav-item"><button class="nav-link"        data-tab="cex"       onclick="switchTab(this,'cex')"><i class="bi bi-building"></i> CEX Flows</button></li>
    <li class="nav-item"><button class="nav-link"        data-tab="stable"    onclick="switchTab(this,'stable')"><i class="bi bi-bank"></i> Stablecoin Intel</button></li>
    <li class="nav-item"><button class="nav-link"        data-tab="supply"    onclick="switchTab(this,'supply')"><i class="bi bi-layers"></i> Supply & Reserves</button></li>
    <li class="nav-item"><button class="nav-link"        data-tab="crosschain" onclick="switchTab(this,'crosschain')"><i class="bi bi-globe"></i> Cross-Chain</button></li>
  </ul>
</div>

<div class="tab-content">

  <!-- ─── TAB 1: OVERVIEW ─── -->
  <div id="tab-overview">
    <div class="section-header">Market Overview · Master Summary</div>
    <div class="row-2">
      <div class="chart-card">
        <div class="chart-title">DEX Volume + Stablecoin Transfer Over Time</div>
        <div class="chart-subtitle">Daily aggregates across all chains · helps identify liquidity demand cycles</div>
        <div id="chartOverviewVol" class="chart-div"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">CEX Flows vs Net Supply Change</div>
        <div class="chart-subtitle">Exchange pressure vs token issuance · signals institutional positioning</div>
        <div id="chartOverviewCex" class="chart-div"></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-title">All Key Metrics by Chain · Daily Comparison</div>
      <div class="chart-subtitle">Multi-chain breakdown from Master Summary — Ethereum dominance, Polygon fee efficiency, BNB Chain activity</div>
      <div id="chartOverviewMaster" class="chart-div"></div>
    </div>
  </div>

  <!-- ─── TAB 2: DEX ACTIVITY ─── -->
  <div id="tab-dex" style="display:none;">
    <div class="section-header">DEX Activity · Uniswap v2/v3 · Swap Volume · Liquidity · Fees</div>
    <div class="chart-card">
      <div class="chart-title">DEX Swap Volume by Pool</div>
      <div class="chart-subtitle">Volume (USD) broken down by trading pair — WETH/USDC dominates institutional flow; use granularity toggle for hourly intraday pattern</div>
      <div id="chartDexVol" class="chart-div"></div>
    </div>
    <div class="row-2">
      <div class="chart-card">
        <div class="chart-title">Liquidity Added vs Removed by Pool</div>
        <div class="chart-subtitle">Net liquidity dynamics — negative net signals capital withdrawal pressure</div>
        <div id="chartDexLiq" class="chart-div"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Fees Collected by Pool &amp; Fee Tier</div>
        <div class="chart-subtitle">Protocol fee revenue — 0.05% tier dominates by volume; 0.30% captures niche pairs</div>
        <div id="chartDexFees" class="chart-div"></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Market Efficiency: Swap Count vs Volume per Pool</div>
      <div class="chart-subtitle">Scatter analysis — high volume / low swap count = large-block institutional trading; low volume / high count = retail activity</div>
      <div id="chartDexScatter" class="chart-div"></div>
    </div>
  </div>

  <!-- ─── TAB 3: CEX FLOWS ─── -->
  <div id="tab-cex" style="display:none;">
    <div class="section-header">CEX Flows · Binance · Bybit · KuCoin · Net Positioning</div>
    <div class="chart-card">
      <div class="chart-title">CEX Inflow vs Outflow by Exchange</div>
      <div class="chart-subtitle">Inflow = coins depositing to CEX (sell pressure); Outflow = withdrawals (self-custody / DeFi migration)</div>
      <div id="chartCexBar" class="chart-div"></div>
    </div>
    <div class="row-2">
      <div class="chart-card">
        <div class="chart-title">Net CEX Flow Over Time (Hourly)</div>
        <div class="chart-subtitle">Positive = net deposit (bearish); Negative = net withdrawal (bullish for DeFi TVL)</div>
        <div id="chartCexLine" class="chart-div"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Net Flow Comparison by Exchange</div>
        <div class="chart-subtitle">Which exchange is accumulating vs distributing — important for market structure analysis</div>
        <div id="chartCexNetBar" class="chart-div"></div>
      </div>
    </div>
  </div>

  <!-- ─── TAB 4: STABLECOIN ─── -->
  <div id="tab-stable" style="display:none;">
    <div class="section-header">Stablecoin Intelligence · USDC · USDT · On-Chain Transfer + CEX Flow</div>
    <div class="chart-card">
      <div class="chart-title">Stablecoin Transfer Volume Over Time</div>
      <div class="chart-subtitle">On-chain stablecoin transfer velocity — strong proxy for DeFi liquidity demand and settlement activity</div>
      <div id="chartStableLine" class="chart-div"></div>
    </div>
    <div class="row-2">
      <div class="chart-card">
        <div class="chart-title">Stablecoin CEX Flows by Exchange &amp; Token</div>
        <div class="chart-subtitle">USDC vs USDT routing preferences across exchanges — reveals liquidity fragmentation dynamics</div>
        <div id="chartStableCex" class="chart-div"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Stablecoin Net Flow by Exchange</div>
        <div class="chart-subtitle">Net stablecoin positioning per CEX — positive = buying power entering; negative = exits</div>
        <div id="chartStableNetCex" class="chart-div"></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Stablecoin Intraday Flow Heatmap (Hour × Exchange)</div>
      <div class="chart-subtitle">Time-of-day concentration of stablecoin movements — reveals trading session patterns and algorithmic activity windows</div>
      <div id="chartStableHeatmap" class="chart-div"></div>
    </div>
  </div>

  <!-- ─── TAB 5: TOKEN SUPPLY & RESERVES ─── -->
  <div id="tab-supply" style="display:none;">
    <div class="section-header">Token Supply Events · Pool Reserves · Mint / Burn Dynamics</div>
    <div class="row-2">
      <div class="chart-card">
        <div class="chart-title">Token Mint Events (ISSUE) by Chain</div>
        <div class="chart-subtitle">USDC issuance events — Ethereum vs Polygon minting volume signals cross-chain liquidity bridging activity</div>
        <div id="chartMint" class="chart-div"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Token Supply Event Count by Chain &amp; Date</div>
        <div class="chart-subtitle">Number of individual mint transactions — event frequency reveals smart contract activity cadence</div>
        <div id="chartMintCount" class="chart-div"></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Pool Reserves: Token 0 vs Token 1 (USD) by Pool</div>
      <div class="chart-subtitle">AMM reserve composition — reserve imbalance indicates price pressure direction; WETH/USDC composition reflects ETH price impact on pool depth</div>
      <div id="chartReserves" class="chart-div"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Total Pool Reserve Depth Over Time</div>
      <div class="chart-subtitle">Aggregate TVL evolution — declining reserves signal liquidity provider withdrawal; rising reserves indicate capital inflows</div>
      <div id="chartReservesLine" class="chart-div"></div>
    </div>
  </div>

  <!-- ─── TAB 6: CROSS-CHAIN ─── -->
  <div id="tab-crosschain" style="display:none;">
    <div class="section-header">Cross-Chain Intelligence · Ethereum vs BNB Chain vs Polygon</div>
    <div class="row-2">
      <div class="chart-card">
        <div class="chart-title">Cross-Chain Comparison: Radar Chart</div>
        <div class="chart-subtitle">Normalized 5-axis fingerprint — DEX volume, fees, stablecoin volume, CEX flow, supply change; Ethereum dominates value-weighted metrics</div>
        <div id="chartRadar" class="chart-div"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Cross-Chain Metrics: Side-by-Side</div>
        <div class="chart-subtitle">Absolute comparison across all 5 core metrics — reveals each chain's specialisation in the DeFi ecosystem</div>
        <div id="chartCrossBar" class="chart-div"></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Per-Chain Key Metrics Over Time (Master Summary)</div>
      <div class="chart-subtitle">Ethereum, Polygon day-by-day — DEX volume trajectory, CEX flow direction, and supply dynamics during the observation window</div>
      <div id="chartMasterLine" class="chart-div"></div>
    </div>
  </div>

</div><!-- /tab-content -->

<!-- ═══════════════════════ FOOTER ═══════════════════════ -->
<footer class="dash-footer">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;flex-wrap:wrap;">
    <div>
      <h6><i class="bi bi-mortarboard" style="color:var(--blue);"></i> Academic Research Context</h6>
      <p>This dashboard is part of an independent research project on <strong style="color:var(--text);">cross-chain DeFi market microstructure</strong>, developed to support applications to <strong style="color:var(--text);">Masters programmes in Business Finance &amp; Economics</strong>.</p>
      <p>The analysis demonstrates applied competencies in <em>on-chain data engineering</em>, <em>financial market analytics</em>, and <em>multi-chain protocol economics</em> — directly relevant to quantitative finance and fintech research tracks.</p>
    </div>
    <div>
      <h6><i class="bi bi-lightbulb" style="color:var(--yellow);"></i> Key Research Findings</h6>
      <p><strong style="color:var(--text);">1. CEX-DEX Arbitrage Pressure</strong> — Net CEX outflows concurrent with rising DEX volume signal capital migration from centralised to decentralised venues.</p>
      <p><strong style="color:var(--text);">2. Stablecoin as Liquidity Proxy</strong> — Stablecoin on-chain transfer velocity ($88B+ in 3 days) significantly exceeds DEX spot volume, revealing settlement layer depth.</p>
      <p><strong style="color:var(--text);">3. Chain Specialisation</strong> — Ethereum concentrates high-value DEX flow; Polygon handles high-frequency, lower-value stablecoin transfers at fraction of the cost.</p>
    </div>
    <div>
      <h6><i class="bi bi-tools" style="color:var(--green);"></i> Technical Skills Demonstrated</h6>
      <p>
        <span class="skill-tag">On-Chain Data Engineering</span>
        <span class="skill-tag">Python / Pandas</span>
        <span class="skill-tag">Multi-chain Analytics</span>
        <span class="skill-tag">DeFi Protocol Analysis</span>
        <span class="skill-tag">Plotly.js Visualisation</span>
        <span class="skill-tag">Market Microstructure</span>
        <span class="skill-tag">Stablecoin Economics</span>
        <span class="skill-tag">CEX-DEX Dynamics</span>
        <span class="skill-tag">AMM Pool Analytics</span>
        <span class="skill-tag">Liquidity Research</span>
        <span class="skill-tag">Token Supply Modelling</span>
        <span class="skill-tag">Cross-chain Comparison</span>
      </p>
      <p style="margin-top:10px;">Data: Feb 10–12, 2026 · Chains: Ethereum, BNB Chain, Polygon · Generated: %%GEN_TIME%%</p>
    </div>
  </div>
</footer>

<!-- ═══════════════════════ JAVASCRIPT ═══════════════════════ -->
<script>
// ── Embedded data ────────────────────────────────────────────────────────────
const DATA  = %%DATA%%;
const KPIS  = %%KPIS%%;

// ── Plotly base layout ────────────────────────────────────────────────────────
const COLORS = ['#58a6ff','#3fb950','#d29922','#f85149','#bc8cff','#f0883e','#39d353','#e879f9','#38d9a9','#74c0fc'];
const BG     = '#161b22';
const PLOTBG = '#0d1117';

function baseLayout(extra) {
  return Object.assign({
    template:       'plotly_dark',
    paper_bgcolor:  BG,
    plot_bgcolor:   PLOTBG,
    font:           { family: '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif', color: '#c9d1d9', size: 11 },
    margin:         { t: 30, r: 20, b: 55, l: 75 },
    legend:         { bgcolor: 'rgba(0,0,0,0)', borderwidth: 0, font: { size: 11 } },
    colorway:       COLORS,
    hoverlabel:     { bgcolor: '#21262d', bordercolor: '#30363d', font: { size: 11 } },
    xaxis:          { gridcolor: '#21262d', linecolor: '#30363d' },
    yaxis:          { gridcolor: '#21262d', linecolor: '#30363d' },
  }, extra || {});
}

function plotConfig() {
  return { responsive: true, displayModeBar: true, displaylogo: false,
    modeBarButtonsToRemove: ['select2d','lasso2d','autoScale2d'] };
}

// ── Filter helpers ────────────────────────────────────────────────────────────
function F() {
  return {
    chain:   document.getElementById('filterChain').value,
    pool:    document.getElementById('filterPool').value,
    cex:     document.getElementById('filterCEX').value,
    token:   document.getElementById('filterToken').value,
    gran:    document.getElementById('filterGran').value,
    dexVer:  document.getElementById('filterDexVer').value,
    feeTier: document.getElementById('filterFeeTier').value,
  };
}

function fChain(d, f)   { return f.chain   === 'All' || d.chain_name  === f.chain; }
function fPool(d, f)    { return f.pool    === 'All' || d.pool_symbol === f.pool; }
function fCEX(d, f)     { return f.cex     === 'All' || d.cex_name    === f.cex; }
function fToken(d, f)   { return f.token   === 'All' || d.token_symbol=== f.token; }
function fDexVer(d, f)  { return f.dexVer  === 'All' || !d.dex_version || d.dex_version === f.dexVer; }
function fFeeTier(d, f) { return f.feeTier === 'All' || !d.fee_tier   || String(d.fee_tier) === f.feeTier; }

// groupBy + aggregate
function groupSum(data, keyFields, sumField) {
  const map = {};
  for (const d of data) {
    const k = keyFields.map(f => d[f]).join('||');
    if (!map[k]) { map[k] = { ...Object.fromEntries(keyFields.map(f=>[f,d[f]])), _sum: 0 }; }
    map[k]._sum += (d[sumField] || 0);
  }
  return Object.values(map);
}

function unique(data, field) {
  return [...new Set(data.map(d => d[field]).filter(Boolean))].sort();
}

function fmt(v) {
  if (v == null) return '0';
  const a = Math.abs(v);
  if (a >= 1e9)  return (v/1e9).toFixed(2) + 'B';
  if (a >= 1e6)  return (v/1e6).toFixed(2) + 'M';
  if (a >= 1e3)  return (v/1e3).toFixed(1) + 'K';
  return v.toFixed(2);
}

// ── Tab switching ─────────────────────────────────────────────────────────────
let activeTab = 'overview';
const RENDERERS = {};

function switchTab(btn, tab) {
  document.querySelectorAll('#mainTabs .nav-link').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.tab-content > div').forEach(d => d.style.display = 'none');
  document.getElementById('tab-' + tab).style.display = 'block';
  activeTab = tab;
  if (RENDERERS[tab]) RENDERERS[tab]();
}

function onFilterChange() {
  if (RENDERERS[activeTab]) RENDERERS[activeTab]();
  updateKPIs();
}

function resetFilters() {
  ['filterChain','filterPool','filterCEX','filterToken','filterDexVer','filterFeeTier'].forEach(id => {
    document.getElementById(id).value = 'All';
  });
  document.getElementById('filterGran').value = 'daily';
  onFilterChange();
}

// ── Dynamic KPI update ────────────────────────────────────────────────────────
function updateKPIs() {
  const f = F();
  let m = DATA.f16.filter(d => fChain(d, f));
  const dv  = m.reduce((s,d) => s+(d.dex_volume_usd||0), 0);
  const df  = m.reduce((s,d) => s+(d.dex_fees_usd||0), 0);
  const sv  = m.reduce((s,d) => s+(d.stablecoin_transfer_volume_usd||0), 0);
  const nc  = m.reduce((s,d) => s+(d.net_cex_flow_usd||0), 0);
  const ns  = m.reduce((s,d) => s+(d.net_supply_change_usd||0), 0);

  function fmtKPI(v) {
    const s = v<0?'-':''; const a=Math.abs(v);
    if(a>=1e12) return s+'$'+(a/1e12).toFixed(2)+'T';
    if(a>=1e9)  return s+'$'+(a/1e9).toFixed(2)+'B';
    if(a>=1e6)  return s+'$'+(a/1e6).toFixed(2)+'M';
    if(a>=1e3)  return s+'$'+(a/1e3).toFixed(1)+'K';
    return s+'$'+a.toFixed(2);
  }
  document.getElementById('kpiDexVol').textContent = fmtKPI(dv);
  document.getElementById('kpiFees').textContent   = fmtKPI(df);
  document.getElementById('kpiStable').textContent = fmtKPI(sv);
  document.getElementById('kpiCex').textContent    = fmtKPI(nc);
  document.getElementById('kpiSupply').textContent = fmtKPI(ns);
  document.getElementById('kpiCex').className    = 'kpi-value ' + (nc>=0?'text-success':'text-danger');
  document.getElementById('kpiSupply').className = 'kpi-value ' + (ns>=0?'text-success':'text-danger');
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB 1 — OVERVIEW
// ════════════════════════════════════════════════════════════════════════════════
RENDERERS.overview = function() {
  const f = F();

  // Chart 1: DEX Volume + Stablecoin by date (cross-chain aggregate)
  {
    const raw = DATA.f17;  // already cross-chain aggregated
    const traces = [
      { x: raw.map(d=>d.block_date), y: raw.map(d=>d.dex_volume_usd||0),
        name: 'DEX Volume', type:'scatter', mode:'lines+markers',
        marker:{size:7}, line:{width:2.5},
        hovertemplate:'%{x}<br>DEX Vol: $%{y:,.0f}<extra></extra>' },
      { x: raw.map(d=>d.block_date), y: raw.map(d=>d.stablecoin_transfer_volume_usd||0),
        name: 'Stablecoin Volume', type:'scatter', mode:'lines+markers',
        marker:{size:7}, line:{width:2.5}, yaxis:'y2',
        hovertemplate:'%{x}<br>Stablecoin Vol: $%{y:,.0f}<extra></extra>' },
    ];
    Plotly.react('chartOverviewVol', traces, baseLayout({
      height: 280,
      yaxis:  { title:'DEX Volume (USD)', tickformat:'$.2s', gridcolor:'#21262d' },
      yaxis2: { title:'Stablecoin Volume (USD)', tickformat:'$.2s', overlaying:'y', side:'right', showgrid:false },
      legend: { x:0, y:1.12, orientation:'h' },
    }), plotConfig());
  }

  // Chart 2: CEX flows vs net supply
  {
    const raw = DATA.f17;
    const traces = [
      { x: raw.map(d=>d.block_date), y: raw.map(d=>d.net_cex_flow_usd||0),
        name: 'Net CEX Flow', type:'bar', marker:{color: raw.map(d=>(d.net_cex_flow_usd||0)>=0?'#3fb950':'#f85149')},
        hovertemplate:'%{x}<br>Net CEX: $%{y:,.0f}<extra></extra>' },
      { x: raw.map(d=>d.block_date), y: raw.map(d=>d.net_supply_change_usd||0),
        name: 'Net Supply Change', type:'scatter', mode:'lines+markers',
        marker:{size:7,color:'#bc8cff'}, line:{width:2,color:'#bc8cff'}, yaxis:'y2',
        hovertemplate:'%{x}<br>Supply Δ: $%{y:,.0f}<extra></extra>' },
    ];
    Plotly.react('chartOverviewCex', traces, baseLayout({
      height: 280,
      yaxis:  { title:'Net CEX Flow (USD)', tickformat:'$.2s', gridcolor:'#21262d' },
      yaxis2: { title:'Net Supply Change (USD)', tickformat:'$.2s', overlaying:'y', side:'right', showgrid:false },
      legend: { x:0, y:1.12, orientation:'h' },
      barmode: 'group',
    }), plotConfig());
  }

  // Chart 3: Master summary grouped bar (all chains, all metrics)
  {
    const raw = DATA.f16.filter(d => fChain(d,f));
    const chains = unique(raw, 'chain_name');
    const dates  = unique(raw, 'block_date');
    const metrics = [
      { field:'dex_volume_usd',                  label:'DEX Volume' },
      { field:'dex_fees_usd',                    label:'DEX Fees' },
      { field:'stablecoin_transfer_volume_usd',  label:'Stablecoin Vol' },
      { field:'cex_inflow_usd',                  label:'CEX Inflow' },
      { field:'cex_outflow_usd',                 label:'CEX Outflow' },
    ];
    const traces = [];
    chains.forEach((ch, ci) => {
      metrics.forEach((m, mi) => {
        const rows = raw.filter(d => d.chain_name === ch);
        traces.push({
          x: rows.map(d => d.block_date + '<br>' + m.label),
          y: rows.map(d => d[m.field] || 0),
          name: ch + ' · ' + m.label,
          type: 'bar',
          marker: { color: COLORS[(ci*metrics.length + mi) % COLORS.length], opacity:0.85 },
          hovertemplate: ch + ' ' + m.label + '<br>%{x}<br>$%{y:,.0f}<extra></extra>',
          legendgroup: ch,
          showlegend: mi === 0,
          legendgrouptitle: mi===0 ? {text: ch} : undefined,
        });
      });
    });
    Plotly.react('chartOverviewMaster', traces, baseLayout({
      height: 340,
      barmode: 'stack',
      yaxis:  { title:'USD', tickformat:'$.2s', gridcolor:'#21262d' },
      legend: { x:1.01, y:1, xanchor:'left' },
      margin: { t:30, r:180, b:80, l:80 },
      xaxis:  { tickangle: -30 },
    }), plotConfig());
  }
};

// ════════════════════════════════════════════════════════════════════════════════
// TAB 2 — DEX ACTIVITY
// ════════════════════════════════════════════════════════════════════════════════
RENDERERS.dex = function() {
  const f = F();
  const src     = f.gran === 'hourly' ? DATA.f01 : DATA.f02;
  const srcLiq  = f.gran === 'hourly' ? DATA.f03 : DATA.f04;
  const srcFees = f.gran === 'hourly' ? DATA.f05 : DATA.f06;
  const tField  = f.gran === 'hourly' ? 'block_hour' : 'block_date';

  // Filter
  const vol  = src.filter(d => fChain(d,f) && fPool(d,f) && fDexVer(d,f) && fFeeTier(d,f));
  const liq  = srcLiq.filter(d => fChain(d,f) && fPool(d,f));
  const fees = srcFees.filter(d => fChain(d,f) && fPool(d,f) && fFeeTier(d,f));

  // Chart: Volume line by pool
  {
    const pools = unique(vol, 'pool_symbol');
    const traces = pools.map((pool,i) => {
      const rows = vol.filter(d => d.pool_symbol === pool);
      return {
        x: rows.map(d => d[tField]),
        y: rows.map(d => d.volume_usd || 0),
        name: pool, type:'scatter', mode: f.gran==='hourly'?'lines':'lines+markers',
        line:{width:2}, marker:{size:6},
        hovertemplate: pool+'<br>%{x}<br>Vol: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartDexVol', traces.length?traces:[noDataTrace()], baseLayout({
      height: 300,
      yaxis:  { title:'Volume USD', tickformat:'$.2s' },
      xaxis:  { title: f.gran==='hourly' ? 'Hour' : 'Date' },
      legend: { x:0, y:1.1, orientation:'h' },
    }), plotConfig());
  }

  // Chart: Liquidity added vs removed (grouped bar by pool)
  {
    const pools = unique(liq, 'pool_symbol');
    const added   = groupSum(liq, ['pool_symbol'], 'liquidity_added_usd');
    const removed = groupSum(liq, ['pool_symbol'], 'liquidity_removed_usd');
    const aMap = Object.fromEntries(added.map(r=>[r.pool_symbol, r._sum]));
    const rMap = Object.fromEntries(removed.map(r=>[r.pool_symbol, r._sum]));
    const traces = [
      { x:pools, y:pools.map(p=>aMap[p]||0), name:'Liquidity Added', type:'bar',
        marker:{color:'#3fb950'}, hovertemplate:'%{x}<br>Added: $%{y:,.0f}<extra></extra>' },
      { x:pools, y:pools.map(p=>-(rMap[p]||0)), name:'Liquidity Removed', type:'bar',
        marker:{color:'#f85149'}, hovertemplate:'%{x}<br>Removed: $%{y:,.0f}<extra></extra>' },
    ];
    Plotly.react('chartDexLiq', traces, baseLayout({
      height: 280, barmode:'group',
      yaxis:{ title:'USD', tickformat:'$.2s' },
      legend:{ x:0, y:1.1, orientation:'h' },
    }), plotConfig());
  }

  // Chart: Fees by pool + fee tier
  {
    const pools    = unique(fees, 'pool_symbol');
    const tiers    = unique(fees, 'fee_tier');
    const traces   = tiers.map((tier,i) => {
      const rows = fees.filter(d => d.fee_tier == tier);
      const byPool = groupSum(rows, ['pool_symbol'], 'fees_usd');
      const pMap = Object.fromEntries(byPool.map(r=>[r.pool_symbol, r._sum]));
      return {
        x: pools, y: pools.map(p=>pMap[p]||0),
        name: 'Tier ' + tier + ' bps', type:'bar',
        marker:{color:COLORS[i+1]},
        hovertemplate:'%{x}<br>Fees: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartDexFees', traces.length?traces:[noDataTrace()], baseLayout({
      height: 280, barmode:'stack',
      yaxis:{ title:'Fees USD', tickformat:'$.2s' },
      legend:{ x:0, y:1.1, orientation:'h' },
    }), plotConfig());
  }

  // Chart: Scatter swap_count vs volume_usd
  {
    const dailyVol = DATA.f02.filter(d => fChain(d,f) && fPool(d,f) && fDexVer(d,f));
    const pools    = unique(dailyVol, 'pool_symbol');
    const traces   = pools.map((pool,i) => {
      const rows = dailyVol.filter(d => d.pool_symbol === pool);
      return {
        x: rows.map(d => d.swap_count||0),
        y: rows.map(d => d.volume_usd||0),
        text: rows.map(d => pool + ' · ' + d.block_date),
        name: pool, type:'scatter', mode:'markers',
        marker:{size:12, color:COLORS[i], opacity:0.85, line:{width:1,color:'#30363d'}},
        hovertemplate: '%{text}<br>Swaps: %{x:,}<br>Volume: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartDexScatter', traces.length?traces:[noDataTrace()], baseLayout({
      height: 300,
      xaxis:{ title:'Swap Count', gridcolor:'#21262d' },
      yaxis:{ title:'Volume USD', tickformat:'$.2s' },
    }), plotConfig());
  }
};

// ════════════════════════════════════════════════════════════════════════════════
// TAB 3 — CEX FLOWS
// ════════════════════════════════════════════════════════════════════════════════
RENDERERS.cex = function() {
  const f   = F();
  const src = f.gran === 'hourly' ? DATA.f07 : DATA.f08;
  const rows = src.filter(d => fChain(d,f) && fCEX(d,f));
  const tField = f.gran === 'hourly' ? 'block_hour' : 'block_date';

  // Chart: Grouped bar inflow vs outflow by CEX
  {
    const cexes = unique(rows, 'cex_name');
    const inMap  = Object.fromEntries(groupSum(rows, ['cex_name'], 'INFLOW').map(r=>[r.cex_name, r._sum]));
    const outMap = Object.fromEntries(groupSum(rows, ['cex_name'], 'OUTFLOW').map(r=>[r.cex_name, r._sum]));
    const traces = [
      { x:cexes, y:cexes.map(c=>inMap[c]||0),  name:'Inflow',  type:'bar', marker:{color:'#3fb950'},
        hovertemplate:'%{x}<br>Inflow: $%{y:,.0f}<extra></extra>' },
      { x:cexes, y:cexes.map(c=>outMap[c]||0), name:'Outflow', type:'bar', marker:{color:'#f85149'},
        hovertemplate:'%{x}<br>Outflow: $%{y:,.0f}<extra></extra>' },
    ];
    Plotly.react('chartCexBar', traces, baseLayout({
      height:280, barmode:'group',
      yaxis:{ title:'USD', tickformat:'$.2s' },
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Net flow line (hourly)
  {
    const hRows  = DATA.f07.filter(d => fChain(d,f) && fCEX(d,f));
    const cexes  = unique(hRows, 'cex_name');
    const traces = cexes.map((c,i) => {
      const cr = hRows.filter(d => d.cex_name === c);
      return {
        x: cr.map(d => d.block_hour),
        y: cr.map(d => d.net_flow_usd||0),
        name: c, type:'scatter', mode:'lines', line:{width:2},
        hovertemplate: c+'<br>%{x}<br>Net: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartCexLine', traces.length?traces:[noDataTrace()], baseLayout({
      height:280,
      yaxis:{ title:'Net Flow USD', tickformat:'$.2s', zeroline:true, zerolinecolor:'#30363d' },
      xaxis:{ title:'Hour' },
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Net flow by CEX (daily bar)
  {
    const cexes  = unique(rows, 'cex_name');
    const dates  = unique(rows, tField);
    const traces = dates.map((dt,i) => {
      const dr = rows.filter(d => d[tField] === dt);
      const nMap = Object.fromEntries(groupSum(dr, ['cex_name'], 'net_flow_usd').map(r=>[r.cex_name, r._sum]));
      return {
        x: cexes, y: cexes.map(c=>nMap[c]||0),
        name: dt, type:'bar', marker:{color:COLORS[i]},
        hovertemplate:'%{x} · '+dt+'<br>Net: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartCexNetBar', traces.length?traces:[noDataTrace()], baseLayout({
      height:280, barmode:'group',
      yaxis:{ title:'Net Flow USD', tickformat:'$.2s', zeroline:true, zerolinecolor:'#30363d' },
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }
};

// ════════════════════════════════════════════════════════════════════════════════
// TAB 4 — STABLECOIN INTELLIGENCE
// ════════════════════════════════════════════════════════════════════════════════
RENDERERS.stable = function() {
  const f = F();
  const stSrc   = f.gran==='hourly' ? DATA.f09 : DATA.f10;
  const cexSrc  = f.gran==='hourly' ? DATA.f11 : DATA.f12;
  const tField  = f.gran==='hourly' ? 'block_hour' : 'block_date';

  const stRows  = stSrc.filter(d  => fChain(d,f) && fToken(d,f));
  const cexRows = cexSrc.filter(d => fChain(d,f) && fCEX(d,f) && fToken(d,f));

  // Chart: Transfer volume line by token
  {
    const tokens = unique(stRows, 'token_symbol');
    const traces = tokens.map((tok,i) => {
      const tr = stRows.filter(d => d.token_symbol === tok);
      return {
        x: tr.map(d=>d[tField]), y: tr.map(d=>d.total_amount_usd||0),
        name: tok, type:'scatter', mode: f.gran==='hourly'?'lines':'lines+markers',
        line:{width:2.5}, marker:{size:7},
        hovertemplate:tok+'<br>%{x}<br>$%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartStableLine', traces.length?traces:[noDataTrace()], baseLayout({
      height:280,
      yaxis:{title:'Transfer Volume USD', tickformat:'$.2s'},
      xaxis:{title: f.gran==='hourly'?'Hour':'Date'},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Stablecoin CEX inflow vs outflow grouped bar (by cex × token)
  {
    const pairs = [...new Set(cexRows.map(d=>d.cex_name+'|'+d.token_symbol))].sort();
    const labels = pairs.map(p=>p.replace('|',' / '));
    const inSums  = pairs.map(p => { const [c,t]=p.split('|'); return cexRows.filter(d=>d.cex_name===c&&d.token_symbol===t).reduce((s,d)=>s+(d.INFLOW||0),0); });
    const outSums = pairs.map(p => { const [c,t]=p.split('|'); return cexRows.filter(d=>d.cex_name===c&&d.token_symbol===t).reduce((s,d)=>s+(d.OUTFLOW||0),0); });
    const traces = [
      { x:labels, y:inSums,  name:'Inflow',  type:'bar', marker:{color:'#3fb950'}, hovertemplate:'%{x}<br>Inflow: $%{y:,.0f}<extra></extra>' },
      { x:labels, y:outSums, name:'Outflow', type:'bar', marker:{color:'#f85149'}, hovertemplate:'%{x}<br>Outflow: $%{y:,.0f}<extra></extra>' },
    ];
    Plotly.react('chartStableCex', traces, baseLayout({
      height:280, barmode:'group',
      xaxis:{tickangle:-30},
      yaxis:{title:'USD', tickformat:'$.2s'},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Net flow by CEX (stablecoin)
  {
    const cexes  = unique(cexRows, 'cex_name');
    const tokens = unique(cexRows, 'token_symbol');
    const traces = tokens.map((tok,i) => {
      const tRows = cexRows.filter(d=>d.token_symbol===tok);
      const nMap  = Object.fromEntries(groupSum(tRows,['cex_name'],'net_flow_usd').map(r=>[r.cex_name,r._sum]));
      return {
        x:cexes, y:cexes.map(c=>nMap[c]||0),
        name:tok, type:'bar', marker:{color:COLORS[i]},
        hovertemplate:'%{x} '+tok+'<br>Net: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartStableNetCex', traces, baseLayout({
      height:280, barmode:'group',
      yaxis:{title:'Net Flow USD', tickformat:'$.2s', zeroline:true, zerolinecolor:'#30363d'},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Heatmap — hour-of-day × CEX (hourly stablecoin data)
  {
    const hRows = DATA.f11.filter(d => fChain(d,f) && fToken(d,f));
    const cexes = unique(hRows, 'cex_name');
    const hours = Array.from({length:24},(_,i)=>i);
    const z = cexes.map(c => {
      return hours.map(h => {
        const matching = hRows.filter(d => {
          if (d.cex_name !== c) return false;
          const ts = d.block_hour || '';
          const parts = ts.split(' ');
          const hh = parts[1] ? parseInt(parts[1].split(':')[0]) : -1;
          return hh === h;
        });
        return matching.reduce((s,d)=>s+(d.net_flow_usd||0), 0);
      });
    });
    const traces = [{
      z: z, x: hours.map(h=>String(h).padStart(2,'0')+':00'), y: cexes,
      type:'heatmap', colorscale:'RdYlGn', zmid:0,
      hovertemplate:'%{y} · %{x}<br>Net Flow: $%{z:,.0f}<extra></extra>',
      colorbar:{ tickformat:'$.2s', title:'Net Flow', titleside:'right', thickness:14 },
    }];
    Plotly.react('chartStableHeatmap', traces, baseLayout({
      height:260,
      xaxis:{title:'Hour of Day (UTC)', gridcolor:'rgba(0,0,0,0)'},
      yaxis:{title:'', gridcolor:'rgba(0,0,0,0)'},
      margin:{t:20,r:100,b:55,l:80},
    }), plotConfig());
  }
};

// ════════════════════════════════════════════════════════════════════════════════
// TAB 5 — TOKEN SUPPLY & RESERVES
// ════════════════════════════════════════════════════════════════════════════════
RENDERERS.supply = function() {
  const f = F();

  // Chart: Mint events bar by chain
  {
    const rows   = DATA.f14.filter(d => fChain(d,f));
    const chains = unique(rows, 'chain_name');
    const dates  = unique(rows, 'block_date');
    const traces = dates.map((dt,i) => {
      const dr   = rows.filter(d=>d.block_date===dt);
      const sMap = Object.fromEntries(groupSum(dr,['chain_name'],'total_amount_usd').map(r=>[r.chain_name,r._sum]));
      return {
        x:chains, y:chains.map(c=>sMap[c]||0),
        name:dt, type:'bar', marker:{color:COLORS[i]},
        hovertemplate:'%{x} · '+dt+'<br>Minted: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartMint', traces.length?traces:[noDataTrace()], baseLayout({
      height:280, barmode:'group',
      yaxis:{title:'USD Minted', tickformat:'$.2s'},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Event count by chain + date
  {
    const rows   = DATA.f14.filter(d => fChain(d,f));
    const chains = unique(rows, 'chain_name');
    const dates  = unique(rows, 'block_date');
    const traces = chains.map((ch,i) => {
      const cr = rows.filter(d=>d.chain_name===ch);
      return {
        x: cr.map(d=>d.block_date), y: cr.map(d=>d.event_count||0),
        name:ch, type:'bar', marker:{color:COLORS[i]},
        hovertemplate:ch+'<br>%{x}<br>Events: %{y:,}<extra></extra>',
      };
    });
    Plotly.react('chartMintCount', traces.length?traces:[noDataTrace()], baseLayout({
      height:280, barmode:'group',
      yaxis:{title:'Event Count', tickformat:','},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Pool reserves stacked bar
  {
    const rows  = DATA.f15.filter(d => fChain(d,f) && fPool(d,f));
    const pools = unique(rows, 'pool_symbol');
    const agg = Object.fromEntries(pools.map(p => {
      const pr = rows.filter(d=>d.pool_symbol===p);
      return [p, {
        r0: pr.reduce((s,d)=>s+(d.reserve_token_0_usd||0),0)/pr.length,
        r1: pr.reduce((s,d)=>s+(d.reserve_token_1_usd||0),0)/pr.length,
        total: pr.reduce((s,d)=>s+(d.total_reserve_usd||0),0)/pr.length,
      }];
    }));
    const traces = [
      { x:pools, y:pools.map(p=>agg[p]?.r0||0), name:'Token 0 Reserve', type:'bar', marker:{color:COLORS[0]},
        hovertemplate:'%{x}<br>Token 0: $%{y:,.0f}<extra></extra>' },
      { x:pools, y:pools.map(p=>agg[p]?.r1||0), name:'Token 1 Reserve', type:'bar', marker:{color:COLORS[2]},
        hovertemplate:'%{x}<br>Token 1: $%{y:,.0f}<extra></extra>' },
    ];
    Plotly.react('chartReserves', traces, baseLayout({
      height:280, barmode:'stack',
      yaxis:{title:'Reserve (USD avg)', tickformat:'$.2s'},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // Chart: Total reserve over time (line by pool)
  {
    const rows  = DATA.f15.filter(d => fChain(d,f) && fPool(d,f));
    const pools = unique(rows, 'pool_symbol');
    const traces = pools.map((pool,i) => {
      const pr = rows.filter(d=>d.pool_symbol===pool);
      return {
        x: pr.map(d=>d.block_date), y: pr.map(d=>d.total_reserve_usd||0),
        name:pool, type:'scatter', mode:'lines+markers',
        line:{width:2.5}, marker:{size:8},
        hovertemplate:pool+'<br>%{x}<br>Total Reserve: $%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartReservesLine', traces.length?traces:[noDataTrace()], baseLayout({
      height:280,
      yaxis:{title:'Total Reserve USD', tickformat:'$.2s'},
      xaxis:{title:'Date'},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }
};

// ════════════════════════════════════════════════════════════════════════════════
// TAB 6 — CROSS-CHAIN COMPARISON
// ════════════════════════════════════════════════════════════════════════════════
RENDERERS.crosschain = function() {
  const f = F();

  // ── Radar chart (file 17) ──
  {
    const raw    = DATA.f17;
    const fields = ['dex_volume_usd','dex_fees_usd','stablecoin_transfer_volume_usd','net_cex_flow_usd','net_supply_change_usd'];
    const labels = ['DEX Volume','DEX Fees','Stablecoin Vol','Net CEX Flow','Net Supply'];

    // Compute per-chain aggregates from master summary (f16) for radar
    const f16 = DATA.f16.filter(d => fChain(d,f));
    const chains = unique(f16, 'chain_name');
    const chainTotals = chains.map(ch => {
      const cr = f16.filter(d=>d.chain_name===ch);
      return fields.map(fi => cr.reduce((s,d)=>s+(d[fi]||0),0));
    });

    // Normalize for radar (0–1 per field)
    const maxes = fields.map((_,fi) => Math.max(...chainTotals.map(ct=>Math.abs(ct[fi])), 1));
    const norm  = chainTotals.map(ct => ct.map((v,fi)=>Math.abs(v)/maxes[fi]));

    const traces = chains.map((ch,i) => ({
      type:'scatterpolar', r:[...norm[i], norm[i][0]],
      theta:[...labels, labels[0]],
      fill:'toself', name:ch, opacity:0.7,
      line:{color:COLORS[i]}, marker:{color:COLORS[i]},
      hovertemplate:ch+'<br>%{theta}: %{r:.2f}<extra></extra>',
    }));
    Plotly.react('chartRadar', traces.length?traces:[noDataTrace()], {
      ...baseLayout({height:340}),
      polar:{ bgcolor:PLOTBG, radialaxis:{visible:true,range:[0,1],gridcolor:'#30363d',linecolor:'#30363d',tickfont:{size:9}}, angularaxis:{gridcolor:'#30363d',linecolor:'#30363d'} },
      legend:{x:0,y:1.1,orientation:'h'},
    }, plotConfig());
  }

  // ── Grouped bar: cross-chain metrics ──
  {
    const f16    = DATA.f16.filter(d => fChain(d,f));
    const chains = unique(f16, 'chain_name');
    const metrics = [
      {f:'dex_volume_usd', l:'DEX Volume'},
      {f:'dex_fees_usd',   l:'DEX Fees'},
      {f:'stablecoin_transfer_volume_usd', l:'Stablecoin Vol'},
      {f:'cex_inflow_usd', l:'CEX Inflow'},
      {f:'net_supply_change_usd', l:'Net Supply'},
    ];
    const traces = chains.map((ch,i)=>{
      const cr = f16.filter(d=>d.chain_name===ch);
      return {
        x: metrics.map(m=>m.l),
        y: metrics.map(m=>cr.reduce((s,d)=>s+(d[m.f]||0),0)),
        name:ch, type:'bar', marker:{color:COLORS[i]},
        hovertemplate:ch+'<br>%{x}<br>$%{y:,.0f}<extra></extra>',
      };
    });
    Plotly.react('chartCrossBar', traces.length?traces:[noDataTrace()], baseLayout({
      height:340, barmode:'group',
      yaxis:{title:'USD', tickformat:'$.2s'},
      xaxis:{tickangle:-20},
      legend:{x:0,y:1.1,orientation:'h'},
    }), plotConfig());
  }

  // ── Multi-line: per-chain metrics over time ──
  {
    const f16    = DATA.f16.filter(d => fChain(d,f));
    const chains = unique(f16, 'chain_name');
    const metricsLine = [
      {f:'dex_volume_usd',                 l:'DEX Volume'},
      {f:'stablecoin_transfer_volume_usd', l:'Stablecoin Vol'},
      {f:'net_cex_flow_usd',               l:'Net CEX Flow'},
    ];
    const traces = [];
    chains.forEach((ch,ci)=>{
      metricsLine.forEach((m,mi)=>{
        const cr = f16.filter(d=>d.chain_name===ch).sort((a,b)=>a.block_date>b.block_date?1:-1);
        traces.push({
          x: cr.map(d=>d.block_date),
          y: cr.map(d=>d[m.f]||0),
          name: ch+' · '+m.l,
          type:'scatter', mode:'lines+markers',
          line:{width:2, dash: mi===0?'solid': mi===1?'dash':'dot'},
          marker:{size:7, color:COLORS[ci]},
          legendgroup:ch,
          hovertemplate:ch+' '+m.l+'<br>%{x}<br>$%{y:,.0f}<extra></extra>',
        });
      });
    });
    Plotly.react('chartMasterLine', traces.length?traces:[noDataTrace()], baseLayout({
      height:340,
      yaxis:{title:'USD', tickformat:'$.2s'},
      xaxis:{title:'Date'},
      legend:{x:0,y:1.12,orientation:'h'},
      margin:{t:40,r:20,b:55,l:80},
    }), plotConfig());
  }
};

// ── Utility: no-data placeholder trace ───────────────────────────────────────
function noDataTrace() {
  return {
    x:[0.5], y:[0.5], mode:'text', type:'scatter',
    text:['No data for current filters'], textfont:{size:14,color:'#8b949e'},
    showlegend:false,
    hoverinfo:'none',
    xaxis:'x', yaxis:'y',
  };
}

// ── Bootstrap 5 tab shim (we use our own click handlers) ─────────────────────
// ── Initialise ────────────────────────────────────────────────────────────────
document.querySelectorAll('.tab-content > div').forEach(d => d.style.display = 'none');
document.getElementById('tab-overview').style.display = 'block';

RENDERERS.overview();
</script>

</body>
</html>
"""

# ── Substitute placeholders ───────────────────────────────────────────────────
HTML = (HTML
    .replace("%%DATA%%",        DATA_JSON)
    .replace("%%KPIS%%",        KPIS_JSON)
    .replace("%%GEN_TIME%%",    GEN_TIME)
    .replace("%%KPI_DEX_VOL%%", KPI_DEX_VOL)
    .replace("%%KPI_FEES%%",    KPI_FEES)
    .replace("%%KPI_STABLE%%",  KPI_STABLE)
    .replace("%%KPI_CEX%%",     KPI_CEX)
    .replace("%%KPI_SUPPLY%%",  KPI_SUPPLY)
    .replace("%%CEX_SIGN%%",    CEX_SIGN)
    .replace("%%SUP_SIGN%%",    SUP_SIGN)
)

OUT = os.path.join(BASE, "dashboard.html")
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(HTML)

size_kb = os.path.getsize(OUT) / 1024
print(f"\nDashboard generated successfully!")
print(f"  Output : {OUT}")
print(f"  Size   : {size_kb:.1f} KB")
print(f"\nKey metrics:")
print(f"  DEX Volume      : {KPI_DEX_VOL}")
print(f"  DEX Fees        : {KPI_FEES}")
print(f"  Stablecoin Vol  : {KPI_STABLE}")
print(f"  Net CEX Flow    : {KPI_CEX}")
print(f"  Net Supply Chg  : {KPI_SUPPLY}")
print(f"\nOpen dashboard.html in any browser (no server required).")
