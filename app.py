#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""
import psycopg
from psycopg.rows import dict_row
from flask import Flask, render_template, jsonify, request

from db import DatabaseConfigurationError, get_connection

app = Flask(__name__)

app_data = {
    "name": "Drukāšanas plāna optimizācija",
    "description": "Grāmatu drukāšanas pasūtījumu plānošanas sistēma",
    "author": "ProjLab6k",
    "html_title": "Drukāšanas plāna optimizācija",
    "project_name": "TBDPRINTSOS",
    "keywords": "drukāšana, optimizācija, grāmatas, plānošana",
}

@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)


@app.route("/healthz")
def health():
    with get_connection() as conn:
        conn.execute("SELECT 1")
    return jsonify({"status": "ok"})


@app.route("/about")
def about():
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute("""
            SELECT o.id AS order_id, b.title AS book, b.profit_per_unit,
                   o.min_quantity, m.name AS machine, m.available_time,
                   p.processing_time
            FROM books b
            LEFT JOIN orders o ON o.book_id = b.id
            LEFT JOIN processing_times p ON p.book_id = b.id
            FULL JOIN machines m ON m.id = p.machine_id
            ORDER BY b.id, o.id, m.id
        """).fetchall()

    response = jsonify(rows)
    response.headers["Content-Disposition"] = 'inline; filename="about.json"'
    return response


@app.route("/service")
def service():
    return render_template("service.html", app_data=app_data)


@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)


@app.errorhandler(DatabaseConfigurationError)
@app.errorhandler(psycopg.OperationalError)
def handle_database_unavailable(error):
    if isinstance(error, DatabaseConfigurationError):
        app.logger.error("DATABASE_URL is missing or empty")
    else:
        app.logger.error("PostgreSQL connection unavailable")
    return jsonify({"error": "Database unavailable"}), 503


@app.route("/api/books", methods=["GET"])
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
            "title": row[1],
            "profit_per_unit": float(row[2])
        }
        for row in rows
    ]

    return jsonify(books)



@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    profit = data.get("profit_per_unit")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Invalid book title"}), 400

    try:
        from decimal import Decimal, InvalidOperation

        if isinstance(profit, bool) or profit is None:
            raise ValueError()

        profit = Decimal(str(profit))

        if not profit.is_finite():
            raise ValueError()

    except (ValueError, InvalidOperation):
        return jsonify({"error": "Invalid profit value"}), 400

    if len(title.strip()) > 255:
        return jsonify({"error": "Title is too long"}), 400

    if profit.as_tuple().exponent < -2 or abs(profit) >= 100000000:
        return jsonify({"error": "Profit exceeds allowed precision"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, profit_per_unit)
                VALUES (%s, %s)
                RETURNING id
                """,
                (title.strip(), profit)
            )
            book_id = cur.fetchone()[0]

    return jsonify({
        "id": book_id,
        "title": title.strip(),
        "profit_per_unit": float(profit)
    }), 201








if __name__ == "__main__":
    app.run()
