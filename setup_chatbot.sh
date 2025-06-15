#!/bin/bash

echo "🚀 Quick Setup & Test for Health Chatbot Service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start database and redis first
echo "🗄️ Starting database and redis..."
docker-compose up -d db redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 15

# Build and start chatbot service
echo "🏗️ Building and starting chatbot service..."
docker-compose up -d chatbot-service

# Wait for service to start
echo "⏳ Waiting for chatbot service to start..."
sleep 30

# Check service health
echo "🩺 Checking service health..."
if curl -f http://localhost:8007/health/ > /dev/null 2>&1; then
    print_status "Chatbot service is healthy!"
else
    print_warning "Chatbot service health check failed, checking logs..."
    docker-compose logs chatbot-service | tail -20
fi

# Test API endpoints
echo "🧪 Testing API endpoints..."

# Test health endpoint
if curl -s http://localhost:8007/health/ | grep -q "healthy"; then
    print_status "Health endpoint working!"
else
    print_error "Health endpoint failed"
fi

# Test chat endpoint
echo "💬 Testing chat endpoint..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8007/api/ai/chat/ \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, I have a headache"}' 2>/dev/null)

if echo "$CHAT_RESPONSE" | grep -q "response"; then
    print_status "Chat endpoint working!"
    echo "Response: $(echo "$CHAT_RESPONSE" | jq -r '.response' 2>/dev/null || echo "$CHAT_RESPONSE")"
else
    print_error "Chat endpoint failed"
    echo "Response: $CHAT_RESPONSE"
fi

# Show running services
echo "📋 Running services:"
docker-compose ps

# Show logs if there are errors
if docker-compose logs chatbot-service 2>&1 | grep -i error; then
    print_warning "Found errors in logs:"
    docker-compose logs chatbot-service | grep -i error | tail -10
fi

echo "🎉 Setup and test completed!"
echo "🌐 Access chatbot service at: http://localhost:8007"
echo "🔗 Health check: http://localhost:8007/health/"
echo "💬 Chat API: http://localhost:8007/api/ai/chat/"
echo "👨‍💼 Admin panel: http://localhost:8007/admin/"
