from django.contrib.auth.models import User, Group
from hospital.models import Patient

username = 'smit27'
user = User.objects.filter(username=username).first()

if user:
    print(f"Fixing user '{username}'...")
    
    # Remove from ADMIN group
    admin_group = Group.objects.filter(name='ADMIN').first()
    if admin_group and user.groups.filter(name='ADMIN').exists():
        user.groups.remove(admin_group)
        print("  ✓ Removed from ADMIN group")
    
    # Add to PATIENT group
    patient_group = Group.objects.get_or_create(name='PATIENT')[0]
    user.groups.add(patient_group)
    print("  ✓ Added to PATIENT group")
    
    # Check if Patient profile exists
    patient = Patient.objects.filter(user=user).first()
    if not patient:
        # Create Patient profile
        patient = Patient.objects.create(
            user=user,
            address='Address not provided',
            mobile='0000000000',
            symptoms='',
            assignedDoctorId=None,
            admitDate=None,
            status=True  # Auto-approve
        )
        print("  ✓ Created Patient profile")
        print("  ✓ Status set to Approved")
    else:
        print("  ✗ Patient profile already exists")
    
    print(f"\n✓ User '{username}' can now log in as a Patient!")
    print(f"  Username: {username}")
    print(f"  They should use their existing password")
else:
    print(f"✗ User '{username}' not found")
