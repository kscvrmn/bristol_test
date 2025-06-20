import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import database, warehouse_states, movements
from datetime import datetime, timedelta, timezone
import asyncio

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    async def setup():
        await database.connect()

        await database.execute(warehouse_states.delete())
        await database.execute(movements.delete())

        await database.execute(
            warehouse_states.insert().values(
                id="WH-1:PROD-1",
                warehouse_id="WH-1",
                product_id="PROD-1",
                quantity=100
            )
        )

        departure_time = datetime.now(timezone.utc) - timedelta(hours=2)
        arrival_time = datetime.now(timezone.utc) - timedelta(hours=1)

        await database.execute(
            movements.insert().values(
                movement_id="MOV-1",
                source_warehouse="WH-1",
                destination_warehouse="WH-2",
                product_id="PROD-1",
                departure_time=departure_time,
                arrival_time=arrival_time,
                time_difference_seconds=3600.0,
                departure_quantity=50,
                arrival_quantity=50,
                quantity_difference=0
            )
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup())

    yield

    async def teardown():
        await database.disconnect()

    loop.run_until_complete(teardown())
    loop.close()


def test_read_movement():
    """Тест получения информации о перемещении"""
    response = client.get("/api/movements/MOV-1")
    assert response.status_code == 200
    data = response.json()
    assert data["movement_id"] == "MOV-1"
    assert data["source_warehouse"] == "WH-1"
    assert data["destination_warehouse"] == "WH-2"
    assert data["product_id"] == "PROD-1"
    assert data["departure_quantity"] == 50
    assert data["arrival_quantity"] == 50
    assert data["quantity_difference"] == 0
    assert data["time_difference_seconds"] == 3600.0


def test_read_movement_not_found():
    """Тест получения информации о несуществующем перемещении"""
    response = client.get("/api/movements/NON-EXISTENT")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_read_warehouse_state():
    """Тест получения информации о состоянии склада"""
    response = client.get("/api/warehouses/WH-1/products/PROD-1")
    assert response.status_code == 200
    data = response.json()
    assert data["warehouse_id"] == "WH-1"
    assert data["product_id"] == "PROD-1"
    assert data["quantity"] == 100


def test_read_warehouse_state_not_found():
    """Тест получения информации о несуществующем складе"""
    response = client.get("/api/warehouses/NON-EXISTENT/products/NON-EXISTENT")
    assert response.status_code == 200
    data = response.json()
    assert data["warehouse_id"] == "NON-EXISTENT"
    assert data["product_id"] == "NON-EXISTENT"
    assert data["quantity"] == 0