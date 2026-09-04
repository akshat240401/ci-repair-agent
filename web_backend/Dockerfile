FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir -r web_backend/requirements.txt

# Demo backend runs as a non-root user. For public untrusted uploads, place
# test execution in a stronger isolation boundary (separate sandbox/VM).
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "web_backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
