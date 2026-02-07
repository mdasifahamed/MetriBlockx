import { JsonRpcProvider } from "ethers";

export class RpcManager {
  private providers: JsonRpcProvider[] = [];
  private currentIndex = 0;
  private failedAttempts: Map<number, number> = new Map();
  private chainName: string;
  private targetBlock: number;

  constructor(endpoints: string[], chainName: string = "unknown", targetBlock: number) {
    if (!endpoints.length) {
      throw new Error("No RPC endpoints provided");
    }


    this.chainName = chainName;
    this.targetBlock = targetBlock
    this.providers = endpoints.map(
      (url) => new JsonRpcProvider(url, undefined, { staticNetwork: true })
    );

    // Initialize failed attempts counter for each provider
    endpoints.forEach((_, index) => {
      this.failedAttempts.set(index, 0);
    });
  }

  /**
   * Main executor that execute rpc call based on the methdod and params  
   * @param method name of the methods to be called
   * @param params paramte that will be passed to that rpc call 
   * @returns it will return json repsone to rpc specific response format that we will reformat accodign to that network
   */
  async execute<T>(method: string, params: unknown[]): Promise<T> {
    const maxAttempts = this.providers.length; // to track anb reinfomrtion aut retry
    let lastError: Error | undefined; // to track the shutdown error

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const provider = this.providers[this.currentIndex]!;

      try {
        const result = await provider.send(method, params);
        // Reset failed attempts on success
        this.failedAttempts.set(this.currentIndex, 0);
        return result as T;
      } catch (error: unknown) {
        lastError = error instanceof Error ? error : new Error(String(error));
        const failures = (this.failedAttempts.get(this.currentIndex) || 0) + 1;
        this.failedAttempts.set(this.currentIndex, failures);

        const errorMessage = lastError.message || "";
        const errorCode = (error as { code?: number }).code;

        // Rate limit detection
        if (errorCode === 429 || errorMessage.includes("rate limit")) {
          console.log(`[${this.chainName}] Rate limited on endpoint ${this.currentIndex}, rotating...`);
          this.rotateEndpoint();
          await this.sleep(10000); // 10 second sleep after the endpoint rotation if the rate limit hit that use another end point
        } else {
          console.log(`[${this.chainName}] RPC error on endpoint ${this.currentIndex}: ${errorMessage.slice(0, 100)}`);
          this.rotateEndpoint();
          await this.sleep(10000); // 10 Second sleep if the any another erro countered
        }
      }
    }

    throw new Error(`[${this.chainName}] All RPC endpoints failed. Last error: ${lastError?.message}`);
  }

  private rotateEndpoint(): void {
    this.currentIndex = (this.currentIndex + 1) % this.providers.length;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

}
