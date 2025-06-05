from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import MovementInfo, WarehouseState
from app.services.warehouse_services import get_movement_info_sync, get_warehouse_state_sync
from app.models.database import get_db
from sqlalchemy.orm import Session
import logging

router = APIRouter()

@router.get("/movements/{movement_id}", response_model=MovementInfo)
def read_movement(movement_id: str, db: Session = Depends(get_db)):
    """
    Получение информации о перемещении товара по ID
    """
    movement = get_movement_info_sync(db, movement_id)
    if movement is None:
        raise HTTPException(status_code=404, detail="Перемещение не найдено")
    return movement

@router.get("/warehouses/{warehouse_id}/products/{product_id}", response_model=WarehouseState)
def read_warehouse_state(warehouse_id: str, product_id: str, db: Session = Depends(get_db)):
    """
    Получение информации о текущем запасе товара на складе
    """
    return get_warehouse_state_sync(db, warehouse_id, product_id) 