FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/Varunshiyam/Syntrix-Cloud-Monitoring-and-Observability"
LABEL org.opencontainers.image.description="Syntrix Cloud Monitoring and Observability Platform"
LABEL org.opencontainers.image.licenses="Apache-2.0"

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY shared /app/shared


ARG SERVICE_NAME
ENV SERVICE_DIR=${SERVICE_NAME}
ENV PYTHONPATH=/app


COPY ${SERVICE_DIR} /app/${SERVICE_DIR}


COPY frontend /app/frontend

EXPOSE 8000

CMD uvicorn $(echo ${SERVICE_DIR} | tr '/' '.').main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2
