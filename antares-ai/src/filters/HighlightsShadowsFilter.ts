import type { ImageFilter } from "./ImageFilter";

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function getLuma(r: number, g: number, b: number): number {
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function smoothstep(edge0: number, edge1: number, x: number): number {
  const t = clamp((x - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

export class HighlightsShadowsFilter implements ImageFilter {
  amount = 0;

  apply(imageData: ImageData): ImageData {
    const data = imageData.data;
    const strength = Math.abs(this.amount) / 100;
    const isShadowLift = this.amount > 0;
    const isHighlightRecovery = this.amount < 0;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const luma = getLuma(r, g, b);

      if (isShadowLift) {
        // Smoothly affect only the darker range, with a gentle roll-off into midtones.
        const shadowMask = 1 - smoothstep(28, 96, luma);
        const lift = (1 - (1 - strength) ** 2) * shadowMask * shadowMask;
        const blend = lift * 0.72;

        data[i] = clamp(r + (255 - r) * blend, 0, 255);
        data[i + 1] = clamp(g + (255 - g) * blend, 0, 255);
        data[i + 2] = clamp(b + (255 - b) * blend, 0, 255);
      } else if (isHighlightRecovery) {
        // Smoothly affect only the brighter range, with a soft shoulder near the threshold.
        const highlightMask = smoothstep(174, 242, luma);
        const recovery = (1 - (1 - strength) ** 2) * highlightMask * highlightMask;
        const blend = recovery * 0.68;

        data[i] = clamp(r - r * blend, 0, 255);
        data[i + 1] = clamp(g - g * blend, 0, 255);
        data[i + 2] = clamp(b - b * blend, 0, 255);
      }
    }

    return imageData;
  }
}
