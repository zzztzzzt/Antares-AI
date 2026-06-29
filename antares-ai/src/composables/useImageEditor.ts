import { ref } from "vue";
import type { Ref } from "vue";

import { CanvasEngine } from "../core/CanvasEngine";
import { VibranceFilter } from "../filters/VibranceFilter";
import type { ImageFilter } from "../filters/ImageFilter";

function cloneImageData(imageData: ImageData): ImageData {
  return new ImageData(
    new Uint8ClampedArray(imageData.data),
    imageData.width,
    imageData.height
  );
}

export function useImageEditor(canvasRef: Ref<HTMLCanvasElement | null>) {
  const vibrance = ref(60);

  let engine: CanvasEngine | null = null;
  let originalImageData: ImageData | null = null;

  const vibranceFilter = new VibranceFilter();
  vibranceFilter.amount = vibrance.value;

  const filters: ImageFilter[] = [vibranceFilter];

  function render() {
    if (!engine || !originalImageData) return;

    const image = cloneImageData(originalImageData);

    for (const filter of filters) {
      filter.apply(image);
    }

    engine.putImageData(image);
  }

  function onVibranceInput() {
    vibranceFilter.amount = vibrance.value;
    render();
  }

  function openImage(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const file = input.files[0];
    const reader = new FileReader();

    reader.onload = () => {
      const img = new Image();

      img.onload = () => {
        const canvas = canvasRef.value;
        if (!canvas) return;

        engine = new CanvasEngine(canvas);
        engine.drawImage(img);
        originalImageData = engine.getImageData();

        render();
      };

      img.src = reader.result as string;
    };

    reader.readAsDataURL(file);
  }

  return { vibrance, openImage, onVibranceInput };
}