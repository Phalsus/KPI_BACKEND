from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Initializes default user groups and assigns model-level permissions for the KPI Tracking Portal."

    def handle(self, *args, **options):
        # 1. Define Role Groups and model assignments
        role_definitions = {
            'Support Desk Agent': {
                'support_desk': ['supportincident'],
            },
            'Asset Manager': {
                'asset_license': [
                    'hardwareasset',
                    'softwarelicense',
                    'assetuser',
                    'assetbrand',
                    'assetmodel',
                    'assetassignmenthistory',
                ],
            },
            'Developer / Engineer': {
                'daily_workflow': ['dailycheckin'],
                'custom_logs': ['customworklog'],
                'inhouse_systems': ['inhousesystem'],
            },
            'HR / People Ops': {
                'growth_conduct': ['learningrecord', 'behavioralreviewrecord'],
                'custom_logs': ['kpimaster'],
            },
            'Executive / Leadership': {
                # Read-only across all domain models
                'all_view_only': True
            }
        }

        all_models = [
            ('custom_logs', 'kpimaster'),
            ('custom_logs', 'customworklog'),
            ('support_desk', 'supportincident'),
            ('daily_workflow', 'dailycheckin'),
            ('asset_license', 'hardwareasset'),
            ('asset_license', 'softwarelicense'),
            ('asset_license', 'assetuser'),
            ('asset_license', 'assetbrand'),
            ('asset_license', 'assetmodel'),
            ('asset_license', 'assetassignmenthistory'),
            ('inhouse_systems', 'inhousesystem'),
            ('growth_conduct', 'learningrecord'),
            ('growth_conduct', 'behavioralreviewrecord'),
        ]

        for group_name, config in role_definitions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            action_label = "Created" if created else "Updated"
            group.permissions.clear()

            if config.get('all_view_only'):
                # Assign 'view' permission for all domain models
                for app_label, model_name in all_models:
                    perms = Permission.objects.filter(
                        content_type__app_label=app_label,
                        codename=f'view_{model_name}'
                    )
                    group.permissions.add(*perms)
            else:
                for app_label, models in config.items():
                    for model_name in models:
                        # Assign view, add, change permissions
                        perms = Permission.objects.filter(
                            content_type__app_label=app_label,
                            codename__in=[
                                f'view_{model_name}',
                                f'add_{model_name}',
                                f'change_{model_name}',
                            ]
                        )
                        group.permissions.add(*perms)

            self.stdout.write(self.style.SUCCESS(
                f"{action_label} group '{group_name}' with {group.permissions.count()} permissions."
            ))

        self.stdout.write(self.style.SUCCESS("All role groups initialized successfully."))
