import importlib
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def api(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    module = importlib.import_module("app")
    connection = MagicMock()
    cursor = connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    monkeypatch.setattr(module, "get_connection", lambda: connection)
    return module, module.app.test_client(), cursor


def test_optimize_reads_database_minutes_and_returns_api_hours(api):
    _, client, cursor = api
    cursor.fetchall.side_effect = [
        [(1, 4, Decimal("6.00"), 2, "Book A"), (2, 5, Decimal("10.00"), 1, "Book B")],
        [(7, 10, 4, 1, "Printer"), (8, 9, 3, 1, "Cutter")],
        [(4, 7, 1), (4, 8, 1), (5, 7, 2), (5, 8, 1)],
    ]
    response = client.post("/api/optimize", json={})
    assert response.status_code == 200
    assert response.json == {
        "status": "optimal",
        "totalProfit": 46,
        "items": [
            {"orderId": 1, "bookName": "Book A", "quantity": 6, "profit": 36},
            {"orderId": 2, "bookName": "Book B", "quantity": 1, "profit": 10},
        ],
        "machines": [
            {
                "machineId": 7, "machineName": "Printer", "used": 9 / 60,
                "available": 10 / 60, "remaining": 1 / 60, "printingTime": 8 / 60,
                "maintenanceCount": 1, "maintenanceTime": 1 / 60,
                "effectivePrintingTime": 8 / 60, "utilizationPercent": 90,
            },
            {
                "machineId": 8, "machineName": "Cutter", "used": 9 / 60,
                "available": 9 / 60, "remaining": 0, "printingTime": 7 / 60,
                "maintenanceCount": 2, "maintenanceTime": 2 / 60,
                "effectivePrintingTime": 7 / 60, "utilizationPercent": 100,
            },
        ],
    }


@pytest.mark.parametrize(
    ("total", "work", "times", "http_status", "status"),
    [
        (6, 4, [(4, 7, 3)], 200, "infeasible"),
        (6, 4, [], 400, "invalid_input"),
        (6, 0, [(4, 7, 1)], 400, "invalid_input"),
        (6, 4, [(4, 7, 0)], 422, "unbounded"),
    ],
)
def test_optimize_errors_use_existing_message_format(api, total, work, times, http_status, status):
    _, client, cursor = api
    cursor.fetchall.side_effect = [[(1, 4, 6, 2, "Book A")], [(7, total, work, 1, "Printer")], times]
    response = client.post("/api/optimize", json={})
    assert response.status_code == http_status
    assert response.json["status"] == status
    assert set(response.json) == {"status", "message"}


def test_outside_data_is_rejected_for_optimize(api):
    _, client, cursor = api
    response = client.post("/api/optimize", json={"orders": []})
    assert response.status_code == 400
    cursor.execute.assert_not_called()


def test_machine_parameters_are_stored_in_minutes_and_optional_on_update(api):
    _, client, cursor = api
    body = {"name": "Printer", "availableTime": 12, "continuousPrintingTime": 4, "maintenanceTime": 1}
    cursor.fetchone.return_value = (7, "Printer", 720, 240, 60)
    created = client.post("/api/machines", json=body)
    assert created.status_code == 201
    assert created.json == {"id": 7, **body}
    assert cursor.execute.call_args.args[1] == ("Printer", 720, 240, 60)

    updated = client.put("/api/machines/7", json={"name": "Printer", "availableTime": 12})
    assert updated.status_code == 200
    assert updated.json == created.json
    assert cursor.execute.call_args.args[1] == ("Printer", 720, None, None, 7)


def test_processing_time_round_trip_in_api_hours(api):
    _, client, cursor = api
    cursor.fetchone.side_effect = [(1,), (1,), (Decimal("9.0000"),)]
    cursor.fetchall.return_value = [(4, 7, Decimal("9.0000"))]
    body = {"bookId": 4, "machineId": 7, "time": 0.15}
    response = client.put("/api/processing-times", json=body)
    assert response.status_code == 200
    assert response.json == body
    assert cursor.execute.call_args.args[1] == (4, 7, Decimal("9.00"))
    assert client.get("/api/processing-times").json == [body]
