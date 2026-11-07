"""Visas lietotnes lapas un formas. Katra funkcija = viena adrese (URL)."""
import math

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from .models import Book, Machine, MachineLoad, Order, Plan, PlanLine, ProcessingTime, db
from .optimizer import OptimizationError, optimize

bp = Blueprint("pages", __name__)


def read_number(field, label, minimum=0, integer=False, required=True):
    """Nolasa skaitli no formas. Pieņem arī komatu (4,50). Kļūdas gadījumā — ValueError."""
    raw = request.form.get(field, "").strip().replace(",", ".")
    if raw == "":
        if required:
            raise ValueError(f"Aizpildiet lauku «{label}».")
        return None
    try:
        value = int(raw) if integer else float(raw)
    except ValueError:
        raise ValueError(f"Laukā «{label}» jābūt {'veselam ' if integer else ''}skaitlim.") from None
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f"Laukā «{label}» jābūt skaitlim, kas nav mazāks par {minimum}.")
    return value


@bp.get("/")
def index():
    return render_template("index.html")


# ---------- 1. Grāmatas ----------

@bp.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        try:
            if not title:
                raise ValueError("Aizpildiet lauku «Nosaukums».")
            if Book.query.filter_by(title=title).first():
                raise ValueError(f"Grāmata «{title}» jau eksistē.")
            profit = read_number("profit_per_unit", "Peļņa par vienību")
        except ValueError as err:
            flash(str(err), "danger")
        else:
            db.session.add(Book(title=title, profit_per_unit=profit))
            db.session.commit()
            flash(f"Grāmata «{title}» pievienota.", "success")
        return redirect(url_for("pages.books"))
    return render_template("books.html", books=Book.query.order_by(Book.title).all())


# ---------- 2. Pasūtījumi ----------

@bp.route("/orders", methods=["GET", "POST"])
def orders():
    if request.method == "POST":
        book = db.session.get(Book, request.form.get("book_id", type=int) or 0)
        try:
            if book is None:
                raise ValueError("Izvēlieties grāmatu.")
            min_qty = read_number("min_quantity", "Minimums", minimum=1, integer=True)
            max_qty = read_number("max_quantity", "Maksimums", minimum=1, integer=True, required=False)
            if max_qty is not None and max_qty < min_qty:
                raise ValueError("Maksimums nedrīkst būt mazāks par minimumu.")
        except ValueError as err:
            flash(str(err), "danger")
        else:
            db.session.add(Order(book=book, min_quantity=min_qty, max_quantity=max_qty))
            db.session.commit()
            flash(f"Pasūtījums grāmatai «{book.title}» pievienots.", "success")
        return redirect(url_for("pages.orders"))
    return render_template(
        "orders.html",
        orders=Order.query.order_by(Order.id).all(),
        books=Book.query.order_by(Book.title).all(),
    )


# ---------- 3. Iekārtas ----------

@bp.route("/machines", methods=["GET", "POST"])
def machines():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            if not name:
                raise ValueError("Aizpildiet lauku «Nosaukums».")
            if Machine.query.filter_by(name=name).first():
                raise ValueError(f"Iekārta «{name}» jau eksistē.")
            available = read_number("available_time", "Pieejamais laiks", minimum=1)
        except ValueError as err:
            flash(str(err), "danger")
        else:
            db.session.add(Machine(name=name, available_time=available))
            db.session.commit()
            flash(f"Iekārta «{name}» pievienota.", "success")
        return redirect(url_for("pages.machines"))
    return render_template("machines.html", machines=Machine.query.order_by(Machine.id).all())


# ---------- 4. Apstrādes laiki ----------

@bp.route("/processing-times", methods=["GET", "POST"])
def processing_times():
    all_books = Book.query.order_by(Book.title).all()
    all_machines = Machine.query.order_by(Machine.id).all()

    if request.method == "POST":
        # Vienkāršākais veids: izdzēst vecos laikus un saglabāt visu tabulu no jauna.
        new_times = []
        try:
            for b in all_books:
                for m in all_machines:
                    value = read_number(f"t_{b.id}_{m.id}", f"{b.title} – {m.name}", required=False)
                    if value is not None:
                        new_times.append(ProcessingTime(book_id=b.id, machine_id=m.id, time_per_unit=value))
        except ValueError as err:
            flash(str(err), "danger")
            return redirect(url_for("pages.processing_times"))
        ProcessingTime.query.delete()
        db.session.add_all(new_times)
        db.session.commit()
        flash("Apstrādes laiki saglabāti.", "success")
        return redirect(url_for("pages.processing_times"))

    values = {f"t_{pt.book_id}_{pt.machine_id}": pt.time_per_unit for pt in ProcessingTime.query.all()}
    return render_template("processing_times.html", books=all_books, machines=all_machines, values=values)


# ---------- 5. Plāna aprēķins ----------

@bp.get("/plan")
def plan():
    return render_template("plan.html")


@bp.post("/api/optimize")
def run_optimization():
    """Izsauc JavaScript (static/js/plan.js). Atbilde — JSON."""
    # 1) Nolasām datus no DB un pārveidojam vienkāršās vārdnīcās optimizatoram
    orders = [
        {"id": o.id, "book_id": o.book_id, "title": o.book.title, "min": o.min_quantity,
         "max": o.max_quantity, "profit": float(o.book.profit_per_unit)}
        for o in Order.query.all()
    ]
    machine_list = [
        {"id": m.id, "name": m.name, "available": float(m.available_time)} for m in Machine.query.all()
    ]
    times = {(pt.book_id, pt.machine_id): float(pt.time_per_unit) for pt in ProcessingTime.query.all()}

    # 2) Aprēķins
    try:
        result = optimize(orders, machine_list, times)
    except OptimizationError as err:
        return jsonify({"error": str(err)}), 422

    # 3) Saglabājam plānu, tā rindas un iekārtu noslodzi
    new_plan = Plan(total_profit=result["total_profit"])
    for order_id, quantity in result["quantities"].items():
        new_plan.lines.append(PlanLine(order_id=order_id, quantity=quantity))
    for machine_id, used in result["used_time"].items():
        new_plan.loads.append(MachineLoad(machine_id=machine_id, used_time=round(used, 2)))
    db.session.add(new_plan)
    db.session.commit()

    return jsonify({"plan_id": new_plan.id, "total_profit": result["total_profit"]}), 201


@bp.get("/plans/<int:plan_id>")
def plan_detail(plan_id):
    saved_plan = db.session.get(Plan, plan_id) or abort(404)
    return render_template("plan_detail.html", plan=saved_plan)
