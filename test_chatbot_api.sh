#!/bin/bash

echo "🧪 Testing Health Chatbot API"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# Check if service is running
print_info "Checking if chatbot service is running..."
if docker-compose ps chatbot-service | grep -q "Up"; then
    print_status "Chatbot service is running"
else
    print_error "Chatbot service is not running"
    echo "Starting service..."
    docker-compose up -d chatbot-service
    sleep 30
fi

# Test health endpoint
print_info "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8007/health/ 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status "Health endpoint OK"
    echo "Response: $HEALTH_RESPONSE"
else
    print_error "Health endpoint failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test API health endpoint
print_info "Testing API health endpoint..."
API_HEALTH_RESPONSE=$(curl -s http://localhost:8007/api/health/ 2>/dev/null)
if echo "$API_HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status "API health endpoint OK"
else
    print_error "API health endpoint failed"
    echo "Response: $API_HEALTH_RESPONSE"
fi

# Test chat endpoint with health query
print_info "Testing chat endpoint with health query..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8007/api/ai/chat/ \
    -H "Content-Type: application/json" \
    -d '{"message": "Tôi bị đau đầu, có thể làm gì?", "session_id": "test-session"}' 2>/dev/null)

if echo "$CHAT_RESPONSE" | grep -q "response"; then
    print_status "Chat endpoint working!"
    echo "Response: $(echo "$CHAT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CHAT_RESPONSE")"
else
    print_error "Chat endpoint failed"
    echo "Response: $CHAT_RESPONSE"
fi

# Test health info endpoint
print_info "Testing health info endpoint..."
HEALTH_INFO_RESPONSE=$(curl -s http://localhost:8007/api/ai/health/ 2>/dev/null)
if echo "$HEALTH_INFO_RESPONSE" | grep -q "advice"; then
    print_status "Health info endpoint working!"
    echo "Response: $(echo "$HEALTH_INFO_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_INFO_RESPONSE")"
else
    print_error "Health info endpoint failed"
    echo "Response: $HEALTH_INFO_RESPONSE"
fi

# Show service logs if there are errors
print_info "Checking for errors in logs..."
if docker-compose logs chatbot-service 2>&1 | grep -i "error\|exception\|traceback" | tail -5; then
    print_error "Found errors in logs (showing last 5 lines)"
else
    print_status "No errors found in recent logs"
fi

echo ""
print_info "Service URLs:"
echo "🌐 Health Check: http://localhost:8007/health/"
echo "💬 Chat API: http://localhost:8007/api/ai/chat/"
echo "🩺 Health Info: http://localhost:8007/api/ai/health/"
echo "👨‍💼 Admin: http://localhost:8007/admin/"

echo ""
print_info "Example curl commands:"
echo "curl -X POST http://localhost:8007/api/ai/chat/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Tôi bị đau đầu\", \"session_id\": \"test\"}'"
