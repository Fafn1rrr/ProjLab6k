BEGIN;

INSERT INTO books (title, profit_per_unit)
SELECT 'Test Book ' || n, random(2.00, 12.00)
FROM generate_series(1, 6) AS n
WHERE NOT EXISTS (SELECT 1 FROM books WHERE title = 'Test Book ' || n);

INSERT INTO orders (book_id, min_quantity)
SELECT b.id, random(5, 20)
FROM books b
WHERE b.title SIMILAR TO 'Test Book [1-6]'
  AND NOT EXISTS (SELECT 1 FROM orders WHERE book_id = b.id);

INSERT INTO machines (name, available_time)
SELECT 'Test Printer ' || n, 480
FROM generate_series(1, 3) AS n
WHERE NOT EXISTS (SELECT 1 FROM machines WHERE name = 'Test Printer ' || n);

INSERT INTO processing_times (book_id, machine_id, processing_time)
SELECT b.id, m.id, random(0.50, 1.50)
FROM books b
CROSS JOIN machines m
WHERE b.title SIMILAR TO 'Test Book [1-6]'
  AND m.name SIMILAR TO 'Test Printer [1-3]'
ON CONFLICT (book_id, machine_id) DO NOTHING;

COMMIT;
