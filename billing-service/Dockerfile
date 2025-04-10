FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client
COPY billing-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install common-auth
COPY common-auth /app/common-auth
RUN pip install -e /app/common-auth

# Copy entrypoint script first
COPY billing-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project
COPY billing-service /app

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]
