#!/usr/bin/env python
"""
Script to create a test user for the Differential Privacy Dashboard
Run this with: python create_user.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin user
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

# Check if user already exists
if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists!")
    user = User.objects.get(username=username)
    # Update password
    user.set_password(password)
    user.save()
    print(f"Password updated for '{username}'")
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='admin',
        is_staff=True,
        is_superuser=True
    )
    print(f"User '{username}' created successfully!")

print("\n" + "="*60)
print("LOGIN CREDENTIALS:")
print("="*60)
print(f"Username: {username}")
print(f"Password: {password}")
print("="*60)
print("\nYou can now log in to the dashboard!")
