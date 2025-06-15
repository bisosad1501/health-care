import uuid
from django.db import models
from django.utils import timezone


class KnowledgeCategory(models.Model):
    """Danh mục kiến thức y tế"""
    
    CATEGORY_TYPES = [
        ('DISEASE', 'Bệnh lý'),
        ('SYMPTOM', 'Triệu chứng'),
        ('TREATMENT', 'Điều trị'),
        ('PREVENTION', 'Phòng ngừa'),
        ('MEDICATION', 'Thuốc'),
        ('PROCEDURE', 'Thủ thuật'),
        ('ANATOMY', 'Giải phẫu'),
        ('NUTRITION', 'Dinh dưỡng'),
        ('EMERGENCY', 'Cấp cứu'),
        ('FAQ', 'Câu hỏi thường gặp'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name="Loại danh mục")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, 
                              related_name='children', verbose_name="Danh mục cha")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Danh mục kiến thức"
        verbose_name_plural = "Danh mục kiến thức"
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class KnowledgeEntry(models.Model):
    """Bài viết kiến thức y tế"""
    
    CONTENT_TYPES = [
        ('ARTICLE', 'Bài viết'),
        ('FAQ', 'Câu hỏi thường gặp'),
        ('GUIDE', 'Hướng dẫn'),
        ('WARNING', 'Cảnh báo'),
        ('FACT', 'Thông tin y tế'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('BASIC', 'Cơ bản'),
        ('INTERMEDIATE', 'Trung bình'),
        ('ADVANCED', 'Nâng cao'),
        ('PROFESSIONAL', 'Chuyên nghiệp'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung")
    summary = models.TextField(max_length=500, blank=True, null=True, verbose_name="Tóm tắt")
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE, 
                                related_name='entries', verbose_name="Danh mục")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='ARTICLE', 
                                   verbose_name="Loại nội dung")
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='BASIC',
                                       verbose_name="Mức độ")
    keywords = models.TextField(blank=True, null=True, verbose_name="Từ khóa", 
                               help_text="Các từ khóa phân cách bằng dấu phẩy")
    tags = models.ManyToManyField('KnowledgeTag', blank=True, related_name='entries', verbose_name="Thẻ")
    
    # Metadata
    author = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tác giả")
    source = models.CharField(max_length=500, blank=True, null=True, verbose_name="Nguồn")
    last_reviewed = models.DateTimeField(blank=True, null=True, verbose_name="Xem xét lần cuối")
    reliability_score = models.FloatField(default=1.0, verbose_name="Điểm tin cậy")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    is_verified = models.BooleanField(default=False, verbose_name="Đã xác minh")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bài kiến thức"
        verbose_name_plural = "Bài kiến thức"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['content_type', 'is_active']),
            models.Index(fields=['keywords']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_keywords_list(self):
        """Trả về danh sách từ khóa"""
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',')]
        return []
    
    def increment_view_count(self):
        """Tăng lượt xem"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class KnowledgeTag(models.Model):
    """Thẻ cho kiến thức"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên thẻ")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Màu sắc")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Thẻ kiến thức"
        verbose_name_plural = "Thẻ kiến thức"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MedicalTerm(models.Model):
    """Thuật ngữ y tế"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=200, unique=True, verbose_name="Thuật ngữ")
    definition = models.TextField(verbose_name="Định nghĩa")
    vietnamese_term = models.CharField(max_length=200, blank=True, null=True, 
                                     verbose_name="Thuật ngữ tiếng Việt")
    pronunciation = models.CharField(max_length=300, blank=True, null=True, 
                                   verbose_name="Cách phát âm")
    synonyms = models.TextField(blank=True, null=True, verbose_name="Từ đồng nghĩa",
                               help_text="Các từ đồng nghĩa phân cách bằng dấu phẩy")
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE,
                                related_name='medical_terms', verbose_name="Danh mục")
    related_entries = models.ManyToManyField(KnowledgeEntry, blank=True,
                                           related_name='related_terms', verbose_name="Bài viết liên quan")
    
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Thuật ngữ y tế"
        verbose_name_plural = "Thuật ngữ y tế"
        ordering = ['term']
        indexes = [
            models.Index(fields=['term']),
            models.Index(fields=['vietnamese_term']),
        ]
    
    def __str__(self):
        return f"{self.term} ({self.vietnamese_term or 'N/A'})"
    
    def get_synonyms_list(self):
        """Trả về danh sách từ đồng nghĩa"""
        if self.synonyms:
            return [s.strip() for s in self.synonyms.split(',')]
        return []


class DiseaseInformation(models.Model):
    """Thông tin bệnh lý"""
    
    SEVERITY_LEVELS = [
        ('MILD', 'Nhẹ'),
        ('MODERATE', 'Vừa'),
        ('SEVERE', 'Nặng'),
        ('CRITICAL', 'Nguy kịch'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300, verbose_name="Tên bệnh")
    icd_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Mã ICD-10")
    description = models.TextField(verbose_name="Mô tả")
    causes = models.TextField(blank=True, null=True, verbose_name="Nguyên nhân")
    symptoms = models.TextField(blank=True, null=True, verbose_name="Triệu chứng")
    diagnosis = models.TextField(blank=True, null=True, verbose_name="Chẩn đoán")
    treatment = models.TextField(blank=True, null=True, verbose_name="Điều trị")
    prevention = models.TextField(blank=True, null=True, verbose_name="Phòng ngừa")
    complications = models.TextField(blank=True, null=True, verbose_name="Biến chứng")
    prognosis = models.TextField(blank=True, null=True, verbose_name="Tiên lượng")
    
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='MILD',
                                     verbose_name="Mức độ nghiêm trọng")
    is_contagious = models.BooleanField(default=False, verbose_name="Có lây nhiễm")
    is_chronic = models.BooleanField(default=False, verbose_name="Bệnh mãn tính")
    
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE,
                                related_name='diseases', verbose_name="Danh mục")
    related_diseases = models.ManyToManyField('self', blank=True, symmetrical=True,
                                            verbose_name="Bệnh liên quan")
    knowledge_entries = models.ManyToManyField(KnowledgeEntry, blank=True,
                                             related_name='diseases', verbose_name="Bài viết liên quan")
    
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Thông tin bệnh lý"
        verbose_name_plural = "Thông tin bệnh lý"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['icd_code']),
            models.Index(fields=['is_contagious', 'is_chronic']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.icd_code or 'N/A'})"


class SymptomInformation(models.Model):
    """Thông tin triệu chứng"""
    
    URGENCY_LEVELS = [
        ('LOW', 'Thấp'),
        ('MEDIUM', 'Trung bình'),
        ('HIGH', 'Cao'),
        ('EMERGENCY', 'Cấp cứu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Tên triệu chứng")
    description = models.TextField(verbose_name="Mô tả")
    body_part = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bộ phận cơ thể")
    urgency_level = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='LOW',
                                   verbose_name="Mức độ khẩn cấp")
    
    possible_causes = models.TextField(blank=True, null=True, verbose_name="Nguyên nhân có thể")
    when_to_see_doctor = models.TextField(blank=True, null=True, verbose_name="Khi nào cần gặp bác sĩ")
    home_remedies = models.TextField(blank=True, null=True, verbose_name="Cách xử lý tại nhà")
    
    related_diseases = models.ManyToManyField(DiseaseInformation, blank=True,
                                            related_name='symptoms', verbose_name="Bệnh liên quan")
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE,
                                related_name='symptoms', verbose_name="Danh mục")
    
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Thông tin triệu chứng"
        verbose_name_plural = "Thông tin triệu chứng"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['urgency_level']),
            models.Index(fields=['body_part']),
        ]
    
    def __str__(self):
        return self.name


class ChatbotResponse(models.Model):
    """Phản hồi của chatbot được lưu trữ"""
    
    RESPONSE_TYPES = [
        ('GENERAL', 'Thông tin chung'),
        ('SYMPTOM_CHECK', 'Kiểm tra triệu chứng'),
        ('DISEASE_INFO', 'Thông tin bệnh lý'),
        ('MEDICATION_INFO', 'Thông tin thuốc'),
        ('EMERGENCY', 'Cấp cứu'),
        ('APPOINTMENT', 'Đặt lịch hẹn'),
        ('FAQ', 'Câu hỏi thường gặp'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(verbose_name="Câu hỏi")
    response = models.TextField(verbose_name="Phản hồi")
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES, default='GENERAL',
                                   verbose_name="Loại phản hồi")
    
    # References to knowledge base
    referenced_entries = models.ManyToManyField(KnowledgeEntry, blank=True,
                                              related_name='chatbot_responses', verbose_name="Bài viết tham khảo")
    referenced_diseases = models.ManyToManyField(DiseaseInformation, blank=True,
                                               related_name='chatbot_responses', verbose_name="Bệnh tham khảo")
    referenced_symptoms = models.ManyToManyField(SymptomInformation, blank=True,
                                               related_name='chatbot_responses', verbose_name="Triệu chứng tham khảo")
    
    # Usage statistics
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Số lần sử dụng")
    confidence_score = models.FloatField(default=1.0, verbose_name="Điểm tin cậy")
    user_feedback = models.IntegerField(blank=True, null=True, verbose_name="Phản hồi người dùng",
                                       help_text="1-5 sao")
    
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Phản hồi chatbot"
        verbose_name_plural = "Phản hồi chatbot"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['response_type']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.get_response_type_display()}: {self.question[:50]}..."
    
    def increment_usage(self):
        """Tăng số lần sử dụng"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class KnowledgeSearchLog(models.Model):
    """Log tìm kiếm kiến thức"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.TextField(verbose_name="Truy vấn")
    results_count = models.PositiveIntegerField(verbose_name="Số kết quả")
    user_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP người dùng")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User agent")
    search_duration = models.FloatField(blank=True, null=True, verbose_name="Thời gian tìm kiếm (giây)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log tìm kiếm"
        verbose_name_plural = "Log tìm kiếm"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['query']),
        ]
    
    def __str__(self):
        return f"{self.query[:50]}... ({self.results_count} kết quả)"
