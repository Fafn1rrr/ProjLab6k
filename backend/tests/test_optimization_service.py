"""Pure-Python tests for the DB adapter and API response formatting."""

import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from optimization_service import format_optimization_result, load_optimizer_input


class OptimizationServiceTests(unittest.TestCase):
    def setUp(self):
        connection = MagicMock()
        self.cursor = connection.cursor.return_value.__enter__.return_value
        self.cursor.fetchall.side_effect = [
            [(1, 4, Decimal("6.00"), 2, "Book A")],
            [(7, Decimal("720.00"), Decimal("240.00"), Decimal("60.00"), "Printer A")],
            [(4, 7, Decimal("30.00"))],
        ]
        self.input = load_optimizer_input(connection)

    def test_adapter_reads_three_queries_with_minutes_unchanged(self):
        self.assertEqual(self.cursor.execute.call_count, 3)
        self.assertEqual(self.input["orders"], [
            {"id": 1, "book_id": 4, "profit_per_unit": Decimal("6.00"), "min_quantity": 2}
        ])
        self.assertEqual(self.input["machines"], [
            {"id": 7, "available_time": Decimal("720.00"),
             "continuous_printing_time": Decimal("240.00"),
             "maintenance_time": Decimal("60.00")}
        ])
        self.assertEqual(self.input["processing_times"], [
            {"book_id": 4, "machine_id": 7, "time": Decimal("30.00")}
        ])
        self.assertEqual(self.input["order_names"], {1: "Book A"})
        self.assertEqual(self.input["machine_names"], {7: "Printer A"})

    def test_optimal_result_matches_frontend_format(self):
        plan = {
            "status": "optimal",
            "total_profit": 36,
            "items": [{"order_id": 1, "quantity": 6, "profit": 36}],
            "machines": [{
                "machine_id": 7, "used_time": 360.0, "available_time": 720.0,
                "remaining_time": 360.0, "printing_time": 300.0,
                "maintenance_count": 1, "maintenance_time": 60.0,
                "effective_printing_time": 600.0, "utilization_percent": 50.0,
            }],
        }
        response, code = format_optimization_result(plan, self.input)
        self.assertEqual(code, 200)
        self.assertEqual(response, {
            "status": "optimal",
            "totalProfit": 36,
            "items": [{"orderId": 1, "bookName": "Book A", "quantity": 6, "profit": 36}],
            "machines": [{
                "machineId": 7, "machineName": "Printer A", "used": 6.0,
                "available": 12.0, "remaining": 6.0, "printingTime": 5.0,
                "maintenanceCount": 1, "maintenanceTime": 1.0,
                "effectivePrintingTime": 10.0, "utilizationPercent": 50.0,
            }],
        })

    def test_error_status_codes_are_preserved(self):
        for status, expected_code in [
            ("infeasible", 200), ("invalid_input", 400),
            ("unbounded", 422), ("solver_error", 503), ("not_solved", 503),
        ]:
            with self.subTest(status=status):
                plan = {"status": status, "message": "Example"}
                response, code = format_optimization_result(plan, self.input)
                self.assertEqual(code, expected_code)
                self.assertEqual(response, plan)


if __name__ == "__main__":
    unittest.main()
