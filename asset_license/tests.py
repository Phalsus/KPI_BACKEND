from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from .models import (
    AssetBrand,
    AssetModel,
    AssetUser,
    HardwareAsset,
    AssetAssignmentHistory,
    SoftwareLicense,
)
from common.models import ProofModel


class AssetLicenseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.today = timezone.localdate()
        self.superuser = User.objects.create_superuser(
            username='admin_user',
            password='password123',
            email='admin@example.com'
        )
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='password123',
            email='user@example.com'
        )
        self.asset_manager = User.objects.create_user(
            username='asset_mgr',
            password='password123',
            email='mgr@example.com'
        )
        for perm_name in [
            'view_hardwareasset', 'add_hardwareasset', 'change_hardwareasset',
            'view_softwarelicense', 'add_softwarelicense',
            'view_assetuser', 'add_assetuser',
            'view_assetbrand', 'add_assetbrand',
            'view_assetmodel', 'add_assetmodel',
        ]:
            perm = Permission.objects.get(codename=perm_name)
            self.asset_manager.user_permissions.add(perm)

    def test_auto_creation_entities_via_api(self):
        self.client.force_authenticate(user=self.asset_manager)
        payload = {
            'tag_id': 'AST-LPT-001',
            'serial_number': 'SN-LEN-987654',
            'asset_type': 'LAPTOP',
            'brand_input': 'Lenovo',
            'model_input': 'ThinkPad T14 Gen 4',
            'current_user_input': 'Jane Doe',
            'processor': 'Intel Core i7-1365U',
            'ram_gb': 32,
            'storage_type': 'NVMe SSD',
            'storage_capacity': '1TB',
            'status': 'WORKING',
            'cost': 1450.00,
            'proof_type': 'CLOUD_LINK',
            'proof_reference': 'https://drive.company.com/assets/AST-LPT-001-invoice.pdf'
        }

        response = self.client.post('/api/v1/assets/hardware/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify database auto-creations
        self.assertTrue(AssetBrand.objects.filter(name='Lenovo').exists())
        self.assertTrue(AssetModel.objects.filter(name='ThinkPad T14 Gen 4').exists())
        self.assertTrue(AssetUser.objects.filter(full_name='Jane Doe').exists())

        asset = HardwareAsset.objects.get(tag_id='AST-LPT-001')
        self.assertEqual(asset.brand.name, 'Lenovo')
        self.assertEqual(asset.model.name, 'ThinkPad T14 Gen 4')
        self.assertEqual(asset.current_user.full_name, 'Jane Doe')

        # Verify initial assignment history automatically created
        history = AssetAssignmentHistory.objects.filter(asset=asset)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().user.full_name, 'Jane Doe')
        self.assertIsNone(history.first().returned_date)

    def test_reassignment_history_transitions(self):
        self.client.force_authenticate(user=self.asset_manager)
        # Create initial asset
        create_payload = {
            'tag_id': 'AST-LPT-002',
            'serial_number': 'SN-DELL-112233',
            'brand_input': 'Dell',
            'model_input': 'Latitude 7440',
            'current_user_input': 'Alice Smith',
            'processor': 'Core i5',
            'ram_gb': 16,
            'storage_capacity': '512GB',
            'proof_reference': 'https://drive.company.com/assets/AST-LPT-002.pdf'
        }
        res_create = self.client.post('/api/v1/assets/hardware/', create_payload, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        asset_id = res_create.data['id']

        # Reassign to Bob Johnson
        update_payload = {
            'current_user_input': 'Bob Johnson'
        }
        res_update = self.client.patch(f'/api/v1/assets/hardware/{asset_id}/', update_payload, format='json')
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)

        asset = HardwareAsset.objects.get(id=asset_id)
        self.assertEqual(asset.current_user.full_name, 'Bob Johnson')

        # Check assignment records: Alice returned today, Bob active
        alice_hist = AssetAssignmentHistory.objects.get(asset=asset, user__full_name='Alice Smith')
        bob_hist = AssetAssignmentHistory.objects.get(asset=asset, user__full_name='Bob Johnson')

        self.assertEqual(alice_hist.returned_date, self.today)
        self.assertIsNone(bob_hist.returned_date)

    def test_software_license_creation_and_permissions(self):
        self.client.force_authenticate(user=self.asset_manager)
        lic_payload = {
            'software_name': 'JetBrains All Products Pack',
            'vendor': 'JetBrains s.r.o.',
            'annual_cost_usd': 8990.00,
            'renewal_date': (self.today + timedelta(days=90)).isoformat(),
            'is_active': True,
            'optimization_plan': 'Downsized unused PyCharm individual licenses to floating pool.',
            'proof_type': 'CLOUD_LINK',
            'proof_reference': 'https://drive.company.com/licenses/jb-renewal-2026.pdf'
        }
        response = self.client.post('/api/v1/assets/licenses/', lic_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SoftwareLicense.objects.count(), 1)

    def test_api_permission_denials(self):
        # Anonymous
        res_anon = self.client.get('/api/v1/assets/hardware/')
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Regular user without permission
        self.client.force_authenticate(user=self.regular_user)
        res_reg = self.client.get('/api/v1/assets/hardware/')
        self.assertEqual(res_reg.status_code, status.HTTP_403_FORBIDDEN)
