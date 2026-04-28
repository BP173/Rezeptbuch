FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py models.py routes.py ./
COPY templates ./templates/

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--factory", "app:create_app"]
