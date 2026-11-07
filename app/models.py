"""Datu modelis. Katra klase = viens koncepts no konceptu modeļa (koncepta_modelis_v6.svg).
Visi laiki glabājas minūtēs, peļņa — eiro."""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    """Grāmata"""
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, unique=True)
    profit_per_unit = db.Column(db.Numeric(10, 2), nullable=False)


class Order(db.Model):
    """Pasūtījums — vienmēr vienai grāmatai"""
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    min_quantity = db.Column(db.Integer, nullable=False)
    max_quantity = db.Column(db.Integer, nullable=True)  # neobligāts; tukšs = bez ierobežojuma
    book = db.relationship("Book")


class Machine(db.Model):
    """Iekārta"""
    __tablename__ = "machines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    available_time = db.Column(db.Numeric(10, 2), nullable=False)


class ProcessingTime(db.Model):
    """Laiks uz vienību — cik minūšu iekārta patērē vienai grāmatai"""
    __tablename__ = "processing_times"
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), primary_key=True)
    time_per_unit = db.Column(db.Numeric(10, 2), nullable=False)


class Plan(db.Model):
    """Drukāšanas plāns"""
    __tablename__ = "plans"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    total_profit = db.Column(db.Numeric(12, 2), nullable=False)
    lines = db.relationship("PlanLine", order_by="PlanLine.order_id")
    loads = db.relationship("MachineLoad", order_by="MachineLoad.machine_id")


class PlanLine(db.Model):
    """Plāna rinda — cik grāmatu drukāt vienam pasūtījumam"""
    __tablename__ = "plan_lines"
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship("Order")


class MachineLoad(db.Model):
    """Iekārtas noslodze plānā. Atlikušais laiks ir atvasināts (netiek glabāts)."""
    __tablename__ = "machine_loads"
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False)
    used_time = db.Column(db.Numeric(12, 2), nullable=False)
    machine = db.relationship("Machine")

    @property
    def remaining_time(self):
        return self.machine.available_time - self.used_time
