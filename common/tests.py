from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Permission, Group
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework import status
from common.models import ProofModel
from common.permissions import (
    BaseModelPermission,
    SupportIncidentPermission,
    DailyCheckinPermission,
    ScorecardSummaryPermission
)


class DummyProofModel(ProofModel):
    name = "Test"

    class Meta:
        app_label = 'common'


class CommonModuleTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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
        self.exec_user = User.objects.create_user(
            username='exec_user',
            password='password123',
            email='exec@example.com'
        )
        exec_group, _ = Group.objects.get_or_create(name='Executive / Leadership')
        self.exec_user.groups.add(exec_group)

    def test_proof_model_choices(self):
        self.assertEqual(ProofModel.ProofType.CLOUD_LINK, 'CLOUD_LINK')
        self.assertEqual(ProofModel.ProofType.EMAIL_REF, 'EMAIL_REF')
        self.assertEqual(ProofModel.ProofType.DOC_URL, 'DOC_URL')
        self.assertEqual(ProofModel.ProofType.NOTE, 'NOTE')

    def test_base_model_permission_anonymous(self):
        request = self.factory.get('/api/v1/support/incidents/')
        request.user = None
        perm = SupportIncidentPermission()
        self.assertFalse(perm.has_permission(request, None))

    def test_base_model_permission_superuser(self):
        request = self.factory.get('/api/v1/support/incidents/')
        request.user = self.superuser
        perm = SupportIncidentPermission()
        self.assertTrue(perm.has_permission(request, None))

    def test_base_model_permission_denied_without_perm(self):
        request = self.factory.get('/api/v1/support/incidents/')
        request.user = self.regular_user
        perm = SupportIncidentPermission()
        self.assertFalse(perm.has_permission(request, None))

    def test_scorecard_permission_executive_group(self):
        request = self.factory.get('/api/v1/scorecard/summary/')
        request.user = self.exec_user
        perm = ScorecardSummaryPermission()
        self.assertTrue(perm.has_permission(request, None))

    def test_scorecard_permission_regular_user_denied(self):
        request = self.factory.get('/api/v1/scorecard/summary/')
        request.user = self.regular_user
        perm = ScorecardSummaryPermission()
        self.assertFalse(perm.has_permission(request, None))

    def test_setup_roles_management_command(self):
        call_command('setup_roles')
        expected_groups = [
            'Support Desk Agent',
            'Asset Manager',
            'Developer / Engineer',
            'HR / People Ops',
            'Executive / Leadership'
        ]
        for name in expected_groups:
            group = Group.objects.filter(name=name).first()
            self.assertIsNotNone(group, f"Group '{name}' should exist")
            self.assertGreater(group.permissions.count(), 0, f"Group '{name}' should have permissions")

    def test_role_based_model_permission_granularity(self):
        call_command('setup_roles')

        # Support Desk Agent user
        support_agent = User.objects.create_user(
            username='agent_user',
            password='password123'
        )
        support_group = Group.objects.get(name='Support Desk Agent')
        support_agent.groups.add(support_group)

        # Refreshed permissions
        support_agent = User.objects.get(pk=support_agent.pk)

        # Check SupportIncident GET request
        req_support = self.factory.get('/api/v1/support/incidents/')
        req_support.user = support_agent
        self.assertTrue(SupportIncidentPermission().has_permission(req_support, None))

        # Check SupportIncident POST request
        req_support_post = self.factory.post('/api/v1/support/incidents/')
        req_support_post.user = support_agent
        self.assertTrue(SupportIncidentPermission().has_permission(req_support_post, None))

        # Check DailyCheckin GET request (should be denied)
        req_daily = self.factory.get('/api/v1/workflow/checkins/')
        req_daily.user = support_agent
        self.assertFalse(DailyCheckinPermission().has_permission(req_daily, None))

    def test_jwt_auth_flow(self):
        # 1. Login with valid credentials
        resp = self.client.post('/api/v1/auth/login/', {
            'username': 'regular_user',
            'password': 'password123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        access_token = resp.data['access']
        refresh_token = resp.data['refresh']

        # 2. Login with invalid credentials
        bad_resp = self.client.post('/api/v1/auth/login/', {
            'username': 'regular_user',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(bad_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # 3. Refresh access token
        refresh_resp = self.client.post('/api/v1/auth/refresh/', {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_resp.data)

        # 4. Access endpoint without token -> 401
        anon_client = APIClient()
        unauth_resp = anon_client.get('/api/v1/support/incidents/')
        self.assertEqual(unauth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # 5. Access endpoint with valid token
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        # regular_user doesn't have view_supportincident permission -> 403 Forbidden
        auth_resp = auth_client.get('/api/v1/support/incidents/')
        self.assertEqual(auth_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_default_admin_command(self):
        import os
        from unittest.mock import patch

        # 1. When users exist (from setUp), command should skip
        call_command('create_default_admin')
        # Total users created in setUp was 3 (superuser, regular_user, exec_user)
        self.assertEqual(User.objects.filter(username='env_admin').count(), 0)

        # 2. When database has no users, command creates user from env
        User.objects.all().delete()
        self.assertEqual(User.objects.count(), 0)

        with patch.dict(os.environ, {
            'DJANGO_SUPERUSER_USERNAME': 'env_admin',
            'DJANGO_SUPERUSER_EMAIL': 'env_admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'EnvPassword123!'
        }):
            call_command('create_default_admin')

        created_admin = User.objects.filter(username='env_admin').first()
        self.assertIsNotNone(created_admin)
        self.assertTrue(created_admin.is_superuser)
        self.assertTrue(created_admin.is_staff)
        self.assertTrue(created_admin.check_password('EnvPassword123!'))

