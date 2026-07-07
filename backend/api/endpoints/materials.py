from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db


router = APIRouter()


@router.get("/", response_model=List[schemas.MaterialOut])
def get_materials(db: Session = Depends(get_db)):
    return db.query(models.Material).all()


@router.post("/", response_model=schemas.MaterialOut)
def create_material(material: schemas.MaterialBase, db: Session = Depends(get_db)):
    db_material = models.Material(
        sku=material.sku,
        description=material.description,
        quantity=material.quantity,
        status=material.status,
        current_location=material.current_location,
        vendor_name=material.vendor_name,
        promised_delivery_date=material.promised_delivery_date,
        activity_id=material.activity_id
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.get("/{material_id}", response_model=schemas.MaterialOut)
def get_material(material_id: int, db: Session = Depends(get_db)):
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")
    return mat