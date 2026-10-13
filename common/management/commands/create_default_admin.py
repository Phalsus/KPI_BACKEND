import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates an initial superuser from environment variables if no user exists."

    def handle(self, *args, **options):
        username = (
            os.getenv("DJANGO_SUPERUSER_USERNAME") or
            os.getenv("ADMIN_USERNAME") or
            "admin"
        )
        email = (
            os.getenv("DJANGO_SUPERUSER_EMAIL") or
            os.getenv("ADMIN_EMAIL") or
            "admin@example.com"
        )
        password = (
            os.getenv("DJANGO_SUPERUSER_PASSWORD") or
            os.getenv("ADMIN_PASSWORD")
        )

        # Check if any user or superuser already exists
        if User.objects.exists():
            self.stdout.write(
                self.style.SUCCESS(f"User(s) already exist ({User.objects.count()} total). Skipping initial user creation.")
            )
            return

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "No user password found in environment (set DJANGO_SUPERUSER_PASSWORD or ADMIN_PASSWORD). "
                    "Skipping initial user creation."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(
            self.style.SUCCESS(f"Initial superuser '{username}' ({email}) created successfully from environment.")
        )
