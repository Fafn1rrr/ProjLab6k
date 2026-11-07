"""Optimizācijas modulis. Nepiekļūst datu bāzei — saņem gatavus datus no routes.py.

Matemātiskais modelis (veselo skaitļu lineārā programmēšana, ILP):
    x_o   — cik grāmatu drukāt pasūtījumam o (vesels skaitlis)
    max   Σ peļņa_o · x_o
    kur   min_o ≤ x_o ≤ max_o                       katram pasūtījumam (max_o var nebūt)
          Σ laiks(grāmata_o, m) · x_o ≤ pieejams_m   katrai iekārtai m
"""
import pulp


class OptimizationError(Exception):
    """Plānu nevar aprēķināt. Teksts ir paredzēts lietotājam."""


def optimize(orders, machines, times):
    """
    orders:   [{"id": 1, "book_id": 1, "title": "Ziemas pasakas", "min": 200, "max": 400, "profit": 4.5}]
              ("max" var būt None — tad augšējās robežas nav)
    machines: [{"id": 1, "name": "Druka", "available": 2400}]
    times:    {(book_id, machine_id): minūtes vienas grāmatas apstrādei}

    Atgriež:  {"total_profit": 4742.4, "quantities": {order_id: skaits}, "used_time": {machine_id: minūtes}}
    """
    if not orders or not machines:
        raise OptimizationError("Vispirms pievienojiet pasūtījumus un iekārtas.")

    missing = sorted({
        f"{o['title']} – {m['name']}"
        for o in orders for m in machines
        if (o["book_id"], m["id"]) not in times
    })
    if missing:
        raise OptimizationError("Nav norādīts apstrādes laiks: " + ", ".join(missing))

    model = pulp.LpProblem("drukas_plans", pulp.LpMaximize)

    # Mainīgie: x[pasūtījuma id] — drukājamais skaits
    x = {
        o["id"]: pulp.LpVariable(f"x_{o['id']}", lowBound=o["min"], upBound=o["max"], cat="Integer")
        for o in orders
    }

    # Mērķis: maksimāla kopējā peļņa
    model += pulp.lpSum(o["profit"] * x[o["id"]] for o in orders)

    # Ierobežojums: nevienai iekārtai nepārsniegt pieejamo laiku
    for m in machines:
        model += pulp.lpSum(times[(o["book_id"], m["id"])] * x[o["id"]] for o in orders) <= m["available"]

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[model.status]

    if status == "Infeasible":
        raise OptimizationError("Minimālos daudzumus nav iespējams izdrukāt pieejamajā iekārtu laikā.")
    if status != "Optimal":
        raise OptimizationError(f"Plānu neizdevās aprēķināt (risinātāja statuss: {status}).")

    quantities = {o["id"]: round(x[o["id"]].value()) for o in orders}
    used_time = {
        m["id"]: sum(times[(o["book_id"], m["id"])] * quantities[o["id"]] for o in orders)
        for m in machines
    }
    total_profit = sum(o["profit"] * quantities[o["id"]] for o in orders)

    return {"total_profit": round(total_profit, 2), "quantities": quantities, "used_time": used_time}
