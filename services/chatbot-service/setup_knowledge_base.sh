#!/bin/bash

# Healthcare Knowledge Base Setup Script
# This script sets up the knowledge base for the healthcare chatbot

echo "🏥 Healthcare Knowledge Base Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "manage.py" ]; then
    print_error "Please run this script from the chatbot-service directory"
    exit 1
fi

# Step 1: Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi

# Step 2: Run migrations
print_status "Running database migrations..."
python manage.py makemigrations knowledge
python manage.py migrate

if [ $? -ne 0 ]; then
    print_error "Failed to run migrations"
    exit 1
fi

# Step 3: Create directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p knowledge/fixtures/data
mkdir -p media/uploads

# Step 4: Load sample data
print_status "Loading sample knowledge base data..."
python manage.py load_knowledge_data --data-file=knowledge/fixtures/sample_knowledge_data.json

if [ $? -ne 0 ]; then
    print_warning "Failed to load sample data - you may need to create it manually"
fi

# Step 5: Build search index
print_status "Building search index..."
python manage.py build_search_index

if [ $? -ne 0 ]; then
    print_warning "Failed to build search index"
fi

# Step 6: Download NLTK data
print_status "Downloading NLTK data..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'Failed to download NLTK data: {e}')
"

# Step 7: Test the setup
print_status "Testing knowledge base setup..."
python manage.py shell -c "
from knowledge.models import KnowledgeEntry, KnowledgeCategory
from knowledge.services import KnowledgeSearchEngine

# Test database
print(f'Categories: {KnowledgeCategory.objects.count()}')
print(f'Entries: {KnowledgeEntry.objects.count()}')

# Test search engine
try:
    search_engine = KnowledgeSearchEngine()
    results = search_engine.search_knowledge('tim mạch')
    print(f'Search test: {len(results)} results found')
except Exception as e:
    print(f'Search test failed: {e}')
"

# Step 8: Create superuser (optional)
read -p "Do you want to create a superuser for admin access? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating superuser..."
    python manage.py createsuperuser
fi

# Step 9: Start development server
print_status "Setup completed successfully!"
echo
echo "📚 Knowledge Base Statistics:"
python manage.py shell -c "
from knowledge.models import *
print(f'  - Categories: {KnowledgeCategory.objects.count()}')
print(f'  - Knowledge Entries: {KnowledgeEntry.objects.count()}')
print(f'  - Diseases: {DiseaseInformation.objects.count()}')
print(f'  - Symptoms: {SymptomInformation.objects.count()}')
print(f'  - Medical Terms: {MedicalTerm.objects.count()}')
"

echo
echo "🚀 Ready to start the server!"
echo "Run: python manage.py runserver"
echo
echo "📖 API Endpoints:"
echo "  - Knowledge Base: http://localhost:8000/api/knowledge/"
echo "  - Search: http://localhost:8000/api/knowledge/search/"
echo "  - Symptom Check: http://localhost:8000/api/knowledge/symptom-check/"
echo "  - Admin: http://localhost:8000/admin/"
echo
echo "🔧 Management Commands:"
echo "  - Load data: python manage.py load_knowledge_data"
echo "  - Build index: python manage.py build_search_index"
echo "  - Shell: python manage.py shell"

# Optional: Start server
read -p "Do you want to start the development server now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting development server..."
    python manage.py runserver
fi
