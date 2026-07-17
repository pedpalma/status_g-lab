# Imagem de desenvolvimento do backend.
# Otimizada para hot reload via docker-compose (código montado como volume).
# TODO: quando houver necessidade de deploy de produção, avaliar build multi-stage separado.

FROM python:3.13-slim

WORKDIR /app


# gcc e libpq-dev são necessários para compilar dependencies nativas
# (psycopg2-binary já traz binário próprio, mas libpq-dev cobre casos em
# que o wheel pré-compilado não esta disponível para a plataforma).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
