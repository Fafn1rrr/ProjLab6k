"""Optimize production quantities using prepared data. All times are in minutes."""

import math
from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction
from typing import Literal, TypedDict

import pulp

Identifier = int | str
Number = int | float | Decimal
# Bundled CBC writes eight significant digits in its solution file.
QUANTITY_BASE = 10**7


class Order(TypedDict):
    """An order with profit from its book and a mandatory minimum."""

    id: Identifier
    book_id: Identifier
    profit_per_unit: Number
    min_quantity: int


class Machine(TypedDict):
    """A machine's total availability and maintenance parameters in minutes."""

    id: Identifier
    available_time: Number
    continuous_printing_time: Number
    maintenance_time: Number


class ProcessingTime(TypedDict):
    """Time in minutes per book and machine pair."""

    book_id: Identifier
    machine_id: Identifier
    time: Number


class OrderQuantity(TypedDict):
    """Optimized quantity and profit for one order."""

    order_id: Identifier
    quantity: int
    profit: float


class MachineUsage(TypedDict):
    """Time and utilization metrics for one machine."""

    machine_id: Identifier
    available_time: float
    printing_time: float
    maintenance_count: int
    maintenance_time: float
    used_time: float
    remaining_time: float
    effective_printing_time: float
    utilization_percent: float


FailureStatus = Literal[
    "invalid_input", "infeasible", "unbounded", "solver_error", "not_solved"
]


class OptimizationFailure(TypedDict):
    """An unsuccessful outcome and its diagnostic message."""

    status: FailureStatus
    message: str


class OptimalPlan(TypedDict):
    """A solved plan with quantities, profit and machine utilization."""

    status: Literal["optimal"]
    total_profit: float
    items: list[OrderQuantity]
    machines: list[MachineUsage]


def _records(values: object, name: str) -> list[dict[str, object]]:
    """Check that a collection contains only data records."""
    if not isinstance(values, (list, tuple)) or any(
        not isinstance(value, dict) for value in values
    ):
        raise ValueError(f"{name} must be a list of records.")
    return list(values)


def _identifier(value: object, name: str) -> Identifier:
    """Validate database IDs and string IDs used by standalone callers."""
    if type(value) is int or (isinstance(value, str) and value.strip()):
        return value
    raise ValueError(f"{name} must be an integer or a non-empty string.")


def _number(value: object, name: str) -> Fraction:
    """Keep decimal values exact for feasibility and maintenance calculations."""
    if (
        not isinstance(value, (int, float, Decimal))
        or isinstance(value, bool)
        or not math.isfinite(value)
    ):
        raise ValueError(f"{name} must be a finite number.")
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")
    return Fraction(str(value))


def _effective_time(total: Fraction, work: Fraction, service: Fraction) -> Fraction:
    """Compute the maximum printing time including maintenance breaks."""
    cycles, remainder = divmod(total, work + service)
    return cycles * work + min(remainder, work)


def _validate(
    orders: list[Order] | tuple[Order, ...],
    machines: list[Machine] | tuple[Machine, ...],
    processing_times: list[ProcessingTime] | tuple[ProcessingTime, ...],
) -> tuple[
    dict[Identifier, tuple[Identifier, Fraction, int]],
    dict[Identifier, tuple[Fraction, Fraction, Fraction]],
    dict[tuple[Identifier, Identifier], Fraction],
]:
    """Validate input and index orders, machines and book-machine times."""
    indexed_orders = {}
    for row in _records(orders, "Orders"):
        order_id = _identifier(row.get("id"), "Order ID")
        if order_id in indexed_orders:
            raise ValueError(f"Duplicate order ID {order_id!r}.")
        book_id = _identifier(row.get("book_id"), f"Book ID for order {order_id!r}")
        profit = _number(row.get("profit_per_unit"), f"Profit for order {order_id!r}")
        minimum = row.get("min_quantity")
        if type(minimum) is not int or minimum <= 0:
            raise ValueError(f"Minimum quantity for order {order_id!r} must be a positive integer.")
        indexed_orders[order_id] = (book_id, profit, minimum)
    if not indexed_orders:
        raise ValueError("At least one order is required.")

    indexed_machines = {}
    for row in _records(machines, "Machines"):
        machine_id = _identifier(row.get("id"), "Machine ID")
        if machine_id in indexed_machines:
            raise ValueError(f"Duplicate machine ID {machine_id!r}.")
        total = _number(row.get("available_time"), f"Available time for machine {machine_id!r}")
        work = _number(row.get("continuous_printing_time"), f"Continuous printing time for machine {machine_id!r}")
        service = _number(row.get("maintenance_time"), f"Maintenance time for machine {machine_id!r}")
        if not work:
            raise ValueError(f"Continuous printing time for machine {machine_id!r} must be greater than zero.")
        indexed_machines[machine_id] = (total, work, service)
    if not indexed_machines:
        raise ValueError("At least one machine is required.")

    ordered_books = {order[0] for order in indexed_orders.values()}
    indexed_times = {}
    for row in _records(processing_times, "Processing times"):
        book_id = _identifier(row.get("book_id"), "Processing time book ID")
        machine_id = _identifier(row.get("machine_id"), "Processing time machine ID")
        if book_id not in ordered_books:
            raise ValueError(f"Processing time references unknown ordered book {book_id!r}.")
        if machine_id not in indexed_machines:
            raise ValueError(f"Processing time references unknown machine {machine_id!r}.")
        pair = (book_id, machine_id)
        if pair in indexed_times:
            raise ValueError(f"Duplicate processing time for book {book_id!r} and machine {machine_id!r}.")
        indexed_times[pair] = _number(row.get("time"), f"Processing time for {pair!r}")
    for book_id in ordered_books:
        for machine_id in indexed_machines:
            if (book_id, machine_id) not in indexed_times:
                raise ValueError(f"Missing processing time for book {book_id!r} and machine {machine_id!r}.")
    return indexed_orders, indexed_machines, indexed_times


def _integer_coefficients(values: Sequence[Fraction]) -> tuple[list[int], Fraction]:
    """Return integer coefficients and the common unit by which they were divided."""
    denominator = math.lcm(*(value.denominator for value in values))
    coefficients = [int(value * denominator) for value in values]
    divisor = math.gcd(*coefficients) or 1
    return [value // divisor for value in coefficients], Fraction(divisor, denominator)


def _build_model(
    profits: list[Fraction],
    processing: list[list[Fraction]],
    spare_times: list[Fraction],
) -> tuple[pulp.LpProblem, dict[int, pulp.LpAffineExpression]]:
    """Build the integer program for quantities above the mandatory minimums."""
    problem = pulp.LpProblem("PrintingPlan", pulp.LpMaximize)
    decisions = {}
    for index, times in enumerate(zip(*processing)):
        limit = min(
            (spare // time for spare, time in zip(spare_times, times) if time),
            default=0,
        )
        if limit == 0:
            continue
        # Represent large quantities using smaller integer variables so none are
        # rounded in CBC's textual output. Machine constraints still bound their sum.
        terms = {}
        place = 1
        while limit:
            digit = pulp.LpVariable(
                f"extra_{index}_{place}", lowBound=0,
                upBound=min(limit, QUANTITY_BASE - 1), cat=pulp.LpInteger,
            )
            terms[digit] = place
            place *= QUANTITY_BASE
            limit //= QUANTITY_BASE
        decisions[index] = pulp.LpAffineExpression(terms)
    objective, _ = _integer_coefficients([profits[index] for index in decisions])
    problem += pulp.lpSum(
        coefficient * decision for coefficient, decision in zip(objective, decisions.values())
    )
    for row, spare in zip(processing, spare_times):
        coefficients, unit = _integer_coefficients([row[index] for index in decisions])
        if any(coefficients):
            problem += pulp.lpSum(
                coefficient * decision
                for coefficient, decision in zip(coefficients, decisions.values())
            ) <= spare // unit
    return problem, decisions


def _machine_usage(
    machine_id: Identifier,
    machine: tuple[Fraction, Fraction, Fraction],
    printing: Fraction,
    capacity: Fraction,
) -> MachineUsage:
    """Calculate utilization and verify the solution against exact times."""
    total, work, service = machine
    count = max(0, math.ceil(printing / work) - 1)
    service_time = count * service
    used = printing + service_time
    if printing > capacity or used > total:
        raise ValueError("CBC returned quantities exceeding machine capacity.")
    return {
        "machine_id": machine_id,
        "available_time": float(total),
        "printing_time": float(printing),
        "maintenance_count": count,
        "maintenance_time": float(service_time),
        "used_time": float(used),
        "remaining_time": float(total - used),
        "effective_printing_time": float(capacity),
        "utilization_percent": float(used / total * 100) if total else 0.0,
    }


def optimize(
    orders: list[Order] | tuple[Order, ...],
    machines: list[Machine] | tuple[Machine, ...],
    processing_times: list[ProcessingTime] | tuple[ProcessingTime, ...],
) -> OptimalPlan | OptimizationFailure:
    """Return a JSON-ready optimal plan or a status and error message."""
    try:
        indexed_orders, indexed_machines, indexed_times = _validate(
            orders, machines, processing_times
        )
    except (ValueError, ArithmeticError) as error:
        return {"status": "invalid_input", "message": str(error)}

    books = [book for book, _, _ in indexed_orders.values()]
    profits = [profit for _, profit, _ in indexed_orders.values()]
    minimums = [minimum for _, _, minimum in indexed_orders.values()]
    processing = [
        [indexed_times[book_id, machine_id] for book_id in books]
        for machine_id in indexed_machines
    ]
    capacities = [_effective_time(*machine) for machine in indexed_machines.values()]

    spare_times = [
        capacity - sum(time * minimum for time, minimum in zip(row, minimums))
        for row, capacity in zip(processing, capacities)
    ]
    if any(spare < 0 for spare in spare_times):
        return {
            "status": "infeasible",
            "message": "The minimum quantities cannot be met with the available machine time.",
        }
    if any(profit > 0 and not any(times) for profit, times in zip(profits, zip(*processing))):
        return {"status": "unbounded", "message": "A profitable order uses no machine time."}

    try:
        solver = pulp.PULP_CBC_CMD(msg=False, gapRel=0, gapAbs=0)
        if not solver.available():
            return {"status": "solver_error", "message": "CBC solver is unavailable."}
        problem, decisions = _build_model(profits, processing, spare_times)
        status = problem.solve(solver)
        if status == pulp.LpStatusInfeasible:
            return {"status": "infeasible", "message": "CBC reported an infeasible plan."}
        if status == pulp.LpStatusUnbounded:
            return {"status": "unbounded", "message": "CBC reported an unbounded objective."}
        if status != pulp.LpStatusOptimal or problem.sol_status != pulp.LpSolutionOptimal:
            return {"status": "not_solved", "message": "CBC did not prove an optimal solution."}

        quantities = minimums.copy()
        for index, decision in decisions.items():
            for variable, place in decision.items():
                value = variable.value()
                if value is None or not math.isfinite(value):
                    raise ValueError("CBC did not return a finite order quantity.")
                digit = round(value)
                if abs(value - digit) > 1e-7 or not 0 <= digit <= variable.upBound:
                    raise ValueError("CBC returned an invalid integer quantity.")
                quantities[index] += digit * place

        order_profits = [profit * quantity for profit, quantity in zip(profits, quantities)]
        return {
            "status": "optimal",
            "total_profit": float(sum(order_profits)),
            "items": [
                {"order_id": order_id, "quantity": quantity, "profit": float(profit)}
                for order_id, quantity, profit in zip(indexed_orders, quantities, order_profits)
            ],
            "machines": [
                _machine_usage(
                    machine_id, machine,
                    sum(time * quantity for time, quantity in zip(row, quantities)),
                    capacity,
                )
                for (machine_id, machine), row, capacity in zip(
                    indexed_machines.items(), processing, capacities
                )
            ],
        }
    except (pulp.PulpError, OSError):
        return {"status": "solver_error", "message": "CBC solver could not run."}
    except (ValueError, OverflowError) as error:
        return {"status": "solver_error", "message": str(error)}
