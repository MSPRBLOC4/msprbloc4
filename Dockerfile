
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/msprbloc4/requirements.txt
RUN pip install --no-cache-dir -r /app/msprbloc4/requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app/msprbloc4
ENV PYTHONPATH=/app
EXPOSE 8000
ENV HOST=0.0.0.0
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl --fail http://localhost:8000/health || exit 1
ENTRYPOINT ["python", "-m", "msprbloc4.main"]
