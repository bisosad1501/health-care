#!/usr/bin/env python3
"""
Script thu thập dữ liệu từ các nguồn y tế uy tín
CHẠY SCRIPT NÀY NGAY để có dữ liệu thực tế!
"""

import requests
import json
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrustedHealthDataCollector:
    """Thu thập dữ liệu từ nguồn y tế uy tín"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Healthcare Knowledge Base Builder 1.0'
        })
        self.collected_data = {
            'categories': [],
            'knowledge_entries': [],
            'diseases': [],
            'symptoms': [],
            'medical_terms': []
        }
    
    def collect_medlineplus_data(self):
        """Thu thập từ MedlinePlus (Public Domain)"""
        logger.info("🔍 Thu thập dữ liệu từ MedlinePlus...")
        
        # Danh sách các health topics phổ biến
        medlineplus_topics = [
            'https://medlineplus.gov/heartdisease.html',
            'https://medlineplus.gov/highbloodpressure.html', 
            'https://medlineplus.gov/diabetes.html',
            'https://medlineplus.gov/stroke.html',
            'https://medlineplus.gov/cancer.html',
            'https://medlineplus.gov/mentalhealth.html',
            'https://medlineplus.gov/obesity.html',
            'https://medlineplus.gov/flu.html'
        ]
        
        for topic_url in medlineplus_topics:
            try:
                self._extract_medlineplus_topic(topic_url)
                time.sleep(1)  # Respectful crawling
            except Exception as e:
                logger.error(f"Lỗi khi thu thập {topic_url}: {e}")
    
    def _extract_medlineplus_topic(self, url):
        """Trích xuất thông tin từ một topic của MedlinePlus"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Lấy tiêu đề
            title_elem = soup.find('h1')
            if not title_elem:
                return
            
            title = title_elem.text.strip()
            
            # Lấy nội dung chính
            main_content = soup.find('div', {'class': 'page-info'})
            if not main_content:
                main_content = soup.find('article')
            
            if not main_content:
                return
            
            # Trích xuất các đoạn văn
            paragraphs = main_content.find_all('p')
            content_parts = []
            
            for p in paragraphs[:5]:  # Lấy 5 đoạn đầu
                text = p.get_text().strip()
                if len(text) > 50:  # Bỏ qua đoạn quá ngắn
                    content_parts.append(text)
            
            if not content_parts:
                return
            
            content = '\\n\\n'.join(content_parts)
            
            # Tạo knowledge entry
            knowledge_entry = {
                'title': title,
                'content': content,
                'summary': content_parts[0] if content_parts else '',
                'category': 'Thông Tin Y Tế',
                'content_type': 'ARTICLE',
                'difficulty_level': 'BASIC',
                'keywords': self._extract_keywords(title + ' ' + content),
                'author': 'MedlinePlus',
                'source': url,
                'reliability_score': 0.95,
                'is_verified': True,
                'tags': ['medlineplus', 'public-health']
            }
            
            self.collected_data['knowledge_entries'].append(knowledge_entry)
            logger.info(f"✅ Thu thập thành công: {title}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý {url}: {e}")
    
    def collect_who_data(self):
        """Thu thập từ WHO (Creative Commons License)"""
        logger.info("🔍 Thu thập dữ liệu từ WHO...")
        
        # Danh sách các fact sheets của WHO
        who_topics = [
            'https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)',
            'https://www.who.int/news-room/fact-sheets/detail/hypertension',
            'https://www.who.int/news-room/fact-sheets/detail/diabetes',
            'https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight',
            'https://www.who.int/news-room/fact-sheets/detail/mental-disorders'
        ]
        
        for topic_url in who_topics:
            try:
                self._extract_who_factsheet(topic_url)
                time.sleep(2)  # Respectful crawling
            except Exception as e:
                logger.error(f"Lỗi khi thu thập WHO {topic_url}: {e}")
    
    def _extract_who_factsheet(self, url):
        """Trích xuất WHO fact sheet"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Lấy tiêu đề
            title_elem = soup.find('h1')
            if not title_elem:
                return
            
            title = title_elem.text.strip()
            
            # Lấy key facts
            key_facts = soup.find('div', string=re.compile('Key facts', re.I))
            if key_facts:
                facts_section = key_facts.find_next('ul')
                if facts_section:
                    facts = [li.get_text().strip() for li in facts_section.find_all('li')]
                    
                    knowledge_entry = {
                        'title': f"{title} - Key Facts",
                        'content': '\\n'.join([f"• {fact}" for fact in facts]),
                        'summary': facts[0] if facts else '',
                        'category': 'Thông Tin Y Tế WHO',
                        'content_type': 'FACT',
                        'difficulty_level': 'INTERMEDIATE',
                        'keywords': self._extract_keywords(title),
                        'author': 'World Health Organization',
                        'source': url,
                        'reliability_score': 0.98,
                        'is_verified': True,
                        'tags': ['who', 'international-health']
                    }
                    
                    self.collected_data['knowledge_entries'].append(knowledge_entry)
                    logger.info(f"✅ Thu thập WHO thành công: {title}")
                    
        except Exception as e:
            logger.error(f"Lỗi khi xử lý WHO {url}: {e}")
    
    def collect_vietnamese_health_data(self):
        """Thu thập dữ liệu y tế Việt Nam"""
        logger.info("🔍 Thu thập dữ liệu y tế Việt Nam...")
        
        # Tạo dữ liệu mẫu dựa trên thống kê y tế VN
        vietnamese_diseases = [
            {
                'name': 'Tăng huyết áp',
                'icd_code': 'I10',
                'description': 'Bệnh lý tim mạch phổ biến nhất tại Việt Nam, ảnh hưởng đến 25.1% dân số trưởng thành',
                'causes': 'Di truyền, lối sống không lành mạnh, ăn nhiều muối, ít vận động, stress',
                'symptoms': 'Thường không có triệu chứng rõ ràng ở giai đoạn đầu, có thể đau đầu, chóng mặt, mệt mỏi',
                'treatment': 'Thay đổi lối sống, thuốc hạ áp theo chỉ định bác sĩ, theo dõi thường xuyên',
                'prevention': 'Ăn ít muối (<5g/ngày), tập thể dục đều đặn, kiểm soát cân nặng, không hút thuốc',
                'category': 'Bệnh Tim Mạch',
                'severity_level': 'MODERATE',
                'is_chronic': True
            },
            {
                'name': 'Viêm gan B',
                'icd_code': 'B18.1',
                'description': 'Bệnh truyền nhiễm phổ biến tại Việt Nam, khoảng 7-8% dân số mang virus',
                'causes': 'Virus viêm gan B (HBV), lây truyền qua đường máu, tình dục, từ mẹ sang con',
                'symptoms': 'Mệt mỏi, chán ăn, buồn nôn, đau bụng, vàng da, nước tiểu sẫm màu',
                'treatment': 'Thuốc kháng virus, theo dõi chức năng gan, chế độ ăn uống phù hợp',
                'prevention': 'Tiêm vaccine, tránh dùng chung kim tiêm, quan hệ tình dục an toàn',
                'category': 'Bệnh Truyền Nhiễm',
                'severity_level': 'SEVERE',
                'is_contagious': True
            }
        ]
        
        for disease_data in vietnamese_diseases:
            self.collected_data['diseases'].append(disease_data)
        
        # Triệu chứng phổ biến tại VN
        vietnamese_symptoms = [
            {
                'name': 'Sốt',
                'description': 'Thân nhiệt tăng cao trên 37.5°C, phản ứng của cơ thể với nhiễm trùng hoặc bệnh lý',
                'body_part': 'Toàn thân',
                'urgency_level': 'MEDIUM',
                'possible_causes': 'Nhiễm virus, nhiễm khuẩn, sốt rét, sốt xuất huyết',
                'when_to_see_doctor': 'Sốt trên 39°C, sốt kéo dài >3 ngày, kèm khó thở, co giật',
                'home_remedies': 'Uống nhiều nước, nghỉ ngơi, chườm mát, theo dõi thân nhiệt',
                'category': 'Triệu Chứng Thường Gặp'
            },
            {
                'name': 'Ho',
                'description': 'Phản xạ để loại bỏ chất lạ khỏi đường hô hấp',
                'body_part': 'Hệ hô hấp',
                'urgency_level': 'LOW',
                'possible_causes': 'Cảm lạnh, viêm phổi, dị ứng, lao phổi, COVID-19',
                'when_to_see_doctor': 'Ho ra máu, ho kéo dài >3 tuần, kèm sốt cao, khó thở',
                'home_remedies': 'Uống nước ấm, nghỉ ngọi, tránh khói bụi, súc họng nước muối',
                'category': 'Triệu Chứng Thường Gặp'
            }
        ]
        
        for symptom_data in vietnamese_symptoms:
            self.collected_data['symptoms'].append(symptom_data)
    
    def _extract_keywords(self, text):
        """Trích xuất từ khóa từ văn bản"""
        # Loại bỏ ký tự đặc biệt và chuyển về chữ thường
        clean_text = re.sub(r'[^\\w\\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Loại bỏ stop words và lấy từ khóa quan trọng
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Lấy top 10 từ khóa duy nhất
        unique_keywords = list(dict.fromkeys(keywords))[:10]
        return ', '.join(unique_keywords)
    
    def save_collected_data(self, filename='collected_health_data.json'):
        """Lưu dữ liệu đã thu thập"""
        # Thêm categories cần thiết
        self.collected_data['categories'] = [
            {
                'name': 'Thông Tin Y Tế',
                'category_type': 'DISEASE',
                'description': 'Thông tin y tế từ nguồn uy tín quốc tế'
            },
            {
                'name': 'Thông Tin Y Tế WHO', 
                'category_type': 'DISEASE',
                'description': 'Thông tin từ Tổ chức Y tế Thế giới'
            },
            {
                'name': 'Bệnh Tim Mạch',
                'category_type': 'DISEASE', 
                'description': 'Các bệnh lý tim mạch'
            },
            {
                'name': 'Bệnh Truyền Nhiễm',
                'category_type': 'DISEASE',
                'description': 'Các bệnh truyền nhiễm'
            },
            {
                'name': 'Triệu Chứng Thường Gặp',
                'category_type': 'SYMPTOM',
                'description': 'Các triệu chứng thường gặp'
            }
        ]
        
        # Thêm tags
        self.collected_data['tags'] = [
            {'name': 'medlineplus', 'description': 'Thông tin từ MedlinePlus'},
            {'name': 'who', 'description': 'Thông tin từ WHO'},
            {'name': 'public-health', 'description': 'Y tế công cộng'},
            {'name': 'international-health', 'description': 'Y tế quốc tế'},
            {'name': 'vietnam-health', 'description': 'Y tế Việt Nam'}
        ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Đã lưu dữ liệu vào {filename}")
        logger.info(f"📊 Thống kê thu thập:")
        logger.info(f"   - Categories: {len(self.collected_data['categories'])}")
        logger.info(f"   - Knowledge Entries: {len(self.collected_data['knowledge_entries'])}")
        logger.info(f"   - Diseases: {len(self.collected_data['diseases'])}")
        logger.info(f"   - Symptoms: {len(self.collected_data['symptoms'])}")


def main():
    """Chạy script thu thập dữ liệu"""
    print("🚀 BẮT ĐẦU THU THẬP KNOWLEDGE BASE TỪ NGUỒN UY TÍN")
    print("=" * 60)
    
    collector = TrustedHealthDataCollector()
    
    # Thu thập từ các nguồn
    collector.collect_medlineplus_data()
    collector.collect_who_data() 
    collector.collect_vietnamese_health_data()
    
    # Lưu dữ liệu
    collector.save_collected_data('trusted_health_knowledge.json')
    
    print("=" * 60)
    print("✅ HOÀN THÀNH! Dữ liệu đã được lưu vào 'trusted_health_knowledge.json'")
    print("📝 Bước tiếp theo:")
    print("   1. Review dữ liệu trong file JSON")
    print("   2. Load vào database: python manage.py load_knowledge_data --data-file=trusted_health_knowledge.json")
    print("   3. Build search index: python manage.py build_search_index")


if __name__ == "__main__":
    main()
