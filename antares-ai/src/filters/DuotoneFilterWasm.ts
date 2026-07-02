import type { ImageFilter } from "./ImageFilter";
import { getWasmFilterEngine } from "../wasm/WasmFilterEngine";

/**
 * WASM-accelerated Duotone Filter
 *
 * Drop-in replacement for the TypeScript DuotoneFilter
 * Uses Rust + WASM for significantly better performance
 */
export class DuotoneFilterWasm implements ImageFilter {
  amount = 100;
  contrastCurve = 0.82;

  darkColor = { r: 43, g: 12, b: 86 };
  lightColor = { r: 255, g: 72, b: 176 };

  setColors(
    darkColor: { r: number; g: number; b: number },
    lightColor: { r: number; g: number; b: number }
  ): void {
    this.darkColor = darkColor;
    this.lightColor = lightColor;
  }

  async apply(imageData: ImageData): Promise<ImageData> {
    const engine = await getWasmFilterEngine();
    await engine.applyDuotone(
      imageData,
      this.amount,
      this.contrastCurve,
      this.darkColor.r,
      this.darkColor.g,
      this.darkColor.b,
      this.lightColor.r,
      this.lightColor.g,
      this.lightColor.b
    );
    return imageData;
  }
}
