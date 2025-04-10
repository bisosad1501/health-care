from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Notification, NotificationTemplate, NotificationSchedule
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer, NotificationScheduleSerializer,
    SendEmailNotificationSerializer, SendSMSNotificationSerializer, ScheduleNotificationSerializer,
    EventSerializer
)
from .tasks import send_email_notification, send_sms_notification, send_notification_from_template
from .authentication import HeaderAuthentication
from .permissions import IsAdmin, IsAdminOrStaff
from .event_handlers import (
    process_appointment_event, process_medical_record_event, process_billing_event,
    process_pharmacy_event, process_laboratory_event
)
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notifications.
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    authentication_classes = [HeaderAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['recipient_id', 'recipient_email', 'recipient_phone', 'subject', 'content']
    ordering_fields = ['created_at', 'sent_at', 'delivered_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Notification.objects.all().order_by('-created_at')

        # Filter by recipient_id if provided
        recipient_id = self.request.query_params.get('recipient_id', None)
        if recipient_id:
            queryset = queryset.filter(recipient_id=recipient_id)

        # Filter by notification_type if provided
        notification_type = self.request.query_params.get('notification_type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Filter by channel if provided
        channel = self.request.query_params.get('channel', None)
        if channel:
            queryset = queryset.filter(channel=channel)

        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by reference_id if provided
        reference_id = self.request.query_params.get('reference_id', None)
        if reference_id:
            queryset = queryset.filter(reference_id=reference_id)

        # Filter by reference_type if provided
        reference_type = self.request.query_params.get('reference_type', None)
        if reference_type:
            queryset = queryset.filter(reference_type=reference_type)

        return queryset

    @action(detail=False, methods=['post'])
    def send_email(self, request):
        """
        Send an email notification.
        """
        serializer = SendEmailNotificationSerializer(data=request.data)
        if serializer.is_valid():
            # Create a notification
            notification = Notification(
                recipient_id=serializer.validated_data['recipient_id'],
                recipient_type=serializer.validated_data['recipient_type'],
                recipient_email=serializer.validated_data['recipient_email'],
                notification_type=serializer.validated_data['notification_type'],
                channel=Notification.Channel.EMAIL,
                subject=serializer.validated_data['subject'],
                content=serializer.validated_data['content'],
                reference_id=serializer.validated_data.get('reference_id'),
                reference_type=serializer.validated_data.get('reference_type'),
                status=Notification.Status.PENDING
            )
            notification.save()

            # Send the email asynchronously
            send_email_notification.delay(notification.id)

            return Response({'id': notification.id, 'status': 'pending'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_sms(self, request):
        """
        Send an SMS notification.
        """
        serializer = SendSMSNotificationSerializer(data=request.data)
        if serializer.is_valid():
            # Create a notification
            notification = Notification(
                recipient_id=serializer.validated_data['recipient_id'],
                recipient_type=serializer.validated_data['recipient_type'],
                recipient_phone=serializer.validated_data['recipient_phone'],
                notification_type=serializer.validated_data['notification_type'],
                channel=Notification.Channel.SMS,
                subject='',
                content=serializer.validated_data['content'],
                reference_id=serializer.validated_data.get('reference_id'),
                reference_type=serializer.validated_data.get('reference_type'),
                status=Notification.Status.PENDING
            )
            notification.save()

            # Send the SMS asynchronously
            send_sms_notification.delay(notification.id)

            return Response({'id': notification.id, 'status': 'pending'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_from_template(self, request):
        """
        Send a notification using a template.
        """
        template_id = request.data.get('template_id')
        recipient_id = request.data.get('recipient_id')
        recipient_type = request.data.get('recipient_type')
        context_data = request.data.get('context_data', {})
        reference_id = request.data.get('reference_id')
        reference_type = request.data.get('reference_type')

        if not template_id or not recipient_id or not recipient_type:
            return Response(
                {'error': 'template_id, recipient_id, and recipient_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send the notification asynchronously
        notification_id = send_notification_from_template.delay(
            template_id, recipient_id, recipient_type, context_data, reference_id, reference_type
        )

        if notification_id:
            return Response({'id': notification_id, 'status': 'pending'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error': 'Failed to send notification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notification templates.
    """
    queryset = NotificationTemplate.objects.all().order_by('-created_at')
    serializer_class = NotificationTemplateSerializer
    authentication_classes = [HeaderAuthentication]
    permission_classes = [IsAdminOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject_template', 'content_template']
    ordering_fields = ['name', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = NotificationTemplate.objects.all().order_by('-created_at')

        # Filter by notification_type if provided
        notification_type = self.request.query_params.get('notification_type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Filter by channel if provided
        channel = self.request.query_params.get('channel', None)
        if channel:
            queryset = queryset.filter(channel=channel)

        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)

        return queryset


class NotificationScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notification schedules.
    """
    queryset = NotificationSchedule.objects.all().order_by('-scheduled_at')
    serializer_class = NotificationScheduleSerializer
    authentication_classes = [HeaderAuthentication]
    permission_classes = [IsAdminOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['recipient_id', 'subject', 'content']
    ordering_fields = ['scheduled_at', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = NotificationSchedule.objects.all().order_by('-scheduled_at')

        # Filter by recipient_id if provided
        recipient_id = self.request.query_params.get('recipient_id', None)
        if recipient_id:
            queryset = queryset.filter(recipient_id=recipient_id)

        # Filter by notification_type if provided
        notification_type = self.request.query_params.get('notification_type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by scheduled_after if provided
        scheduled_after = self.request.query_params.get('scheduled_after', None)
        if scheduled_after:
            queryset = queryset.filter(scheduled_at__gte=scheduled_after)

        # Filter by scheduled_before if provided
        scheduled_before = self.request.query_params.get('scheduled_before', None)
        if scheduled_before:
            queryset = queryset.filter(scheduled_at__lte=scheduled_before)

        return queryset

    @action(detail=False, methods=['post'])
    def schedule(self, request):
        """
        Schedule a notification.
        """
        serializer = ScheduleNotificationSerializer(data=request.data)
        if serializer.is_valid():
            # Create a notification schedule
            schedule = NotificationSchedule(
                recipient_id=serializer.validated_data['recipient_id'],
                recipient_type=serializer.validated_data['recipient_type'],
                recipient_email=serializer.validated_data.get('recipient_email'),
                recipient_phone=serializer.validated_data.get('recipient_phone'),
                notification_type=serializer.validated_data['notification_type'],
                channel=serializer.validated_data['channel'],
                subject=serializer.validated_data.get('subject', ''),
                content=serializer.validated_data['content'],
                scheduled_at=serializer.validated_data['scheduled_at'],
                status=NotificationSchedule.Status.SCHEDULED,
                reference_id=serializer.validated_data.get('reference_id'),
                reference_type=serializer.validated_data.get('reference_type')
            )

            # Set template if provided
            template_id = serializer.validated_data.get('template_id')
            if template_id:
                try:
                    template = NotificationTemplate.objects.get(id=template_id, is_active=True)
                    schedule.template = template
                except NotificationTemplate.DoesNotExist:
                    return Response(
                        {'error': f'Template with ID {template_id} not found or not active'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            schedule.save()

            return Response(
                NotificationScheduleSerializer(schedule).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a scheduled notification.
        """
        schedule = self.get_object()

        if schedule.status != NotificationSchedule.Status.SCHEDULED:
            return Response(
                {'error': f'Cannot cancel notification with status {schedule.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        schedule.status = NotificationSchedule.Status.CANCELLED
        schedule.save()

        return Response(
            NotificationScheduleSerializer(schedule).data,
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def process_event(request):
    """
    Process events from other services and create appropriate notifications.
    """
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        service = serializer.validated_data['service']
        event_data = serializer.validated_data['event_data']

        try:
            # Process the event based on the service
            if service == 'APPOINTMENT':
                result = process_appointment_event(event_data)
            elif service == 'MEDICAL_RECORD':
                result = process_medical_record_event(event_data)
            elif service == 'BILLING':
                result = process_billing_event(event_data)
            elif service == 'PHARMACY':
                result = process_pharmacy_event(event_data)
            elif service == 'LABORATORY':
                result = process_laboratory_event(event_data)
            else:
                return Response({'error': f'Unknown service: {service}'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(result, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"Error processing {service} event: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
