from rest_framework import serializers
from .models import (
    Medication, Prescription, PrescriptionItem,
    Inventory, Dispensing, DispensingItem
)

class MedicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Medication model.
    """
    dosage_form_display = serializers.CharField(source='get_dosage_form_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'description', 'dosage_form', 'dosage_form_display',
            'strength', 'manufacturer', 'category', 'category_display',
            'requires_prescription', 'side_effects', 'contraindications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PrescriptionItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PrescriptionItem model.
    """
    medication_details = MedicationSerializer(source='medication', read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'prescription', 'medication', 'medication_details',
            'dosage', 'frequency', 'duration', 'instructions', 'quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'prescription': {'required': False}}


class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Prescription model.
    """
    items = PrescriptionItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient_id', 'doctor_id', 'date_prescribed',
            'status', 'status_display', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Prescription with items.
    """
    items = PrescriptionItemSerializer(many=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient_id', 'doctor_id', 'date_prescribed',
            'status', 'notes', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)

        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)

        return prescription


class InventorySerializer(serializers.ModelSerializer):
    """
    Serializer for Inventory model.
    """
    medication_details = MedicationSerializer(source='medication', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'medication', 'medication_details', 'batch_number',
            'expiry_date', 'quantity', 'unit_price', 'location',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DispensingItemSerializer(serializers.ModelSerializer):
    """
    Serializer for DispensingItem model.
    """
    prescription_item_details = PrescriptionItemSerializer(source='prescription_item', read_only=True)
    inventory_details = InventorySerializer(source='inventory', read_only=True)

    class Meta:
        model = DispensingItem
        fields = [
            'id', 'dispensing', 'prescription_item', 'prescription_item_details',
            'inventory', 'inventory_details', 'quantity_dispensed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DispensingSerializer(serializers.ModelSerializer):
    """
    Serializer for Dispensing model.
    """
    items = DispensingItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prescription_details = PrescriptionSerializer(source='prescription', read_only=True)

    class Meta:
        model = Dispensing
        fields = [
            'id', 'prescription', 'prescription_details', 'pharmacist_id',
            'date_dispensed', 'status', 'status_display', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DispensingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Dispensing with items.
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Dispensing
        fields = [
            'id', 'prescription', 'pharmacist_id', 'date_dispensed',
            'status', 'notes', 'items'
        ]

    def validate(self, data):
        items_data = data.get('items', [])
        prescription = data.get('prescription')

        # Check if all prescription items are included
        prescription_items = PrescriptionItem.objects.filter(prescription=prescription)
        prescription_item_ids = set(item.id for item in prescription_items)
        dispensing_item_ids = set(item.get('prescription_item') for item in items_data)

        if prescription_item_ids != dispensing_item_ids:
            raise serializers.ValidationError("All prescription items must be dispensed")

        # Check inventory availability
        for item_data in items_data:
            prescription_item = PrescriptionItem.objects.get(id=item_data.get('prescription_item'))
            inventory = Inventory.objects.get(id=item_data.get('inventory'))
            quantity_dispensed = item_data.get('quantity_dispensed')

            if inventory.medication.id != prescription_item.medication.id:
                raise serializers.ValidationError(
                    f"Inventory item {inventory.id} does not match medication in prescription item {prescription_item.id}"
                )

            if inventory.quantity < quantity_dispensed:
                raise serializers.ValidationError(
                    f"Not enough stock for medication {prescription_item.medication.name}. "
                    f"Available: {inventory.quantity}, Required: {quantity_dispensed}"
                )

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        dispensing = Dispensing.objects.create(**validated_data)

        # Create dispensing items and update inventory
        for item_data in items_data:
            prescription_item = PrescriptionItem.objects.get(id=item_data.get('prescription_item'))
            inventory = Inventory.objects.get(id=item_data.get('inventory'))
            quantity_dispensed = item_data.get('quantity_dispensed')

            # Create dispensing item
            DispensingItem.objects.create(
                dispensing=dispensing,
                prescription_item=prescription_item,
                inventory=inventory,
                quantity_dispensed=quantity_dispensed
            )

            # Update inventory
            inventory.quantity -= quantity_dispensed
            inventory.save()

        # Update prescription status
        prescription = dispensing.prescription
        prescription.status = 'DISPENSED'
        prescription.save()

        return dispensing
