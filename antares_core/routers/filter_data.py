from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Image, UserFilterData
from schemas import UserFilterDataIn, UserFilterDataOut

router = APIRouter()


@router.put("/images/{image_id}/filter-data", response_model=UserFilterDataOut)
async def upsert_filter_data(
    image_id: int,
    payload: UserFilterDataIn,
    db: AsyncSession = Depends(get_db),
):
    image = await db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    result = await db.execute(
        select(UserFilterData).where(UserFilterData.image_id == image_id)
    )
    filter_data = result.scalar_one_or_none()

    if filter_data:
        for field, value in payload.model_dump().items():
            setattr(filter_data, field, value)
    else:
        filter_data = UserFilterData(image_id=image_id, **payload.model_dump())
        db.add(filter_data)

    await db.commit()
    await db.refresh(filter_data)
    return filter_data


@router.get("/images/{image_id}/filter-data", response_model=UserFilterDataOut)
async def get_filter_data(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserFilterData).where(UserFilterData.image_id == image_id)
    )
    filter_data = result.scalar_one_or_none()
    if not filter_data:
        raise HTTPException(status_code=404, detail="Filter data not found")
    return filter_data