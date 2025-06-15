#!/bin/bash

# 🚀 SCRIPT NHANH CHÓNG THU THẬP KNOWLEDGE BASE

echo "🏥 THU THẬP KNOWLEDGE BASE TỪ NGUỒN UY TÍN"
echo "============================================="

# Step 1: Install dependencies
echo "📦 Cài đặt dependencies..."
pip install requests beautifulsoup4 lxml

# Step 2: Chạy script thu thập
echo "🔍 Thu thập dữ liệu từ nguồn uy tín..."
python collect_trusted_data.py

# Step 3: Load vào database
echo "💾 Load dữ liệu vào database..."
python manage.py load_knowledge_data --data-file=trusted_health_knowledge.json --clear-existing

# Step 4: Build search index
echo "🔍 Build search index..."
python manage.py build_search_index

# Step 5: Test
echo "🧪 Test hệ thống..."
python manage.py shell -c "
from knowledge.models import KnowledgeEntry, DiseaseInformation, SymptomInformation
from knowledge.services import KnowledgeSearchEngine

print(f'📊 Thống kê Knowledge Base:')
print(f'   - Knowledge Entries: {KnowledgeEntry.objects.count()}')
print(f'   - Diseases: {DiseaseInformation.objects.count()}')
print(f'   - Symptoms: {SymptomInformation.objects.count()}')

# Test search
search_engine = KnowledgeSearchEngine()
results = search_engine.search_knowledge('tăng huyết áp')
print(f'   - Search test: {len(results)} results found')

if results:
    print(f'   - Top result: {results[0][\"entry\"].title}')
"

echo "✅ HOÀN THÀNH! Knowledge Base đã sẵn sàng sử dụng"
echo ""
echo "📈 Bạn có thể:"
echo "   - Start server: python manage.py runserver"
echo "   - Test API: curl -X POST http://localhost:8000/api/knowledge/search/ -H 'Content-Type: application/json' -d '{\"query\": \"tim mạch\"}'"
echo "   - Admin: http://localhost:8000/admin/"
