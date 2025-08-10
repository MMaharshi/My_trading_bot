FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service /app/service
COPY scripts /app/scripts
COPY pine /app/pine
ENV PYTHONPATH=/app
CMD ["uvicorn", "service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
