FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir .

EXPOSE 10000

CMD ["uvicorn", "congo_brain.api.server:app", "--host", "0.0.0.0", "--port", "10000"]
