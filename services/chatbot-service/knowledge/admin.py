from django.contrib import admin
from .models import (
    KnowledgeCategory, KnowledgeEntry, KnowledgeTag, MedicalTerm,
    DiseaseInformation, SymptomInformation, ChatbotResponse, KnowledgeSearchLog
)


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'parent', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category_type', 'name']
    list_editable = ['is_active']


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'difficulty_level', 
                   'is_verified', 'view_count', 'updated_at']
    list_filter = ['category', 'content_type', 'difficulty_level', 'is_verified', 'is_active']
    search_fields = ['title', 'content', 'keywords']
    ordering = ['-updated_at']
    list_editable = ['is_verified', 'is_active']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']


@admin.register(KnowledgeTag)
class KnowledgeTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']


@admin.register(MedicalTerm)
class MedicalTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'vietnamese_term', 'category', 'is_active', 'updated_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['term', 'vietnamese_term', 'definition']
    ordering = ['term']
    list_editable = ['is_active']
    filter_horizontal = ['related_entries']


@admin.register(DiseaseInformation)
class DiseaseInformationAdmin(admin.ModelAdmin):
    list_display = ['name', 'icd_code', 'category', 'severity_level', 
                   'is_contagious', 'is_chronic', 'is_active']
    list_filter = ['category', 'severity_level', 'is_contagious', 'is_chronic', 'is_active']
    search_fields = ['name', 'icd_code', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    filter_horizontal = ['related_diseases', 'knowledge_entries']


@admin.register(SymptomInformation)
class SymptomInformationAdmin(admin.ModelAdmin):
    list_display = ['name', 'body_part', 'urgency_level', 'category', 'is_active']
    list_filter = ['urgency_level', 'body_part', 'category', 'is_active']
    search_fields = ['name', 'description', 'body_part']
    ordering = ['name']
    list_editable = ['is_active']
    filter_horizontal = ['related_diseases']


@admin.register(ChatbotResponse)
class ChatbotResponseAdmin(admin.ModelAdmin):
    list_display = ['question', 'response_type', 'confidence_score', 
                   'usage_count', 'user_feedback', 'is_active']
    list_filter = ['response_type', 'is_active', 'created_at']
    search_fields = ['question', 'response']
    ordering = ['-updated_at']
    list_editable = ['is_active']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    filter_horizontal = ['referenced_entries', 'referenced_diseases', 'referenced_symptoms']


@admin.register(KnowledgeSearchLog)
class KnowledgeSearchLogAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'search_duration', 'created_at']
    list_filter = ['created_at', 'results_count']
    search_fields = ['query']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
