use bytemuck::{Pod, Zeroable};
use wgpu::util::DeviceExt;

#[repr(C)]
#[derive(Copy, Clone, Pod, Zeroable)]
struct DuotoneParams {
    width: u32,
    height: u32,
    strength: f32,
    contrast_curve: f32,
    dark_color: [f32; 4],
    light_color: [f32; 4],
}

#[derive(Clone)]
pub struct DuotonePipeline {
    pipeline: wgpu::ComputePipeline,
    bind_group_layout: wgpu::BindGroupLayout,
}

impl DuotonePipeline {
    pub fn new(device: &wgpu::Device) -> Self {
        let color_common = include_str!("../shaders/common/color.wgsl");
        let duotone_shader = include_str!("../shaders/duotone.wgsl");
        let shader_source = format!("{}\n\n{}", color_common, duotone_shader);

        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("duotone_shader"),
            source: wgpu::ShaderSource::Wgsl(shader_source.into()),
        });

        let bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("duotone_bind_group_layout"),
            entries: &[
                wgpu::BindGroupLayoutEntry {
                    binding: 0,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Storage { read_only: false },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
                wgpu::BindGroupLayoutEntry {
                    binding: 1,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Uniform,
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
            ],
        });

        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("duotone_pipeline_layout"),
            bind_group_layouts: &[Some(&bind_group_layout)],
            immediate_size: 0,
        });

        let pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
            label: Some("duotone_pipeline"),
            layout: Some(&pipeline_layout),
            module: &shader,
            entry_point: Some("main"),
            compilation_options: Default::default(),
            cache: None,
        });

        Self {
            pipeline,
            bind_group_layout,
        }
    }

    pub async fn apply(
        &self,
        device: &wgpu::Device,
        queue: &wgpu::Queue,
        data: Vec<u8>,
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
    ) -> Result<Vec<u8>, String> {
        let pixel_count = (width * height) as usize;
        let expected_len = pixel_count * 4;
        if data.len() != expected_len {
            return Err(format!(
                "Invalid buffer length: expected {expected_len}, got {}",
                data.len()
            ));
        }

        let packed: Vec<u32> = data
            .chunks_exact(4)
            .map(|px| {
                u32::from(px[0])
                    | (u32::from(px[1]) << 8)
                    | (u32::from(px[2]) << 16)
                    | (u32::from(px[3]) << 24)
            })
            .collect();

        let params = DuotoneParams {
            width,
            height,
            strength: (amount / 100.0).clamp(0.0, 1.0),
            contrast_curve,
            dark_color: [dr / 255.0, dg / 255.0, db / 255.0, 1.0],
            light_color: [lr / 255.0, lg / 255.0, lb / 255.0, 1.0],
        };

        let pixel_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("duotone_pixels"),
            contents: bytemuck::cast_slice(&packed),
            usage: wgpu::BufferUsages::STORAGE
                | wgpu::BufferUsages::COPY_SRC
                | wgpu::BufferUsages::COPY_DST,
        });

        let uniform_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("duotone_params"),
            contents: bytemuck::bytes_of(&params),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        });

        let staging_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("duotone_staging"),
            size: (packed.len() * std::mem::size_of::<u32>()) as u64,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("duotone_bind_group"),
            layout: &self.bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: pixel_buffer.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: uniform_buffer.as_entire_binding(),
                },
            ],
        });

        let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("duotone_encoder"),
        });

        {
            let mut pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor {
                label: Some("duotone_pass"),
                timestamp_writes: None,
            });
            pass.set_pipeline(&self.pipeline);
            pass.set_bind_group(0, &bind_group, &[]);
            let workgroups_x = width.div_ceil(16);
            let workgroups_y = height.div_ceil(16);
            pass.dispatch_workgroups(workgroups_x, workgroups_y, 1);
        }

        encoder.copy_buffer_to_buffer(&pixel_buffer, 0, &staging_buffer, 0, staging_buffer.size());

        queue.submit(Some(encoder.finish()));

        let buffer_slice = staging_buffer.slice(..);
        let (sender, receiver) = futures_channel::oneshot::channel();
        buffer_slice.map_async(wgpu::MapMode::Read, move |result| {
            let _ = sender.send(result);
        });

        device
            .poll(wgpu::PollType::wait_indefinitely())
            .map_err(|e| format!("Failed while waiting for GPU readback: {e:?}"))?;

        receiver
            .await
            .map_err(|_| "GPU readback channel closed".to_string())?
            .map_err(|e| format!("Failed to map GPU buffer: {e:?}"))?;

        let mapped = buffer_slice
            .get_mapped_range()
            .map_err(|e| format!("Failed to get mapped GPU buffer range: {e:?}"))?;
        let result_packed: &[u32] = bytemuck::cast_slice(&mapped);

        let mut output = data;
        for (i, px) in result_packed.iter().enumerate().take(pixel_count) {
            let base = i * 4;
            output[base] = (*px & 0xff) as u8;
            output[base + 1] = ((*px >> 8) & 0xff) as u8;
            output[base + 2] = ((*px >> 16) & 0xff) as u8;
            output[base + 3] = ((*px >> 24) & 0xff) as u8;
        }

        drop(mapped);
        staging_buffer.unmap();

        Ok(output)
    }
}
