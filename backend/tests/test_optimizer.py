import json
from decimal import Decimal
from itertools import product

import pulp
import pytest

from backend.optimizer import optimize


def make_problem(order_specs, machine_specs, times):
    orders = [
        {"id": f"O{i}", "book_id": f"B{i}", "profit_per_unit": profit, "min_quantity": minimum}
        for i, (profit, minimum) in enumerate(order_specs)
    ]
    machines = [
        {
            "id": f"M{i}", "available_time": total,
            "continuous_printing_time": work, "maintenance_time": maintenance,
        }
        for i, (total, work, maintenance) in enumerate(machine_specs)
    ]
    processing_times = [
        {"book_id": order["book_id"], "machine_id": machine["id"], "time": time}
        for order, row in zip(orders, times)
        for machine, time in zip(machines, row)
    ]
    return orders, machines, processing_times


def test_control_example():
    orders, machines, times = make_problem([(6, 2), (10, 1)], [(10, 4, 1), (9, 3, 1)], [(1, 1), (2, 1)])
    plan = optimize(orders, machines, times)

    assert plan == {
        "status": "optimal",
        "total_profit": 46,
        "items": [
            {"order_id": "O0", "quantity": 6, "profit": 36},
            {"order_id": "O1", "quantity": 1, "profit": 10},
        ],
        "machines": [
            {
                "machine_id": "M0", "available_time": 10, "printing_time": 8,
                "maintenance_count": 1, "maintenance_time": 1, "used_time": 9,
                "remaining_time": 1, "effective_printing_time": 8, "utilization_percent": 90,
            },
            {
                "machine_id": "M1", "available_time": 9, "printing_time": 7,
                "maintenance_count": 2, "maintenance_time": 2, "used_time": 9,
                "remaining_time": 0, "effective_printing_time": 7, "utilization_percent": 100,
            },
        ],
    }
    assert all(type(item["quantity"]) is int for item in plan["items"])
    assert json.loads(json.dumps(plan, allow_nan=False)) == plan


@pytest.mark.parametrize(
    ("order_specs", "machine_specs", "times"),
    [
        ([(6, 1), (10, 1), (4, 1)], [(8, 3, 1), (7, 4, 1)], [(1, 0), (2, 2), (0, 1)]),
        ([(3, 1), (4, 2)], [(9, 4, 2), (7, 3, 1), (8, 2, 0)], [(3, 1, 1), (1, 2, 2)]),
        ([(2, 2), (0, 1)], [(5, 5, 1)], [(2,), (0,)]),
        ([(0, 2)], [(0, 5, 1)], [(0,)]),
    ],
)
def test_optimal_profit_matches_exhaustive_search(order_specs, machine_specs, times):
    plan = optimize(*make_problem(order_specs, machine_specs, times))
    assert plan["status"] == "optimal"

    def fits(quantities):
        for (total, work, maintenance), per_order in zip(machine_specs, zip(*times)):
            printing = sum(time * quantity for time, quantity in zip(per_order, quantities))
            service_count = (printing - 1) // work if printing else 0
            if printing + service_count * maintenance > total:
                return False
        return True

    domains = [
        range(minimum, min(
            (machine[0] // time for machine, time in zip(machine_specs, row) if time),
            default=minimum,
        ) + 1)
        for (_, minimum), row in zip(order_specs, times)
    ]
    quantities = [item["quantity"] for item in plan["items"]]
    assert all(type(quantity) is int and quantity in domain for quantity, domain in zip(quantities, domains))
    assert fits(quantities)
    assert plan["total_profit"] == max(
        sum(profit * quantity for (profit, _), quantity in zip(order_specs, candidate))
        for candidate in product(*domains) if fits(candidate)
    )


@pytest.mark.parametrize(
    ("total", "work", "service", "time", "quantity", "capacity", "count", "remaining"),
    [
        (4, 4, 1, 1, 4, 4, 0, 0),
        (6, 4, 1, 1, 5, 5, 1, 0),
        (10, 4, 1, 1, 8, 8, 1, 1),
        (9, 4, 0, 1, 9, 9, 2, 0),
        (3, 4, 1, 1, 3, 3, 0, 0),
        (5, 4, 2, 1, 4, 4, 0, 1),
        (0.7, 0.3, 0.1, 0.1, 6, 0.6, 1, 0),
        (0.4, 0.3, 0.2, 0.100000000001, 2, 0.3, 0, 0.199999999998),
        (0.6, 0.3, 0.2, 0.100000000001, 3, 0.4, 1, 0.099999999997),
        (0.3, 1, 0, Decimal("0.000000001"), 300000000, 0.3, 0, 0),
        (0.299999999, 1, 0, Decimal("0.000000001"), 299999999, 0.299999999, 0, 0),
        (720, 240, 60, 1, 600, 600, 2, 0),
    ],
)
def test_maintenance_boundaries(total, work, service, time, quantity, capacity, count, remaining):
    plan = optimize(*make_problem([(2, 1)], [(total, work, service)], [(time,)]))
    assert plan["status"] == "optimal"
    assert plan["items"][0]["quantity"] == quantity
    assert plan["total_profit"] == 2 * quantity
    machine = plan["machines"][0]
    assert machine["maintenance_count"] == count
    assert machine["maintenance_time"] == pytest.approx(count * service)
    assert machine["effective_printing_time"] == capacity
    assert machine["printing_time"] == pytest.approx(float(time) * quantity)
    assert machine["used_time"] == pytest.approx(total - remaining)
    assert machine["remaining_time"] == pytest.approx(remaining)
    assert machine["utilization_percent"] == pytest.approx((total - remaining) / total * 100)


def test_zero_load_on_available_and_unavailable_machines():
    plan = optimize(*make_problem([(1, 1)], [(2, 2, 0), (3, 2, 1), (0, 2, 1)], [(1, 0, 0)]))
    assert plan["status"] == "optimal"
    for machine, remaining in zip(plan["machines"][1:], (3, 0)):
        assert machine["printing_time"] == machine["used_time"] == machine["maintenance_time"] == 0
        assert machine["maintenance_count"] == machine["utilization_percent"] == 0
        assert machine["remaining_time"] == remaining


def test_orders_for_same_book_share_processing_time():
    orders, machines, times = make_problem([(2, 1), (3, 2)], [(6, 5, 1)], [(1,)])
    orders[1]["book_id"] = orders[0]["book_id"]
    plan = optimize(orders, machines, times)
    assert plan["status"] == "optimal"
    assert [item["quantity"] for item in plan["items"]] == [1, 4]


@pytest.mark.parametrize(
    ("case", "status"),
    [
        ([(3, 1)], "infeasible"),
        ([(0, 0)], "unbounded"),
    ],
)
def test_infeasible_and_unbounded(case, status):
    plan = optimize(*make_problem([(2, 2)], [(6, 4, 1), (4, 4, 0)], case))
    assert plan["status"] == status
    assert set(plan) == {"status", "message"}


@pytest.mark.parametrize(
    ("collection", "field", "value"),
    [
        (0, "id", True), (0, "id", ""), (0, "book_id", 9), (0, "min_quantity", -1),
        (0, "min_quantity", 0), (0, "min_quantity", True), (0, "min_quantity", 1.5),
        (0, "profit_per_unit", float("nan")), (0, "profit_per_unit", float("inf")),
        (0, "profit_per_unit", -1), (1, "available_time", -1),
        (1, "continuous_printing_time", 0), (1, "continuous_printing_time", -1),
        (1, "maintenance_time", -1), (1, "maintenance_time", "1"),
        (2, "time", -1), (2, "time", None), (2, "time", False),
        (2, "machine_id", "unknown"), (2, "book_id", "unknown"),
        (2, "order_id", "unknown"),
    ],
)
def test_invalid_values(collection, field, value):
    data = make_problem([(2, 1)], [(3, 2, 1)], [(1,)])
    if field == "order_id":
        data[collection][0].pop("book_id")
    data[collection][0][field] = value
    assert optimize(*data)["status"] == "invalid_input"


@pytest.mark.parametrize("index", range(3))
@pytest.mark.parametrize("shape", ["empty", "duplicated", "bad_collection", "bad_record", "missing_field"])
def test_invalid_collections(index, shape):
    data = list(make_problem([(2, 1)], [(3, 2, 1)], [(1,)]))
    if shape == "empty":
        data[index] = []
    elif shape == "duplicated":
        data[index] *= 2
    elif shape == "bad_collection":
        data[index] = {}
    elif shape == "bad_record":
        data[index] = [0]
    else:
        data[index][0].pop(next(iter(data[index][0])))
    failure = optimize(*data)
    assert failure["status"] == "invalid_input"
    assert set(failure) == {"status", "message"}


@pytest.mark.parametrize(
    ("sewing", "available", "expected", "profit"),
    [
        (1, [2400, 1200, 1800, 1500], [655, 100, 150], 4427.5),
        (3, [2400, 1200, 2000, 1500], [344, 104, 352], 4106.4),
        (1, [1350, 1200, 1800, 1500], None, None),
    ],
)
def test_project_reference_cases(sewing, available, expected, profit):
    plan = optimize(*make_problem(
        [(4.5, 200), (7, 100), (5.2, 150)],
        [(total, 480, 60) for total in available],
        [(2, 0.5, sewing, 0.8), (4, 1, 2.5, 1.5), (3, 0.8, 1.5, 1.2)],
    ))
    if expected is None:
        assert plan["status"] == "infeasible"
    else:
        assert plan["status"] == "optimal"
        assert [item["quantity"] for item in plan["items"]] == expected
        assert plan["total_profit"] == profit


@pytest.mark.parametrize(
    ("scenario", "expected"),
    [
        ("unavailable", "solver_error"),
        ("exception", "solver_error"),
        ("not_solved", "not_solved"),
        ("unproven", "not_solved"),
        ("invalid_candidate", "solver_error"),
    ],
)
def test_solver_failures(monkeypatch, scenario, expected):
    def solve(problem, solver):
        if scenario == "exception":
            raise pulp.PulpSolverError("CBC failed")
        if scenario == "not_solved":
            return pulp.LpStatusNotSolved
        if scenario == "unproven":
            problem.sol_status = pulp.LpSolutionIntegerFeasible
        else:
            problem.sol_status = pulp.LpSolutionOptimal
            for variable in problem.variables():
                variable.varValue = 100
        return pulp.LpStatusOptimal

    monkeypatch.setattr(pulp.PULP_CBC_CMD, "available", lambda _: scenario != "unavailable")
    monkeypatch.setattr(pulp.LpProblem, "solve", solve)
    plan = optimize(*make_problem([(2, 1)], [(3, 2, 1)], [(1,)]))
    assert plan["status"] == expected
    assert set(plan) == {"status", "message"}
