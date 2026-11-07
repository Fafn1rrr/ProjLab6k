
CREATE TABLE IF NOT EXISTS books (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    profit_per_unit NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id),
    min_quantity INTEGER NOT NULL CHECK (min_quantity > 0)
);

CREATE TABLE IF NOT EXISTS machines (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    available_time NUMERIC(12,2) NOT NULL
        CHECK (available_time >= 0)
);

CREATE TABLE IF NOT EXISTS processing_times (
    book_id INTEGER NOT NULL REFERENCES books(id),
    machine_id INTEGER NOT NULL REFERENCES machines(id),
    processing_time NUMERIC(12,4) NOT NULL,
    PRIMARY KEY (book_id, machine_id)
);
