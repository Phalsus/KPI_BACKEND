from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from .models import LearningRecord, BehavioralReviewRecord
from common.models import ProofModel


class GrowthConductTests(TestCase):
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
        self.hr_user = User.objects.create_user(
            username='hr_admin',
            password='password123',
            email='hr@example.com'
        )
        for perm_name in [
            'view_learningrecord', 'add_learningrecord', 'change_learningrecord',
            'view_behavioralreviewrecord', 'add_behavioralreviewrecord'
        ]:
            perm = Permission.objects.get(codename=perm_name)
            self.hr_user.user_permissions.add(perm)

    def test_learning_record_submitted_within_24h(self):
        # Submitted same day
        record_same_day = LearningRecord.objects.create(
            title='AWS Certified Solutions Architect',
            record_type=LearningRecord.RecordType.CERTIFICATION,
            score_pct=88.00,
            completed_date=self.today,
            submitted_to_hr_date=self.today,
            proof_type=ProofModel.ProofType.CLOUD_LINK,
            proof_reference='https://drive.company.com/certs/aws-cert.pdf'
        )
        self.assertTrue(record_same_day.submitted_within_24h)

        # Submitted next day (within 24h / 1 day)
        record_next_day = LearningRecord.objects.create(
            title='Security Awareness Training',
            record_type=LearningRecord.RecordType.ASSIGNED_COURSE,
            score_pct=95.00,
            completed_date=self.today - timedelta(days=1),
            submitted_to_hr_date=self.today,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='LMS completion badge verified'
        )
        self.assertTrue(record_next_day.submitted_within_24h)

        # Submitted late (3 days later)
        record_late = LearningRecord.objects.create(
            title='Kubernetes Administration',
            record_type=LearningRecord.RecordType.ASSIGNED_COURSE,
            score_pct=82.00,
            completed_date=self.today - timedelta(days=4),
            submitted_to_hr_date=self.today - timedelta(days=1),
            proof_type=ProofModel.ProofType.CLOUD_LINK,
            proof_reference='https://drive.company.com/certs/k8s.pdf'
        )
        self.assertFalse(record_late.submitted_within_24h)

    def test_behavioral_review_record(self):
        review = BehavioralReviewRecord.objects.create(
            review_period='H1 2026',
            peer_review_score=4.6,
            zero_escalations_maintained=True,
            attendance_adherence_pct=98.50,
            supervisor_feedback='Exemplary cross-functional leadership and zero team conflicts.',
            proof_type=ProofModel.ProofType.DOC_URL,
            proof_reference='https://hris.company.com/reviews/H1-2026/signed-review.pdf'
        )
        self.assertEqual(review.peer_review_score, 4.6)
        self.assertTrue(review.zero_escalations_maintained)

    def test_api_permission_denials(self):
        # Anonymous
        res_anon = self.client.get('/api/v1/growth/learning/')
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Regular user without permission
        self.client.force_authenticate(user=self.regular_user)
        res_reg = self.client.get('/api/v1/growth/learning/')
        self.assertEqual(res_reg.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_create_learning_record(self):
        self.client.force_authenticate(user=self.hr_user)
        payload = {
            'title': 'Certified Information Systems Auditor (CISA)',
            'record_type': 'CERTIFICATION',
            'score_pct': 91.00,
            'completed_date': self.today.isoformat(),
            'submitted_to_hr_date': self.today.isoformat(),
            'proof_type': 'CLOUD_LINK',
            'proof_reference': 'https://drive.company.com/cisa-verified.pdf',
            'proof_description': 'HR validated official ISACA certificate'
        }

        response = self.client.post('/api/v1/growth/learning/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Certified Information Systems Auditor (CISA)')
        self.assertTrue(response.data['submitted_within_24h'])
