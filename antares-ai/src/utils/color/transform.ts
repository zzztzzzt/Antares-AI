import type { RGB, OKLCH } from "./types";

import { rgbToOKLab, okLabToRGB } from "./oklab";
import { okLabToOKLCH, okLCHToOKLab } from "./oklch";

export function transformOKLCH(
  rgb: RGB,
  transform: (color: OKLCH) => void
): RGB {

  const lab = rgbToOKLab(rgb);

  const lch = okLabToOKLCH(lab);

  transform(lch);

  return okLabToRGB(
    okLCHToOKLab(lch)
  );
}