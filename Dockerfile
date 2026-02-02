# For containerization, I wrote this Dockerfile using a Multi-Stage Build process. The first stage compiles our dependencies, and the second stage runs the app. Crucially, I implemented a Security Best Practice by creating a non-root user named appuser. This ensures that even if our application is compromised, the attacker cannot gain root access to the underlying host system.

# done by ryan




# Stage 1: Build
FROM python:3.10-slim as builder
WORKDIR /app

# Seperating dependency install helps caching and repeatable builds
COPY requirements.txt .

# Install dependencies to a local user directory
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
# Optimization: Use a slim image for the final container to reduce size
FROM python:3.10-slim
WORKDIR /app

# --- FIX: Create user FIRST, then copy files to THEIR home directory ---
# This prevents hackers from getting root access to the server if the app is compromised.
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

# Runs Flask app via python app.py
CMD ["python", "app.py"]