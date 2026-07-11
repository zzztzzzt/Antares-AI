from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from database import Base


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    upload_time = Column(DateTime, default=datetime.utcnow)
    
    features = relationship("ImageFeature", back_populates="image", uselist=False)


class ImageFeature(Base):
    __tablename__ = "image_features"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True, nullable=False)
    
    # Exposure Features
    brightness_mean = Column(Float, nullable=False)
    brightness_std = Column(Float, nullable=False)
    brightness_p5 = Column(Float, nullable=False)
    brightness_p50 = Column(Float, nullable=False)
    brightness_p95 = Column(Float, nullable=False)
    dynamic_range = Column(Float, nullable=False)
    black_clip_ratio = Column(Float, nullable=False)
    white_clip_ratio = Column(Float, nullable=False)
    
    # Color Features
    saturation_mean = Column(Float, nullable=False)
    saturation_std = Column(Float, nullable=False)
    mean_r = Column(Float, nullable=False)
    mean_g = Column(Float, nullable=False)
    mean_b = Column(Float, nullable=False)
    lab_a_mean = Column(Float, nullable=False)
    lab_b_mean = Column(Float, nullable=False)
    dominant_colors = Column(JSON, nullable=False) # [{"rgb": [r,g,b], "percentage": 0.xx}, ...]
    unique_colors_ratio = Column(Float, nullable=False) # Color complexity ( 0.0-1.0 )
    
    # Detail Features
    sharpness = Column(Float, nullable=False)
    edge_density = Column(Float, nullable=False)
    entropy = Column(Float, nullable=False)
    local_contrast = Column(Float, nullable=False)
    
    image = relationship("Image", back_populates="features")

class UserFilterData(Base):
    __tablename__ = "user_filter_data"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, unique=True)

    brightness = Column(Float, nullable=False, default=0)
    vibrance = Column(Float, nullable=False, default=0)
    highlights_shadows = Column(Float, nullable=False, default=0)
    temperature = Column(Float, nullable=False, default=0)
    tint = Column(Float, nullable=False, default=0)
    duotone = Column(Float, nullable=False, default=0)
    duotone_dark = Column(String(7), nullable=False, default="#000000")
    duotone_light = Column(String(7), nullable=False, default="#ffffff")

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    image = relationship("Image", backref="filter_data")
