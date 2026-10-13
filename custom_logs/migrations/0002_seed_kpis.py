from django.db import migrations


def seed_kpis(apps, schema_editor):
    KPIMaster = apps.get_model('custom_logs', 'KPIMaster')
    records = [
        # Finance (25%)
        {
            "code": "FIN_REV_TARGET",
            "perspective": "FINANCE",
            "name": "Annual Revenue Target Achievement",
            "weight": 5.0,
            "smart_target": "Support group to achieve >= 100% of NGN 15b target via >= 95% system uptime."
        },
        {
            "code": "FIN_COST_SAVINGS",
            "perspective": "FINANCE",
            "name": "Cost Savings via In-House Development",
            "weight": 5.0,
            "smart_target": "Achieve >= $30,000 annual savings by replacing >= 3 third-party systems."
        },
        {
            "code": "FIN_LICENSE_OPT",
            "perspective": "FINANCE",
            "name": "Software License Cost Optimization",
            "weight": 8.0,
            "smart_target": "Reduce license costs by >= 15% annually; 100% timely renewals."
        },
        {
            "code": "FIN_ASSET_CONTROL",
            "perspective": "FINANCE",
            "name": "IT Asset Cost Control",
            "weight": 7.0,
            "smart_target": "Maintain >= 98% accuracy of IT asset register and reduce unused assets by 15%."
        },

        # Customer (30%)
        {
            "code": "CUST_UPTIME",
            "perspective": "CUSTOMER",
            "name": "System Uptime",
            "weight": 8.0,
            "smart_target": "Maintain >= 99% uptime across all company systems monthly."
        },
        {
            "code": "CUST_RTC_COMPLIANCE",
            "perspective": "CUSTOMER",
            "name": "Resolution - Time Compliance (RTC)",
            "weight": 5.0,
            "smart_target": "Meet >= 95% RTC compliance (30m ack, 1h solution, 4h resolution)."
        },
        {
            "code": "CUST_SATISFACTION",
            "perspective": "CUSTOMER",
            "name": "Internal User Satisfaction (CSAT)",
            "weight": 7.0,
            "smart_target": "Achieve >= 90% satisfaction score from internal users quarterly."
        },
        {
            "code": "CUST_FIRST_TIME_FIX",
            "perspective": "CUSTOMER",
            "name": "First-Time Fix Rate",
            "weight": 5.0,
            "smart_target": "Achieve >= 90% first-time resolution rate; document RCA."
        },
        {
            "code": "CUST_SYS_EFFICIENCY",
            "perspective": "CUSTOMER",
            "name": "System Performance & External Sale Ability",
            "weight": 5.0,
            "smart_target": "Ensure >= 95% efficiency across systems; package solutions for external sale."
        },

        # Process (16%)
        {
            "code": "PROC_ERP_ADOPTION",
            "perspective": "PROCESS",
            "name": "ERP Adoption (Odoo)",
            "weight": 3.0,
            "smart_target": "Achieve 100% ERP adoption and usage across organization; train users weekly."
        },
        {
            "code": "PROC_OP_EFFICIENCY",
            "perspective": "PROCESS",
            "name": "Operational Efficiency",
            "weight": 5.0,
            "smart_target": "Achieve >= 90% on-time delivery; escalate delays at least 5 business days early."
        },
        {
            "code": "PROC_INNOVATION",
            "perspective": "PROCESS",
            "name": "Innovation Pipeline Contribution",
            "weight": 3.0,
            "smart_target": "Contribute >= 2 innovation/system improvement ideas annually."
        },
        {
            "code": "PROC_CYBERSECURITY",
            "perspective": "PROCESS",
            "name": "Cybersecurity Compliance",
            "weight": 3.0,
            "smart_target": "Conduct quarterly tests and provide monthly reports with 100% issue tracking."
        },
        {
            "code": "PROC_GIT_JIRA",
            "perspective": "PROCESS",
            "name": "GitHub & Jira Compliance",
            "weight": 3.0,
            "smart_target": "Ensure 100% code updates, Jira updates, and documentation daily."
        },
        {
            "code": "PROC_DAILY_SCRUM",
            "perspective": "PROCESS",
            "name": "Daily Scrum Participation",
            "weight": 4.0,
            "smart_target": "Attend 100% of daily scrum meetings by 9:00 AM and escalate blockers."
        },

        # Learning & Growth (15%)
        {
            "code": "LRN_CERTIFICATION",
            "perspective": "LEARNING",
            "name": "Professional Certification Rate",
            "weight": 2.0,
            "smart_target": "Obtain required certifications to perform job functions."
        },
        {
            "code": "LRN_ASSIGNED_COURSES",
            "perspective": "LEARNING",
            "name": "Complete Assigned Courses",
            "weight": 13.0,
            "smart_target": "Complete >= 90% of assigned trainings with score >= 70%; report within 24 hours."
        },

        # Behavioral (10%)
        {
            "code": "BEH_EXCELLENCE",
            "perspective": "BEHAVIORAL",
            "name": "Excellence",
            "weight": 2.0,
            "smart_target": "Deliver >= 95% first-time error-free tasks and 100% on-time delivery."
        },
        {
            "code": "BEH_COLLABORATION",
            "perspective": "BEHAVIORAL",
            "name": "Collaboration",
            "weight": 2.0,
            "smart_target": "Score >= 4.0/5.0 on bi-annual 360 assessments with zero team escalations."
        },
        {
            "code": "BEH_ATTENDANCE",
            "perspective": "BEHAVIORAL",
            "name": "Punctuality and Attendance",
            "weight": 2.0,
            "smart_target": "Maintain >= 90% adherence to schedule; 100% clock-in compliance via HRIS."
        },
        {
            "code": "BEH_INTEGRITY",
            "perspective": "BEHAVIORAL",
            "name": "Integrity",
            "weight": 2.0,
            "smart_target": "Demonstrate ethical conduct; 100% policy compliance with zero infractions."
        }
    ]
    for r in records:
        KPIMaster.objects.update_or_create(code=r['code'], defaults=r)


class Migration(migrations.Migration):
    dependencies = [
        ('custom_logs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_kpis),
    ]
