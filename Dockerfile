# Use Python 3.12 as specified in your dependencies
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       g++ \
       make \
       libssl-dev \
       python3-dev \
       autoconf \
       automake \
       libtool \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy only requirements to cache them in docker layer
# Copy just the dependency files initially for better caching
COPY pyproject.toml poetry.lock* /app/

# Configure poetry to not use virtualenvs inside Docker
RUN poetry config virtualenvs.create false

# Install dependencies with extended timeout for complex builds
RUN poetry config installer.max-workers 4 && \
    poetry install --no-interaction --no-ansi --no-dev

# Copy project files
COPY . /app/

# Set the PYTHONPATH
ENV PYTHONPATH=/app/src

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]