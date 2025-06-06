from sqlalchemy import and_, select
import logging
import sqlite3
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.database import WarehouseState, Movement, database, warehouse_states, movements
from app.models.schemas import WarehouseState as WarehouseStateSchema
from app.models.schemas import MovementInfo
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_warehouse_state(warehouse_id: str, product_id: str) -> WarehouseStateSchema:
    """Получает текущее состояние склада для указанного товара"""
    logger.info(f"Запрос состояния склада: warehouse_id={warehouse_id}, product_id={product_id}")
    
    query = select(warehouse_states).where(
        and_(
            warehouse_states.c.warehouse_id == warehouse_id,
            warehouse_states.c.product_id == product_id
        )
    )
    
    result = await database.fetch_one(query)
    
    if result:
        logger.info(f"Найдено состояние склада: {result}")
        return WarehouseStateSchema(
            warehouse_id=result["warehouse_id"],
            product_id=result["product_id"],
            quantity=result["quantity"]
        )
    
    logger.warning(f"Склад не найден: warehouse_id={warehouse_id}, product_id={product_id}")
    if warehouse_id is None:
        raise HTTPException(status_code=404, detail="Склад не найден")
        
    return WarehouseStateSchema(
        warehouse_id=warehouse_id,
        product_id=product_id,
        quantity=0
    )


def get_warehouse_state_sync(db: Session, warehouse_id: str, product_id: str) -> WarehouseStateSchema:
    """Синхронная версия получения состояния склада для указанного товара"""
    logger.info(f"Запрос состояния склада (sync): warehouse_id={warehouse_id}, product_id={product_id}")
    
    try:
        state = db.query(WarehouseState).filter(
            WarehouseState.warehouse_id == warehouse_id,
            WarehouseState.product_id == product_id
        ).first()
        
        if state:
            logger.info(f"Найдено состояние склада: {state}")
            return WarehouseStateSchema(
                warehouse_id=state.warehouse_id,
                product_id=state.product_id,
                quantity=state.quantity
            )
        
        logger.warning(f"Склад не найден: warehouse_id={warehouse_id}, product_id={product_id}")
        
        return WarehouseStateSchema(
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=0
        )
    except Exception as e:
        logger.error(f"Ошибка при получении состояния склада: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных")


async def update_warehouse_state(warehouse_id: str, product_id: str, quantity: int):
    """Обновляет состояние склада для указанного товара"""
    record_id = f"{warehouse_id}:{product_id}"
    
    # Проверяем наличие записи
    query = select(warehouse_states).where(
        and_(
            warehouse_states.c.warehouse_id == warehouse_id,
            warehouse_states.c.product_id == product_id
        )
    )
    
    result = await database.fetch_one(query)
    
    if result:
        query = warehouse_states.update().where(
            warehouse_states.c.id == record_id
        ).values(quantity=quantity)
        await database.execute(query)
    else:
        query = warehouse_states.insert().values(
            id=record_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=quantity
        )
        await database.execute(query)


def update_warehouse_state_sync(db: Session, warehouse_id: str, product_id: str, quantity: int):
    """Синхронная версия обновления состояния склада для указанного товара"""
    record_id = f"{warehouse_id}:{product_id}"
    
    state = db.query(WarehouseState).filter(
        WarehouseState.warehouse_id == warehouse_id,
        WarehouseState.product_id == product_id
    ).first()
    
    if state:
        state.quantity = quantity
    else:
        new_state = WarehouseState(
            id=record_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(new_state)
    
    db.commit()


async def update_movement_departure(movement_id: str, warehouse_id: str, product_id: str, timestamp: datetime,
                                    quantity: int):
    query = select(movements).where(movements.c.movement_id == movement_id)
    movement = await database.fetch_one(query)

    if movement:
        values = {
            "source_warehouse": warehouse_id,
            "departure_time": timestamp,
            "departure_quantity": quantity
        }

        if movement["arrival_time"]:
            try:
                time_diff = (movement["arrival_time"] - timestamp).total_seconds()
                quantity_diff = movement["arrival_quantity"] - quantity

                values["time_difference_seconds"] = time_diff
                values["quantity_difference"] = quantity_diff
            except Exception as e:
                logger.error(f"Ошибка при расчете разницы времени: {e}")
                values["time_difference_seconds"] = 0
                values["quantity_difference"] = 0

        query = movements.update().where(
            movements.c.movement_id == movement_id
        ).values(**values)
    else:
        query = movements.insert().values(
            movement_id=movement_id,
            source_warehouse=warehouse_id,
            product_id=product_id,
            departure_time=timestamp,
            departure_quantity=quantity
        )

    await database.execute(query)


async def update_movement_arrival(movement_id: str, warehouse_id: str, product_id: str, timestamp: datetime,
                                  quantity: int):
    query = select(movements).where(movements.c.movement_id == movement_id)
    movement = await database.fetch_one(query)

    if movement:
        values = {
            "destination_warehouse": warehouse_id,
            "arrival_time": timestamp,
            "arrival_quantity": quantity
        }

        if movement["departure_time"]:
            try:
                time_diff = (timestamp - movement["departure_time"]).total_seconds()
                quantity_diff = quantity - movement["departure_quantity"]

                values["time_difference_seconds"] = time_diff
                values["quantity_difference"] = quantity_diff
            except Exception as e:
                logger.error(f"Ошибка при расчете разницы времени: {e}")
                values["time_difference_seconds"] = 0
                values["quantity_difference"] = 0

        query = movements.update().where(
            movements.c.movement_id == movement_id
        ).values(**values)
    else:
        query = movements.insert().values(
            movement_id=movement_id,
            destination_warehouse=warehouse_id,
            product_id=product_id,
            arrival_time=timestamp,
            arrival_quantity=quantity
        )

    await database.execute(query)


async def get_movement_info(movement_id: str) -> MovementInfo:
    """Получает информацию о перемещении по его ID"""
    logger.info(f"Запрос информации о перемещении: movement_id={movement_id}")
    
    query = select(movements).where(movements.c.movement_id == movement_id)
    result = await database.fetch_one(query)
    
    if not result:
        logger.warning(f"Перемещение не найдено: movement_id={movement_id}")
        return None
    
    logger.info(f"Найдено перемещение: {result}")
    
    return MovementInfo(
        movement_id=result["movement_id"],
        source_warehouse=result["source_warehouse"],
        destination_warehouse=result["destination_warehouse"],
        product_id=result["product_id"],
        departure_time=result["departure_time"],
        arrival_time=result["arrival_time"],
        time_difference_seconds=float(result["time_difference_seconds"]) if result["time_difference_seconds"] else None,
        departure_quantity=result["departure_quantity"],
        arrival_quantity=result["arrival_quantity"],
        quantity_difference=result["quantity_difference"]
    )


def get_movement_info_sync(db: Session, movement_id: str) -> MovementInfo:
    """Синхронная версия получения информации о перемещении по его ID"""
    try:
        logger.info(f"Запрос информации о перемещении (sync): movement_id={movement_id}")
        
        movement = db.query(Movement).filter(Movement.movement_id == movement_id).first()
        
        if not movement:
            logger.warning(f"Перемещение не найдено: movement_id={movement_id}")
            return None
        
        logger.info(f"Найдено перемещение: {movement}")
        
        return MovementInfo(
            movement_id=movement.movement_id,
            source_warehouse=movement.source_warehouse,
            destination_warehouse=movement.destination_warehouse,
            product_id=movement.product_id,
            departure_time=movement.departure_time,
            arrival_time=movement.arrival_time,
            time_difference_seconds=float(movement.time_difference_seconds) if movement.time_difference_seconds else None,
            departure_quantity=movement.departure_quantity,
            arrival_quantity=movement.arrival_quantity,
            quantity_difference=movement.quantity_difference
        )
    except Exception as e:
        logger.error(f"Ошибка при получении информации о перемещении: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных")