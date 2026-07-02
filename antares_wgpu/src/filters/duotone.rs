use crate::gpu;

/// Apply duotone filter using GPU compute shader ( OKLab color space ).
pub async fn apply_duotone(
    data: &mut [u8],
    width: u32,
    height: u32,
    amount: f32,
    contrast_curve: f32,
    dr: f32,
    dg: f32,
    db: f32,
    lr: f32,
    lg: f32,
    lb: f32,
) -> Result<(), String> {
    let (device, queue, dt) =
        gpu::with_gpu_state(|s| (s.device.clone(), s.queue.clone(), s.duotone.clone()))?;
    let owned = data.to_vec();
    let result = dt
        .apply(
            &device,
            &queue,
            owned,
            width,
            height,
            amount,
            contrast_curve,
            dr,
            dg,
            db,
            lr,
            lg,
            lb,
        )
        .await?;
    data.copy_from_slice(&result);
    Ok(())
}
