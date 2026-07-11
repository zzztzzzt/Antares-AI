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