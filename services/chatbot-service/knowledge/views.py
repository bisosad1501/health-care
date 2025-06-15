from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
import logging

from .models import (
    KnowledgeCategory, KnowledgeEntry, KnowledgeTag, MedicalTerm,
    DiseaseInformation, SymptomInformation, ChatbotResponse
)
from .serializers import (
    KnowledgeCategorySerializer, KnowledgeEntrySerializer, KnowledgeEntryListSerializer,
    KnowledgeTagSerializer, MedicalTermSerializer, DiseaseInformationSerializer,
    SymptomInformationSerializer, ChatbotResponseSerializer, KnowledgeSearchSerializer,
    SymptomCheckSerializer, KnowledgeRecommendationSerializer, FeedbackSerializer,
    KnowledgeStatsSerializer
)
from .services import (
    KnowledgeSearchEngine, SymptomChecker, KnowledgeRecommendationEngine
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class KnowledgeCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet cho KnowledgeCategory"""
    
    queryset = KnowledgeCategory.objects.filter(is_active=True)
    serializer_class = KnowledgeCategorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_type = self.request.query_params.get('type')
        parent_id = self.request.query_params.get('parent')
        
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif parent_id == 'null':
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset.order_by('category_type', 'name')
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Lấy cây danh mục"""
        root_categories = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)


class KnowledgeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet cho KnowledgeEntry"""
    
    queryset = KnowledgeEntry.objects.filter(is_active=True)
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return KnowledgeEntryListSerializer
        return KnowledgeEntrySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        content_type = self.request.query_params.get('content_type')
        difficulty = self.request.query_params.get('difficulty')
        verified_only = self.request.query_params.get('verified_only')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        if verified_only == 'true':
            queryset = queryset.filter(is_verified=True)
        
        return queryset.order_by('-updated_at')
    
    def retrieve(self, request, *args, **kwargs):
        """Lấy chi tiết entry và tăng view count"""
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Lấy các entry phổ biến"""
        popular_entries = self.get_queryset().order_by('-view_count')[:10]
        serializer = KnowledgeEntryListSerializer(popular_entries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Lấy các entry mới nhất"""
        recent_entries = self.get_queryset().order_by('-created_at')[:10]
        serializer = KnowledgeEntryListSerializer(recent_entries, many=True)
        return Response(serializer.data)


class KnowledgeTagViewSet(viewsets.ModelViewSet):
    """ViewSet cho KnowledgeTag"""
    
    queryset = KnowledgeTag.objects.filter(is_active=True)
    serializer_class = KnowledgeTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().order_by('name')


class MedicalTermViewSet(viewsets.ModelViewSet):
    """ViewSet cho MedicalTerm"""
    
    queryset = MedicalTerm.objects.filter(is_active=True)
    serializer_class = MedicalTermSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        category_id = self.request.query_params.get('category')
        
        if search:
            queryset = queryset.filter(
                Q(term__icontains=search) |
                Q(vietnamese_term__icontains=search) |
                Q(definition__icontains=search)
            )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.order_by('term')


class DiseaseInformationViewSet(viewsets.ModelViewSet):
    """ViewSet cho DiseaseInformation"""
    
    queryset = DiseaseInformation.objects.filter(is_active=True)
    serializer_class = DiseaseInformationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        severity = self.request.query_params.get('severity')
        is_contagious = self.request.query_params.get('is_contagious')
        is_chronic = self.request.query_params.get('is_chronic')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(icd_code__icontains=search) |
                Q(description__icontains=search)
            )
        
        if severity:
            queryset = queryset.filter(severity_level=severity)
        
        if is_contagious is not None:
            queryset = queryset.filter(is_contagious=is_contagious.lower() == 'true')
        
        if is_chronic is not None:
            queryset = queryset.filter(is_chronic=is_chronic.lower() == 'true')
        
        return queryset.order_by('name')


class SymptomInformationViewSet(viewsets.ModelViewSet):
    """ViewSet cho SymptomInformation"""
    
    queryset = SymptomInformation.objects.filter(is_active=True)
    serializer_class = SymptomInformationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        urgency = self.request.query_params.get('urgency')
        body_part = self.request.query_params.get('body_part')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(body_part__icontains=search)
            )
        
        if urgency:
            queryset = queryset.filter(urgency_level=urgency)
        
        if body_part:
            queryset = queryset.filter(body_part__icontains=body_part)
        
        return queryset.order_by('name')


class ChatbotResponseViewSet(viewsets.ModelViewSet):
    """ViewSet cho ChatbotResponse"""
    
    queryset = ChatbotResponse.objects.filter(is_active=True)
    serializer_class = ChatbotResponseSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        response_type = self.request.query_params.get('type')
        
        if response_type:
            queryset = queryset.filter(response_type=response_type)
        
        return queryset.order_by('-updated_at')


class KnowledgeSearchViewSet(viewsets.ViewSet):
    """ViewSet cho tìm kiếm kiến thức"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_engine = KnowledgeSearchEngine()
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Tìm kiếm kiến thức"""
        serializer = KnowledgeSearchSerializer(data=request.data)
        if serializer.is_valid():
            try:
                query = serializer.validated_data['query']
                filters = {
                    'category': serializer.validated_data.get('category'),
                    'content_type': serializer.validated_data.get('content_type'),
                    'difficulty_level': serializer.validated_data.get('difficulty_level'),
                }
                limit = serializer.validated_data.get('limit', 10)
                
                # Xóa filters None
                filters = {k: v for k, v in filters.items() if v is not None}
                
                # Tìm kiếm
                results = self.search_engine.search_knowledge(query, filters, limit)
                
                # Serialize kết quả
                search_results = []
                for result in results:
                    entry_data = KnowledgeEntryListSerializer(result['entry']).data
                    entry_data['relevance_score'] = result['score']
                    entry_data['search_type'] = result['type']
                    search_results.append(entry_data)
                
                return Response({
                    'query': query,
                    'results': search_results,
                    'total': len(search_results),
                    'filters_applied': filters
                })
                
            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                return Response(
                    {'error': 'Lỗi trong quá trình tìm kiếm'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Gợi ý tìm kiếm"""
        query = request.query_params.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Response({'suggestions': []})
        
        # Tìm kiếm gợi ý từ titles và keywords
        entries = KnowledgeEntry.objects.filter(
            Q(title__icontains=query) | Q(keywords__icontains=query),
            is_active=True
        )[:10]
        
        suggestions = []
        for entry in entries:
            suggestions.append({
                'text': entry.title,
                'type': 'entry',
                'category': entry.category.name
            })
        
        # Gợi ý từ medical terms
        terms = MedicalTerm.objects.filter(
            Q(term__icontains=query) | Q(vietnamese_term__icontains=query),
            is_active=True
        )[:5]
        
        for term in terms:
            suggestions.append({
                'text': term.vietnamese_term or term.term,
                'type': 'term',
                'category': 'Thuật ngữ y tế'
            })
        
        return Response({'suggestions': suggestions})


class SymptomCheckViewSet(viewsets.ViewSet):
    """ViewSet cho kiểm tra triệu chứng"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symptom_checker = SymptomChecker()
    
    @action(detail=False, methods=['post'])
    def check(self, request):
        """Kiểm tra triệu chứng"""
        serializer = SymptomCheckSerializer(data=request.data)
        if serializer.is_valid():
            try:
                symptoms = serializer.validated_data['symptoms']
                context = {
                    'age': serializer.validated_data.get('age'),
                    'gender': serializer.validated_data.get('gender'),
                    'duration': serializer.validated_data.get('duration'),
                    'severity': serializer.validated_data.get('severity'),
                }
                
                result = self.symptom_checker.check_symptoms(symptoms, context)
                return Response(result)
                
            except Exception as e:
                logger.error(f"Symptom check error: {str(e)}")
                return Response(
                    {'error': 'Lỗi trong quá trình kiểm tra triệu chứng'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KnowledgeRecommendationViewSet(viewsets.ViewSet):
    """ViewSet cho gợi ý kiến thức"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recommendation_engine = KnowledgeRecommendationEngine()
    
    @action(detail=False, methods=['post'])
    def recommend(self, request):
        """Gợi ý kiến thức"""
        serializer = KnowledgeRecommendationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_query = serializer.validated_data['user_query']
                context = serializer.validated_data.get('context', {})
                max_recommendations = serializer.validated_data.get('max_recommendations', 5)
                
                recommendations = self.recommendation_engine.get_recommendations(
                    user_query, context, max_recommendations
                )
                
                return Response({
                    'query': user_query,
                    'recommendations': recommendations,
                    'total': len(recommendations)
                })
                
            except Exception as e:
                logger.error(f"Recommendation error: {str(e)}")
                return Response(
                    {'error': 'Lỗi trong quá trình tạo gợi ý'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KnowledgeStatsViewSet(viewsets.ViewSet):
    """ViewSet cho thống kê kiến thức"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Thống kê tổng quan"""
        try:
            stats = {
                'total_entries': KnowledgeEntry.objects.filter(is_active=True).count(),
                'total_categories': KnowledgeCategory.objects.filter(is_active=True).count(),
                'total_diseases': DiseaseInformation.objects.filter(is_active=True).count(),
                'total_symptoms': SymptomInformation.objects.filter(is_active=True).count(),
                'total_terms': MedicalTerm.objects.filter(is_active=True).count(),
                'most_viewed_entries': [],
                'recent_searches': [],
                'response_stats': {}
            }
            
            # Most viewed entries
            most_viewed = KnowledgeEntry.objects.filter(
                is_active=True
            ).order_by('-view_count')[:5]
            
            stats['most_viewed_entries'] = [
                {
                    'id': str(entry.id),
                    'title': entry.title,
                    'view_count': entry.view_count,
                    'category': entry.category.name
                }
                for entry in most_viewed
            ]
            
            # Response type statistics
            response_stats = ChatbotResponse.objects.filter(
                is_active=True
            ).values('response_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            stats['response_stats'] = {
                item['response_type']: item['count'] for item in response_stats
            }
            
            serializer = KnowledgeStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return Response(
                {'error': 'Lỗi khi tạo thống kê'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackViewSet(viewsets.ViewSet):
    """ViewSet cho phản hồi người dùng"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Gửi phản hồi"""
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            try:
                response_id = serializer.validated_data['response_id']
                rating = serializer.validated_data['rating']
                comment = serializer.validated_data.get('comment', '')
                
                # Cập nhật rating cho ChatbotResponse
                try:
                    chatbot_response = ChatbotResponse.objects.get(id=response_id)
                    chatbot_response.user_feedback = rating
                    chatbot_response.save()
                    
                    return Response({
                        'message': 'Cảm ơn phản hồi của bạn!',
                        'rating': rating
                    })
                    
                except ChatbotResponse.DoesNotExist:
                    return Response(
                        {'error': 'Không tìm thấy phản hồi'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
            except Exception as e:
                logger.error(f"Feedback error: {str(e)}")
                return Response(
                    {'error': 'Lỗi khi gửi phản hồi'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
