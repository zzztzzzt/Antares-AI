use crate::gpu;

/// Apply vibrance filter via WGPU compute shader ( OKLCH color space ).
pub async fn apply_vibrance(
    data: &mut [u8],
    width: u32,
    height: u32,
    amount: f32,
) -> Result<(), String> {
    let (device, queue, vibrance) = gpu::get_handles()?;
    let owned = data.to_vec();
    let result = vibrance
        .apply(&device, &queue, owned, width, height, amount)
        .await?;
    data.copy_from_slice(&result);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::utils::color::{oklab_to_oklch, oklab_to_rgb, oklch_to_oklab, rgb_to_oklab, RGB};

    const MAX_CHROMA: f32 = 0.45;
    const SCALE: f32 = 0.12;

    fn apply_vibrance_cpu(data: &mut [u8], width: u32, height: u32, amount: f32) {
        let strength = amount / 100.0;
        let pixel_count = (width * height) as usize;

        for i in 0..pixel_count {
            let idx = i * 4;
            let rgb = RGB {
                r: data[idx],
                g: data[idx + 1],
                b: data[idx + 2],
            };

            let lab = rgb_to_oklab(rgb);
            let mut lch = oklab_to_oklch(lab);
            let chroma_boost = 1.0 - (lch.c / MAX_CHROMA).min(1.0);
            let luma_mask = 1.0 - (lch.l - 0.5).abs() * 0.3;
            let boost = chroma_boost * luma_mask;
            lch.c = (lch.c + strength * boost * SCALE).max(0.0);

            let lab = oklch_to_oklab(lch);
            let result = oklab_to_rgb(lab);

            data[idx] = result.r;
            data[idx + 1] = result.g;
            data[idx + 2] = result.b;
        }
    }

    #[test]
    fn test_vibrance_identity_cpu() {
        let mut data = vec![128u8; 4 * 4];
        let original = data.clone();
        apply_vibrance_cpu(&mut data, 2, 2, 0.0);
        for i in 0..data.len() {
            assert!((data[i] as i32 - original[i] as i32).abs() <= 1);
        }
    }

    #[test]
    fn test_vibrance_increase_cpu() {
        let mut data = vec![255u8, 0, 0, 255];
        apply_vibrance_cpu(&mut data, 1, 1, 50.0);
        assert!(data[0] > data[1]);
        assert!(data[0] > data[2]);
    }
}
