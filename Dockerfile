# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for some ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (We append the full-stack requirements)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir Flask-SQLAlchemy Flask-Login Flask-Bcrypt Flask-SocketIO eventlet gunicorn

# Copy the rest of the application code
COPY . .

# Expose port (default for Flask/Gunicorn)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Command to run the application using eventlet and gunicorn for WebSockets
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
