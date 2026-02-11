from django.db import models
from django.contrib.auth.models import User


DEPARTMENTS = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons'),
]


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='Cardiologist')
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} — {self.department}"

    class Meta:
        ordering = ['-id']


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20)
    symptoms = models.CharField(max_length=100)
    assignedDoctorId = models.PositiveIntegerField(null=True)
    admitDate = models.DateField(auto_now=True)
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} ({self.symptoms})"

    class Meta:
        ordering = ['-id']


class Appointment(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    doctorId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40, null=True)
    doctorName = models.CharField(max_length=40, null=True)
    appointmentDate = models.DateField(auto_now=True)
    description = models.TextField(max_length=500)
    status = models.BooleanField(default=False)
    consultationDate = models.DateField(null=True, blank=True)
    consultationTime = models.TimeField(null=True, blank=True)
    consultationNotes = models.TextField(max_length=1000, null=True, blank=True)

    @property
    def has_consultation(self):
        return self.consultationDate is not None

    def __str__(self):
        return f"{self.patientName} - {self.doctorName}"

    class Meta:
        ordering = ['-appointmentDate']


class PatientDischargeDetails(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40)
    assignedDoctorName = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    symptoms = models.CharField(max_length=100, null=True)
    admitDate = models.DateField()
    releaseDate = models.DateField()
    daySpent = models.PositiveIntegerField()
    roomCharge = models.PositiveIntegerField()
    medicineCost = models.PositiveIntegerField()
    doctorFee = models.PositiveIntegerField()
    OtherCharge = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    canReapply = models.BooleanField(default=True)
    followUpNotes = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.patientName} (Discharged)"

    class Meta:
        verbose_name_plural = 'Patient Discharge Details'
        ordering = ['-releaseDate']

