from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from inhouse_systems.models import InHouseSystem
from support_desk.models import SupportIncident
from daily_workflow.models import DailyCheckin
from growth_conduct.models import LearningRecord
from common.models import ProofModel


class ScorecardSummaryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.today = timezone.localdate()
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
        self.executive_user = User.objects.create_user(
            username='exec_director',
            password='password123',
            email='exec@example.com'
        )
        exec_group, _ = Group.objects.get_or_create(name='Executive')
        self.executive_user.groups.add(exec_group)

    def test_empty_database_scorecard_baseline(self):
        self.client.force_authenticate(user=self.executive_user)
        response = self.client.get('/api/v1/scorecard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['finance']['inhouse_savings_usd']['current'], 0.0)
        self.assertEqual(data['finance']['systems_replaced']['current'], 0)
        self.assertEqual(data['customer']['rtc_compliance_pct']['current'], 100.0)
        self.assertEqual(data['customer']['first_time_fix_pct']['current'], 100.0)
        self.assertEqual(data['customer']['csat_score']['current'], 0.0)
        self.assertEqual(data['process']['scrum_attendance_pct']['current'], 100.0)
        self.assertEqual(data['process']['git_jira_compliance_pct']['current'], 100.0)
        self.assertEqual(data['learning']['course_pass_rate_pct']['current'], 100.0)

    def test_populated_scorecard_aggregation(self):
        self.client.force_authenticate(user=self.executive_user)

        # 1. Finance: 2 live systems with $32,000 total savings (meets >= $30k target)
        InHouseSystem.objects.create(
            system_name='Tool A',
            replaced_vendor_tool='Vendor A',
            annual_cost_saved_usd=20000.00,
            status=InHouseSystem.DevelopmentStatus.LIVE,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='Audit note'
        )
        InHouseSystem.objects.create(
            system_name='Tool B',
            replaced_vendor_tool='Vendor B',
            annual_cost_saved_usd=12000.00,
            status=InHouseSystem.DevelopmentStatus.LIVE,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='Audit note'
        )
        InHouseSystem.objects.create(
            system_name='Tool C (In Dev)',
            replaced_vendor_tool='Vendor C',
            annual_cost_saved_usd=15000.00,
            status=InHouseSystem.DevelopmentStatus.IN_DEV,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='WIP note'
        )

        # 2. Customer: 2 incidents: 1 compliant, 1 non-compliant; both first-time fixes; csat 94 and 90 -> avg 92.0
        SupportIncident.objects.create(
            ticket_ref='INC-A',
            title='Issue A',
            system_name='Sys A',
            reported_at=self.now,
            acknowledged_at=self.now + timedelta(minutes=10),
            solution_provided_at=self.now + timedelta(minutes=40),
            resolved_at=self.now + timedelta(hours=2),
            first_time_fix=True,
            csat_score=94.0,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='Resolved note'
        )
        SupportIncident.objects.create(
            ticket_ref='INC-B',
            title='Issue B',
            system_name='Sys B',
            reported_at=self.now,
            acknowledged_at=self.now + timedelta(minutes=45), # Breach
            solution_provided_at=self.now + timedelta(minutes=50),
            resolved_at=self.now + timedelta(hours=1),
            first_time_fix=True,
            csat_score=90.0,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='Resolved note'
        )

        # 3. Process: 2 checkins: 2 scrum attended, 1 git/jira pass
        DailyCheckin.objects.create(
            date=self.today,
            scrum_attended=True,
            jira_updated=True,
            jira_tickets_worked='T-1',
            github_pushed=True,
            daily_notes='Notes 1'
        )
        DailyCheckin.objects.create(
            date=self.today - timedelta(days=1),
            scrum_attended=True,
            jira_updated=False, # Did not update Jira
            jira_tickets_worked='None',
            github_pushed=True,
            daily_notes='Notes 2'
        )

        # 4. Learning: 2 assigned courses: 1 scored 85 (pass >= 70), 1 scored 60 (fail) -> 50.0% pass rate
        LearningRecord.objects.create(
            title='Course 1',
            record_type=LearningRecord.RecordType.ASSIGNED_COURSE,
            score_pct=85.0,
            completed_date=self.today,
            submitted_to_hr_date=self.today,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='Note'
        )
        LearningRecord.objects.create(
            title='Course 2',
            record_type=LearningRecord.RecordType.ASSIGNED_COURSE,
            score_pct=60.0,
            completed_date=self.today,
            submitted_to_hr_date=self.today,
            proof_type=ProofModel.ProofType.NOTE,
            proof_reference='Note'
        )

        response = self.client.get('/api/v1/scorecard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Check Finance
        self.assertEqual(data['finance']['inhouse_savings_usd']['current'], 32000.0)
        self.assertTrue(data['finance']['inhouse_savings_usd']['status']) # >= 30,000 target met
        self.assertEqual(data['finance']['systems_replaced']['current'], 2)

        # Check Customer
        self.assertEqual(data['customer']['rtc_compliance_pct']['current'], 50.0) # 1 of 2
        self.assertEqual(data['customer']['first_time_fix_pct']['current'], 100.0) # 2 of 2
        self.assertEqual(data['customer']['csat_score']['current'], 92.0)

        # Check Process
        self.assertEqual(data['process']['scrum_attendance_pct']['current'], 100.0)
        self.assertEqual(data['process']['git_jira_compliance_pct']['current'], 50.0)

        # Check Learning
        self.assertEqual(data['learning']['course_pass_rate_pct']['current'], 50.0)

    def test_permission_enforcement(self):
        # Anonymous
        res_anon = self.client.get('/api/v1/scorecard/summary/')
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Regular user without executive role
        self.client.force_authenticate(user=self.regular_user)
        res_reg = self.client.get('/api/v1/scorecard/summary/')
        self.assertEqual(res_reg.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser
        self.client.force_authenticate(user=self.superuser)
        res_admin = self.client.get('/api/v1/scorecard/summary/')
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
