import uuid
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Model cho hội thoại"""
    
    CONVERSATION_TYPES = [
        ('HEALTH_ASSISTANT', 'Trợ lý sức khỏe AI'),
        ('DOCTOR_PATIENT', 'Bác sĩ - Bệnh nhân'),
        ('GENERAL_CHAT', 'Trò chuyện chung'),
        ('SYMPTOM_CHECK', 'Kiểm tra triệu chứng'),
        ('APPOINTMENT_BOOKING', 'Đặt lịch hẹn'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Đang hoạt động'),
        ('PAUSED', 'Tạm dừng'),
        ('COMPLETED', 'Hoàn thành'),
        ('ARCHIVED', 'Lưu trữ'),
        ('DELETED', 'Đã xóa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề")
    conversation_type = models.CharField(max_length=30, choices=CONVERSATION_TYPES, 
                                       default='HEALTH_ASSISTANT', verbose_name="Loại hội thoại")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='ACTIVE', verbose_name="Trạng thái")
    
    # User information - stored as string to avoid dependency on User service
    user_id = models.CharField(max_length=50, verbose_name="ID người dùng")
    user_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tên người dùng")
    user_role = models.CharField(max_length=50, blank=True, null=True, verbose_name="Vai trò người dùng")
    
    # For doctor-patient conversations
    doctor_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID bác sĩ")
    doctor_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tên bác sĩ")
    patient_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID bệnh nhân")
    patient_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tên bệnh nhân")
    
    # Metadata
    language = models.CharField(max_length=10, default='vi', verbose_name="Ngôn ngữ")
    priority = models.IntegerField(default=1, verbose_name="Độ ưu tiên")
    is_private = models.BooleanField(default=True, verbose_name="Riêng tư")
    
    # Reference to other services
    appointment_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID lịch hẹn")
    medical_record_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID hồ sơ y tế")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(blank=True, null=True, verbose_name="Tin nhắn cuối")
    ended_at = models.DateTimeField(blank=True, null=True, verbose_name="Kết thúc lúc")
    
    # AI specific fields
    ai_context = models.JSONField(default=dict, blank=True, verbose_name="Ngữ cảnh AI")
    ai_settings = models.JSONField(default=dict, blank=True, verbose_name="Cài đặt AI")
    
    class Meta:
        verbose_name = "Hội thoại"
        verbose_name_plural = "Hội thoại"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user_id', 'status']),
            models.Index(fields=['conversation_type', 'status']),
            models.Index(fields=['doctor_id', 'patient_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.conversation_type == 'DOCTOR_PATIENT':
            return f"BS {self.doctor_name or self.doctor_id} - BN {self.patient_name or self.patient_id}"
        else:
            return f"{self.get_conversation_type_display()} - {self.user_name or self.user_id}"
    
    def save(self, *args, **kwargs):
        """Override save để tự động tạo title nếu chưa có"""
        if not self.title:
            if self.conversation_type == 'DOCTOR_PATIENT':
                self.title = f"Tư vấn với BS {self.doctor_name or 'Bác sĩ'}"
            elif self.conversation_type == 'SYMPTOM_CHECK':
                self.title = "Kiểm tra triệu chứng"
            elif self.conversation_type == 'APPOINTMENT_BOOKING':
                self.title = "Đặt lịch hẹn"
            else:
                self.title = f"Trò chuyện {self.get_conversation_type_display()}"
        
        super().save(*args, **kwargs)
    
    def get_message_count(self):
        """Lấy số lượng tin nhắn"""
        return self.messages.count()
    
    def get_last_message(self):
        """Lấy tin nhắn cuối cùng"""
        return self.messages.order_by('-created_at').first()
    
    def update_last_message_time(self):
        """Cập nhật thời gian tin nhắn cuối"""
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at', 'updated_at'])
    
    def mark_as_completed(self):
        """Đánh dấu hội thoại đã hoàn thành"""
        self.status = 'COMPLETED'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at', 'updated_at'])
    
    def archive(self):
        """Lưu trữ hội thoại"""
        self.status = 'ARCHIVED'
        self.save(update_fields=['status', 'updated_at'])
    
    def get_participants(self):
        """Lấy danh sách người tham gia"""
        participants = [self.user_id]
        
        if self.conversation_type == 'DOCTOR_PATIENT':
            if self.doctor_id:
                participants.append(self.doctor_id)
            if self.patient_id and self.patient_id != self.user_id:
                participants.append(self.patient_id)
        
        return list(set(participants))
    
    def is_participant(self, user_id):
        """Kiểm tra user có phải participant không"""
        return user_id in self.get_participants()


class ConversationParticipant(models.Model):
    """Model cho người tham gia hội thoại"""
    
    PARTICIPANT_ROLES = [
        ('USER', 'Người dùng'),
        ('DOCTOR', 'Bác sĩ'),
        ('PATIENT', 'Bệnh nhân'),
        ('NURSE', 'Y tá'),
        ('ASSISTANT', 'Trợ lý'),
        ('AI', 'AI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, 
                                   related_name='participants', verbose_name="Hội thoại")
    user_id = models.CharField(max_length=50, verbose_name="ID người dùng")
    user_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tên người dùng")
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLES, verbose_name="Vai trò")
    
    # Permissions
    can_read = models.BooleanField(default=True, verbose_name="Có thể đọc")
    can_write = models.BooleanField(default=True, verbose_name="Có thể viết")
    can_moderate = models.BooleanField(default=False, verbose_name="Có thể điều hành")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    is_online = models.BooleanField(default=False, verbose_name="Đang online")
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name="Lần cuối trực tuyến")
    
    # Notifications
    notifications_enabled = models.BooleanField(default=True, verbose_name="Bật thông báo")
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True, verbose_name="Rời khỏi lúc")
    
    class Meta:
        verbose_name = "Người tham gia"
        verbose_name_plural = "Người tham gia"
        unique_together = ['conversation', 'user_id']
        indexes = [
            models.Index(fields=['conversation', 'is_active']),
            models.Index(fields=['user_id', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user_name or self.user_id} ({self.get_role_display()}) - {self.conversation}"
    
    def mark_as_online(self):
        """Đánh dấu online"""
        self.is_online = True
        self.last_seen = timezone.now()
        self.save(update_fields=['is_online', 'last_seen'])
    
    def mark_as_offline(self):
        """Đánh dấu offline"""
        self.is_online = False
        self.last_seen = timezone.now()
        self.save(update_fields=['is_online', 'last_seen'])
    
    def leave_conversation(self):
        """Rời khỏi hội thoại"""
        self.is_active = False
        self.left_at = timezone.now()
        self.save(update_fields=['is_active', 'left_at'])


class ConversationSummary(models.Model):
    """Tóm tắt hội thoại"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, 
                                      related_name='summary', verbose_name="Hội thoại")
    
    # Summary content
    summary = models.TextField(verbose_name="Tóm tắt")
    key_points = models.JSONField(default=list, verbose_name="Điểm chính")
    diagnosis_mentioned = models.TextField(blank=True, null=True, verbose_name="Chẩn đoán được đề cập")
    treatments_discussed = models.TextField(blank=True, null=True, verbose_name="Điều trị thảo luận")
    medications_mentioned = models.JSONField(default=list, verbose_name="Thuốc được đề cập")
    follow_up_required = models.BooleanField(default=False, verbose_name="Cần theo dõi")
    follow_up_notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú theo dõi")
    
    # Generated metadata
    sentiment_score = models.FloatField(default=0.0, verbose_name="Điểm cảm xúc")
    complexity_score = models.FloatField(default=0.0, verbose_name="Điểm phức tạp")
    satisfaction_score = models.FloatField(blank=True, null=True, verbose_name="Điểm hài lòng")
    
    # Generation info
    generated_by = models.CharField(max_length=50, default='AI', verbose_name="Tạo bởi")
    generated_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tóm tắt hội thoại"
        verbose_name_plural = "Tóm tắt hội thoại"
    
    def __str__(self):
        return f"Tóm tắt: {self.conversation}"


class ConversationTemplate(models.Model):
    """Template cho hội thoại"""
    
    TEMPLATE_TYPES = [
        ('GREETING', 'Chào hỏi'),
        ('SYMPTOM_INTAKE', 'Thu thập triệu chứng'),
        ('DIAGNOSIS_EXPLANATION', 'Giải thích chẩn đoán'),
        ('TREATMENT_PLAN', 'Kế hoạch điều trị'),
        ('MEDICATION_INSTRUCTION', 'Hướng dẫn dùng thuốc'),
        ('FOLLOW_UP', 'Theo dõi'),
        ('EMERGENCY_RESPONSE', 'Phản ứng cấp cứu'),
        ('CLOSING', 'Kết thúc'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Tên template")
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, verbose_name="Loại template")
    content = models.TextField(verbose_name="Nội dung")
    variables = models.JSONField(default=list, verbose_name="Biến số",
                               help_text="Danh sách các biến có thể thay thế trong template")
    
    # Usage conditions
    conversation_types = models.JSONField(default=list, verbose_name="Loại hội thoại áp dụng")
    user_roles = models.JSONField(default=list, verbose_name="Vai trò người dùng áp dụng")
    
    # Metadata
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Số lần sử dụng")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_by = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tạo bởi")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Template hội thoại"
        verbose_name_plural = "Template hội thoại"
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.get_template_type_display()}: {self.name}"
    
    def render(self, context=None):
        """Render template với context"""
        if not context:
            return self.content
        
        rendered_content = self.content
        for variable in self.variables:
            if variable in context:
                placeholder = f"{{{variable}}}"
                rendered_content = rendered_content.replace(placeholder, str(context[variable]))
        
        return rendered_content
    
    def increment_usage(self):
        """Tăng số lần sử dụng"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class Message(models.Model):
    """Model cho tin nhắn trong hội thoại"""
    
    MESSAGE_TYPES = [
        ('USER', 'Người dùng'),
        ('ASSISTANT', 'Trợ lý AI'),
        ('SYSTEM', 'Hệ thống'),
        ('DOCTOR', 'Bác sĩ'),
        ('NOTIFICATION', 'Thông báo'),
    ]
    
    CONTENT_TYPES = [
        ('TEXT', 'Văn bản'),
        ('IMAGE', 'Hình ảnh'),
        ('FILE', 'Tệp tin'),
        ('AUDIO', 'Âm thanh'),
        ('VIDEO', 'Video'),
        ('QUICK_REPLY', 'Trả lời nhanh'),
        ('CARD', 'Card'),
        ('CAROUSEL', 'Carousel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, 
                                   related_name='messages', verbose_name="Hội thoại")
    sender_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, 
                                 default='USER', verbose_name="Loại người gửi")
    content = models.TextField(verbose_name="Nội dung tin nhắn")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, 
                                  default='TEXT', verbose_name="Loại nội dung")
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata")
    is_edited = models.BooleanField(default=False, verbose_name="Đã chỉnh sửa")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Thời gian cập nhật")
    
    class Meta:
        db_table = 'conversations_message'
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender_type']),
            models.Index(fields=['content_type']),
        ]
    
    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}..."
    
    @property
    def is_from_user(self):
        return self.sender_type == 'USER'
    
    @property
    def is_from_assistant(self):
        return self.sender_type == 'ASSISTANT'
