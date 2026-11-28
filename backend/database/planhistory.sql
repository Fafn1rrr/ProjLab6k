BEGIN;

CREATE TABLE IF NOT EXISTS printing_plans (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_profit NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS printing_plan_items (
    plan_id BIGINT NOT NULL REFERENCES printing_plans(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    book_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    profit NUMERIC NOT NULL,
    PRIMARY KEY (plan_id, order_id)
);

CREATE TABLE IF NOT EXISTS printing_plan_machine_usage (
    plan_id BIGINT NOT NULL REFERENCES printing_plans(id) ON DELETE CASCADE,
    machine_id INTEGER NOT NULL REFERENCES machines(id),
    machine_name VARCHAR(255) NOT NULL,
    available_time NUMERIC NOT NULL CHECK (available_time >= 0),
    printing_time NUMERIC NOT NULL CHECK (printing_time >= 0),
    maintenance_time NUMERIC NOT NULL CHECK (maintenance_time >= 0),
    remaining_time NUMERIC NOT NULL CHECK (remaining_time >= 0),
    PRIMARY KEY (plan_id, machine_id)
);

COMMENT ON TABLE printing_plan_items IS
    'Calculated order quantities, book names and profit saved at calculation time';

COMMENT ON TABLE printing_plan_machine_usage IS
    'Machine names and utilization in minutes saved at calculation time';

COMMIT;
