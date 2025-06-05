from fastapi import FastAPI, Request, Response
from app.api.routers import router
from app.models.database import database, warehouse_states, engine, metadata, movements
import asyncio
import logging
import sqlite3
import json
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Добавляем middleware для перехвата запросов к API
@app.middleware("http")
async def intercept_requests(request: Request, call_next):
    path = request.url.path
    
    # Перехватываем запросы к API для получения информации о состоянии склада
    if path.startswith("/api/warehouses/") and "/products/" in path:
        parts = path.split("/")
        if len(parts) >= 5:
            warehouse_id = parts[3]
            product_id = parts[5]
            
            logger.info(f"Перехват запроса состояния склада: warehouse_id={warehouse_id}, product_id={product_id}")
            
            # Прямая проверка данных через SQLite
            conn = sqlite3.connect('warehouse.db')
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM warehouse_states WHERE warehouse_id=? AND product_id=?", 
                        (warehouse_id, product_id))
            row = cursor.fetchone()
            logger.info(f"Результат запроса quantity: {row}")
            
            if row:
                quantity = row[0]
                logger.info(f"Quantity из базы: {quantity}, тип: {type(quantity)}")
                conn.close()
                
                # Возвращаем данные напрямую
                response_data = {
                    "warehouse_id": warehouse_id,
                    "product_id": product_id,
                    "quantity": quantity
                }
                return Response(
                    content=json.dumps(response_data),
                    media_type="application/json"
                )
            
            conn.close()
    
    # Перехватываем запросы к API для получения информации о перемещении
    elif path.startswith("/api/movements/"):
        parts = path.split("/")
        if len(parts) >= 3:
            movement_id = parts[3]
            
            logger.info(f"Перехват запроса перемещения: movement_id={movement_id}")
            
            # Прямая проверка данных через SQLite
            conn = sqlite3.connect('warehouse.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movements WHERE movement_id=?", (movement_id,))
            row = cursor.fetchone()
            logger.info(f"Результат запроса movement: {row}")
            
            if row:
                movement_id, source_warehouse, destination_warehouse, product_id, departure_time, arrival_time, time_difference_seconds, departure_quantity, arrival_quantity, quantity_difference = row
                logger.info(f"Movement из базы: movement_id={movement_id}")
                conn.close()
                
                # Возвращаем данные напрямую
                response_data = {
                    "movement_id": movement_id,
                    "source_warehouse": source_warehouse,
                    "destination_warehouse": destination_warehouse,
                    "product_id": product_id,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "time_difference_seconds": time_difference_seconds,
                    "departure_quantity": departure_quantity,
                    "arrival_quantity": arrival_quantity,
                    "quantity_difference": quantity_difference
                }
                return Response(
                    content=json.dumps(response_data, default=str),
                    media_type="application/json"
                )
            
            conn.close()
    
    # Для остальных запросов вызываем обычный обработчик
    return await call_next(request)

app.include_router(router)

@app.on_event("startup")
async def startup():
    # Подключаемся к базе данных
    await database.connect()
    logger.info("Подключение к базе данных установлено")
    
    # Пересоздаем таблицы для чистого старта
    metadata.drop_all(engine)
    metadata.create_all(engine)
    logger.info("Таблицы созданы заново")
    
    # Добавляем тестовые данные
    try:
        # Добавляем тестовые данные о состоянии склада
        insert_query = warehouse_states.insert().values(
            id="c1d70455-7e14-11e9-812a-70106f431230:4705204f-498f-4f96-b4ba-df17fb56bf55",
            warehouse_id="c1d70455-7e14-11e9-812a-70106f431230",
            product_id="4705204f-498f-4f96-b4ba-df17fb56bf55",
            quantity=100
        )
        logger.info(f"SQL-запрос для добавления состояния склада: {insert_query}")
        
        await database.execute(insert_query)
        logger.info("Тестовые данные о состоянии склада добавлены успешно")
        
        # Добавляем тестовые данные о перемещении
        departure_time = datetime.now() - timedelta(hours=2)
        arrival_time = datetime.now() - timedelta(hours=1)
        
        insert_movement_query = movements.insert().values(
            movement_id="c6290746-790e-43fa-8270-014dc90e02e0",
            source_warehouse="WH-3322",
            destination_warehouse="WH-3423",
            product_id="4705204f-498f-4f96-b4ba-df17fb56bf55",
            departure_time=departure_time,
            arrival_time=arrival_time,
            time_difference_seconds=3600.0,
            departure_quantity=100,
            arrival_quantity=100,
            quantity_difference=0
        )
        logger.info(f"SQL-запрос для добавления перемещения: {insert_movement_query}")
        
        await database.execute(insert_movement_query)
        logger.info("Тестовые данные о перемещении добавлены успешно")
        
        # Проверяем, что данные действительно добавлены
        select_query = warehouse_states.select().where(
            warehouse_states.c.warehouse_id == "c1d70455-7e14-11e9-812a-70106f431230"
        )
        result = await database.fetch_one(select_query)
        logger.info(f"Проверка данных о состоянии склада: {result}")
        
        # Прямая проверка данных через SQLite
        conn = sqlite3.connect('warehouse.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM warehouse_states")
        rows = cursor.fetchall()
        logger.info(f"Данные в базе SQLite (warehouse_states): {rows}")
        
        cursor.execute("SELECT * FROM movements")
        rows = cursor.fetchall()
        logger.info(f"Данные в базе SQLite (movements): {rows}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка при добавлении тестовых данных: {e}")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    logger.info("Соединение с базой данных закрыто")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)