from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Conversation, ConversationParticipant, ConversationSummary, ConversationTemplate


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0
    readonly_fields = ['joined_at', 'left_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'conversation_type', 'status', 'priority',
        'created_by', 'participant_count', 'message_count',
        'created_at', 'is_archived'
    ]
    list_filter = [
        'conversation_type', 'status', 'priority', 'is_archived',
        'created_at', 'updated_at'
    ]
    search_fields = ['title', 'created_by__username', 'metadata']
    readonly_fields = ['created_at', 'updated_at', 'archived_at']
    inlines = [ConversationParticipantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'conversation_type', 'status', 'priority')
        }),
        ('Participants', {
            'fields': ('created_by',),
            'description': 'Participants are managed through the inline section below.'
        }),
        ('Archive', {
            'fields': ('is_archived', 'archived_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def participant_count(self, obj):
        return obj.participants.filter(is_active=True).count()
    participant_count.short_description = 'Active Participants'
    
    def message_count(self, obj):
        count = obj.messages.count()
        if count > 0:
            url = reverse('admin:messages_message_changelist') + f'?conversation__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    message_count.short_description = 'Messages'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by').prefetch_related('participants')


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = [
        'conversation', 'user', 'role', 'is_active',
        'joined_at', 'left_at'
    ]
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = [
        'conversation__title', 'user__username', 'user__email'
    ]
    readonly_fields = ['joined_at', 'left_at']
    
    fieldsets = (
        ('Participant Information', {
            'fields': ('conversation', 'user', 'role')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_at', 'left_at')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'user')


@admin.register(ConversationSummary)
class ConversationSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'conversation', 'summary_type', 'created_by',
        'created_at', 'summary_preview'
    ]
    list_filter = ['summary_type', 'created_at']
    search_fields = [
        'conversation__title', 'summary_text', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Summary Information', {
            'fields': ('conversation', 'summary_type', 'created_by')
        }),
        ('Content', {
            'fields': ('summary_text', 'key_points', 'action_items')
        }),
        ('Participants Summary', {
            'fields': ('participants_summary',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def summary_preview(self, obj):
        if obj.summary_text:
            preview = obj.summary_text[:100]
            return preview + "..." if len(obj.summary_text) > 100 else preview
        return "No summary"
    summary_preview.short_description = 'Summary Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'created_by')


@admin.register(ConversationTemplate)
class ConversationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type', 'category', 'is_active',
        'created_by', 'usage_count', 'created_at'
    ]
    list_filter = [
        'template_type', 'category', 'is_active', 'created_at'
    ]
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'usage_count_display']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'template_type', 'category')
        }),
        ('Content', {
            'fields': ('initial_message', 'suggested_responses')
        }),
        ('Settings', {
            'fields': ('is_active', 'created_by')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('usage_count_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def usage_count(self, obj):
        # Count conversations that used this template
        from .models import Conversation
        return Conversation.objects.filter(
            metadata__template_id=obj.id
        ).count()
    usage_count.short_description = 'Times Used'
    
    def usage_count_display(self, obj):
        count = self.usage_count(obj)
        if count > 0:
            return f"{count} conversations created from this template"
        return "Not used yet"
    usage_count_display.short_description = 'Usage Statistics'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


# Customization for better admin experience
admin.site.site_header = "Healthcare Chatbot Administration"
admin.site.site_title = "Chatbot Admin"
admin.site.index_title = "Conversation Management"
