FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client curl
COPY services/notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install common-auth
COPY services/common-auth /app/common-auth
RUN pip install -e /app/common-auth

# Copy project
COPY services/notification-service /app

# Copy entrypoint script from /app to /
RUN cp /app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Run the application (entrypoint.sh will start Daphne)
CMD ["bash"]
