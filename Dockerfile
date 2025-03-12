# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.4 \
    POETRY_VIRTUALENVS_IN_PROJECT=false  

# Install system dependencies required for Poetry
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry 
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set Poetry’s bin directory to be on PATH
ENV PATH="/root/.local/bin:${PATH}"

# Set the working directory to /src
WORKDIR /src

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock /src/

# Install the dependencies with Poetry 
RUN poetry install --no-interaction --no-root

# Copy the rest of the application files
COPY . /src

# Expose the port your app will run on
EXPOSE 7860

# Run the Python application
CMD ["poetry", "run", "python", "-m", "src.serve_app"]
