from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Invoice, InvoiceItem, Payment, InsuranceClaim
from .serializers import (
    InvoiceSerializer, InvoiceDetailSerializer, InvoiceCreateSerializer,
    InvoiceItemSerializer, PaymentSerializer, PaymentCreateSerializer,
    InsuranceClaimSerializer, InsuranceClaimCreateSerializer
)
from .authentication import HeaderAuthentication
from .permissions import IsAdmin, IsAdminOrBillingStaff, IsPatientOwner, IsAdminOrOwner
from .services import (
    create_invoice_from_appointment, create_invoice_from_lab_test,
    create_invoice_from_prescription, create_invoice_from_medical_record,
    apply_insurance_to_invoice
)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing invoices.
    """
    queryset = Invoice.objects.all().order_by('-created_at')
    authentication_classes = [HeaderAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice_number', 'status', 'patient_id']
    ordering_fields = ['issue_date', 'due_date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrBillingStaff]
        else:
            # Allow patients to view their own invoices
            permission_classes = [IsAdminOrOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Invoice.objects.all().order_by('-created_at')

        # Filter by patient_id if the user is a patient
        if self.request.user and self.request.user.get('role') == 'PATIENT':
            queryset = queryset.filter(patient_id=self.request.user.get('id'))

        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by patient_id if provided (for admin/staff)
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id and (self.request.user.get('role') in ['ADMIN', 'BILLING_STAFF', 'INSURANCE_PROVIDER']):
            queryset = queryset.filter(patient_id=patient_id)

        return queryset

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        invoice = self.get_object()
        serializer = InvoiceItemSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(invoice=invoice)

            # Update invoice total
            invoice.total_amount += serializer.validated_data['total_price']
            invoice.final_amount = invoice.total_amount - invoice.discount + invoice.tax
            invoice.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        invoice = self.get_object()
        serializer = PaymentCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(invoice=invoice)

            # Update invoice status based on payments
            # Include the new payment in the calculation
            from decimal import Decimal
            total_paid = sum(payment.amount for payment in invoice.payments.all()) + Decimal(serializer.validated_data['amount'])

            if total_paid >= invoice.final_amount:
                invoice.status = Invoice.Status.PAID
            elif total_paid > 0:
                invoice.status = Invoice.Status.PARTIALLY_PAID

            invoice.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit_insurance_claim(self, request, pk=None):
        invoice = self.get_object()
        serializer = InsuranceClaimCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(invoice=invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def apply_insurance(self, request, pk=None):
        """
        Apply insurance coverage to an invoice automatically.
        """
        invoice = self.get_object()

        # Check if invoice is already paid
        if invoice.status == Invoice.Status.PAID:
            return Response(
                {'error': 'Cannot apply insurance to a paid invoice'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Apply insurance
        claim = apply_insurance_to_invoice(invoice, request.headers)

        if not claim:
            return Response(
                {'error': 'No active insurance found or failed to apply insurance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return updated invoice with insurance claim
        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing invoice items.
    """
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    authentication_classes = [HeaderAuthentication]
    permission_classes = [IsAdminOrBillingStaff]

    def get_queryset(self):
        invoice_id = self.request.query_params.get('invoice_id', None)
        if invoice_id:
            return InvoiceItem.objects.filter(invoice_id=invoice_id)
        return InvoiceItem.objects.all()


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing payments.
    """
    queryset = Payment.objects.all().order_by('-payment_date')
    serializer_class = PaymentSerializer
    authentication_classes = [HeaderAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrBillingStaff]
        else:
            permission_classes = [IsAdminOrOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Payment.objects.all().order_by('-payment_date')

        # Filter by invoice_id if provided
        invoice_id = self.request.query_params.get('invoice_id', None)
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)

        # Filter by patient_id if the user is a patient
        if self.request.user and self.request.user.get('role') == 'PATIENT':
            queryset = queryset.filter(invoice__patient_id=self.request.user.get('id'))

        return queryset


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing insurance claims.
    """
    queryset = InsuranceClaim.objects.all().order_by('-submission_date')
    serializer_class = InsuranceClaimSerializer
    authentication_classes = [HeaderAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrBillingStaff]
        else:
            permission_classes = [IsAdminOrOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = InsuranceClaim.objects.all().order_by('-submission_date')

        # Filter by invoice_id if provided
        invoice_id = self.request.query_params.get('invoice_id', None)
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)

        # Filter by patient_id if the user is a patient
        if self.request.user and self.request.user.get('role') == 'PATIENT':
            queryset = queryset.filter(invoice__patient_id=self.request.user.get('id'))

        # Filter by insurance_provider_id if the user is an insurance provider
        if self.request.user and self.request.user.get('role') == 'INSURANCE_PROVIDER':
            queryset = queryset.filter(insurance_provider_id=self.request.user.get('id'))

        return queryset

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        claim = self.get_object()
        status_param = request.data.get('status', None)

        if not status_param:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        if status_param not in dict(InsuranceClaim.Status.choices):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        claim.status = status_param

        # If status is APPROVED or PARTIALLY_APPROVED, update approved_amount
        if status_param in [InsuranceClaim.Status.APPROVED, InsuranceClaim.Status.PARTIALLY_APPROVED]:
            approved_amount = request.data.get('approved_amount', None)
            if approved_amount is not None:
                claim.approved_amount = approved_amount

        # If status is REJECTED, update rejection_reason
        if status_param == InsuranceClaim.Status.REJECTED:
            rejection_reason = request.data.get('rejection_reason', None)
            if rejection_reason:
                claim.rejection_reason = rejection_reason

        claim.save()

        # If claim is approved, create a payment
        if status_param == InsuranceClaim.Status.APPROVED and claim.approved_amount:
            payment = Payment.objects.create(
                invoice=claim.invoice,
                payment_method=Payment.PaymentMethod.INSURANCE,
                amount=claim.approved_amount,
                payment_date=claim.updated_at,
                status=Payment.Status.COMPLETED,
                notes=f"Insurance payment for claim #{claim.claim_number}"
            )

            # Update invoice status
            total_paid = sum(payment.amount for payment in claim.invoice.payments.all())

            if total_paid >= claim.invoice.final_amount:
                claim.invoice.status = Invoice.Status.PAID
            elif total_paid > 0:
                claim.invoice.status = Invoice.Status.PARTIALLY_PAID

            claim.invoice.save()

        serializer = InsuranceClaimSerializer(claim)
        return Response(serializer.data)


# API endpoints for creating invoices from other services
@api_view(['POST'])
def create_invoice_from_appointment_view(request):
    """
    Create an invoice from an appointment.
    """
    appointment_id = request.data.get('appointment_id')
    if not appointment_id:
        return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    invoice = create_invoice_from_appointment(appointment_id, request.headers)
    if not invoice:
        return Response({'error': 'Failed to create invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Apply insurance automatically if requested
    apply_insurance = request.data.get('apply_insurance', True)
    if apply_insurance:
        apply_insurance_to_invoice(invoice, request.headers)

    serializer = InvoiceDetailSerializer(invoice)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice_from_lab_test_view(request):
    """
    Create an invoice from a lab test.
    """
    lab_test_id = request.data.get('lab_test_id')
    if not lab_test_id:
        return Response({'error': 'Lab test ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    invoice = create_invoice_from_lab_test(lab_test_id, request.headers)
    if not invoice:
        return Response({'error': 'Failed to create invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Apply insurance automatically if requested
    apply_insurance = request.data.get('apply_insurance', True)
    if apply_insurance:
        apply_insurance_to_invoice(invoice, request.headers)

    serializer = InvoiceDetailSerializer(invoice)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice_from_prescription_view(request):
    """
    Create an invoice from a prescription.
    """
    prescription_id = request.data.get('prescription_id')
    if not prescription_id:
        return Response({'error': 'Prescription ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    invoice = create_invoice_from_prescription(prescription_id, request.headers)
    if not invoice:
        return Response({'error': 'Failed to create invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Apply insurance automatically if requested
    apply_insurance = request.data.get('apply_insurance', True)
    if apply_insurance:
        apply_insurance_to_invoice(invoice, request.headers)

    serializer = InvoiceDetailSerializer(invoice)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice_from_medical_record_view(request):
    """
    Create an invoice from a medical record.
    """
    record_id = request.data.get('record_id')
    if not record_id:
        return Response({'error': 'Medical record ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    invoice = create_invoice_from_medical_record(record_id, request.headers)
    if not invoice:
        return Response({'error': 'Failed to create invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Apply insurance automatically if requested
    apply_insurance = request.data.get('apply_insurance', True)
    if apply_insurance:
        apply_insurance_to_invoice(invoice, request.headers)

    serializer = InvoiceDetailSerializer(invoice)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
