from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Image, ImageFeature, UserFilterData
from schemas import ImageFeatureHistoryItem, ImageHistoryItem, FilterDataHistoryItem

router = APIRouter(prefix="/training-data-history", tags=["training-data-history"])


@router.get("", response_model=list[FilterDataHistoryItem])
async def list_training_data_history(
    image_id: int | None = None,
    id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(
            UserFilterData.id,
            UserFilterData.image_id,
            Image.filename,
            UserFilterData.brightness,
            UserFilterData.vibrance,
            UserFilterData.highlights_shadows,
            UserFilterData.temperature,
            UserFilterData.tint,
            UserFilterData.duotone,
            UserFilterData.duotone_dark,
            UserFilterData.duotone_light,
            UserFilterData.updated_at,
        )
        .join(Image, Image.id == UserFilterData.image_id)
        .order_by(UserFilterData.updated_at.desc().nullslast(), UserFilterData.id.desc())
    )

    if image_id is not None:
        stmt = stmt.where(UserFilterData.image_id == image_id)
    if id is not None:
        stmt = stmt.where(UserFilterData.id == id)

    result = await db.execute(stmt)
    rows = result.all()
    return [
        FilterDataHistoryItem(
            id=row.id,
            image_id=row.image_id,
            filename=row.filename,
            brightness=row.brightness,
            vibrance=row.vibrance,
            highlights_shadows=row.highlights_shadows,
            temperature=row.temperature,
            tint=row.tint,
            duotone=row.duotone,
            duotone_dark=row.duotone_dark,
            duotone_light=row.duotone_light,
            updated_at=row.updated_at.isoformat() if row.updated_at else None,
        )
        for row in rows
    ]


@router.get("/images", response_model=list[ImageHistoryItem])
async def list_images(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Image).order_by(Image.upload_time.desc().nullslast(), Image.id.desc())
    )
    rows = result.scalars().all()
    return [
        ImageHistoryItem(
            id=row.id,
            filename=row.filename,
            width=row.width,
            height=row.height,
            file_size=row.file_size,
            upload_time=row.upload_time,
        )
        for row in rows
    ]


@router.get("/image-features", response_model=list[ImageFeatureHistoryItem])
async def list_image_features(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ImageFeature, Image.filename)
        .join(Image, Image.id == ImageFeature.image_id)
        .order_by(ImageFeature.id.desc())
    )
    rows = result.all()
    return [
        ImageFeatureHistoryItem(
            id=row[0].id,
            image_id=row[0].image_id,
            filename=row[1],
            brightness_mean=row[0].brightness_mean,
            brightness_std=row[0].brightness_std,
            brightness_p5=row[0].brightness_p5,
            brightness_p50=row[0].brightness_p50,
            brightness_p95=row[0].brightness_p95,
            dynamic_range=row[0].dynamic_range,
            black_clip_ratio=row[0].black_clip_ratio,
            white_clip_ratio=row[0].white_clip_ratio,
            saturation_mean=row[0].saturation_mean,
            saturation_std=row[0].saturation_std,
            mean_r=row[0].mean_r,
            mean_g=row[0].mean_g,
            mean_b=row[0].mean_b,
            lab_a_mean=row[0].lab_a_mean,
            lab_b_mean=row[0].lab_b_mean,
            dominant_colors=row[0].dominant_colors,
            unique_colors_ratio=row[0].unique_colors_ratio,
            sharpness=row[0].sharpness,
            edge_density=row[0].edge_density,
            entropy=row[0].entropy,
            local_contrast=row[0].local_contrast,
        )
        for row in rows
    ]


@router.delete("/user-filter-data/{image_id}")
async def delete_training_data(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    image = await db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    feature_result = await db.execute(
        select(ImageFeature).where(ImageFeature.image_id == image_id)
    )
    feature = feature_result.scalar_one_or_none()

    filter_result = await db.execute(
        select(UserFilterData).where(UserFilterData.image_id == image_id)
    )
    filter_data = filter_result.scalar_one_or_none()

    if filter_data:
        await db.delete(filter_data)
    if feature:
        await db.delete(feature)
    await db.delete(image)
    await db.commit()
    return {
        "status": "success",
        "deleted_image_id": image_id,
        "deleted_related_rows": {
            "image": True,
            "image_feature": feature is not None,
            "user_filter_data": filter_data is not None,
        },
    }
