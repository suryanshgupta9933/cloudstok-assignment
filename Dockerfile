FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy the project description
COPY pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
RUN uv sync --frozen --no-install-project

# Copy the project source code
COPY . .

# Install the project itself
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the application (Default to backend, overridden in compose)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
