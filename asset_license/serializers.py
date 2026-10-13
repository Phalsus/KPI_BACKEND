from rest_framework import serializers
from django.utils import timezone
from .models import (
    AssetBrand,
    AssetModel,
    AssetUser,
    HardwareAsset,
    AssetAssignmentHistory,
    SoftwareLicense,
)


class AssetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetUser
        fields = ['id', 'full_name', 'email', 'department']


class AssetBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetBrand
        fields = ['id', 'name']


class AssetModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = AssetModel
        fields = ['id', 'brand', 'brand_name', 'name']


class AssetAssignmentHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = AssetAssignmentHistory
        fields = ['id', 'user', 'user_name', 'assigned_date', 'returned_date', 'notes']


class HardwareAssetSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    current_user_details = AssetUserSerializer(source='current_user', read_only=True)
    assignment_history = AssetAssignmentHistorySerializer(many=True, read_only=True)

    brand_input = serializers.CharField(write_only=True, required=False)
    model_input = serializers.CharField(write_only=True, required=False)
    current_user_input = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = HardwareAsset
        fields = [
            'id',
            'tag_id',
            'serial_number',
            'asset_type',
            'brand',
            'brand_name',
            'brand_input',
            'model',
            'model_name',
            'model_input',
            'current_user',
            'current_user_details',
            'current_user_input',
            'processor',
            'ram_gb',
            'storage_type',
            'storage_capacity',
            'status',
            'status_details',
            'date_bought',
            'cost',
            'proof_type',
            'proof_reference',
            'proof_description',
            'last_info_updated_at',
            'assignment_history',
            'created_at',
        ]
        extra_kwargs = {
            'brand': {'required': False, 'allow_null': True},
            'model': {'required': False, 'allow_null': True},
            'current_user': {'required': False, 'allow_null': True},
        }

    def _resolve_entities(self, validated_data):
        brand_str = validated_data.pop('brand_input', None)
        model_str = validated_data.pop('model_input', None)
        user_str = validated_data.pop('current_user_input', None)

        brand = validated_data.get('brand')
        if brand_str:
            brand, _ = AssetBrand.objects.get_or_create(name=brand_str.strip())
            validated_data['brand'] = brand

        if model_str:
            if not brand:
                raise serializers.ValidationError({"model_input": "Brand must be defined before adding model."})
            model_obj, _ = AssetModel.objects.get_or_create(brand=brand, name=model_str.strip())
            validated_data['model'] = model_obj

        if user_str is not None:
            if user_str and user_str.strip():
                user_obj, _ = AssetUser.objects.get_or_create(full_name=user_str.strip())
                validated_data['current_user'] = user_obj
            else:
                validated_data['current_user'] = None

        return validated_data

    def create(self, validated_data):
        validated_data = self._resolve_entities(validated_data)
        asset = super().create(validated_data)
        if asset.current_user:
            AssetAssignmentHistory.objects.create(
                asset=asset,
                user=asset.current_user,
                assigned_date=timezone.localdate(),
                notes="Initial deployment register"
            )
        return asset

    def update(self, instance, validated_data):
        old_user = instance.current_user
        validated_data = self._resolve_entities(validated_data)
        asset = super().update(instance, validated_data)

        new_user = asset.current_user
        if old_user != new_user:
            if old_user:
                AssetAssignmentHistory.objects.filter(
                    asset=asset, user=old_user, returned_date__isnull=True
                ).update(returned_date=timezone.localdate())
            if new_user:
                AssetAssignmentHistory.objects.create(
                    asset=asset,
                    user=new_user,
                    assigned_date=timezone.localdate(),
                    notes=f"Reassigned from {old_user.full_name if old_user else 'Storage Pool'}"
                )
        return asset


class SoftwareLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareLicense
        fields = [
            'id',
            'software_name',
            'vendor',
            'annual_cost_usd',
            'renewal_date',
            'is_active',
            'optimization_plan',
            'proof_type',
            'proof_reference',
            'proof_description',
        ]
