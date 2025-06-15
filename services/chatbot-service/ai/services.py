import json
import random
import time
from typing import Dict, List, Any
from django.conf import settings
import os


class HealthKnowledgeService:
    """Service to handle health knowledge base queries"""
    
    def __init__(self):
        self.knowledge_file = os.path.join(
            settings.BASE_DIR, 
            'comprehensive_health_knowledge.json'
        )
        self.knowledge_data = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge base from JSON file"""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "symptoms": {},
                "conditions": {},
                "treatments": {},
                "medications": {},
                "general_advice": []
            }
    
    def search_symptoms(self, symptom: str) -> List[Dict[str, Any]]:
        """Search for symptom information"""
        results = []
        symptom_lower = symptom.lower()
        
        for key, data in self.knowledge_data.get("symptoms", {}).items():
            if symptom_lower in key.lower() or symptom_lower in data.get("description", "").lower():
                results.append({
                    "type": "symptom",
                    "name": key,
                    "data": data
                })
        
        return results
    
    def search_conditions(self, condition: str) -> List[Dict[str, Any]]:
        """Search for medical condition information"""
        results = []
        condition_lower = condition.lower()
        
        for key, data in self.knowledge_data.get("conditions", {}).items():
            if condition_lower in key.lower() or condition_lower in data.get("description", "").lower():
                results.append({
                    "type": "condition",
                    "name": key,
                    "data": data
                })
        
        return results
    
    def get_general_advice(self) -> str:
        """Get random general health advice"""
        advice_list = self.knowledge_data.get("general_advice", [])
        if advice_list:
            return random.choice(advice_list)
        return "Always consult with a healthcare professional for medical advice."


class AIHealthChatService:
    """Service to handle AI health chat interactions"""
    
    def __init__(self):
        self.knowledge_service = HealthKnowledgeService()
    
    def process_health_query(self, query: str, user_id: int = None, session_id: str = None) -> Dict[str, Any]:
        """Process a health-related query and return AI response"""
        start_time = time.time()
        
        try:
            # Simple keyword-based processing
            query_lower = query.lower()
            response_text = ""
            confidence = 0.5
            
            # Check for symptoms
            if any(word in query_lower for word in ['symptom', 'feel', 'pain', 'hurt', 'ache']):
                symptoms = self.knowledge_service.search_symptoms(query)
                if symptoms:
                    symptom_data = symptoms[0]['data']
                    response_text = f"Based on your symptoms, here's what I found: {symptom_data.get('description', '')}. "
                    if 'possible_causes' in symptom_data:
                        response_text += f"Possible causes include: {', '.join(symptom_data['possible_causes'])}. "
                    confidence = 0.7
                else:
                    response_text = "I understand you're experiencing symptoms. "
            
            # Check for conditions
            elif any(word in query_lower for word in ['condition', 'disease', 'illness', 'diagnosis']):
                conditions = self.knowledge_service.search_conditions(query)
                if conditions:
                    condition_data = conditions[0]['data']
                    response_text = f"Here's information about this condition: {condition_data.get('description', '')}. "
                    if 'treatment_options' in condition_data:
                        response_text += f"Treatment options may include: {', '.join(condition_data['treatment_options'])}. "
                    confidence = 0.8
                else:
                    response_text = "I can help you understand various medical conditions. "
            
            # General health advice
            else:
                response_text = self.knowledge_service.get_general_advice() + " "
                confidence = 0.6
            
            # Always add disclaimer
            response_text += "\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only and should not replace professional medical advice. Please consult with a healthcare provider for proper diagnosis and treatment."
            
            response_time = time.time() - start_time
            
            return {
                'response': response_text,
                'confidence': confidence,
                'response_time': response_time,
                'user_id': user_id,
                'session_id': session_id
            }
            
        except Exception as e:
            return {
                'response': "I'm sorry, I encountered an error processing your health query. Please try again or consult with a healthcare professional.",
                'confidence': 0.1,
                'response_time': time.time() - start_time,
                'error': str(e),
                'user_id': user_id,
                'session_id': session_id
            }
