"""
Script to show database users and their hashed password
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospitalmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from hospital.models import Doctor, Patient

print("\n" + "="*100)
print("HOSPITAL MANAGEMENT SYSTEM - DATABASE USERS")
print("="*100 + "\n")

# All users
users = User.objects.all()
print(f"Total Users in Database: {users.count()}\n")

# Admin users
print("\n" + "-"*100)
print("ADMIN USERS:")
print("-"*100)
admin_users = User.objects.filter(groups__name='ADMIN')
if admin_users.exists():
    for user in admin_users:
        print(f"\nUsername: {user.username}")
        print(f"Full Name: {user.first_name} {user.last_name}")
        print(f"Email: {user.email}")
        print(f"Hashed Password: {user.password}")
        print(f"Is Active: {user.is_active}")
else:
    print("No admin users found")

# Doctor users
print("\n" + "-"*100)
print("DOCTOR USERS:")
print("-"*100)
doctor_users = User.objects.filter(groups__name='DOCTOR')
if doctor_users.exists():
    for user in doctor_users:
        try:
            doctor = Doctor.objects.get(user=user)
            print(f"\nUsername: {user.username}")
            print(f"Full Name: {user.first_name} {user.last_name}")
            print(f"Department: {doctor.department}")
            print(f"Status: {'Approved' if doctor.status else 'Pending'}")
            print(f"Hashed Password: {user.password}")
        except:
            pass
else:
    print("No doctor users found")

# Patient users
print("\n" + "-"*100)
print("PATIENT USERS:")
print("-"*100)
patient_users = User.objects.filter(groups__name='PATIENT')
if patient_users.exists():
    for user in patient_users:
        try:
            patient = Patient.objects.get(user=user)
            print(f"\nUsername: {user.username}")
            print(f"Full Name: {user.first_name} {user.last_name}")
            print(f"Symptoms: {patient.symptoms}")
            print(f"Status: {'Approved' if patient.status else 'Pending'}")
            print(f"Hashed Password: {user.password}")
        except:
            pass
else:
    print("No patient users found")

print("\n" + "="*100)
print("PASSWORD HASH EXPLANATION:")
print("="*100)
print("""
Format: pbkdf2_sha256$iterations$salt$hash

- pbkdf2_sha256: Encryption algorithm name
- iterations: Number of times password is hashed (180000)
- salt: Random string added to password
- hash: Final encrypted password
""")


print("\n" + "="*100 + "\n")
