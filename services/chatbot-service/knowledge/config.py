"""
Configuration file for healthcare AI chatbot
"""

# OpenAI Configuration
OPENAI_CONFIG = {
    'model': 'gpt-3.5-turbo',
    'max_tokens': 1000,
    'temperature': 0.7,
    'top_p': 1.0,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0,
}

# Knowledge Base Configuration
KNOWLEDGE_BASE_CONFIG = {
    'search_limit': 10,
    'min_relevance_score': 0.1,
    'cache_timeout': 3600,  # 1 hour
    'rebuild_index_interval': 86400,  # 24 hours
}

# Symptom Checking Configuration
SYMPTOM_CHECK_CONFIG = {
    'similarity_threshold': 0.7,
    'max_symptoms': 10,
    'urgency_levels': {
        'LOW': 0,
        'MEDIUM': 1,
        'HIGH': 2,
        'EMERGENCY': 3
    }
}

# Chatbot Response Configuration
CHATBOT_CONFIG = {
    'default_confidence_threshold': 0.5,
    'response_types': {
        'GENERAL': 'Thông tin chung',
        'SYMPTOM_CHECK': 'Kiểm tra triệu chứng',
        'DISEASE_INFO': 'Thông tin bệnh lý',
        'MEDICATION_INFO': 'Thông tin thuốc',
        'EMERGENCY': 'Cấp cứu',
        'APPOINTMENT': 'Đặt lịch hẹn',
        'FAQ': 'Câu hỏi thường gặp',
    },
    'emergency_keywords': [
        'cấp cứu', 'nguy hiểm', 'nghiêm trọng', 'khẩn cấp', 'gấp',
        'đau dữ dội', 'khó thở nặng', 'ngất xỉu', 'co giật', 'chảy máu',
        'đột quỵ', 'đau tim', 'ngộ độc'
    ],
    'disclaimers': {
        'general': 'Thông tin này chỉ mang tính tham khảo, không thay thế chẩn đoán y khoa chuyên nghiệp.',
        'symptom_check': 'Kết quả kiểm tra triệu chứng chỉ mang tính tham khảo. Hãy tham khảo ý kiến bác sĩ để có chẩn đoán chính xác.',
        'emergency': 'Trong tình huống cấp cứu, hãy gọi 115 hoặc đến cơ sở y tế gần nhất ngay lập tức.',
        'medication': 'Thông tin về thuốc chỉ mang tính tham khảo. Hãy tham khảo ý kiến bác sĩ hoặc dược sĩ trước khi sử dụng.'
    }
}

# Vietnamese Text Processing Configuration
VIETNAMESE_CONFIG = {
    'stopwords': [
        'và', 'của', 'với', 'từ', 'trong', 'trên', 'dưới', 'về', 'cho', 'để',
        'khi', 'nếu', 'vì', 'nhưng', 'mà', 'rồi', 'đã', 'sẽ', 'có', 'là',
        'được', 'bị', 'các', 'những', 'này', 'đó', 'ở', 'tại', 'theo', 'như',
        'chỉ', 'cũng', 'đều', 'cả', 'thì', 'hay', 'hoặc', 'nên', 'phải', 'cần'
    ],
    'medical_keywords': [
        'bệnh', 'triệu chứng', 'điều trị', 'thuốc', 'bác sĩ', 'bệnh viện',
        'khám', 'chẩn đoán', 'phòng ngừa', 'sức khỏe', 'y tế', 'cấp cứu',
        'đau', 'nhức', 'sốt', 'ho', 'viêm', 'nhiễm'
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/chatbot.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'knowledge': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'ai': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    'track_searches': True,
    'track_responses': True,
    'retention_days': 90,
    'export_formats': ['json', 'csv', 'excel']
}
