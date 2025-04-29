# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# install python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy your Streamlit app
COPY src/ ./src/ 

EXPOSE 8501

# point at the file inside ./src/
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
