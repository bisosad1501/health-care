#!/usr/bin/env python3
"""
Demo script để test knowledge base đã thu thập
Chỉ hiển thị dữ liệu không cần database phức tạp
"""

import json
import sys
from datetime import datetime

def demo_knowledge_base():
    """Demo knowledge base đã thu thập"""
    
    print("🏥" + "="*60)
    print("    HEALTHCARE KNOWLEDGE BASE - DEMO")
    print("    Dữ liệu từ nguồn uy tín đã thu thập")
    print("="*63)
    print()
    
    try:
        # Load dữ liệu đã thu thập
        with open('trusted_health_knowledge.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Hiển thị thống kê
        print("📊 THỐNG KÊ KNOWLEDGE BASE:")
        print(f"   ├── Categories: {len(data['categories'])}")
        print(f"   ├── Knowledge Entries: {len(data['knowledge_entries'])}")
        print(f"   ├── Diseases: {len(data['diseases'])}")
        print(f"   ├── Symptoms: {len(data['symptoms'])}")
        print(f"   ├── Medical Terms: {len(data['medical_terms'])}")
        print(f"   └── Tags: {len(data['tags'])}")
        print()
        
        # Hiển thị categories
        print("🏷️  CATEGORIES:")
        for cat in data['categories']:
            print(f"   ├── {cat['name']} ({cat['category_type']})")
            print(f"   │   └── {cat['description']}")
        print()
        
        # Hiển thị diseases
        print("🦠 DISEASES:")
        for disease in data['diseases']:
            print(f"   ├── {disease['name']} (ICD: {disease['icd_code']})")
            print(f"   │   ├── Mô tả: {disease['description'][:80]}...")
            print(f"   │   ├── Nguyên nhân: {disease['causes'][:60]}...")
            print(f"   │   ├── Triệu chứng: {disease['symptoms'][:60]}...")
            print(f"   │   ├── Mức độ: {disease['severity_level']}")
            if disease.get('is_chronic'):
                print(f"   │   └── ⚠️  Bệnh mãn tính")
            if disease.get('is_contagious'):
                print(f"   │   └── 🦠 Bệnh truyền nhiễm")
            print()
        
        # Hiển thị symptoms
        print("⚕️  SYMPTOMS:")
        for symptom in data['symptoms']:
            urgency_icon = {
                'LOW': '🟢',
                'MEDIUM': '🟡', 
                'HIGH': '🔴',
                'EMERGENCY': '🚨'
            }.get(symptom['urgency_level'], '⚪')
            
            print(f"   ├── {symptom['name']} {urgency_icon} {symptom['urgency_level']}")
            print(f"   │   ├── Vị trí: {symptom['body_part']}")
            print(f"   │   ├── Mô tả: {symptom['description'][:70]}...")
            print(f"   │   ├── Nguyên nhân: {symptom['possible_causes'][:60]}...")
            print(f"   │   └── Khi nào khám: {symptom['when_to_see_doctor'][:50]}...")
            print()
        
        # Demo tìm kiếm đơn giản
        print("🔍 DEMO TÌM KIẾM:")
        search_terms = ["tăng huyết áp", "sốt", "ho", "viêm gan"]
        
        for term in search_terms:
            print(f"   🔎 Tìm kiếm: '{term}'")
            found = False
            
            # Tìm trong diseases
            for disease in data['diseases']:
                if term.lower() in disease['name'].lower():
                    print(f"      ✅ Tìm thấy bệnh: {disease['name']}")
                    print(f"         └── {disease['description'][:60]}...")
                    found = True
            
            # Tìm trong symptoms  
            for symptom in data['symptoms']:
                if term.lower() in symptom['name'].lower():
                    print(f"      ✅ Tìm thấy triệu chứng: {symptom['name']}")
                    print(f"         └── {symptom['description'][:60]}...")
                    found = True
            
            if not found:
                print(f"      ❌ Không tìm thấy kết quả cho '{term}'")
            print()
        
        # Demo chatbot response
        print("🤖 DEMO CHATBOT RESPONSES:")
        questions = [
            "Tôi bị tăng huyết áp có nguy hiểm không?",
            "Sốt cao khi nào cần đi bác sĩ?",
            "Ho kéo dài có phải lao không?",
            "Viêm gan B có chữa được không?"
        ]
        
        for question in questions:
            print(f"   ❓ {question}")
            
            # Tìm kiếm thông tin liên quan
            for disease in data['diseases']:
                for word in question.lower().split():
                    if word in disease['name'].lower():
                        print(f"      🤖 Dựa trên thông tin về {disease['name']}:")
                        print(f"         {disease['description']}")
                        print(f"         Điều trị: {disease['treatment']}")
                        print(f"         ⚠️  Lưu ý: Thông tin chỉ tham khảo, hãy tham khảo bác sĩ.")
                        break
            
            for symptom in data['symptoms']:
                for word in question.lower().split():
                    if word in symptom['name'].lower():
                        print(f"      🤖 Về triệu chứng {symptom['name']}:")
                        print(f"         {symptom['description']}")
                        print(f"         Khi cần khám: {symptom['when_to_see_doctor']}")
                        print(f"         ⚠️  Lưu ý: Thông tin chỉ tham khảo, hãy tham khảo bác sĩ.")
                        break
            print()
        
        print("🎉 DEMO HOÀN THÀNH!")
        print("="*63)
        print("✅ Knowledge Base đã sẵn sàng!")
        print("📝 Dữ liệu từ nguồn uy tín đã được thu thập")
        print("🔧 Có thể tích hợp vào Django models")
        print("🤖 Sẵn sàng cho AI chatbot processing")
        print("="*63)
        
    except FileNotFoundError:
        print("❌ Không tìm thấy file trusted_health_knowledge.json")
        print("   Hãy chạy script collect_trusted_data.py trước")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    demo_knowledge_base()
