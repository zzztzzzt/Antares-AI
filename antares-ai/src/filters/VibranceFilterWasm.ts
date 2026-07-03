import { getWasmFilterEngine } from "../wasm/WasmFilterEngine";

/**
 * WASM-accelerated Vibrance Filter
 * 
 * Drop-in replacement for the TypeScript VibranceFilter
 * Uses Rust + WASM for significantly better performance
 */
export class VibranceFilterWasm {
  amount = 0; // Range : -100 to +100

  async apply(imageData: ImageData): Promise<ImageData> {
    const engine = await getWasmFilterEngine();
    await engine.applyVibrance(imageData, this.amount);
    return imageData;
  }
}
