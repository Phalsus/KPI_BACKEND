#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files for WhiteNoise
python manage.py collectstatic --no-input

# Run database migrations on Neon PostgreSQL
python manage.py migrate

# Initialize or update functional role groups and permissions
python manage.py setup_roles

# Create default admin from environment if no user exists
python manage.py create_default_admin
