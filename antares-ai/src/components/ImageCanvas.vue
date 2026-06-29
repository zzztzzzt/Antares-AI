<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  vibrance: number;
}>();

const emit = defineEmits<{
  "update:vibrance": [value: number];
  "update:canvasEl": [el: HTMLCanvasElement | null];
  "vibrance-input": [];
}>();

const showControls = ref(false);
const dragging = ref(false);

function onVibranceChange(event: Event) {
  const input = event.target as HTMLInputElement;
  emit("update:vibrance", Number(input.value));
  emit("vibrance-input");
}

function onPointerDown() {
  dragging.value = true;
}

function onPointerUp() {
  dragging.value = false;
}
</script>

<template>
  <div
    class="relative flex justify-center"
    @mouseenter="showControls = true"
    @mouseleave="showControls = false"
  >
    <canvas
      :ref="(el) => emit('update:canvasEl', el as HTMLCanvasElement | null)"
      class="max-w-full border border-neutral-200"
    />

    <div
      :class="[
        'absolute inset-0 flex items-center justify-center transition-opacity duration-300',
        showControls && !dragging ? 'opacity-100' : 'opacity-0 pointer-events-none',
      ]"
    >
      <div class="w-80">
        <input
          :value="vibrance"
          type="range"
          min="-100"
          max="100"
          class="w-full accent-black"
          @input="onVibranceChange"
          @pointerdown="onPointerDown"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
        />

        <p class="mt-2 text-center text-sm text-neutral-500">
          Vibrance {{ vibrance }}
        </p>
      </div>
    </div>
  </div>
</template>