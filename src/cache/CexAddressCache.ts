import { prisma } from "../storage/DatabaseClient";

class CexAddressCache {
  private static instance: CexAddressCache;
  private byChainAndCex: Map<number, Map<string, Set<string>>> = new Map();
  private allByChain: Map<number, Set<string>> = new Map();

  static getInstance(): CexAddressCache {
    if (!CexAddressCache.instance) {
      CexAddressCache.instance = new CexAddressCache();
    }
    return CexAddressCache.instance;
  }

  async load(): Promise<void> {
    const rows = await prisma.cexAddress.findMany();
    for (const row of rows) {
      if (!this.byChainAndCex.has(row.chainId)) {
        this.byChainAndCex.set(row.chainId, new Map());
      }
      const cexMap = this.byChainAndCex.get(row.chainId)!;
      if (!cexMap.has(row.cexName)) {
        cexMap.set(row.cexName, new Set());
      }
      cexMap.get(row.cexName)!.add(row.address.toLowerCase());

      if (!this.allByChain.has(row.chainId)) {
        this.allByChain.set(row.chainId, new Set());
      }
      this.allByChain.get(row.chainId)!.add(row.address.toLowerCase());
    }
    console.log(`CexAddressCache Loaded ${rows.length}`);
  }

  getCexAddressSetsForChain(chainId: number): Map<string, Set<string>> {
    return this.byChainAndCex.get(chainId) ?? new Map();
  }

  getAllCexAddressesForChain(chainId: number): Set<string> {
    return this.allByChain.get(chainId) ?? new Set();
  }
}

export { CexAddressCache };
