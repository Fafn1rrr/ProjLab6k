FROM python:3.14-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY backend/app.py .
COPY backend/db.py .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
