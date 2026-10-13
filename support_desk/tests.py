from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from .models import SupportIncident
from common.models import ProofModel


class SupportIncidentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()
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
        self.support_agent = User.objects.create_user(
            username='support_agent',
            password='password123',
            email='agent@example.com'
        )
        for perm_name in ['view_supportincident', 'add_supportincident', 'change_supportincident']:
            perm = Permission.objects.get(codename=perm_name)
            self.support_agent.user_permissions.add(perm)

    def test_rtc_compliant_incident(self):
        incident = SupportIncident.objects.create(
            ticket_ref='INC-1001',
            title='Core switch port flap',
            system_name='Network Core',
            reported_at=self.now,
            acknowledged_at=self.now + timedelta(minutes=15),   # 15m <= 30m
            solution_provided_at=self.now + timedelta(minutes=45), # 45m <= 60m
            resolved_at=self.now + timedelta(hours=2),            # 2h <= 4h
            first_time_fix=True,
            csat_score=95.0,
            rca_notes='Bad SFP transceiver replaced',
            proof_type=ProofModel.ProofType.DOC_URL,
            proof_reference='https://confluence.internal/rca/INC-1001'
        )

        self.assertTrue(incident.ack_within_30m)
        self.assertTrue(incident.solution_within_1h)
        self.assertTrue(incident.resolved_within_4h)
        self.assertTrue(incident.is_rtc_compliant)

    def test_rtc_breached_ack_sla(self):
        incident = SupportIncident.objects.create(
            ticket_ref='INC-1002',
            title='Slow query on reporting DB',
            system_name='Analytics DB',
            reported_at=self.now,
            acknowledged_at=self.now + timedelta(minutes=35), # 35m > 30m BREACH
            solution_provided_at=self.now + timedelta(minutes=50),
            resolved_at=self.now + timedelta(hours=2),
            first_time_fix=True,
            csat_score=85.0
        )

        self.assertFalse(incident.ack_within_30m)
        self.assertTrue(incident.solution_within_1h)
        self.assertTrue(incident.resolved_within_4h)
        self.assertFalse(incident.is_rtc_compliant)

    def test_rtc_breached_solution_sla(self):
        incident = SupportIncident.objects.create(
            ticket_ref='INC-1003',
            title='VPN Gateway authentication timeout',
            system_name='VPN Gateway',
            reported_at=self.now,
            acknowledged_at=self.now + timedelta(minutes=10),
            solution_provided_at=self.now + timedelta(minutes=75), # 75m > 60m BREACH
            resolved_at=self.now + timedelta(hours=3),
            first_time_fix=True
        )

        self.assertTrue(incident.ack_within_30m)
        self.assertFalse(incident.solution_within_1h)
        self.assertTrue(incident.resolved_within_4h)
        self.assertFalse(incident.is_rtc_compliant)

    def test_rtc_breached_resolution_sla(self):
        incident = SupportIncident.objects.create(
            ticket_ref='INC-1004',
            title='Disk partition full on worker node',
            system_name='K8s Cluster',
            reported_at=self.now,
            acknowledged_at=self.now + timedelta(minutes=10),
            solution_provided_at=self.now + timedelta(minutes=40),
            resolved_at=self.now + timedelta(hours=5), # 5h > 4h BREACH
            first_time_fix=False
        )

        self.assertTrue(incident.ack_within_30m)
        self.assertTrue(incident.solution_within_1h)
        self.assertFalse(incident.resolved_within_4h)
        self.assertFalse(incident.is_rtc_compliant)

    def test_api_permission_anonymous_denied(self):
        response = self.client.get('/api/v1/support/incidents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_permission_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/support/incidents/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_create_incident_with_computed_sla_properties(self):
        self.client.force_authenticate(user=self.support_agent)
        reported = self.now.isoformat()
        ack = (self.now + timedelta(minutes=20)).isoformat()
        sol = (self.now + timedelta(minutes=50)).isoformat()
        res = (self.now + timedelta(hours=3)).isoformat()

        payload = {
            'ticket_ref': 'INC-2000',
            'title': 'Email Relay queue backlog',
            'system_name': 'Mail Gateway',
            'reported_at': reported,
            'acknowledged_at': ack,
            'solution_provided_at': sol,
            'resolved_at': res,
            'first_time_fix': True,
            'csat_score': 92.5,
            'rca_notes': 'Flushed stuck SMTP connection pool',
            'proof_type': 'EMAIL_REF',
            'proof_reference': 'FW: Mail queue cleared by NOC'
        }

        response = self.client.post('/api/v1/support/incidents/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ticket_ref'], 'INC-2000')
        self.assertTrue(response.data['ack_within_30m'])
        self.assertTrue(response.data['solution_within_1h'])
        self.assertTrue(response.data['resolved_within_4h'])
        self.assertTrue(response.data['is_rtc_compliant'])
