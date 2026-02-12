from django.contrib.auth.models import User
from hospital.models import Patient

username = 'smit27'
user = User.objects.filter(username=username).first()

if user:
    print(f"✓ User '{username}' exists")
    print(f"  - ID: {user.id}")
    print(f"  - Email: {user.email}")
    print(f"  - Groups: {[g.name for g in user.groups.all()]}")
    
    patient = Patient.objects.filter(user=user).first()
    if patient:
        print(f"✓ Patient profile exists")
        print(f"  - Status: {'Approved' if patient.status else 'Pending Approval'}")
        print(f"  - Mobile: {patient.mobile}")
        print(f"  - Assigned Doctor ID: {patient.assignedDoctorId}")
    else:
        print(f"✗ No Patient profile found for user '{username}'")
else:
    print(f"✗ User '{username}' does NOT exist in database")
    print("\nSuggestion: User needs to sign up first")
