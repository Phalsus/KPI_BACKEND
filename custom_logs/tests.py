from django.test import TestCase
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from rest_framework import status
from .models import KPIMaster, CustomWorkLog
from common.models import ProofModel


class KPIMasterAndWorkLogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.authorized_user = User.objects.create_user(
            username='auth_user',
            password='password123',
            email='auth@example.com'
        )
        # Grant specific permissions to authorized_user
        for perm_name in ['view_kpimaster', 'view_customworklog', 'add_customworklog', 'change_customworklog']:
            perm = Permission.objects.get(codename=perm_name)
            self.authorized_user.user_permissions.add(perm)

    def test_seeded_kpi_count_and_distribution(self):
        self.assertEqual(KPIMaster.objects.count(), 21)
        self.assertEqual(KPIMaster.objects.filter(perspective='FINANCE').count(), 4)
        self.assertEqual(KPIMaster.objects.filter(perspective='CUSTOMER').count(), 5)
        self.assertEqual(KPIMaster.objects.filter(perspective='PROCESS').count(), 6)
        self.assertEqual(KPIMaster.objects.filter(perspective='LEARNING').count(), 2)
        self.assertEqual(KPIMaster.objects.filter(perspective='BEHAVIORAL').count(), 4)

    def test_kpi_str_representation(self):
        kpi = KPIMaster.objects.get(code='FIN_REV_TARGET')
        self.assertIn('Finance', str(kpi))
        self.assertIn('Annual Revenue Target Achievement', str(kpi))

    def test_create_work_log_with_proof(self):
        primary = KPIMaster.objects.get(code='FIN_COST_SAVINGS')
        secondary = KPIMaster.objects.get(code='PROC_INNOVATION')
        log = CustomWorkLog.objects.create(
            title='Built In-house Analytics Script',
            description='Automated weekly report to replace manual tool',
            hours_spent=3.5,
            primary_kpi=primary,
            impact_result='Saved 5 engineer hours weekly',
            proof_type=ProofModel.ProofType.CLOUD_LINK,
            proof_reference='https://drive.google.com/audit/report-123',
            proof_description='Approved by Team Lead'
        )
        log.additional_kpis.add(secondary)

        self.assertEqual(log.primary_kpi.code, 'FIN_COST_SAVINGS')
        self.assertEqual(log.additional_kpis.count(), 1)
        self.assertEqual(log.proof_type, 'CLOUD_LINK')
        self.assertEqual(log.hours_spent, 3.5)

    def test_api_permission_anonymous_denied(self):
        response = self.client.get('/api/v1/custom-logs/kpis/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_permission_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/custom-logs/kpis/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_permission_authorized_user_allowed(self):
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get('/api/v1/custom-logs/kpis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results'] if 'results' in response.data else response.data), 21)

    def test_api_permission_superuser_allowed(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/v1/custom-logs/kpis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_work_log_via_api(self):
        self.client.force_authenticate(user=self.authorized_user)
        primary = KPIMaster.objects.get(code='CUST_UPTIME')
        payload = {
            'title': 'Server Failover Config',
            'description': 'Configured automatic failover for high availability',
            'hours_spent': 4.0,
            'primary_kpi': primary.id,
            'impact_result': 'Zero downtime recorded',
            'proof_type': 'DOC_URL',
            'proof_reference': 'https://wiki.internal.net/failover-doc',
            'proof_description': 'Documentation URL in internal wiki'
        }
        response = self.client.post('/api/v1/custom-logs/work-logs/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Server Failover Config')
        self.assertEqual(response.data['primary_kpi_details']['code'], 'CUST_UPTIME')
