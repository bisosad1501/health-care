import openai
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from knowledge.models import ChatbotResponse
from knowledge.services import KnowledgeSearchEngine, SymptomChecker

logger = logging.getLogger(__name__)


class HealthcareAIService:
    """Service tích hợp AI cho healthcare chatbot"""
    
    def __init__(self):
        self.search_engine = KnowledgeSearchEngine()
        self.symptom_checker = SymptomChecker()
        
        # Initialize OpenAI
        if hasattr(settings, 'OPENAI_API_KEY'):
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API key not configured")
    
    def generate_response(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate AI response based on user query and knowledge base"""
        try:
            # Analyze query intent
            intent = self._analyze_intent(user_query)
            
            # Search knowledge base
            knowledge_results = self.search_engine.search_knowledge(user_query, limit=5)
            
            # Generate contextual response
            if intent['type'] == 'symptom_check':
                response = self._handle_symptom_check(user_query, intent, context)
            elif intent['type'] == 'disease_info':
                response = self._handle_disease_info(user_query, knowledge_results)
            elif intent['type'] == 'emergency':
                response = self._handle_emergency(user_query)
            elif intent['type'] == 'appointment':
                response = self._handle_appointment(user_query, context)
            else:
                response = self._handle_general_query(user_query, knowledge_results)
            
            # Save response for learning
            self._save_response(user_query, response, intent['type'])
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                'response': 'Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.',
                'type': 'error',
                'confidence': 0.0
            }
    
    def _analyze_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user intent from query"""
        query_lower = query.lower()
        
        # Symptom checking keywords
        symptom_keywords = [
            'triệu chứng', 'đau', 'nhức', 'sốt', 'ho', 'khó thở', 'chóng mặt',
            'buồn nôn', 'mệt mỏi', 'đau đầu', 'đau bụng', 'đau ngực'
        ]
        
        # Emergency keywords
        emergency_keywords = [
            'cấp cứu', 'nguy hiểm', 'nghiêm trọng', 'khẩn cấp', 'gấp',
            'đau dữ dội', 'khó thở nặng', 'ngất xỉu', 'co giật'
        ]
        
        # Disease information keywords
        disease_keywords = [
            'bệnh', 'chẩn đoán', 'nguyên nhân', 'điều trị', 'thuốc',
            'phòng ngừa', 'biến chứng', 'tiên lượng'
        ]
        
        # Appointment keywords
        appointment_keywords = [
            'đặt lịch', 'hẹn khám', 'booking', 'appointment', 'lịch hẹn',
            'khám bệnh', 'tư vấn', 'gặp bác sĩ'
        ]
        
        # Check intent
        if any(keyword in query_lower for keyword in emergency_keywords):
            return {'type': 'emergency', 'confidence': 0.9}
        elif any(keyword in query_lower for keyword in symptom_keywords):
            return {'type': 'symptom_check', 'confidence': 0.8}
        elif any(keyword in query_lower for keyword in disease_keywords):
            return {'type': 'disease_info', 'confidence': 0.7}
        elif any(keyword in query_lower for keyword in appointment_keywords):
            return {'type': 'appointment', 'confidence': 0.8}
        else:
            return {'type': 'general', 'confidence': 0.5}
    
    def _handle_symptom_check(self, query: str, intent: Dict, context: Dict) -> Dict[str, Any]:
        """Handle symptom checking queries"""
        try:
            # Extract symptoms from query
            symptoms = self._extract_symptoms(query)
            
            if not symptoms:
                return {
                    'response': 'Tôi hiểu bạn muốn kiểm tra triệu chứng. Bạn có thể mô tả cụ thể hơn về triệu chứng đang gặp phải không?',
                    'type': 'symptom_check',
                    'confidence': 0.6,
                    'follow_up': True
                }
            
            # Use symptom checker
            result = self.symptom_checker.check_symptoms(symptoms, context)
            
            # Format response
            response_text = self._format_symptom_response(result)
            
            return {
                'response': response_text,
                'type': 'symptom_check',
                'confidence': 0.8,
                'data': result,
                'disclaimer': result.get('disclaimer')
            }
            
        except Exception as e:
            logger.error(f"Error in symptom checking: {str(e)}")
            return {
                'response': 'Xin lỗi, tôi không thể kiểm tra triệu chứng lúc này. Vui lòng liên hệ bác sĩ nếu triệu chứng nghiêm trọng.',
                'type': 'error',
                'confidence': 0.0
            }
    
    def _handle_disease_info(self, query: str, knowledge_results: List[Dict]) -> Dict[str, Any]:
        """Handle disease information queries"""
        if not knowledge_results:
            return {
                'response': 'Tôi không tìm thấy thông tin về vấn đề bạn hỏi. Bạn có thể diễn đạt lại câu hỏi không?',
                'type': 'disease_info',
                'confidence': 0.3
            }
        
        # Get best match
        best_result = knowledge_results[0]
        entry = best_result['entry']
        
        # Format response based on entry type
        if entry.content_type == 'FAQ':
            response_text = f"**{entry.title}**\\n\\n{entry.content}"
        else:
            response_text = f"**{entry.title}**\\n\\n{entry.summary or entry.content[:500]}..."
        
        # Add related information
        if len(knowledge_results) > 1:
            response_text += "\\n\\n**Thông tin liên quan:**\\n"
            for result in knowledge_results[1:3]:
                response_text += f"- {result['entry'].title}\\n"
        
        return {
            'response': response_text,
            'type': 'disease_info',
            'confidence': best_result['score'],
            'source': {
                'title': entry.title,
                'author': entry.author,
                'reliability': entry.reliability_score
            }
        }
    
    def _handle_emergency(self, query: str) -> Dict[str, Any]:
        """Handle emergency queries"""
        emergency_response = """
🚨 **TÌNH HUỐNG CẤP CỨU**

**Gọi ngay 115 hoặc đến cơ sở y tế gần nhất!**

**Một số xử lý cấp cứu cơ bản:**

1. **Giữ bình tĩnh** và đánh giá tình hình
2. **Đảm bảo an toàn** cho bệnh nhân và người xung quanh
3. **Kiểm tra tri giác, hô hấp, mạch** của bệnh nhân
4. **Không di chuyển** bệnh nhân nếu nghi ngờ chấn thương cột sống
5. **Chuẩn bị thông tin** cho đội cấp cứu

**Lưu ý quan trọng:** Thông tin này chỉ mang tính tham khảo. Trong tình huống cấp cứu, luôn ưu tiên gọi 115 và đến cơ sở y tế.
        """
        
        return {
            'response': emergency_response.strip(),
            'type': 'emergency',
            'confidence': 0.95,
            'urgent': True,
            'actions': ['call_115', 'go_to_hospital']
        }
    
    def _handle_appointment(self, query: str, context: Dict) -> Dict[str, Any]:
        """Handle appointment booking queries"""
        return {
            'response': 'Tôi có thể giúp bạn đặt lịch hẹn khám. Bạn muốn đặt lịch với chuyên khoa nào và vào thời gian nào?',
            'type': 'appointment',
            'confidence': 0.8,
            'actions': ['show_appointment_form', 'list_doctors'],
            'next_step': 'appointment_booking'
        }
    
    def _handle_general_query(self, query: str, knowledge_results: List[Dict]) -> Dict[str, Any]:
        """Handle general healthcare queries"""
        if not knowledge_results:
            return {
                'response': 'Tôi hiểu bạn đang cần thông tin về sức khỏe. Bạn có thể hỏi cụ thể hơn về triệu chứng, bệnh lý, hoặc vấn đề sức khỏe nào đó không?',
                'type': 'general',
                'confidence': 0.4,
                'suggestions': [
                    'Kiểm tra triệu chứng',
                    'Thông tin về bệnh lý',
                    'Đặt lịch khám',
                    'Tư vấn sức khỏe'
                ]
            }
        
        # Combine information from multiple sources
        response_parts = []
        confidence_scores = []
        
        for result in knowledge_results[:3]:
            entry = result['entry']
            response_parts.append(f"**{entry.title}**\\n{entry.summary or entry.content[:300]}...")
            confidence_scores.append(result['score'])
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        return {
            'response': '\\n\\n---\\n\\n'.join(response_parts),
            'type': 'general',
            'confidence': avg_confidence,
            'sources': [{'title': r['entry'].title, 'score': r['score']} for r in knowledge_results[:3]]
        }
    
    def _extract_symptoms(self, query: str) -> List[str]:
        """Extract symptoms from user query"""
        # Simple symptom extraction - can be improved with NLP
        symptom_indicators = [
            'đau', 'nhức', 'sốt', 'ho', 'khó thở', 'chóng mặt', 'buồn nôn',
            'mệt mỏi', 'yếu', 'run', 'tê', 'ngứa', 'sưng', 'phù'
        ]
        
        query_lower = query.lower()
        found_symptoms = []
        
        for indicator in symptom_indicators:
            if indicator in query_lower:
                # Extract context around the symptom
                index = query_lower.find(indicator)
                start = max(0, index - 10)
                end = min(len(query), index + len(indicator) + 20)
                symptom_context = query[start:end].strip()
                found_symptoms.append(symptom_context)
        
        return found_symptoms
    
    def _format_symptom_response(self, result: Dict) -> str:
        """Format symptom checker response"""
        if 'error' in result:
            return result['error']
        
        response_parts = []
        
        # Found symptoms
        if result.get('symptoms'):
            response_parts.append("**Triệu chứng được tìm thấy:**")
            for symptom in result['symptoms']:
                response_parts.append(f"- {symptom['matched']}: {symptom['info']['description']}")
        
        # Urgency assessment
        urgency = result.get('urgency_level', 'LOW')
        if urgency == 'HIGH' or urgency == 'EMERGENCY':
            response_parts.append("\\n⚠️ **Mức độ khẩn cấp: CAO** - Nên gặp bác sĩ ngay")
        elif urgency == 'MEDIUM':
            response_parts.append("\\n⚠️ **Mức độ khẩn cấp: TRUNG BÌNH** - Nên khám trong vài ngày")
        else:
            response_parts.append("\\n✅ **Mức độ khẩn cấp: THẤP** - Theo dõi và tự chăm sóc")
        
        # Related diseases
        if result.get('related_diseases'):
            response_parts.append("\\n**Có thể liên quan đến:**")
            for disease in result['related_diseases'][:3]:
                response_parts.append(f"- {disease['name']}")
        
        # Recommendations
        if result.get('recommendations'):
            response_parts.append("\\n**Khuyến nghị:**")
            for rec in result['recommendations']:
                response_parts.append(f"- {rec}")
        
        # Disclaimer
        response_parts.append("\\n---")
        response_parts.append(result.get('disclaimer', 'Thông tin này chỉ mang tính tham khảo, không thay thế chẩn đoán y khoa.'))
        
        return '\\n'.join(response_parts)
    
    def _save_response(self, question: str, response: Dict, response_type: str):
        """Save chatbot response for learning and analytics"""
        try:
            ChatbotResponse.objects.create(
                question=question,
                response=response.get('response', ''),
                response_type=response_type.upper(),
                confidence_score=response.get('confidence', 0.5)
            )
        except Exception as e:
            logger.error(f"Error saving chatbot response: {str(e)}")
    
    def get_response_analytics(self) -> Dict[str, Any]:
        """Get analytics about chatbot responses"""
        try:
            from django.db.models import Count, Avg
            
            analytics = ChatbotResponse.objects.aggregate(
                total_responses=Count('id'),
                avg_confidence=Avg('confidence_score'),
                total_usage=Count('usage_count')
            )
            
            # Response types breakdown
            type_breakdown = list(
                ChatbotResponse.objects.values('response_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            return {
                'total_responses': analytics['total_responses'] or 0,
                'average_confidence': round(analytics['avg_confidence'] or 0, 2),
                'total_usage': analytics['total_usage'] or 0,
                'response_types': type_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}


class KnowledgeRecommendationEngine:
    """Engine for recommending relevant knowledge"""
    
    def __init__(self):
        self.search_engine = KnowledgeSearchEngine()
    
    def get_recommendations(self, user_profile: Dict, limit: int = 5) -> List[Dict]:
        """Get personalized knowledge recommendations"""
        try:
            recommendations = []
            
            # Based on user's medical history
            if user_profile.get('medical_conditions'):
                for condition in user_profile['medical_conditions']:
                    results = self.search_engine.search_knowledge(condition, limit=2)
                    recommendations.extend(results)
            
            # Based on user's age group
            age = user_profile.get('age', 0)
            if age >= 60:
                elderly_results = self.search_engine.search_by_category('PREVENTION', 'người cao tuổi', limit=2)
                recommendations.extend(elderly_results)
            elif age >= 40:
                midlife_results = self.search_engine.search_by_category('PREVENTION', 'trung niên', limit=2)
                recommendations.extend(midlife_results)
            
            # Remove duplicates and sort by relevance
            seen = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec['entry'].id not in seen:
                    seen.add(rec['entry'].id)
                    unique_recommendations.append(rec)
            
            return sorted(unique_recommendations, key=lambda x: x['score'], reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
