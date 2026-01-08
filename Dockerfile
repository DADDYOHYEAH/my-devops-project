# Stage 1: Build
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
# Install dependencies to a local user directory
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim
WORKDIR /app

# --- FIX: Create user FIRST, then copy files to THEIR home directory ---
RUN adduser --disabled-password --gecos '' appuser

# Copy libraries from builder's root to appuser's home
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set ownership so appuser can read everything
RUN chown -R appuser:appuser /app
# -----------------------------------------------------------------------

# Switch to non-root user
USER appuser

# Update PATH so Python finds the installed libraries in the new location
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 5000
CMD ["python", "app.py"]