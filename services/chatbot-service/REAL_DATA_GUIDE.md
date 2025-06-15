# Hướng dẫn tạo dữ liệu thực tế cho Knowledge Base

## 📝 Template để tạo nội dung chất lượng

### 1. Research Checklist
- [ ] Xác định chủ đề cần thiết (dựa trên thống kê bệnh tật VN)
- [ ] Tìm ít nhất 3 nguồn uy tín cho mỗi chủ đề
- [ ] Kiểm tra thông tin mới nhất (guidelines 2024-2025)
- [ ] Note lại mâu thuẫn giữa các nguồn (nếu có)

### 2. Content Structure Template
```json
{
  "knowledge_entry": {
    "title": "Tên chủ đề rõ ràng",
    "content": "Nội dung chi tiết với đầy đủ thông tin",
    "summary": "Tóm tắt 2-3 câu chính",
    "keywords": "từ khóa, tìm kiếm, liên quan",
    "difficulty_level": "BASIC/INTERMEDIATE/ADVANCED",
    "sources": [
      {
        "name": "Tên nguồn",
        "url": "Link tham khảo", 
        "type": "official/academic/clinical",
        "date": "Ngày cập nhật"
      }
    ],
    "medical_review": {
      "reviewer": "Tên bác sĩ",
      "credentials": "Chuyên khoa",
      "date": "Ngày review",
      "notes": "Ghi chú từ reviewer"
    }
  }
}
```

### 3. Quality Checklist
- [ ] Thông tin chính xác theo nguồn uy tín
- [ ] Ngôn ngữ dễ hiểu với người dân
- [ ] Có disclaimer phù hợp
- [ ] Không khuyến cáo y tế cụ thể
- [ ] Có hướng dẫn khi nào cần gặp bác sĩ

### 4. Priority Topics (Đề xuất cho VN)
1. **Bệnh phổ biến:**
   - Tăng huyết áp, Tiểu đường type 2
   - Viêm gan B, Lao phổi  
   - Đau đầu tension, Đau lưng
   
2. **Triệu chứng cần cấp cứu:**
   - Đau ngực, Khó thở cấp
   - Co giật, Ngất xỉu
   - Chảy máu không cầm được

3. **Chăm sóc sức khỏe:**
   - Dinh dưỡng cân bằng
   - Tập thể dục an toàn
   - Quản lý stress

### 5. Medical Review Process
```
Step 1: Content Draft → Step 2: Peer Review → Step 3: Medical Expert Review → Step 4: Final Approval
```

### 6. Continuous Update Process
- Monthly: Review user queries for content gaps
- Quarterly: Update based on new medical guidelines  
- Annually: Comprehensive content audit
- Ad-hoc: Emergency health information updates
