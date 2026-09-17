FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    curl \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-data.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-data.txt
RUN npm install -g promptfoo@0.122.0

COPY . .

CMD ["make", "run-all"]
