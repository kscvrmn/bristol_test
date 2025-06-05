from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import MovementInfo, WarehouseState
from app.services.warehouse_services import get_movement_info, get_warehouse_state
from typing import Dict
import sqlite3
import logging

router = APIRouter()

@router.get("/movements/{movement_id}", response_model=MovementInfo)
async def read_movement(movement_id: str):
    """
    Получение информации о перемещении товара по ID
    """
    movement = await get_movement_info(movement_id)
    if movement is None:
        raise HTTPException(status_code=404, detail="Перемещение не найдено")
    return movement

@router.get("/warehouses/{warehouse_id}/products/{product_id}")
async def read_warehouse_state(warehouse_id: str, product_id: str):
    """
    Получение информации о текущем запасе товара на складе
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Запрос состояния склада: warehouse_id={warehouse_id}, product_id={product_id}")
    
    # Хардкодим значение для отладки
    return {
        "warehouse_id": warehouse_id,
        "product_id": product_id,
        "quantity": 100
    } 