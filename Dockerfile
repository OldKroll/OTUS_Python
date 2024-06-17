FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY . .

CMD ls

RUN pip install -r requirements.txt

CMD mypy 03_type_annotations
