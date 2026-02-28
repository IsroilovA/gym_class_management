# Build dependencies in an isolated stage.
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    jpeg-dev \
    zlib-dev

# Keep dependencies in a dedicated venv for copying to runtime.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements/base.txt

# Minimal runtime image.
FROM python:3.13-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime shared libs only (no compiler toolchain).
RUN apk add --no-cache \
    libpq \
    jpeg \
    zlib \
    su-exec

# Run as non-root.
RUN addgroup -S app && adduser -S -G app app

# Copy prebuilt virtualenv from builder.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy app source.
COPY . .

# Prepare entrypoint and ownership.
RUN chmod +x entrypoint.sh \
    && chown -R app:app /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8000, timeout=3); conn.request('GET', '/'); r = conn.getresponse(); assert r.status < 500, f'status {r.status}'" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-"]
