from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from support_desk.models import SupportIncident
from daily_workflow.models import DailyCheckin
from inhouse_systems.models import InHouseSystem
from growth_conduct.models import LearningRecord
from common.permissions import ScorecardSummaryPermission


class ScorecardSummaryView(APIView):
    """
    Executive scorecard rollup view computing real-time organizational KPIs
    against targets across Finance, Customer, Process, and Learning & Growth.
    Protected by ScorecardSummaryPermission.
    """
    permission_classes = [ScorecardSummaryPermission]

    def get(self, request):
        # 1. Finance: In-House Tool Savings ($30,000 / 3 systems target)
        inhouse = InHouseSystem.objects.filter(status='LIVE').aggregate(
            total_savings=Sum('annual_cost_saved_usd'),
            system_count=Count('id')
        )
        total_savings = float(inhouse['total_savings'] or 0.0)
        system_count = inhouse['system_count'] or 0

        # 2. Customer: RTC Compliance (>=95%), First-Time Fix (>=90%), CSAT (>=90%)
        incidents = SupportIncident.objects.all()
        inc_count = incidents.count()
        rtc_passed = sum(1 for i in incidents if i.is_rtc_compliant)
        first_fixes = incidents.filter(first_time_fix=True).count()
        csat_avg = incidents.aggregate(avg=Avg('csat_score'))['avg'] or 0.0

        # 3. Process: Daily Scrum Attendance (100%), Git & Jira Updates (100%)
        checkins = DailyCheckin.objects.all()
        total_days = checkins.count()
        scrum_ontime = checkins.filter(scrum_attended=True).count()
        git_jira_pass = checkins.filter(jira_updated=True, github_pushed=True).count()

        # 4. Learning & Growth: Assigned Course Pass Rate (>=70% mark, >=90% target)
        courses = LearningRecord.objects.filter(record_type='ASSIGNED_COURSE')
        courses_count = courses.count()
        courses_passed = courses.filter(score_pct__gte=70.0).count()

        return Response({
            "finance": {
                "inhouse_savings_usd": {
                    "current": total_savings,
                    "target": 30000.0,
                    "status": total_savings >= 30000.0
                },
                "systems_replaced": {
                    "current": system_count,
                    "target": 3,
                    "status": system_count >= 3
                }
            },
            "customer": {
                "rtc_compliance_pct": {
                    "current": round((rtc_passed / inc_count * 100), 1) if inc_count else 100.0,
                    "target": 95.0,
                    "status": (round((rtc_passed / inc_count * 100), 1) if inc_count else 100.0) >= 95.0
                },
                "first_time_fix_pct": {
                    "current": round((first_fixes / inc_count * 100), 1) if inc_count else 100.0,
                    "target": 90.0,
                    "status": (round((first_fixes / inc_count * 100), 1) if inc_count else 100.0) >= 90.0
                },
                "csat_score": {
                    "current": round(float(csat_avg), 1),
                    "target": 90.0,
                    "status": round(float(csat_avg), 1) >= 90.0
                }
            },
            "process": {
                "scrum_attendance_pct": {
                    "current": round((scrum_ontime / total_days * 100), 1) if total_days else 100.0,
                    "target": 100.0,
                    "status": (round((scrum_ontime / total_days * 100), 1) if total_days else 100.0) >= 100.0
                },
                "git_jira_compliance_pct": {
                    "current": round((git_jira_pass / total_days * 100), 1) if total_days else 100.0,
                    "target": 100.0,
                    "status": (round((git_jira_pass / total_days * 100), 1) if total_days else 100.0) >= 100.0
                }
            },
            "learning": {
                "course_pass_rate_pct": {
                    "current": round((courses_passed / courses_count * 100), 1) if courses_count else 100.0,
                    "target": 90.0,
                    "status": (round((courses_passed / courses_count * 100), 1) if courses_count else 100.0) >= 90.0
                }
            }
        })
