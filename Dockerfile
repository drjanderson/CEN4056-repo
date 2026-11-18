# Stage 1: Base Runtime & Dependencies
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Stage 2: Test Runner (used in Session 7 CI)
FROM base AS test
RUN pip install --no-cache-dir pytest
CMD ["pytest", "-v"]

# Stage 3: Lean Production Image (Session 4 & GHCR deployment)
FROM base AS prod
EXPOSE 5000
CMD ["python", "app.py"]