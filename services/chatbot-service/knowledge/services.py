import re
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from django.db.models import Q, Count
from django.conf import settings
from django.utils import timezone
from fuzzywuzzy import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

from .models import (
    KnowledgeEntry, KnowledgeCategory, DiseaseInformation, 
    SymptomInformation, MedicalTerm, ChatbotResponse, KnowledgeSearchLog
)

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass


class VietnameseTextProcessor:
    """Xử lý văn bản tiếng Việt"""
    
    # Stopwords tiếng Việt
    VIETNAMESE_STOPWORDS = {
        'và', 'của', 'với', 'từ', 'trong', 'trên', 'dưới', 'về', 'cho', 'để',
        'khi', 'nếu', 'vì', 'nhưng', 'mà', 'rồi', 'đã', 'sẽ', 'có', 'là',
        'được', 'bị', 'các', 'những', 'này', 'đó', 'ở', 'tại', 'theo', 'như',
        'chỉ', 'cũng', 'đều', 'cả', 'thì', 'hay', 'hoặc', 'nên', 'phải', 'cần',
        'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười'
    }
    
    # Từ khóa y tế tiếng Việt
    MEDICAL_KEYWORDS = {
        'bệnh', 'triệu chứng', 'điều trị', 'thuốc', 'bác sĩ', 'bệnh viện',
        'khám', 'chẩn đoán', 'phòng ngừa', 'sức khỏe', 'y tế', 'cấp cứu',
        'đau', 'nhức', 'sốt', 'ho', 'viêm', 'nhiễm', 'ung thư', 'tim mạch'
    }
    
    def __init__(self):
        try:
            self.stemmer = PorterStemmer()
        except:
            self.stemmer = None
    
    def preprocess_text(self, text: str) -> str:
        """Tiền xử lý văn bản"""
        if not text:
            return ""
        
        # Chuyển về chữ thường
        text = text.lower()
        
        # Loại bỏ ký tự đặc biệt, giữ lại dấu tiếng Việt
        text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text: str) -> str:
        """Loại bỏ stopwords"""
        words = text.split()
        filtered_words = [word for word in words if word not in self.VIETNAMESE_STOPWORDS]
        return ' '.join(filtered_words)
    
    def extract_keywords(self, text: str) -> List[str]:
        """Trích xuất từ khóa"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        # Lọc từ khóa y tế và từ quan trọng
        keywords = []
        for word in words:
            if (len(word) > 2 and 
                word not in self.VIETNAMESE_STOPWORDS and
                (word in self.MEDICAL_KEYWORDS or len(word) > 4)):
                keywords.append(word)
        
        return list(set(keywords))


class KnowledgeSearchEngine:
    """Công cụ tìm kiếm kiến thức"""
    
    def __init__(self):
        self.text_processor = VietnameseTextProcessor()
        self.tfidf_vectorizer = None
        self.document_vectors = None
        self.knowledge_cache = {}
        self.last_cache_update = None
    
    def build_search_index(self):
        """Xây dựng chỉ mục tìm kiếm"""
        try:
            # Lấy tất cả các entry active
            entries = KnowledgeEntry.objects.filter(is_active=True).select_related('category')
            
            if not entries.exists():
                logger.warning("Không có knowledge entry nào để xây dựng index")
                return
            
            # Chuẩn bị dữ liệu
            documents = []
            entry_ids = []
            
            for entry in entries:
                # Kết hợp title, content, summary và keywords
                text_parts = [
                    entry.title,
                    entry.content,
                    entry.summary or '',
                    entry.keywords or '',
                    entry.category.name
                ]
                
                combined_text = ' '.join(filter(None, text_parts))
                processed_text = self.text_processor.preprocess_text(combined_text)
                
                documents.append(processed_text)
                entry_ids.append(entry.id)
            
            # Tạo TF-IDF vectors
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                stop_words=list(self.text_processor.VIETNAMESE_STOPWORDS)
            )
            
            self.document_vectors = self.tfidf_vectorizer.fit_transform(documents)
            
            # Cache entry IDs
            self.knowledge_cache = {
                'entry_ids': entry_ids,
                'documents': documents
            }
            
            self.last_cache_update = time.time()
            logger.info(f"Đã xây dựng search index với {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Lỗi khi xây dựng search index: {str(e)}")
    
    def search_knowledge(self, query: str, limit: int = 10, min_score: float = 0.1) -> List[Dict]:
        """Tìm kiếm kiến thức"""
        start_time = time.time()
        
        try:
            # Kiểm tra và cập nhật cache
            if (not self.tfidf_vectorizer or 
                not self.last_cache_update or 
                time.time() - self.last_cache_update > 3600):  # Cập nhật mỗi giờ
                self.build_search_index()
            
            if not self.tfidf_vectorizer:
                return []
            
            # Xử lý query
            processed_query = self.text_processor.preprocess_text(query)
            query_vector = self.tfidf_vectorizer.transform([processed_query])
            
            # Tính similarity
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Lấy top results
            top_indices = similarities.argsort()[::-1][:limit]
            
            results = []
            for idx in top_indices:
                score = similarities[idx]
                if score >= min_score:
                    entry_id = self.knowledge_cache['entry_ids'][idx]
                    try:
                        entry = KnowledgeEntry.objects.get(id=entry_id)
                        results.append({
                            'entry': entry,
                            'score': float(score),
                            'matched_text': self.knowledge_cache['documents'][idx][:200]
                        })
                    except KnowledgeEntry.DoesNotExist:
                        continue
            
            # Log tìm kiếm
            search_duration = time.time() - start_time
            KnowledgeSearchLog.objects.create(
                query=query,
                results_count=len(results),
                search_duration=search_duration
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm: {str(e)}")
            return []
    
    def search_by_category(self, category_type: str, query: str = None, limit: int = 10) -> List[Dict]:
        """Tìm kiếm theo danh mục"""
        try:
            # Tìm trong category
            entries = KnowledgeEntry.objects.filter(
                category__category_type=category_type,
                is_active=True
            ).select_related('category')
            
            if query:
                # Tìm kiếm fuzzy trong title và content
                query_lower = query.lower()
                filtered_entries = []
                
                for entry in entries:
                    title_score = fuzz.partial_ratio(query_lower, entry.title.lower())
                    content_score = fuzz.partial_ratio(query_lower, entry.content.lower())
                    max_score = max(title_score, content_score)
                    
                    if max_score >= 60:  # Ngưỡng similarity
                        filtered_entries.append({
                            'entry': entry,
                            'score': max_score / 100.0,
                            'matched_text': entry.title
                        })
                
                # Sắp xếp theo score
                filtered_entries.sort(key=lambda x: x['score'], reverse=True)
                return filtered_entries[:limit]
            
            return [{'entry': entry, 'score': 1.0, 'matched_text': entry.title} 
                   for entry in entries[:limit]]
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm theo category: {str(e)}")
            return []
        self._initialize_tfidf()
    
    def _initialize_tfidf(self):
        """Khởi tạo TF-IDF vectorizer"""
        try:
            # Lấy tất cả nội dung để training TF-IDF
            entries = KnowledgeEntry.objects.filter(is_active=True)
            documents = []
            
            for entry in entries:
                content = f"{entry.title} {entry.content} {entry.summary or ''} {entry.keywords or ''}"
                processed_content = self.text_processor.preprocess_text(content)
                documents.append(processed_content)
            
            if documents:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words=list(VietnameseTextProcessor.VIETNAMESE_STOPWORDS),
                    ngram_range=(1, 2)
                )
                self.document_vectors = self.tfidf_vectorizer.fit_transform(documents)
                logger.info(f"TF-IDF initialized with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error initializing TF-IDF: {str(e)}")
    
    def search_knowledge(self, query: str, filters: Dict[str, Any] = None, limit: int = 10) -> List[Dict]:
        """Tìm kiếm kiến thức"""
        start_time = time.time()
        
        try:
            # Tiền xử lý query
            processed_query = self.text_processor.preprocess_text(query)
            
            # Tìm kiếm cơ bản
            basic_results = self._basic_search(processed_query, filters, limit * 2)
            
            # Tìm kiếm semantic nếu có TF-IDF
            if self.tfidf_vectorizer and self.document_vectors is not None:
                semantic_results = self._semantic_search(processed_query, filters, limit * 2)
                
                # Kết hợp kết quả
                combined_results = self._combine_results(basic_results, semantic_results)
            else:
                combined_results = basic_results
            
            # Sắp xếp và giới hạn kết quả
            final_results = self._rank_results(combined_results, query)[:limit]
            
            # Log tìm kiếm
            search_duration = time.time() - start_time
            self._log_search(query, len(final_results), search_duration)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in knowledge search: {str(e)}")
            return []
    
    def _basic_search(self, query: str, filters: Dict[str, Any], limit: int) -> List[Dict]:
        """Tìm kiếm cơ bản"""
        queryset = KnowledgeEntry.objects.filter(is_active=True)
        
        # Áp dụng filters
        if filters:
            if filters.get('category'):
                queryset = queryset.filter(category__name__icontains=filters['category'])
            if filters.get('content_type'):
                queryset = queryset.filter(content_type=filters['content_type'])
            if filters.get('difficulty_level'):
                queryset = queryset.filter(difficulty_level=filters['difficulty_level'])
        
        # Tìm kiếm full-text
        search_query = (
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(keywords__icontains=query)
        )
        
        entries = queryset.filter(search_query)[:limit]
        
        results = []
        for entry in entries:
            # Tính điểm relevance cơ bản
            relevance_score = self._calculate_basic_relevance(query, entry)
            
            results.append({
                'entry': entry,
                'score': relevance_score,
                'type': 'basic'
            })
        
        return results
    
    def _semantic_search(self, query: str, filters: Dict[str, Any], limit: int) -> List[Dict]:
        """Tìm kiếm semantic"""
        try:
            # Vector hóa query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Tính cosine similarity
            similarities = cosine_similarity(query_vector, self.document_vectors)[0]
            
            # Lấy top results
            top_indices = similarities.argsort()[-limit:][::-1]
            
            # Lấy entries tương ứng
            entries = list(KnowledgeEntry.objects.filter(is_active=True))
            
            results = []
            for idx in top_indices:
                if idx < len(entries) and similarities[idx] > 0.1:  # Threshold
                    entry = entries[idx]
                    
                    # Kiểm tra filters
                    if self._match_filters(entry, filters):
                        results.append({
                            'entry': entry,
                            'score': similarities[idx],
                            'type': 'semantic'
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def _calculate_basic_relevance(self, query: str, entry: KnowledgeEntry) -> float:
        """Tính điểm relevance cơ bản"""
        score = 0.0
        query_lower = query.lower()
        
        # Điểm cho title
        if query_lower in entry.title.lower():
            score += 3.0
        
        # Điểm cho keywords
        if entry.keywords and query_lower in entry.keywords.lower():
            score += 2.0
        
        # Điểm cho summary
        if entry.summary and query_lower in entry.summary.lower():
            score += 1.5
        
        # Điểm cho content
        if query_lower in entry.content.lower():
            score += 1.0
        
        # Bonus cho reliability
        score *= entry.reliability_score
        
        # Bonus cho verified content
        if entry.is_verified:
            score *= 1.2
        
        return score
    
    def _match_filters(self, entry: KnowledgeEntry, filters: Dict[str, Any]) -> bool:
        """Kiểm tra entry có match với filters không"""
        if not filters:
            return True
        
        if filters.get('category') and filters['category'].lower() not in entry.category.name.lower():
            return False
        
        if filters.get('content_type') and entry.content_type != filters['content_type']:
            return False
        
        if filters.get('difficulty_level') and entry.difficulty_level != filters['difficulty_level']:
            return False
        
        return True
    
    def _combine_results(self, basic_results: List[Dict], semantic_results: List[Dict]) -> List[Dict]:
        """Kết hợp kết quả từ các phương pháp tìm kiếm"""
        combined = {}
        
        # Thêm basic results
        for result in basic_results:
            entry_id = result['entry'].id
            combined[entry_id] = result
        
        # Thêm semantic results, kết hợp score nếu đã có
        for result in semantic_results:
            entry_id = result['entry'].id
            if entry_id in combined:
                # Kết hợp score
                combined[entry_id]['score'] = (
                    combined[entry_id]['score'] * 0.6 + result['score'] * 0.4
                )
                combined[entry_id]['type'] = 'combined'
            else:
                combined[entry_id] = result
        
        return list(combined.values())
    
    def _rank_results(self, results: List[Dict], original_query: str) -> List[Dict]:
        """Sắp xếp kết quả theo độ liên quan"""
        # Tính toán thêm các yếu tố ranking
        for result in results:
            entry = result['entry']
            
            # Bonus cho view count
            view_bonus = min(entry.view_count / 1000, 0.5)
            result['score'] += view_bonus
            
            # Bonus cho recent updates
            days_since_update = (timezone.now() - entry.updated_at).days
            recency_bonus = max(0, (30 - days_since_update) / 30 * 0.3)
            result['score'] += recency_bonus
        
        # Sắp xếp theo score
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _log_search(self, query: str, results_count: int, duration: float):
        """Log tìm kiếm"""
        try:
            KnowledgeSearchLog.objects.create(
                query=query,
                results_count=results_count,
                search_duration=duration
            )
        except Exception as e:
            logger.error(f"Error logging search: {str(e)}")


class SymptomChecker:
    """Kiểm tra triệu chứng và gợi ý bệnh"""
    
    def __init__(self):
        self.text_processor = VietnameseTextProcessor()
    
    def check_symptoms(self, symptoms: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Kiểm tra triệu chứng và trả về thông tin liên quan"""
        try:
            # Chuẩn hóa triệu chứng
            normalized_symptoms = [self.text_processor.preprocess_text(s) for s in symptoms]
            
            # Tìm triệu chứng trong database
            found_symptoms = self._find_symptoms(normalized_symptoms)
            
            # Tìm bệnh liên quan
            related_diseases = self._find_related_diseases(found_symptoms)
            
            # Đánh giá mức độ khẩn cấp
            urgency_level = self._assess_urgency(found_symptoms)
            
            # Gợi ý hành động
            recommendations = self._generate_recommendations(found_symptoms, urgency_level, context)
            
            return {
                'symptoms': found_symptoms,
                'related_diseases': related_diseases,
                'urgency_level': urgency_level,
                'recommendations': recommendations,
                'disclaimer': self._get_disclaimer()
            }
            
        except Exception as e:
            logger.error(f"Error in symptom checking: {str(e)}")
            return {
                'error': 'Không thể kiểm tra triệu chứng lúc này',
                'disclaimer': self._get_disclaimer()
            }
    
    def _find_symptoms(self, symptoms: List[str]) -> List[Dict]:
        """Tìm triệu chứng trong database"""
        found_symptoms = []
        
        for symptom in symptoms:
            # Tìm kiếm fuzzy matching
            all_symptoms = SymptomInformation.objects.filter(is_active=True)
            
            best_match = None
            best_score = 0
            
            for db_symptom in all_symptoms:
                # So sánh với tên triệu chứng
                score = fuzz.partial_ratio(symptom, db_symptom.name.lower())
                
                if score > best_score and score > 70:  # Threshold
                    best_score = score
                    best_match = db_symptom
            
            if best_match:
                found_symptoms.append({
                    'original': symptom,
                    'matched': best_match.name,
                    'info': {
                        'id': str(best_match.id),
                        'name': best_match.name,
                        'description': best_match.description,
                        'urgency_level': best_match.urgency_level,
                        'when_to_see_doctor': best_match.when_to_see_doctor,
                        'home_remedies': best_match.home_remedies
                    },
                    'confidence': best_score / 100
                })
        
        return found_symptoms
    
    def _find_related_diseases(self, symptoms: List[Dict]) -> List[Dict]:
        """Tìm bệnh liên quan đến triệu chứng"""
        if not symptoms:
            return []
        
        # Lấy ID của các triệu chứng tìm được
        symptom_ids = [s['info']['id'] for s in symptoms]
        
        # Tìm bệnh có liên quan đến các triệu chứng này
        diseases = DiseaseInformation.objects.filter(
            symptoms__id__in=symptom_ids,
            is_active=True
        ).annotate(
            symptom_count=Count('symptoms')
        ).order_by('-symptom_count')[:5]
        
        related_diseases = []
        for disease in diseases:
            # Tính điểm match
            match_score = min(disease.symptom_count / len(symptoms), 1.0)
            
            related_diseases.append({
                'id': str(disease.id),
                'name': disease.name,
                'icd_code': disease.icd_code,
                'description': disease.description[:200] + '...' if len(disease.description) > 200 else disease.description,
                'severity_level': disease.severity_level,
                'is_contagious': disease.is_contagious,
                'match_score': match_score,
                'matched_symptoms': disease.symptom_count
            })
        
        return related_diseases
    
    def _assess_urgency(self, symptoms: List[Dict]) -> str:
        """Đánh giá mức độ khẩn cấp"""
        if not symptoms:
            return 'LOW'
        
        urgency_levels = [s['info']['urgency_level'] for s in symptoms]
        
        if 'EMERGENCY' in urgency_levels:
            return 'EMERGENCY'
        elif 'HIGH' in urgency_levels:
            return 'HIGH'
        elif 'MEDIUM' in urgency_levels:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, symptoms: List[Dict], urgency_level: str, context: Dict) -> List[str]:
        """Tạo gợi ý hành động"""
        recommendations = []
        
        if urgency_level == 'EMERGENCY':
            recommendations.append("🚨 Cần cấp cứu ngay lập tức - Gọi 115 hoặc đến bệnh viện gần nhất")
        elif urgency_level == 'HIGH':
            recommendations.append("⚠️ Nên gặp bác sĩ trong vòng 24 giờ")
        elif urgency_level == 'MEDIUM':
            recommendations.append("📋 Nên đặt lịch khám bác sĩ trong vài ngày tới")
        else:
            recommendations.append("💡 Theo dõi triệu chứng, có thể tự điều trị tại nhà")
        
        # Thêm gợi ý từ thông tin triệu chứng
        for symptom in symptoms:
            if symptom['info'].get('home_remedies'):
                recommendations.append(f"🏠 {symptom['info']['home_remedies']}")
        
        # Thêm gợi ý chung
        recommendations.extend([
            "💧 Uống đủ nước và nghỉ ngơi",
            "📱 Theo dõi triệu chứng và ghi chú lại",
            "🩺 Không tự ý sử dụng thuốc mà không có chỉ định của bác sĩ"
        ])
        
        return recommendations[:5]  # Giới hạn số gợi ý
    
    def _get_disclaimer(self) -> str:
        """Lấy disclaimer"""
        return (
            "⚠️ Thông tin này chỉ mang tính chất tham khảo và không thể thay thế "
            "việc khám và tư vấn trực tiếp với bác sĩ. Khi có triệu chứng bất thường, "
            "hãy liên hệ với cơ sở y tế để được tư vấn chính xác."
        )


class KnowledgeRecommendationEngine:
    """Hệ thống gợi ý kiến thức"""
    
    def __init__(self):
        self.search_engine = KnowledgeSearchEngine()
        self.text_processor = VietnameseTextProcessor()
    
    def get_recommendations(self, user_query: str, context: Dict[str, Any] = None, max_recommendations: int = 5) -> List[Dict]:
        """Lấy gợi ý kiến thức"""
        try:
            # Trích xuất từ khóa từ query
            keywords = self.text_processor.extract_keywords(user_query)
            
            # Tìm kiếm dựa trên từ khóa
            search_results = self.search_engine.search_knowledge(
                ' '.join(keywords), 
                limit=max_recommendations * 2
            )
            
            # Lọc và sắp xếp kết quả
            recommendations = self._filter_and_rank_recommendations(
                search_results, user_query, context, max_recommendations
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def _filter_and_rank_recommendations(self, search_results: List[Dict], user_query: str, 
                                       context: Dict, max_recommendations: int) -> List[Dict]:
        """Lọc và sắp xếp gợi ý"""
        recommendations = []
        
        for result in search_results[:max_recommendations]:
            entry = result['entry']
            
            recommendation = {
                'id': str(entry.id),
                'title': entry.title,
                'summary': entry.summary or entry.content[:200] + '...',
                'category': entry.category.name,
                'content_type': entry.get_content_type_display(),
                'difficulty_level': entry.get_difficulty_level_display(),
                'reliability_score': entry.reliability_score,
                'relevance_score': result['score'],
                'url': f"/api/knowledge/entries/{entry.id}/",
                'why_recommended': self._explain_recommendation(entry, user_query)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _explain_recommendation(self, entry: KnowledgeEntry, user_query: str) -> str:
        """Giải thích tại sao gợi ý này phù hợp"""
        reasons = []
        
        query_words = self.text_processor.preprocess_text(user_query).split()
        
        # Kiểm tra từ khóa trong title
        title_matches = [word for word in query_words if word in entry.title.lower()]
        if title_matches:
            reasons.append(f"Tiêu đề chứa: {', '.join(title_matches)}")
        
        # Kiểm tra category
        if any(word in entry.category.name.lower() for word in query_words):
            reasons.append(f"Thuộc danh mục: {entry.category.name}")
        
        # Kiểm tra keywords
        if entry.keywords:
            keyword_matches = [word for word in query_words if word in entry.keywords.lower()]
            if keyword_matches:
                reasons.append(f"Có từ khóa: {', '.join(keyword_matches)}")
        
        if not reasons:
            reasons.append("Nội dung liên quan đến câu hỏi của bạn")
        
        return "; ".join(reasons)
