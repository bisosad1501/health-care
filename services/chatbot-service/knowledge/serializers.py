from rest_framework import serializers
from .models import (
    KnowledgeCategory, KnowledgeEntry, KnowledgeTag, MedicalTerm,
    DiseaseInformation, SymptomInformation, ChatbotResponse, KnowledgeSearchLog
)


class KnowledgeCategorySerializer(serializers.ModelSerializer):
    """Serializer cho KnowledgeCategory"""
    
    children = serializers.SerializerMethodField()
    entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeCategory
        fields = ['id', 'name', 'category_type', 'description', 'parent', 
                 'is_active', 'children', 'entries_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'children', 'entries_count']
    
    def get_children(self, obj):
        """Lấy danh sách danh mục con"""
        children = obj.children.filter(is_active=True)
        return KnowledgeCategorySerializer(children, many=True, context=self.context).data
    
    def get_entries_count(self, obj):
        """Đếm số bài viết trong danh mục"""
        return obj.entries.filter(is_active=True).count()


class KnowledgeTagSerializer(serializers.ModelSerializer):
    """Serializer cho KnowledgeTag"""
    
    class Meta:
        model = KnowledgeTag
        fields = ['id', 'name', 'description', 'color', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class KnowledgeEntrySerializer(serializers.ModelSerializer):
    """Serializer cho KnowledgeEntry"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = KnowledgeTagSerializer(many=True, read_only=True)
    keywords_list = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeEntry
        fields = ['id', 'title', 'content', 'summary', 'category', 'category_name',
                 'content_type', 'difficulty_level', 'keywords', 'keywords_list',
                 'tags', 'author', 'source', 'last_reviewed', 'reliability_score',
                 'is_active', 'is_verified', 'view_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at', 
                           'category_name', 'keywords_list']
    
    def get_keywords_list(self, obj):
        """Trả về danh sách từ khóa"""
        return obj.get_keywords_list()


class KnowledgeEntryListSerializer(serializers.ModelSerializer):
    """Serializer tóm tắt cho danh sách KnowledgeEntry"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = KnowledgeTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = KnowledgeEntry
        fields = ['id', 'title', 'summary', 'category_name', 'content_type',
                 'difficulty_level', 'tags', 'reliability_score', 'view_count',
                 'is_verified', 'updated_at']


class MedicalTermSerializer(serializers.ModelSerializer):
    """Serializer cho MedicalTerm"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    synonyms_list = serializers.SerializerMethodField()
    related_entries = KnowledgeEntryListSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalTerm
        fields = ['id', 'term', 'definition', 'vietnamese_term', 'pronunciation',
                 'synonyms', 'synonyms_list', 'category', 'category_name',
                 'related_entries', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 'synonyms_list']
    
    def get_synonyms_list(self, obj):
        """Trả về danh sách từ đồng nghĩa"""
        return obj.get_synonyms_list()


class DiseaseInformationSerializer(serializers.ModelSerializer):
    """Serializer cho DiseaseInformation"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    related_diseases = serializers.SerializerMethodField()
    symptoms = serializers.SerializerMethodField()
    knowledge_entries = KnowledgeEntryListSerializer(many=True, read_only=True)
    
    class Meta:
        model = DiseaseInformation
        fields = ['id', 'name', 'icd_code', 'description', 'causes', 'symptoms',
                 'diagnosis', 'treatment', 'prevention', 'complications', 'prognosis',
                 'severity_level', 'is_contagious', 'is_chronic', 'category',
                 'category_name', 'related_diseases', 'knowledge_entries',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 
                           'related_diseases', 'symptoms']
    
    def get_related_diseases(self, obj):
        """Lấy thông tin bệnh liên quan"""
        related = obj.related_diseases.filter(is_active=True)[:3]
        return [{'id': str(d.id), 'name': d.name, 'icd_code': d.icd_code} for d in related]
    
    def get_symptoms(self, obj):
        """Lấy danh sách triệu chứng liên quan"""
        symptoms = obj.symptoms.filter(is_active=True)[:5]
        return [{'id': str(s.id), 'name': s.name, 'urgency_level': s.urgency_level} for s in symptoms]


class SymptomInformationSerializer(serializers.ModelSerializer):
    """Serializer cho SymptomInformation"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    related_diseases = serializers.SerializerMethodField()
    
    class Meta:
        model = SymptomInformation
        fields = ['id', 'name', 'description', 'body_part', 'urgency_level',
                 'possible_causes', 'when_to_see_doctor', 'home_remedies',
                 'category', 'category_name', 'related_diseases',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 'related_diseases']
    
    def get_related_diseases(self, obj):
        """Lấy thông tin bệnh liên quan"""
        diseases = obj.related_diseases.filter(is_active=True)[:3]
        return [{'id': str(d.id), 'name': d.name, 'icd_code': d.icd_code} for d in diseases]


class ChatbotResponseSerializer(serializers.ModelSerializer):
    """Serializer cho ChatbotResponse"""
    
    referenced_entries = KnowledgeEntryListSerializer(many=True, read_only=True)
    referenced_diseases = serializers.SerializerMethodField()
    referenced_symptoms = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatbotResponse
        fields = ['id', 'question', 'response', 'response_type', 'referenced_entries',
                 'referenced_diseases', 'referenced_symptoms', 'usage_count',
                 'confidence_score', 'user_feedback', 'is_active',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at',
                           'referenced_entries', 'referenced_diseases', 'referenced_symptoms']
    
    def get_referenced_diseases(self, obj):
        """Lấy thông tin bệnh được tham khảo"""
        diseases = obj.referenced_diseases.filter(is_active=True)
        return [{'id': str(d.id), 'name': d.name, 'icd_code': d.icd_code} for d in diseases]
    
    def get_referenced_symptoms(self, obj):
        """Lấy thông tin triệu chứng được tham khảo"""
        symptoms = obj.referenced_symptoms.filter(is_active=True)
        return [{'id': str(s.id), 'name': s.name, 'urgency_level': s.urgency_level} for s in symptoms]


class KnowledgeSearchSerializer(serializers.Serializer):
    """Serializer cho tìm kiếm kiến thức"""
    
    query = serializers.CharField(max_length=500, required=True)
    category = serializers.CharField(max_length=50, required=False)
    content_type = serializers.CharField(max_length=20, required=False)
    difficulty_level = serializers.CharField(max_length=20, required=False)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)


class SymptomCheckSerializer(serializers.Serializer):
    """Serializer cho kiểm tra triệu chứng"""
    
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=1,
        max_length=10,
        required=True
    )
    age = serializers.IntegerField(min_value=0, max_value=150, required=False)
    gender = serializers.ChoiceField(choices=['M', 'F', 'OTHER'], required=False)
    duration = serializers.CharField(max_length=100, required=False)
    severity = serializers.ChoiceField(choices=['MILD', 'MODERATE', 'SEVERE'], required=False)


class KnowledgeRecommendationSerializer(serializers.Serializer):
    """Serializer cho gợi ý kiến thức"""
    
    user_query = serializers.CharField(max_length=1000, required=True)
    context = serializers.JSONField(required=False)
    max_recommendations = serializers.IntegerField(min_value=1, max_value=20, default=5)


class FeedbackSerializer(serializers.Serializer):
    """Serializer cho phản hồi người dùng"""
    
    response_id = serializers.UUIDField(required=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    comment = serializers.CharField(max_length=1000, required=False)


class KnowledgeStatsSerializer(serializers.Serializer):
    """Serializer cho thống kê kiến thức"""
    
    total_entries = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_diseases = serializers.IntegerField()
    total_symptoms = serializers.IntegerField()
    total_terms = serializers.IntegerField()
    most_viewed_entries = serializers.ListField()
    recent_searches = serializers.ListField()
    response_stats = serializers.DictField()
