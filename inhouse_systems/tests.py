from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from .models import InHouseSystem
from common.models import ProofModel


class InHouseSystemTests(TestCase):
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
        self.developer = User.objects.create_user(
            username='developer',
            password='password123',
            email='dev@example.com'
        )
        for perm_name in ['view_inhousesystem', 'add_inhousesystem', 'change_inhousesystem']:
            perm = Permission.objects.get(codename=perm_name)
            self.developer.user_permissions.add(perm)

    def test_create_inhouse_system_model(self):
        system = InHouseSystem.objects.create(
            system_name='Internal BI Portal',
            replaced_vendor_tool='Tableau Server',
            annual_cost_saved_usd=12500.00,
            deployment_date=self.today - timedelta(days=60),
            status=InHouseSystem.DevelopmentStatus.LIVE,
            efficiency_pct=98.50,
            packageable_for_external_sale=True,
            proof_type=ProofModel.ProofType.DOC_URL,
            proof_reference='https://wiki.company.com/systems/bi-portal',
            proof_description='Architecture signoff and migration document'
        )

        self.assertEqual(system.system_name, 'Internal BI Portal')
        self.assertEqual(system.annual_cost_saved_usd, 12500.00)
        self.assertEqual(system.status, 'LIVE')
        self.assertTrue(system.packageable_for_external_sale)

    def test_api_permission_denials(self):
        # Anonymous
        res_anon = self.client.get('/api/v1/systems/inhouse/')
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Regular user without permission
        self.client.force_authenticate(user=self.regular_user)
        res_reg = self.client.get('/api/v1/systems/inhouse/')
        self.assertEqual(res_reg.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_create_inhouse_system(self):
        self.client.force_authenticate(user=self.developer)
        payload = {
            'system_name': 'Automated Asset Tracker',
            'replaced_vendor_tool': 'Snipe-IT Hosted Enterprise',
            'annual_cost_saved_usd': 9600.00,
            'deployment_date': self.today.isoformat(),
            'status': 'LIVE',
            'efficiency_pct': 96.00,
            'packageable_for_external_sale': False,
            'proof_type': 'CLOUD_LINK',
            'proof_reference': 'https://drive.company.com/projects/asset-tracker-roi.pdf',
            'proof_description': 'Signed financial savings audit'
        }

        response = self.client.post('/api/v1/systems/inhouse/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['system_name'], 'Automated Asset Tracker')
        self.assertEqual(response.data['status'], 'LIVE')
        self.assertEqual(float(response.data['annual_cost_saved_usd']), 9600.00)
