FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client
COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install common-auth
COPY common-auth /app/common-auth
RUN pip install -e /app/common-auth

# Copy entrypoint script first
COPY user-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project
COPY user-service /app

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
