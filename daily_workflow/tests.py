from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from .models import DailyCheckin


class DailyWorkflowTests(TestCase):
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
        self.engineer = User.objects.create_user(
            username='engineer',
            password='password123',
            email='eng@example.com'
        )
        for perm_name in ['view_dailycheckin', 'add_dailycheckin', 'change_dailycheckin']:
            perm = Permission.objects.get(codename=perm_name)
            self.engineer.user_permissions.add(perm)

    def test_create_daily_checkin_success(self):
        checkin = DailyCheckin.objects.create(
            date=self.today,
            scrum_attended=True,
            scrum_joined_at='09:00:00',
            jira_updated=True,
            jira_tickets_worked='PROJ-101, PROJ-102',
            github_pushed=True,
            github_pr_urls='https://github.com/org/repo/pull/42',
            daily_notes='Completed auth module migration and testing',
            blockers=None
        )
        self.assertEqual(checkin.date, self.today)
        self.assertTrue(checkin.scrum_attended)
        self.assertFalse(checkin.has_potential_delay)

    def test_5_day_delay_escalation_validation_success(self):
        checkin = DailyCheckin(
            date=self.today + timedelta(days=1),
            scrum_attended=True,
            jira_updated=True,
            jira_tickets_worked='PROJ-105',
            github_pushed=True,
            daily_notes='Investigating third-party gateway latency',
            has_potential_delay=True,
            escalated_5_days_prior=True,
            delay_escalation_details='Third-party vendor API documentation missing OAuth specs; line manager alerted.'
        )
        # Should not raise
        checkin.full_clean()
        checkin.save()
        self.assertTrue(checkin.has_potential_delay)
        self.assertTrue(checkin.escalated_5_days_prior)

    def test_5_day_delay_missing_details_raises_error(self):
        checkin = DailyCheckin(
            date=self.today + timedelta(days=2),
            scrum_attended=True,
            jira_updated=True,
            jira_tickets_worked='PROJ-106',
            github_pushed=True,
            daily_notes='Backend migration stuck',
            has_potential_delay=True,
            delay_escalation_details='' # Missing required explanation
        )
        with self.assertRaises(ValidationError):
            checkin.full_clean()

    def test_api_permission_anonymous_denied(self):
        response = self.client.get('/api/v1/workflow/checkins/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_permission_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/workflow/checkins/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_create_checkin_success(self):
        self.client.force_authenticate(user=self.engineer)
        payload = {
            'date': (self.today + timedelta(days=3)).isoformat(),
            'scrum_attended': True,
            'scrum_joined_at': '09:00:00',
            'jira_updated': True,
            'jira_tickets_worked': 'KPI-201, KPI-202',
            'github_pushed': True,
            'github_pr_urls': 'https://github.com/org/kpi/pull/15',
            'daily_notes': 'Implemented DRF viewsets and url routes',
            'blockers': 'None',
            'has_potential_delay': False
        }
        response = self.client.post('/api/v1/workflow/checkins/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['jira_tickets_worked'], 'KPI-201, KPI-202')

    def test_api_create_checkin_with_delay_requires_details(self):
        self.client.force_authenticate(user=self.engineer)
        payload = {
            'date': (self.today + timedelta(days=4)).isoformat(),
            'scrum_attended': True,
            'scrum_joined_at': '09:00:00',
            'jira_updated': True,
            'jira_tickets_worked': 'KPI-203',
            'github_pushed': False,
            'daily_notes': 'Blocked by database migration deadlock',
            'has_potential_delay': True,
            'delay_escalation_details': '' # Empty string should trigger validation error
        }
        response = self.client.post('/api/v1/workflow/checkins/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('delay_escalation_details', response.data)
