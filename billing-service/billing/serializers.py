from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment, InsuranceClaim


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ['invoice']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['invoice']


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = '__all__'
        read_only_fields = ['invoice']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    insurance_claims = InsuranceClaimSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    insurance_claims = InsuranceClaimSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)

        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount', 'transaction_id', 'payment_date', 'status', 'notes']


class InsuranceClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = ['insurance_provider_id', 'policy_number', 'claim_number', 'submission_date', 'status', 'approved_amount', 'rejection_reason', 'notes']
