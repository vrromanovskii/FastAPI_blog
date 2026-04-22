FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Используем зеркало Alibaba
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000"]