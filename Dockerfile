FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir .

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 10000

CMD ["./start.sh"]
