# Proj.Lab.

## Local demo with Docker

Start Docker Desktop, then run this from the project root:

    docker compose up --build --wait

Open http://127.0.0.1:5002/ for the Flask site and
http://127.0.0.1:5002/about for the database output.
Compose starts a local PostgreSQL 18 database and runs `schema.sql` and
`seed.sql` the first time it creates the data volume. The volume keeps
the generated data between starts. Each computer has its own local copy.
The Docker demo uses its own database connection and works without a
Neon account or a `.env` file.

## Local Flask app

Use the project's Python environment and install the packages in
`requirements.txt`. Copy `.env.example` to `.env` in the project root, then
paste the connection URI from Neon's **Connect** dialog after
`DATABASE_URL=`. Keep the TLS options from the Neon URI. Git ignores `.env`.
An existing `DATABASE_URL` environment variable takes precedence.

For a new database, run `database/schema.sql` in Neon's SQL Editor on the
branch and database selected in the connection URI. Run `database/seed.sql`
if you want sample data.

Start Flask with `python -m flask --app app run`. The books API accepts
`GET /api/books` and `POST /api/books`. To create a book, send a JSON body
such as `{"title": "Example book", "profit_per_unit": 5.25}`. A successful
POST returns HTTP 201 and the created book.

## Azure App Service

Select a Linux Web App with Python 3.14 and the **Free F1** plan where
available. Add `DATABASE_URL` in the Web App's **Environment variables**.
For ZIP deployment, add `SCM_DO_BUILD_DURING_DEPLOYMENT=true` so Azure
installs `requirements.txt`. Put `app.py`, `db.py`, `requirements.txt`, and
`templates/` at the ZIP root. Flask's `app.py` entry point is detected
automatically. Check `/api/books` after deployment.

[Microsoft's Python App Service guide](https://learn.microsoft.com/azure/app-service/quickstart-python)
