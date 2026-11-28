"""Database adapter and HTTP response mapping for the printing optimizer.

All machine and processing times are in MINUTES inside this module.
The Flask API returns machine times in HOURS to match existing frontend.
"""


def load_optimizer_input(connection):
    """Read one consistent DB snapshot and prepare PuLP-compatible data.

    The caller must establish the desired transaction isolation before calling.
    Keeping the connection in app.py makes the transaction explicit and lets
    this module be tested without Flask or a running PostgreSQL server.
    """
    with connection.cursor() as cur:
        cur.execute("""
            SELECT o.id, o.book_id, b.profit_per_unit, o.min_quantity, b.title
            FROM orders AS o
            JOIN books AS b ON b.id = o.book_id
            ORDER BY o.id
        """)
        order_rows = cur.fetchall()

        cur.execute("""
            SELECT id, available_time, continuous_printing_time, maintenance_time, name
            FROM machines
            ORDER BY id
        """)
        machine_rows = cur.fetchall()

        cur.execute("""
            SELECT p.book_id, p.machine_id, p.processing_time
            FROM processing_times AS p
            WHERE EXISTS (SELECT 1 FROM orders AS o WHERE o.book_id = p.book_id)
        """)
        processing_rows = cur.fetchall()

    return {
        "orders": [
            {
                "id": order_id,
                "book_id": book_id,
                "profit_per_unit": profit,
                "min_quantity": minimum,
            }
            for order_id, book_id, profit, minimum, _ in order_rows
        ],
        "machines": [
            {
                "id": machine_id,
                "available_time": available,
                "continuous_printing_time": continuous,
                "maintenance_time": maintenance,
            }
            for machine_id, available, continuous, maintenance, _ in machine_rows
        ],
        "processing_times": [
            {"book_id": book_id, "machine_id": machine_id, "time": time}
            for book_id, machine_id, time in processing_rows
        ],
        "order_names": {row[0]: row[4] for row in order_rows},
        "machine_names": {row[0]: row[4] for row in machine_rows},
    }


def _minutes_to_hours(minutes):
    """Convert optimizer minute values into frontend hour values."""
    return float(minutes / 60)


def format_optimization_result(plan, optimizer_data):
    """Return (JSON-compatible response body, HTTP status code).

    The optimizer's own output contract is unchanged. This mapping matches
    the frontend's camelCase JSON fields in API_CONTRACT.md.
    """
    if plan["status"] != "optimal":
        status_code = {
            "infeasible": 200,
            "invalid_input": 400,
            "unbounded": 422,
            "solver_error": 503,
            "not_solved": 503,
        }[plan["status"]]
        return plan, status_code

    book_names = optimizer_data["order_names"]
    machine_names = optimizer_data["machine_names"]

    return {
        "status": plan["status"],
        "totalProfit": plan["total_profit"],
        "items": [
            {
                "orderId": item["order_id"],
                "bookName": book_names[item["order_id"]],
                "quantity": item["quantity"],
                "profit": item["profit"],
            }
            for item in plan["items"]
        ],
        "machines": [
            {
                "machineId": machine["machine_id"],
                "machineName": machine_names[machine["machine_id"]],
                "used": _minutes_to_hours(machine["used_time"]),
                "available": _minutes_to_hours(machine["available_time"]),
                "remaining": _minutes_to_hours(machine["remaining_time"]),
                "printingTime": _minutes_to_hours(machine["printing_time"]),
                "maintenanceCount": machine["maintenance_count"],
                "maintenanceTime": _minutes_to_hours(machine["maintenance_time"]),
                "effectivePrintingTime": _minutes_to_hours(machine["effective_printing_time"]),
                "utilizationPercent": machine["utilization_percent"],
            }
            for machine in plan["machines"]
        ],
    }, 200
