from rest_framework import serializers
from core.models import Pickup, WasteType, PickupWasteType
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role',
                 'province', 'city', 'barangay', 'house_id', 'address', 'is_active']
        read_only_fields = ['id', 'is_active']


class WasteTypeSerializer(serializers.ModelSerializer):
    """Serializer for WasteType model"""

    class Meta:
        model = WasteType
        fields = ['id', 'name', 'description', 'recyclable', 'hazardous', 'base_fee', 'is_active']


class PickupWasteTypeSerializer(serializers.ModelSerializer):
    """Serializer for PickupWasteType model"""

    waste_type = WasteTypeSerializer(read_only=True)
    waste_type_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PickupWasteType
        fields = ['id', 'waste_type', 'waste_type_id', 'quantity', 'weight_kg']


class PickupSerializer(serializers.ModelSerializer):
    """Serializer for Pickup model"""

    user = UserSerializer(read_only=True)
    assigned_staff = UserSerializer(read_only=True)
    waste_types = PickupWasteTypeSerializer(source='pickupwastetype_set', many=True, read_only=True)

    class Meta:
        model = Pickup
        fields = ['id', 'user', 'date', 'time', 'priority', 'notes', 'status',
                 'assigned_staff', 'completed_at', 'completion_notes', 'created_at',
                 'updated_at', 'waste_types']
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Only allow status updates for staff
        user = self.context['request'].user
        if user.role not in ['admin', 'staff']:
            validated_data.pop('status', None)
            validated_data.pop('assigned_staff', None)
        return super().update(instance, validated_data)


class PickupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating pickups with waste types"""

    waste_types_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Pickup
        fields = ['date', 'time', 'priority', 'notes', 'waste_types_data']

    def create(self, validated_data):
        waste_types_data = validated_data.pop('waste_types_data', [])
        validated_data['user'] = self.context['request'].user

        pickup = super().create(validated_data)

        # Create waste type associations
        for waste_data in waste_types_data:
            try:
                waste_type = WasteType.objects.get(id=waste_data['waste_type_id'])
                PickupWasteType.objects.create(
                    pickup=pickup,
                    waste_type=waste_type,
                    quantity=waste_data.get('quantity', 1),
                    weight_kg=waste_data.get('weight_kg')
                )
            except (WasteType.DoesNotExist, KeyError):
                continue

        return pickup