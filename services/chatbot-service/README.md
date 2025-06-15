# Healthcare Chatbot Service

A comprehensive chatbot service for healthcare applications, built with Django and featuring AI integration, real-time messaging, and extensive medical knowledge base.

## Features

### 🧠 Knowledge Base
- Medical terminology dictionary
- Disease information database
- Symptom guidance system
- Treatment recommendations
- Preventive care information

### 💬 Conversations & Messaging
- Real-time chat functionality
- Message attachments and reactions
- Read receipts and status indicators
- Quick replies and message templates
- Conversation summaries and analytics

### 🤖 AI Integration
- OpenAI GPT integration for intelligent responses
- Healthcare-specific prompt templates
- Symptom analysis and health insights
- Intent recognition and classification
- Usage analytics and feedback system

### 🔄 Real-time Features
- WebSocket support for live messaging
- Real-time notifications
- Health monitoring alerts
- Live conversation updates

## Architecture

```
chatbot-service/
├── chatbot_service/          # Django project configuration
├── knowledge/                # Medical knowledge base
├── conversations/            # Conversation management
├── messages/                 # Message handling
├── ai/                       # AI integration and processing
├── websockets/              # Real-time WebSocket consumers
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── manage.py               # Django management
```

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+ (for WebSocket support)
- OpenAI API key (optional, for AI features)

### Installation

1. **Clone and setup**:
```bash
cd services/chatbot-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment variables**:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/chatbot_db"
export REDIS_URL="redis://localhost:6379/0"
export OPENAI_API_KEY="your-openai-api-key"  # Optional
export SECRET_KEY="your-secret-key"
export DEBUG=True
```

3. **Database setup**:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata knowledge/fixtures/initial_data.json
python manage.py loaddata ai/fixtures/ai_models.json
python manage.py loaddata messages/fixtures/message_templates.json
```

4. **Create admin user**:
```bash
python manage.py createsuperuser
```

5. **Run the service**:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Docker Setup

```bash
# Build the image
docker build -t chatbot-service .

# Run with environment variables
docker run -d \
  --name chatbot-service \
  -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  -e REDIS_URL="your-redis-url" \
  -e OPENAI_API_KEY="your-api-key" \
  chatbot-service
```

## API Endpoints

### Knowledge Base
- `GET /api/knowledge/categories/` - List knowledge categories
- `GET /api/knowledge/entries/` - List knowledge entries
- `GET /api/knowledge/diseases/` - Disease information
- `GET /api/knowledge/symptoms/` - Symptom information
- `POST /api/knowledge/search/` - Search knowledge base

### Conversations
- `GET /api/conversations/conversations/` - List conversations
- `POST /api/conversations/conversations/` - Create conversation
- `GET /api/conversations/conversations/{id}/` - Get conversation
- `POST /api/conversations/conversations/{id}/add_participant/` - Add participant
- `POST /api/conversations/conversations/{id}/generate_summary/` - Generate AI summary

### Messages
- `GET /api/messages/messages/` - List messages
- `POST /api/messages/messages/` - Send message
- `POST /api/messages/messages/{id}/react/` - Add reaction
- `POST /api/messages/messages/{id}/mark_read/` - Mark as read
- `GET /api/messages/messages/search/` - Search messages

### AI Services
- `POST /api/ai/chat/chat/` - Chat with AI
- `POST /api/ai/health-analysis/analyze_symptoms/` - Analyze symptoms
- `GET /api/ai/interactions/` - AI interaction history
- `POST /api/ai/interactions/{id}/feedback/` - Provide feedback

### WebSocket Endpoints
- `ws://localhost:8000/ws/chat/{conversation_id}/` - Real-time chat
- `ws://localhost:8000/ws/notifications/{user_id}/` - Notifications
- `ws://localhost:8000/ws/health-monitor/{user_id}/` - Health monitoring

## Configuration

### AI Settings
```python
# In settings.py
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-3.5-turbo'  # or 'gpt-4'
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.7
```

### WebSocket Settings
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## Usage Examples

### Basic Chat Integration
```python
import requests

# Send a message to AI
response = requests.post('http://localhost:8000/api/ai/chat/chat/', {
    'message': 'I have a headache, what should I do?',
    'conversation_id': 1
}, headers={'Authorization': 'Bearer your-token'})

print(response.json())
```

### WebSocket Chat
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/chat/1/');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('New message:', data.message);
};

// Send a message
socket.send(JSON.stringify({
    'message': 'Hello, I need help with my symptoms',
    'type': 'chat_message'
}));
```

### Health Analysis
```python
response = requests.post('http://localhost:8000/api/ai/health-analysis/analyze_symptoms/', {
    'symptoms': ['headache', 'fever', 'nausea'],
    'duration': '2 days',
    'severity': 'moderate'
}, headers={'Authorization': 'Bearer your-token'})

analysis = response.json()
print('Possible conditions:', analysis['possible_conditions'])
print('Recommendations:', analysis['recommendations'])
```

## Development

### Adding New Knowledge
1. Use Django admin at `/admin/` to add knowledge entries
2. Or use fixtures and `loaddata` command
3. Categories, diseases, symptoms, and medical terms are all manageable

### Extending AI Capabilities
1. Create new prompt templates in AI admin
2. Add new intent handlers in `ai/services.py`
3. Extend the `HealthcareAIService` class

### Custom WebSocket Consumers
1. Extend base consumers in `websockets/consumers.py`
2. Add new routing in `websockets/routing.py`
3. Handle custom message types and events

## Security

- All API endpoints require authentication
- WebSocket connections are authenticated
- Sensitive data is encrypted in database
- Rate limiting implemented for AI calls
- Input validation and sanitization

## Monitoring

- AI usage logs and analytics
- Message delivery status
- WebSocket connection monitoring
- Error tracking and reporting
- Performance metrics collection

## Deployment

The service is containerized and ready for deployment with:
- Docker/Kubernetes
- Environment-based configuration
- Health check endpoints
- Graceful shutdown handling
- Auto-scaling support

## Contributing

1. Follow Django best practices
2. Add tests for new features
3. Update documentation
4. Use proper error handling
5. Follow medical data privacy guidelines

## License

This healthcare chatbot service is designed for educational and development purposes. Ensure compliance with healthcare regulations (HIPAA, etc.) before production use.

## Support

For issues and questions:
- Check the Django logs
- Review API documentation  
- Test WebSocket connections
- Verify AI service configuration
- Monitor database performance
