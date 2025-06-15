# Healthcare Knowledge Base - Hướng Dẫn Xây Dựng và Sử Dụng

## 📚 Tổng Quan

Knowledge Base của Healthcare Chatbot là hệ thống lưu trữ và quản lý kiến thức y tế, bao gồm:

- **Thông tin bệnh lý**: Mô tả, nguyên nhân, triệu chứng, điều trị
- **Triệu chứng**: Phân loại và mức độ khẩn cấp
- **Thuật ngữ y tế**: Định nghĩa và giải thích
- **Bài viết kiến thức**: Hướng dẫn, FAQ, thông tin tham khảo
- **Phản hồi chatbot**: Lưu trữ và học từ các cuộc hội thoại

## 🏗️ Kiến Trúc Hệ Thống

### 1. Models (Mô hình dữ liệu)

```python
# Các model chính
- KnowledgeCategory: Danh mục kiến thức
- KnowledgeEntry: Bài viết kiến thức
- DiseaseInformation: Thông tin bệnh lý
- SymptomInformation: Thông tin triệu chứng
- MedicalTerm: Thuật ngữ y tế
- ChatbotResponse: Phản hồi chatbot
```

### 2. Services (Dịch vụ)

```python
# Các service chính
- KnowledgeSearchEngine: Tìm kiếm kiến thức
- SymptomChecker: Kiểm tra triệu chứng
- VietnameseTextProcessor: Xử lý văn bản tiếng Việt
- HealthcareAIService: Tích hợp AI
```

### 3. APIs (Giao diện lập trình)

```python
# Endpoints chính
/api/knowledge/categories/     # Danh mục
/api/knowledge/entries/        # Bài viết
/api/knowledge/search/         # Tìm kiếm
/api/knowledge/symptom-check/  # Kiểm tra triệu chứng
/api/knowledge/chatbot/        # Chatbot response
```

## 🚀 Cài Đặt và Thiết Lập

### 1. Thiết Lập Tự Động

```bash
# Chạy script thiết lập
cd services/chatbot-service
./setup_knowledge_base.sh
```

### 2. Thiết Lập Thủ Công

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Chạy migrations  
python manage.py makemigrations knowledge
python manage.py migrate

# 3. Load dữ liệu mẫu
python manage.py load_knowledge_data

# 4. Build search index
python manage.py build_search_index

# 5. Tạo superuser
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

## 📝 Quản Lý Dữ Liệu

### 1. Load Dữ Liệu từ JSON

```bash
# Load từ file mẫu
python manage.py load_knowledge_data

# Load từ file tùy chỉnh
python manage.py load_knowledge_data --data-file=path/to/data.json

# Xóa dữ liệu cũ trước khi load
python manage.py load_knowledge_data --clear-existing
```

### 2. Quản Lý qua Admin Interface

```python
# Truy cập Django Admin
http://localhost:8000/admin/

# Các tính năng:
- Tạo/sửa/xóa categories
- Quản lý knowledge entries
- Import/export dữ liệu
- Xem thống kê sử dụng
```

### 3. Cấu Trúc Dữ Liệu JSON

```json
{
  "categories": [
    {
      "name": "Tim Mạch",
      "category_type": "DISEASE",
      "description": "Các bệnh lý tim mạch"
    }
  ],
  "knowledge_entries": [
    {
      "title": "Tăng huyết áp",
      "content": "Nội dung chi tiết...",
      "category": "Tim Mạch",
      "keywords": "huyết áp, tim mạch",
      "tags": ["tim-mạch", "phòng-ngừa"]
    }
  ]
}
```

## 🔍 Tìm Kiếm và AI

### 1. Search Engine

```python
from knowledge.services import KnowledgeSearchEngine

search_engine = KnowledgeSearchEngine()
results = search_engine.search_knowledge(
    query="tăng huyết áp",
    filters={'category': 'DISEASE'},
    limit=10
)
```

### 2. Symptom Checker

```python
from knowledge.services import SymptomChecker

checker = SymptomChecker()
result = checker.check_symptoms(
    symptoms=["đau đầu", "chóng mặt"],
    context={'age': 45, 'gender': 'male'}
)
```

### 3. AI Integration

```python
from ai.healthcare_ai_service import HealthcareAIService

ai_service = HealthcareAIService()
response = ai_service.generate_response(
    user_query="Tôi bị đau đầu và chóng mặt",
    context={'user_id': 123}
)
```

## 🔧 API Usage

### 1. Tìm Kiếm Knowledge

```javascript
// POST /api/knowledge/search/
{
  "query": "tăng huyết áp",
  "filters": {
    "category": "DISEASE",
    "difficulty": "BASIC"
  },
  "limit": 10
}
```

### 2. Kiểm Tra Triệu Chứng

```javascript
// POST /api/knowledge/symptom-check/
{
  "symptoms": ["đau đầu", "chóng mặt"],
  "context": {
    "age": 45,
    "gender": "male",
    "medical_history": ["tăng huyết áp"]
  }
}
```

### 3. Chatbot Response

```javascript
// POST /api/knowledge/chatbot/
{
  "query": "Tôi bị đau ngực, có nguy hiểm không?",
  "context": {
    "user_id": 123,
    "conversation_id": "abc-123"
  }
}
```

## 📊 Monitoring và Analytics

### 1. Thống Kê Knowledge Base

```bash
# Xem thống kê
python manage.py shell -c "
from knowledge.models import *
print(f'Entries: {KnowledgeEntry.objects.count()}')
print(f'Categories: {KnowledgeCategory.objects.count()}')
"
```

### 2. Search Analytics

```python
# Xem log tìm kiếm
from knowledge.models import KnowledgeSearchLog
recent_searches = KnowledgeSearchLog.objects.order_by('-created_at')[:10]
```

### 3. Chatbot Performance

```python
# Xem analytics chatbot
from ai.healthcare_ai_service import HealthcareAIService
ai_service = HealthcareAIService()
analytics = ai_service.get_response_analytics()
```

## 🛠️ Tùy Chỉnh và Mở Rộng

### 1. Thêm Loại Knowledge Mới

```python
# Trong models.py
class NewKnowledgeType(models.Model):
    name = models.CharField(max_length=200)
    # Thêm fields khác...
    
    class Meta:
        verbose_name = "Loại Knowledge Mới"
```

### 2. Tùy Chỉnh Search Algorithm

```python
# Trong services.py
class CustomSearchEngine(KnowledgeSearchEngine):
    def custom_search_method(self, query):
        # Implement custom logic
        pass
```

### 3. Tích Hợp AI Models Khác

```python
# Thêm vào ai/healthcare_ai_service.py
def integrate_new_ai_model(self):
    # Tích hợp model mới
    pass
```

## 🔒 Bảo Mật và Quyền Truy Cập

### 1. API Authentication

```python
# Trong settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 2. Data Privacy

```python
# Anonymize sensitive data
def anonymize_user_data(data):
    # Remove personal information
    return cleaned_data
```

## 📈 Performance Optimization

### 1. Database Indexing

```python
# Trong models.py
class Meta:
    indexes = [
        models.Index(fields=['title', 'category']),
        models.Index(fields=['keywords']),
    ]
```

### 2. Caching

```python
# Sử dụng Redis cache
from django.core.cache import cache

def get_cached_search_results(query):
    cache_key = f"search:{hash(query)}"
    return cache.get(cache_key)
```

### 3. Background Tasks

```python
# Sử dụng Celery
from celery import shared_task

@shared_task
def rebuild_search_index():
    search_engine = KnowledgeSearchEngine()
    search_engine.build_search_index()
```

## 🐛 Troubleshooting

### 1. Lỗi Thường Gặp

```bash
# Lỗi migration
python manage.py migrate --fake-initial

# Lỗi search index
python manage.py build_search_index --rebuild

# Lỗi dependencies
pip install -r requirements.txt --upgrade
```

### 2. Debug Mode

```python
# Trong settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'knowledge': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📚 Tài Liệu Tham Khảo

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Scikit-learn](https://scikit-learn.org/)
- [NLTK](https://www.nltk.org/)
- [OpenAI API](https://platform.openai.com/docs)

## 🤝 Đóng Góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Tạo Pull Request

## 📞 Hỗ Trợ

- Email: support@healthcare-chatbot.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]
