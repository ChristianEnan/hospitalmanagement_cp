from django.contrib import admin
from .models import Doctor, Patient, Appointment, PatientDischargeDetails


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'department', 'mobile', 'status')
    list_filter = ('status', 'department')
    search_fields = ('user__first_name', 'user__last_name', 'mobile')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'symptoms', 'mobile', 'status')
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name', 'symptoms')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patientName', 'doctorName', 'appointmentDate', 'status')
    list_filter = ('status', 'appointmentDate')
    search_fields = ('patientName', 'doctorName')


@admin.register(PatientDischargeDetails)
class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    list_display = ('patientName', 'assignedDoctorName', 'admitDate', 'releaseDate', 'total')
    search_fields = ('patientName', 'assignedDoctorName')
