"""Komandrindas komandas:
    flask --app app init-db          izveido datu bāzi (ja tās nav) un tabulas
    flask --app app init-db --drop   izdzēš visas tabulas ar datiem un izveido no jauna
    flask --app app seed             ievieto demonstrācijas datus
"""
import click
import psycopg
from sqlalchemy.engine import make_url

from .models import Book, Machine, Order, ProcessingTime, db

# Demonstrācijas dati. Ar tiem plāna kopējā peļņa ir 4742,40 €.
DEMO_BOOKS = [("Ziemas pasakas", 4.50), ("Rīgas vēsture", 7.00), ("Programmēšana Python valodā", 5.20)]
DEMO_MACHINES = [("Druka", 2400), ("Griešana", 1200), ("Šūšana", 1800), ("Apdare", 1500)]  # minūtes
DEMO_TIMES = {  # minūtes uz vienu grāmatu: Druka, Griešana, Šūšana, Apdare
    "Ziemas pasakas": [2.0, 0.5, 1.0, 0.8],
    "Rīgas vēsture": [4.0, 1.0, 2.5, 1.5],
    "Programmēšana Python valodā": [3.0, 0.8, 1.5, 1.2],
}
DEMO_ORDERS = [  # (grāmata, minimums, maksimums vai None)
    ("Ziemas pasakas", 200, 400),
    ("Rīgas vēsture", 100, None),
    ("Programmēšana Python valodā", 150, 300),
    ("Ziemas pasakas", 50, 150),
]


def create_database_if_missing(uri):
    """Pieslēdzas sistēmas DB «postgres» un izveido mūsu datu bāzi, ja tās vēl nav."""
    url = make_url(uri)
    with psycopg.connect(
        host=url.host or "localhost", port=url.port or 5432, user=url.username,
        password=url.password, dbname="postgres", autocommit=True,
    ) as conn:
        if conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (url.database,)).fetchone():
            return
        # UTF8 — lai latviešu burti strādātu arī serverī ar citu noklusēto kodējumu
        conn.execute(f'CREATE DATABASE "{url.database}" ENCODING \'UTF8\' TEMPLATE template0')
        click.echo(f"Izveidota datu bāze «{url.database}».")


def register_cli(app):
    @app.cli.command("init-db")
    @click.option("--drop", is_flag=True, help="Izdzēst esošās tabulas ar visiem datiem.")
    def init_db(drop):
        """Izveido datu bāzi un tabulas."""
        try:
            create_database_if_missing(app.config["SQLALCHEMY_DATABASE_URI"])
        except psycopg.Error as err:
            raise click.ClickException(
                f"Neizdevās pieslēgties PostgreSQL: {err}\n"
                "Pārbaudiet, vai serveris darbojas un vai DATABASE_URL failā .env ir pareizs."
            ) from err
        if drop:
            db.drop_all()
            click.echo("Esošās tabulas dzēstas.")
        db.create_all()
        click.echo("Tabulas gatavas.")

    @app.cli.command("seed")
    def seed():
        """Ievieto demonstrācijas datus (tikai tukšā datu bāzē)."""
        if Book.query.first() or Machine.query.first():
            raise click.ClickException("Datu bāzē jau ir dati. Sāciet no jauna: flask --app app init-db --drop")

        books = {title: Book(title=title, profit_per_unit=profit) for title, profit in DEMO_BOOKS}
        machines = [Machine(name=name, available_time=minutes) for name, minutes in DEMO_MACHINES]
        db.session.add_all(list(books.values()) + machines)
        db.session.flush()  # pēc flush ierakstiem ir piešķirti id

        for title, minutes_per_machine in DEMO_TIMES.items():
            for machine, minutes in zip(machines, minutes_per_machine):
                db.session.add(ProcessingTime(book_id=books[title].id, machine_id=machine.id, time_per_unit=minutes))
        for title, min_qty, max_qty in DEMO_ORDERS:
            db.session.add(Order(book=books[title], min_quantity=min_qty, max_quantity=max_qty))
        db.session.commit()
        click.echo("Pievienotas 3 grāmatas, 4 iekārtas, 4 pasūtījumi un apstrādes laiki.")
