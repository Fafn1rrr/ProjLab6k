import math
from decimal import Decimal, ROUND_HALF_UP

import psycopg
from flask import Flask, jsonify, request, send_from_directory

from db import DatabaseConfigurationError, get_connection
from optimizer import optimize
from optimization_service import load_optimizer_input, format_optimization_result

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "planner.html")


@app.get("/api/health")
def health():
    with get_connection() as conn:
        conn.execute("SELECT 1")

    return jsonify({"status": "ok"})


@app.get("/api/books")
def get_books():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, profit_per_unit
                FROM books
                ORDER BY id
            """)
            rows = cur.fetchall()

    books = [
        {
            "id": row[0],
            "name": row[1],
            "profitPerUnit": float(row[2])
        }
        for row in rows
    ]

    return jsonify(books)


@app.post("/api/books")
def add_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    profit = data.get("profitPerUnit")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Book name must have at least 2 characters."
        }), 400

    try:
        profit = float(profit)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Profit per unit must be a number."
        }), 400

    if profit < 0:
        return jsonify({
            "message": "Profit per unit cannot be negative."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, profit_per_unit)
                VALUES (%s, %s)
                RETURNING id
                """,
                (name.strip(), profit)
            )
            book_id = cur.fetchone()[0]

    return jsonify({
        "id": book_id,
        "name": name.strip(),
        "profitPerUnit": profit
    }), 201


@app.put("/api/books/<int:book_id>")
def update_book(book_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    profit = data.get("profitPerUnit")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Book name must have at least 2 characters."
        }), 400

    try:
        profit = float(profit)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Profit per unit must be a number."
        }), 400

    if profit < 0:
        return jsonify({
            "message": "Profit per unit cannot be negative."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE books
                SET title = %s,
                    profit_per_unit = %s
                WHERE id = %s
                RETURNING id
                """,
                (name.strip(), profit, book_id)
            )

            updated = cur.fetchone()

    if updated is None:
        return jsonify({"message": "Book not found."}), 404

    return jsonify({
        "id": book_id,
        "name": name.strip(),
        "profitPerUnit": profit
    })


@app.get("/api/orders")
def get_orders():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, book_id, min_quantity
                FROM orders
                ORDER BY id
            """)
            rows = cur.fetchall()

    orders = [
        {
            "id": row[0],
            "bookId": row[1],
            "minQuantity": row[2]
        }
        for row in rows
    ]

    return jsonify(orders)


# Upper bound of the PostgreSQL INTEGER column orders.min_quantity.
MAX_MIN_QUANTITY = 2147483647


@app.post("/api/orders")
def add_order():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    book_id = data.get("bookId")
    min_quantity = data.get("minQuantity")

    # bool is a subclass of int in Python, so True/False must be rejected explicitly.
    if not isinstance(book_id, int) or isinstance(book_id, bool):
        return jsonify({"message": "Book ID must be an integer."}), 400

    if not isinstance(min_quantity, int) or isinstance(min_quantity, bool):
        return jsonify({
            "message": "Minimum quantity must be an integer."
        }), 400

    if min_quantity <= 0:
        return jsonify({
            "message": "Minimum quantity must be greater than 0."
        }), 400

    if min_quantity > MAX_MIN_QUANTITY:
        return jsonify({"message": "Minimum quantity is too large."}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM books WHERE id = %s", (book_id,))
            if cur.fetchone() is None:
                return jsonify({"message": "Book not found."}), 404

            cur.execute(
                """
                INSERT INTO orders (book_id, min_quantity)
                VALUES (%s, %s)
                RETURNING id
                """,
                (book_id, min_quantity)
            )
            order_id = cur.fetchone()[0]

    return jsonify({
        "id": order_id,
        "bookId": book_id,
        "minQuantity": min_quantity
    }), 201


MINUTES_PER_HOUR = 60


def hours_to_minutes(hours: float) -> Decimal:
    """Convert API hours to the database unit."""
    return Decimal(str(hours)) * MINUTES_PER_HOUR


def minutes_to_hours(minutes: Decimal | float) -> float:
    """Convert database or optimizer minutes to API hours."""
    return float(minutes / MINUTES_PER_HOUR)


def machine_times(data: dict) -> tuple[Decimal, Decimal | None, Decimal | None]:
    """Read availability and any provided maintenance settings in API hours."""
    times = []
    for field, label, optional, zero_allowed, limit in (
        ("availableTime", "Available time", False, False, 10**12),
        ("continuousPrintingTime", "Continuous printing time", True, False, 10**10),
        ("maintenanceTime", "Maintenance time", True, True, 10**10),
    ):
        if optional and field not in data:
            times.append(None)
            continue
        raw = data.get(field)
        try:
            value = float(raw)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"{label} must be a finite number.") from None
        if isinstance(raw, bool) or not math.isfinite(value):
            raise ValueError(f"{label} must be a finite number.")
        if value < 0 or (value == 0 and not zero_allowed):
            minimum = "0 or greater" if zero_allowed else "greater than 0"
            raise ValueError(f"{label} must be {minimum}.")
        minutes = hours_to_minutes(value)
        if minutes >= limit - Decimal("0.005"):
            raise ValueError(f"{label} is too large to store.")
        minutes = minutes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if minutes == 0 and not zero_allowed:
            raise ValueError(f"{label} is too small to store.")
        times.append(minutes)
    return tuple(times)


def machine_response(
    machine_id: int, name: str, available: Decimal, continuous: Decimal, maintenance: Decimal
) -> dict:
    """Serialize stored machine times in API hours."""
    return {
        "id": machine_id,
        "name": name,
        "availableTime": minutes_to_hours(available),
        "continuousPrintingTime": minutes_to_hours(continuous),
        "maintenanceTime": minutes_to_hours(maintenance),
    }


@app.get("/api/machines")
def get_machines():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, available_time, continuous_printing_time, maintenance_time
                FROM machines
                ORDER BY id
            """)
            rows = cur.fetchall()

    return jsonify([machine_response(*row) for row in rows])


@app.post("/api/machines")
def add_machine():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Machine name must have at least 2 characters."
        }), 400

    try:
        available, continuous, maintenance = machine_times(data)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO machines
                    (name, available_time, continuous_printing_time, maintenance_time)
                VALUES (%s, %s, COALESCE(%s, 0), COALESCE(%s, 0))
                RETURNING id, name, available_time, continuous_printing_time, maintenance_time
                """,
                (name.strip(), available, continuous, maintenance)
            )
            row = cur.fetchone()

    return jsonify(machine_response(*row)), 201


@app.put("/api/machines/<int:machine_id>")
def update_machine(machine_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Machine name must have at least 2 characters."
        }), 400

    try:
        available, continuous, maintenance = machine_times(data)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE machines
                SET name = %s,
                    available_time = %s,
                    continuous_printing_time = COALESCE(%s, continuous_printing_time),
                    maintenance_time = COALESCE(%s, maintenance_time)
                WHERE id = %s
                RETURNING id, name, available_time, continuous_printing_time, maintenance_time
                """,
                (name.strip(), available, continuous, maintenance, machine_id)
            )
            updated = cur.fetchone()

    if updated is None:
        return jsonify({"message": "Machine not found."}), 404

    return jsonify(machine_response(*updated))


def is_integer_id(value):
    # bool is a subclass of int in Python, so True/False must be rejected explicitly.
    return isinstance(value, int) and not isinstance(value, bool)


@app.get("/api/processing-times")
def get_processing_times():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT book_id, machine_id, processing_time
                FROM processing_times
                ORDER BY book_id, machine_id
            """)
            rows = cur.fetchall()

    processing_times = [
        {
            "bookId": row[0],
            "machineId": row[1],
            "time": minutes_to_hours(row[2])
        }
        for row in rows
    ]

    return jsonify(processing_times)


@app.put("/api/processing-times")
def upsert_processing_time():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    book_id = data.get("bookId")
    machine_id = data.get("machineId")
    time = data.get("time")

    if not is_integer_id(book_id):
        return jsonify({"message": "Book ID must be an integer."}), 400

    if not is_integer_id(machine_id):
        return jsonify({"message": "Machine ID must be an integer."}), 400

    if not isinstance(time, (int, float)) or isinstance(time, bool):
        return jsonify({"message": "Processing time must be a number."}), 400

    try:
        time = float(time)
    except OverflowError:
        return jsonify({"message": "Processing time is too large."}), 400

    # Python's JSON parser accepts NaN/Infinity; PostgreSQL NUMERIC would store NaN.
    if not math.isfinite(time):
        return jsonify({"message": "Processing time must be a number."}), 400

    if time < 0:
        return jsonify({
            "message": "Processing time must be 0 or greater."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM books WHERE id = %s", (book_id,))
            if cur.fetchone() is None:
                return jsonify({"message": "Book not found."}), 404

            cur.execute("SELECT 1 FROM machines WHERE id = %s", (machine_id,))
            if cur.fetchone() is None:
                return jsonify({"message": "Machine not found."}), 404

            try:
                cur.execute(
                    """
                    INSERT INTO processing_times
                        (book_id, machine_id, processing_time)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (book_id, machine_id)
                    DO UPDATE SET processing_time = EXCLUDED.processing_time
                    RETURNING processing_time
                    """,
                    (book_id, machine_id, hours_to_minutes(time))
                )
            except psycopg.errors.NumericValueOutOfRange:
                conn.rollback()
                return jsonify({
                    "message": "Processing time is too large."
                }), 400

            # Return the value as stored (the column rounds to 4 decimals).
            stored_time = cur.fetchone()[0]

    return jsonify({
        "bookId": book_id,
        "machineId": machine_id,
        "time": minutes_to_hours(stored_time)
    })


@app.post("/api/optimize")
def optimize_plan():
    """Run the optimizer using a consistent database snapshot."""
    if request.get_data() and request.get_json(silent=True) != {}:
        return jsonify({"message": "Expected an empty JSON object."}), 400

    with get_connection() as conn:
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        optimizer_data = load_optimizer_input(conn)

    plan = optimize(
        optimizer_data["orders"],
        optimizer_data["machines"],
        optimizer_data["processing_times"],
    )
    response, status_code = format_optimization_result(plan, optimizer_data)
    return jsonify(response), status_code


@app.errorhandler(DatabaseConfigurationError)
def handle_database_configuration_error(error):
    return jsonify({"message": str(error)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)