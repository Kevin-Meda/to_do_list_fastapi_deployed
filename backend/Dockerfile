# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# install python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy your FastAPI app
COPY src/ ./src/

EXPOSE 8000

# note: uvicorn import path is relative to /app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
