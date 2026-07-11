from datetime import datetime

from pydantic import BaseModel, Field


class UserFilterDataIn(BaseModel):
    brightness: float = Field(0, ge=-100, le=100)
    vibrance: float = Field(0, ge=-100, le=100)
    highlights_shadows: float = Field(0, ge=-100, le=100)
    temperature: float = Field(0, ge=-100, le=100)
    tint: float = Field(0, ge=-100, le=100)
    duotone: float = Field(0, ge=0, le=100)
    duotone_dark: str = "#000000"
    duotone_light: str = "#ffffff"


class UserFilterDataOut(UserFilterDataIn):
    id: int
    image_id: int

    class Config:
        from_attributes = True


class FilterDataHistoryItem(BaseModel):
    id: int
    image_id: int
    filename: str | None = None
    brightness: float
    vibrance: float
    highlights_shadows: float
    temperature: float
    tint: float
    duotone: float
    duotone_dark: str
    duotone_light: str
    updated_at: datetime | None = None


class ImageHistoryItem(BaseModel):
    id: int
    filename: str
    width: int
    height: int
    file_size: int
    upload_time: datetime | None = None


class ImageFeatureHistoryItem(BaseModel):
    id: int
    image_id: int
    filename: str | None = None
    brightness_mean: float
    brightness_std: float
    brightness_p5: float
    brightness_p50: float
    brightness_p95: float
    dynamic_range: float
    black_clip_ratio: float
    white_clip_ratio: float
    saturation_mean: float
    saturation_std: float
    mean_r: float
    mean_g: float
    mean_b: float
    lab_a_mean: float
    lab_b_mean: float
    dominant_colors: list[dict]
    unique_colors_ratio: float
    sharpness: float
    edge_density: float
    entropy: float
    local_contrast: float
