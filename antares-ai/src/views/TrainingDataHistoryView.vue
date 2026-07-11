<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import AppHeader from "../components/AppHeader.vue";
import { API_BASE_URL } from "../utils/api";

type ImageRow = {
  id: number;
  filename: string;
  width: number;
  height: number;
  file_size: number;
  upload_time?: string | null;
};

type ImageFeatureRow = {
  id: number;
  image_id: number;
  filename?: string | null;
  brightness_mean: number;
  brightness_std: number;
  brightness_p5: number;
  brightness_p50: number;
  brightness_p95: number;
  dynamic_range: number;
  black_clip_ratio: number;
  white_clip_ratio: number;
  saturation_mean: number;
  saturation_std: number;
  mean_r: number;
  mean_g: number;
  mean_b: number;
  lab_a_mean: number;
  lab_b_mean: number;
  dominant_colors: Array<{ rgb: [number, number, number]; percentage: number }>;
  unique_colors_ratio: number;
  sharpness: number;
  edge_density: number;
  entropy: number;
  local_contrast: number;
};

type UserFilterRow = {
  id: number;
  image_id: number;
  filename?: string | null;
  brightness: number;
  vibrance: number;
  highlights_shadows: number;
  temperature: number;
  tint: number;
  duotone: number;
  duotone_dark: string;
  duotone_light: string;
  updated_at?: string | null;
};

const imageRows = ref<ImageRow[]>([]);
const featureRows = ref<ImageFeatureRow[]>([]);
const filterRows = ref<UserFilterRow[]>([]);
const focusedImageId = ref<number | null>(null);
const focusConfirm = reactive<Record<number, boolean>>({});
const deleteConfirm = reactive<Record<number, boolean>>({});
const deleteResetTimers = new Map<number, ReturnType<typeof setTimeout>>();
const focusResetTimers = new Map<number, ReturnType<typeof setTimeout>>();
const loading = ref(false);
const errorMessage = ref("");
const focusedImageRows = computed(() =>
  focusedImageId.value === null
    ? imageRows.value
    : imageRows.value.filter((row) => row.id === focusedImageId.value)
);
const focusedFeatureRows = computed(() =>
  focusedImageId.value === null
    ? featureRows.value
    : featureRows.value.filter((row) => row.image_id === focusedImageId.value)
);
const focusedFilterRows = computed(() =>
  focusedImageId.value === null
    ? filterRows.value
    : filterRows.value.filter((row) => row.image_id === focusedImageId.value)
);

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

async function loadAll() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const [images, features, filters] = await Promise.all([
      fetchJson<ImageRow[]>(`${API_BASE_URL}/training-data-history/images`),
      fetchJson<ImageFeatureRow[]>(`${API_BASE_URL}/training-data-history/image-features`),
      fetchJson<UserFilterRow[]>(`${API_BASE_URL}/training-data-history`),
    ]);

    imageRows.value = images;
    featureRows.value = features;
    filterRows.value = filters;
    for (const key of Object.keys(focusConfirm)) {
      delete focusConfirm[Number(key)];
    }
    for (const key of Object.keys(deleteConfirm)) {
      delete deleteConfirm[Number(key)];
    }
    for (const timer of focusResetTimers.values()) {
      clearTimeout(timer);
    }
    focusResetTimers.clear();
    for (const timer of deleteResetTimers.values()) {
      clearTimeout(timer);
    }
    deleteResetTimers.clear();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to load data";
  } finally {
    loading.value = false;
  }
}

async function focusImage(row: ImageRow) {
  if (focusedImageId.value === row.id && focusConfirm[row.id]) {
    focusedImageId.value = null;
    delete focusConfirm[row.id];

    const timer = focusResetTimers.get(row.id);
    if (timer) {
      clearTimeout(timer);
      focusResetTimers.delete(row.id);
    }
    return;
  }

  if (focusedImageId.value === row.id) {
    focusConfirm[row.id] = true;

    const existingTimer = focusResetTimers.get(row.id);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    const timer = setTimeout(() => {
      delete focusConfirm[row.id];
      focusResetTimers.delete(row.id);
    }, 5000);

    focusResetTimers.set(row.id, timer);
    return;
  }

  focusedImageId.value = row.id;
  focusConfirm[row.id] = true;

  const existingTimer = focusResetTimers.get(row.id);
  if (existingTimer) {
    clearTimeout(existingTimer);
  }

  const timer = setTimeout(() => {
    delete focusConfirm[row.id];
    focusResetTimers.delete(row.id);
  }, 5000);

  focusResetTimers.set(row.id, timer);
}

function armDeleteConfirm(imageId: number) {
  deleteConfirm[imageId] = true;

  const existingTimer = deleteResetTimers.get(imageId);
  if (existingTimer) {
    clearTimeout(existingTimer);
  }

  const timer = setTimeout(() => {
    delete deleteConfirm[imageId];
    deleteResetTimers.delete(imageId);
  }, 5000);

  deleteResetTimers.set(imageId, timer);
}

async function deleteFilterRow(imageId: number) {
  if (!deleteConfirm[imageId]) {
    armDeleteConfirm(imageId);
    return;
  }

  const response = await fetch(`${API_BASE_URL}/training-data-history/user-filter-data/${imageId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    errorMessage.value = await response.text();
    return;
  }

  delete deleteConfirm[imageId];
  const timer = deleteResetTimers.get(imageId);
  if (timer) {
    clearTimeout(timer);
    deleteResetTimers.delete(imageId);
  }
  await loadAll();
}

onMounted(loadAll);
</script>

<template>
  <main class="min-h-screen bg-neutral-50">
    <div class="mx-auto max-w-7xl p-8">
      <AppHeader />

      <div class="mb-6 flex flex-wrap items-end gap-3 rounded-xl border border-sky-200 bg-sky-50 p-4 shadow-sm">
        <RouterLink class="rounded border border-sky-200 px-4 py-2 text-sky-900" to="/">Back Home</RouterLink>
      </div>

      <p v-if="errorMessage" class="mb-4 rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{{ errorMessage }}</p>
      <p v-if="loading" class="mb-4 text-sm text-neutral-600">Loading...</p>

      <section class="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-amber-950">images</h2>
          <span class="rounded-full bg-amber-200 px-3 py-1 text-xs font-medium text-amber-950">{{ focusedImageRows.length }} rows</span>
        </div>
        <div class="overflow-x-auto rounded-lg border border-amber-200 bg-white">
          <table class="min-w-full border-collapse text-sm">
            <thead class="bg-amber-100 text-left">
              <tr>
                <th class="border-b px-3 py-2">id</th>
                <th class="border-b px-3 py-2">filename</th>
                <th class="border-b px-3 py-2">width</th>
                <th class="border-b px-3 py-2">height</th>
                <th class="border-b px-3 py-2">file_size</th>
                <th class="border-b px-3 py-2">upload_time</th>
                <th class="border-b px-3 py-2">actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in focusedImageRows" :key="row.id" class="odd:bg-white even:bg-amber-50/60">
                <td class="border-b px-3 py-2">{{ row.id }}</td>
                <td class="border-b px-3 py-2">{{ row.filename }}</td>
                <td class="border-b px-3 py-2">{{ row.width }}</td>
                <td class="border-b px-3 py-2">{{ row.height }}</td>
                <td class="border-b px-3 py-2">{{ row.file_size }}</td>
                <td class="border-b px-3 py-2 whitespace-nowrap">{{ row.upload_time }}</td>
                <td class="border-b px-3 py-2">
                  <div class="flex gap-2">
                    <button class="rounded border border-sky-300 px-3 py-1 text-sky-800 transition hover:bg-sky-100" @click="focusImage(row)">
                      {{ focusConfirm[row.id] && focusedImageId === row.id ? "Cancel" : "Focus" }}
                    </button>
                    <button
                      class="rounded border px-3 py-1 transition"
                      :class="deleteConfirm[row.id]
                        ? 'border-red-500 bg-red-500 text-white hover:bg-red-600'
                        : 'border-red-300 text-red-700 hover:bg-red-50'"
                      @click="deleteFilterRow(row.id)"
                    >
                      {{ deleteConfirm[row.id] ? "Sure?" : "Delete" }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="focusedImageRows.length === 0">
                <td class="px-3 py-6 text-center text-neutral-500" colspan="7">No rows found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="mb-8 rounded-2xl border border-violet-200 bg-violet-50 p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-violet-950">image_features</h2>
          <span class="rounded-full bg-violet-200 px-3 py-1 text-xs font-medium text-violet-950">{{ focusedFeatureRows.length }} rows</span>
        </div>
        <div class="overflow-x-auto rounded-lg border border-violet-200 bg-white">
          <table class="min-w-full border-collapse text-sm">
            <thead class="bg-violet-100 text-left">
              <tr>
                <th class="border-b px-3 py-2">id</th>
                <th class="border-b px-3 py-2">image_id</th>
                <th class="border-b px-3 py-2">filename</th>
                <th class="border-b px-3 py-2">brightness_mean</th>
                <th class="border-b px-3 py-2">dynamic_range</th>
                <th class="border-b px-3 py-2">saturation_mean</th>
                <th class="border-b px-3 py-2">mean_rgb</th>
                <th class="border-b px-3 py-2">unique_colors_ratio</th>
                <th class="border-b px-3 py-2">sharpness</th>
                <th class="border-b px-3 py-2">entropy</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in focusedFeatureRows" :key="row.id" class="odd:bg-white even:bg-violet-50/60">
                <td class="border-b px-3 py-2">{{ row.id }}</td>
                <td class="border-b px-3 py-2">{{ row.image_id }}</td>
                <td class="border-b px-3 py-2">{{ row.filename }}</td>
                <td class="border-b px-3 py-2">{{ row.brightness_mean }}</td>
                <td class="border-b px-3 py-2">{{ row.dynamic_range }}</td>
                <td class="border-b px-3 py-2">{{ row.saturation_mean }}</td>
                <td class="border-b px-3 py-2">{{ row.mean_r }}, {{ row.mean_g }}, {{ row.mean_b }}</td>
                <td class="border-b px-3 py-2">{{ row.unique_colors_ratio }}</td>
                <td class="border-b px-3 py-2">{{ row.sharpness }}</td>
                <td class="border-b px-3 py-2">{{ row.entropy }}</td>
              </tr>
              <tr v-if="focusedFeatureRows.length === 0">
                <td class="px-3 py-6 text-center text-neutral-500" colspan="10">No rows found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-emerald-950">user_filter_data</h2>
          <span class="rounded-full bg-emerald-200 px-3 py-1 text-xs font-medium text-emerald-950">{{ focusedFilterRows.length }} rows</span>
        </div>
        <div class="overflow-x-auto rounded-lg border border-emerald-200 bg-white">
          <table class="min-w-full border-collapse text-sm">
            <thead class="bg-emerald-100 text-left">
              <tr>
                <th class="border-b px-3 py-2">id</th>
                <th class="border-b px-3 py-2">image_id</th>
                <th class="border-b px-3 py-2">filename</th>
                <th class="border-b px-3 py-2">brightness</th>
                <th class="border-b px-3 py-2">vibrance</th>
                <th class="border-b px-3 py-2">highlights_shadows</th>
                <th class="border-b px-3 py-2">temperature</th>
                <th class="border-b px-3 py-2">tint</th>
                <th class="border-b px-3 py-2">updated_at</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in focusedFilterRows" :key="row.id" class="odd:bg-white even:bg-emerald-50/60">
                <td class="border-b px-3 py-2">{{ row.id }}</td>
                <td class="border-b px-3 py-2">{{ row.image_id }}</td>
                <td class="border-b px-3 py-2">{{ row.filename }}</td>
                <td class="border-b px-3 py-2">{{ row.brightness }}</td>
                <td class="border-b px-3 py-2">{{ row.vibrance }}</td>
                <td class="border-b px-3 py-2">{{ row.highlights_shadows }}</td>
                <td class="border-b px-3 py-2">{{ row.temperature }}</td>
                <td class="border-b px-3 py-2">{{ row.tint }}</td>
                <td class="border-b px-3 py-2 whitespace-nowrap">{{ row.updated_at }}</td>
              </tr>
              <tr v-if="focusedFilterRows.length === 0">
                <td class="px-3 py-6 text-center text-neutral-500" colspan="9">No rows found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
</template>
