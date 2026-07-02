// Vibrance Filter - GPU Compute Shader
// Boosts saturation of less-saturated colors while preserving highly saturated areas

// Maximum chroma threshold for boost calculation
// OKLCH chroma can exceed 0.4, using 0.45 allows for more headroom
const MAX_CHROMA: f32 = 0.45;

// Base scale factor for chroma adjustment
const SCALE: f32 = 0.12;

struct Params {
    width: u32,
    height: u32,
    strength: f32,
    _padding: u32,
}

@group(0) @binding(0) var<storage, read_write> pixels: array<u32>;
@group(0) @binding(1) var<uniform> params: Params;

@compute @workgroup_size(16, 16, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let x = gid.x;
    let y = gid.y;
    if (x >= params.width || y >= params.height) {
        return;
    }

    let idx = y * params.width + x;
    let rgba = unpack_rgba(pixels[idx]);

    var lab = rgb_to_oklab(rgba.r, rgba.g, rgba.b);
    var lch = oklab_to_oklch(lab);

    let chroma_boost = 1.0 - min(lch.y / MAX_CHROMA, 1.0);
    let luma_mask = 1.0 - abs(lch.x - 0.5) * 0.3;
    let boost = chroma_boost * luma_mask;
    lch.y = max(0.0, lch.y + params.strength * boost * SCALE);

    lab = oklch_to_oklab(lch);
    let result = oklab_to_rgb(lab);

    pixels[idx] = pack_rgba(vec4<f32>(result, rgba.a));
}
