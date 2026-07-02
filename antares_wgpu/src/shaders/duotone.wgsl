// Duotone Filter - GPU Compute Shader
// Maps luminance to a gradient between two colors in OKLab space

struct Params {
    width: u32,
    height: u32,
    strength: f32,
    contrast_curve: f32,
    dark_color: vec4<f32>,
    light_color: vec4<f32>,
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

    // Use OKLab L channel for perceptually uniform luminance
    let lab = rgb_to_oklab(rgba.r, rgba.g, rgba.b);
    let luma = lab.x; // Range : 0-1

    let t = smoothstep(0.0, 1.0, luma);
    let lifted = pow(t, params.contrast_curve);

    let dark_lab = rgb_to_oklab(params.dark_color.r, params.dark_color.g, params.dark_color.b);
    let light_lab = rgb_to_oklab(params.light_color.r, params.light_color.g, params.light_color.b);

    let blended_lab = vec3<f32>(
        mix(dark_lab.x, light_lab.x, lifted),
        mix(dark_lab.y, light_lab.y, lifted),
        mix(dark_lab.z, light_lab.z, lifted),
    );

    let mapped_rgb = oklab_to_rgb(blended_lab);

    let final_rgb = vec3<f32>(
        mix(rgba.r, mapped_rgb.r, params.strength),
        mix(rgba.g, mapped_rgb.g, params.strength),
        mix(rgba.b, mapped_rgb.b, params.strength),
    );

    pixels[idx] = pack_rgba(vec4<f32>(final_rgb, rgba.a));
}
