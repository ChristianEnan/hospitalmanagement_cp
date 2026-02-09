from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from hospital.models import Doctor, Patient, Appointment
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate the database with sample admin, doctor, and patient records'

    def handle(self, *args, **options):
        # Create groups if they don't exist
        admin_group, _ = Group.objects.get_or_create(name='ADMIN')
        doctor_group, _ = Group.objects.get_or_create(name='DOCTOR')
        patient_group, _ = Group.objects.get_or_create(name='PATIENT')

        # Create Admin User
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                first_name='Admin',
                last_name='User',
                email='admin@hospital.com'
            )
            admin_user.groups.add(admin_group)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create Doctor Users and Profiles
        doctors_data = [
            {'username': 'doc_smith', 'first_name': 'John', 'last_name': 'Smith', 'dept': 'Cardiologist', 'mobile': '9876543210', 'address': '123 Medical St'},
            {'username': 'doc_johnson', 'first_name': 'Sarah', 'last_name': 'Johnson', 'dept': 'Dermatologists', 'mobile': '9876543211', 'address': '456 Health Ave'},
            {'username': 'doc_williams', 'first_name': 'Robert', 'last_name': 'Williams', 'dept': 'Emergency Medicine Specialists', 'mobile': '9876543212', 'address': '789 Hospital Rd'},
            {'username': 'doc_brown', 'first_name': 'Emily', 'last_name': 'Brown', 'dept': 'Allergists/Immunologists', 'mobile': '9876543213', 'address': '321 Clinic Ln'},
            {'username': 'doc_miller', 'first_name': 'Michael', 'last_name': 'Miller', 'dept': 'Anesthesiologists', 'mobile': '9876543214', 'address': '654 Medical Dr'},
        ]

        for doc_data in doctors_data:
            if not User.objects.filter(username=doc_data['username']).exists():
                doc_user = User.objects.create_user(
                    username=doc_data['username'],
                    password='doctor123',
                    first_name=doc_data['first_name'],
                    last_name=doc_data['last_name'],
                    email=f"{doc_data['username']}@hospital.com"
                )
                doc_user.groups.add(doctor_group)
                doc_user.save()
                
                Doctor.objects.create(
                    user=doc_user,
                    address=doc_data['address'],
                    mobile=doc_data['mobile'],
                    department=doc_data['dept'],
                    status=True
                )
                self.stdout.write(self.style.SUCCESS(f"Created doctor: {doc_data['first_name']} {doc_data['last_name']}"))

        # Create Patient Users and Profiles
        patients_data = [
            {'username': 'patient_alex', 'first_name': 'Alex', 'last_name': 'Thompson', 'symptoms': 'Chest pain, shortness of breath', 'mobile': '9876543220', 'address': '111 Main Street'},
            {'username': 'patient_mary', 'first_name': 'Mary', 'last_name': 'Davis', 'symptoms': 'Skin rash, itching', 'mobile': '9876543221', 'address': '222 Oak Avenue'},
            {'username': 'patient_james', 'first_name': 'James', 'last_name': 'Wilson', 'symptoms': 'Fever, cough', 'mobile': '9876543222', 'address': '333 Elm Street'},
            {'username': 'patient_lisa', 'first_name': 'Lisa', 'last_name': 'Anderson', 'symptoms': 'Allergic reaction', 'mobile': '9876543223', 'address': '444 Pine Road'},
            {'username': 'patient_david', 'first_name': 'David', 'last_name': 'Martinez', 'symptoms': 'Post-operative pain', 'mobile': '9876543224', 'address': '555 Birch Lane'},
        ]

        for pat_data in patients_data:
            if not User.objects.filter(username=pat_data['username']).exists():
                pat_user = User.objects.create_user(
                    username=pat_data['username'],
                    password='patient123',
                    first_name=pat_data['first_name'],
                    last_name=pat_data['last_name'],
                    email=f"{pat_data['username']}@hospital.com"
                )
                pat_user.groups.add(patient_group)
                pat_user.save()
                
                # Assign to a random doctor
                doctor_user = User.objects.filter(groups__name='DOCTOR').first()
                
                Patient.objects.create(
                    user=pat_user,
                    address=pat_data['address'],
                    mobile=pat_data['mobile'],
                    symptoms=pat_data['symptoms'],
                    assignedDoctorId=doctor_user.id if doctor_user else None,
                    status=True
                )
                self.stdout.write(self.style.SUCCESS(f"Created patient: {pat_data['first_name']} {pat_data['last_name']}"))

        # Create Sample Appointments
        doctors = Doctor.objects.all()
        patients = Patient.objects.all()
        
        if doctors.exists() and patients.exists():
            for i, patient in enumerate(patients[:3]):
                doctor = doctors[i % len(doctors)]
                if not Appointment.objects.filter(patientId=patient.user.id, doctorId=doctor.user.id).exists():
                    Appointment.objects.create(
                        patientId=patient.user.id,
                        doctorId=doctor.user.id,
                        patientName=patient.get_name,
                        doctorName=doctor.get_name,
                        description=f"Follow-up appointment for {patient.symptoms}",
                        status=True
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created appointment for {patient.get_name} with {doctor.get_name}"))

        self.stdout.write(self.style.SUCCESS('\nDatabase successfully populated with sample data!'))
        self.stdout.write(self.style.WARNING('\nDefault login credentials:'))
        self.stdout.write('Admin - username: admin, password: admin123')
        self.stdout.write('Doctors - username: doc_smith (etc), password: doctor123')
        self.stdout.write('Patients - username: patient_alex (etc), password: patient123')
