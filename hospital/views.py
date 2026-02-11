from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from datetime import date
from django.conf import settings
from django.db.models import Q
import io
from xhtml2pdf import pisa
from django.template.loader import get_template


# ──────────────────────────────────────────────────────────────
# ROLE CHECK HELPERS
# ──────────────────────────────────────────────────────────────
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


# ──────────────────────────────────────────────────────────────
# PUBLIC VIEWS
# ──────────────────────────────────────────────────────────────
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/index.html')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/admin/click.html')


def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/doctor/click.html')


def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/patient/click.html')


# ──────────────────────────────────────────────────────────────
# SIGNUP VIEWS
# ──────────────────────────────────────────────────────────────
def admin_signup_view(request):
    form = forms.AdminSigupForm()
    if request.method == 'POST':
        form = forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            messages.success(request, 'Registration successful! Please login to continue.')
            return HttpResponseRedirect('adminlogin')
    return render(request, 'hospital/admin/signup.html', {'form': form})


def doctor_signup_view(request):
    userForm = forms.DoctorUserForm()
    doctorForm = forms.DoctorForm()
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST)
        doctorForm = forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            doctor = doctorForm.save(commit=False)
            doctor.user = user
            doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
            messages.success(request, 'Registration successful! Your account is pending admin approval. Please login to continue.')
            return HttpResponseRedirect('doctorlogin')
        else:
            mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    return render(request, 'hospital/doctor/signup.html', context=mydict)


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    doctors = models.Doctor.objects.filter(status=True)
    mydict = {'userForm': userForm, 'patientForm': patientForm, 'doctors': doctors}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
            messages.success(request, 'Registration successful! Your account is pending admin approval. Please login to continue.')
            return HttpResponseRedirect('patientlogin')
        else:
            mydict = {'userForm': userForm, 'patientForm': patientForm, 'doctors': doctors}
    return render(request, 'hospital/patient/signup.html', context=mydict)


# ──────────────────────────────────────────────────────────────
# ROLE-SPECIFIC LOGIN VIEWS
# ──────────────────────────────────────────────────────────────
def admin_login_view(request):
    form = AuthenticationForm()
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if is_admin(user):
                auth_login(request, user)
                return redirect('admin-dashboard')
            else:
                error_message = 'This account is not registered as an Administrator. Please use the correct login portal.'
                form = AuthenticationForm()
    return render(request, 'hospital/admin/login.html', {'form': form, 'error_message': error_message})


def doctor_login_view(request):
    form = AuthenticationForm()
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if is_doctor(user):
                auth_login(request, user)
                return redirect('afterlogin')
            else:
                error_message = 'This account is not registered as a Doctor. Please use the correct login portal.'
                form = AuthenticationForm()
    return render(request, 'hospital/doctor/login.html', {'form': form, 'error_message': error_message})


def patient_login_view(request):
    form = AuthenticationForm()
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if is_patient(user):
                auth_login(request, user)
                return redirect('afterlogin')
            else:
                error_message = 'This account is not registered as a Patient. Please use the correct login portal.'
                form = AuthenticationForm()
    return render(request, 'hospital/patient/login.html', {'form': form, 'error_message': error_message})


# ──────────────────────────────────────────────────────────────
# AFTER LOGIN REDIRECT
# ──────────────────────────────────────────────────────────────
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval = models.Doctor.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor/wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval = models.Patient.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request, 'hospital/patient/wait_for_approval.html')


# ══════════════════════════════════════════════════════════════
# ADMIN VIEWS
# ══════════════════════════════════════════════════════════════
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    doctors = models.Doctor.objects.all().order_by('-id')
    patients = models.Patient.objects.all().order_by('-id')
    doctorcount = models.Doctor.objects.filter(status=True).count()
    pendingdoctorcount = models.Doctor.objects.filter(status=False).count()
    patientcount = models.Patient.objects.filter(status=True).count()
    pendingpatientcount = models.Patient.objects.filter(status=False).count()
    appointmentcount = models.Appointment.objects.filter(status=True).count()
    pendingappointmentcount = models.Appointment.objects.filter(status=False).count()
    mydict = {
        'doctors': doctors,
        'patients': patients,
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'pendingpatientcount': pendingpatientcount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
    }
    return render(request, 'hospital/admin/dashboard.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request, 'hospital/admin/doctor.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors = models.Doctor.objects.filter(status=True)
    return render(request, 'hospital/admin/view_doctor.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    userForm = forms.DoctorUpdateUserForm(instance=user)
    doctorForm = forms.DoctorForm(instance=doctor)
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUpdateUserForm(request.POST, instance=user)
        doctorForm = forms.DoctorForm(request.POST, request.FILES, instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save(commit=False)
            password = userForm.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            doctor = doctorForm.save(commit=False)
            doctor.status = True
            doctor.save()
            messages.success(request, f'Doctor {user.first_name} {user.last_name} details updated successfully!')
            return redirect('admin-view-doctor')
    return render(request, 'hospital/admin/update_doctor.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm = forms.DoctorUserForm()
    doctorForm = forms.DoctorForm()
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST)
        doctorForm = forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            doctor = doctorForm.save(commit=False)
            doctor.user = user
            doctor.status = True
            doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('admin-view-doctor')
    return render(request, 'hospital/admin/add_doctor.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    doctors = models.Doctor.objects.filter(status=False)
    return render(request, 'hospital/admin/approve_doctor.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    doctor.status = True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors = models.Doctor.objects.filter(status=True)
    return render(request, 'hospital/admin/view_doctor_specialisation.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request, 'hospital/admin/patient.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients = models.Patient.objects.filter(status=True)
    return render(request, 'hospital/admin/view_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)
    userForm = forms.PatientUpdateUserForm(instance=user)
    patientForm = forms.PatientForm(instance=patient)
    doctors = models.Doctor.objects.filter(status=True)
    currentDoctor = None
    if patient.assignedDoctorId:
        try:
            currentDoctor = models.Doctor.objects.get(user_id=patient.assignedDoctorId)
        except models.Doctor.DoesNotExist:
            currentDoctor = None
    mydict = {'userForm': userForm, 'patientForm': patientForm, 'patient': patient, 'doctors': doctors, 'currentDoctor': currentDoctor}
    if request.method == 'POST':
        userForm = forms.PatientUpdateUserForm(request.POST, instance=user)
        patientForm = forms.PatientForm(request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            password = userForm.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.status = True
            # Only update assigned doctor if a new one is selected
            new_doctor_id = request.POST.get('assignedDoctorId')
            if new_doctor_id:
                patient.assignedDoctorId = new_doctor_id
            patient.save()
            messages.success(request, f'Patient {user.first_name} {user.last_name} details updated successfully!')
            return redirect('admin-view-patient')
        else:
            # Re-populate context with doctors on validation error
            mydict = {'userForm': userForm, 'patientForm': patientForm, 'patient': patient, 'doctors': doctors, 'currentDoctor': currentDoctor}
    return render(request, 'hospital/admin/update_patient.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    doctors = models.Doctor.objects.filter(status=True)
    mydict = {'userForm': userForm, 'patientForm': patientForm, 'doctors': doctors}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.status = True
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('admin-view-patient')
    return render(request, 'hospital/admin/add_patient.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    patients = models.Patient.objects.filter(status=False)
    return render(request, 'hospital/admin/approve_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    patient.status = True
    patient.save()
    return redirect(reverse('admin-approve-patient'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')


# ──────────────── DISCHARGE PATIENT ────────────────
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients = models.Patient.objects.filter(status=True)
    return render(request, 'hospital/admin/discharge_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    days = (date.today() - patient.admitDate)
    assignedDoctor = models.User.objects.filter(id=patient.assignedDoctorId)
    d = max(days.days, 1)  # Minimum 1 day for billing
    patientDict = {
        'patientId': pk,
        'name': patient.get_name,
        'mobile': patient.mobile,
        'address': patient.address,
        'symptoms': patient.symptoms,
        'admitDate': patient.admitDate,
        'todayDate': date.today(),
        'day': d,
        'assignedDoctorName': f"Dr. {assignedDoctor[0].first_name} {assignedDoctor[0].last_name}",
    }
    if request.method == 'POST':
        feeDict = {
            'roomCharge': int(request.POST['roomCharge']) * int(d),
            'doctorFee': request.POST['doctorFee'],
            'medicineCost': request.POST['medicineCost'],
            'OtherCharge': request.POST['OtherCharge'],
            'total': (int(request.POST['roomCharge']) * int(d)) + int(request.POST['doctorFee']) + int(request.POST['medicineCost']) + int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        pDD = models.PatientDischargeDetails()
        pDD.patientId = pk
        pDD.patientName = patient.get_name
        pDD.assignedDoctorName = f"Dr. {assignedDoctor[0].first_name} {assignedDoctor[0].last_name}"
        pDD.address = patient.address
        pDD.mobile = patient.mobile
        pDD.symptoms = patient.symptoms
        pDD.admitDate = patient.admitDate
        pDD.releaseDate = date.today()
        pDD.daySpent = int(d)
        pDD.medicineCost = int(request.POST['medicineCost'])
        pDD.roomCharge = int(request.POST['roomCharge']) * int(d)
        pDD.doctorFee = int(request.POST['doctorFee'])
        pDD.OtherCharge = int(request.POST['OtherCharge'])
        pDD.total = (int(request.POST['roomCharge']) * int(d)) + int(request.POST['doctorFee']) + int(request.POST['medicineCost']) + int(request.POST['OtherCharge'])
        pDD.canReapply = request.POST.get('canReapply', '') == 'on'
        pDD.followUpNotes = request.POST.get('followUpNotes', '')
        pDD.save()
        
        # Mark patient as discharged
        patient.status = False
        patient.save()
        
        return render(request, 'hospital/patient/final_bill.html', context=patientDict)
    return render(request, 'hospital/patient/generate_bill.html', context=patientDict)


# ──────────────── PDF DOWNLOAD ────────────────
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF', status=400)


def download_pdf_view(request, pk):
    dischargeDetails = models.PatientDischargeDetails.objects.filter(patientId=pk).order_by('-id')[:1]
    detail = dischargeDetails[0]
    context = {
        'patientName': detail.patientName,
        'assignedDoctorName': detail.assignedDoctorName,
        'address': detail.address,
        'mobile': detail.mobile,
        'symptoms': detail.symptoms,
        'admitDate': detail.admitDate,
        'releaseDate': detail.releaseDate,
        'daySpent': detail.daySpent,
        'medicineCost': detail.medicineCost,
        'roomCharge': detail.roomCharge,
        'doctorFee': detail.doctorFee,
        'OtherCharge': detail.OtherCharge,
        'total': detail.total,
    }
    return render_to_pdf('hospital/download_bill.html', context)


# ──────────────── APPOINTMENTS (ADMIN) ────────────────
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request, 'hospital/admin/appointment.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments = models.Appointment.objects.filter(status=True)
    return render(request, 'hospital/admin/view_appointment.html', {'appointments': appointments})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm = forms.AppointmentForm()
    mydict = {'appointmentForm': appointmentForm}
    if request.method == 'POST':
        appointmentForm = forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.POST.get('doctorId')
            appointment.patientId = request.POST.get('patientId')
            appointment.doctorName = models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName = models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status = True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request, 'hospital/admin/add_appointment.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    appointments = models.Appointment.objects.filter(status=False)
    return render(request, 'hospital/admin/approve_appointment.html', {'appointments': appointments})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.status = True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')


# ══════════════════════════════════════════════════════════════
# DOCTOR VIEWS
# ══════════════════════════════════════════════════════════════
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    patientcount = models.Patient.objects.filter(status=True, assignedDoctorId=request.user.id).count()
    appointmentcount = models.Appointment.objects.filter(status=True, doctorId=request.user.id).count()
    doctorFullName = f"Dr. {request.user.first_name} {request.user.last_name}"
    patientdischarged = models.PatientDischargeDetails.objects.distinct().filter(assignedDoctorName=doctorFullName).count()
    appointments = models.Appointment.objects.filter(status=True, doctorId=request.user.id).order_by('-id')
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.filter(status=True, user_id__in=patientid).order_by('-id')
    appointments = zip(appointments, patients)
    mydict = {
        'patientcount': patientcount,
        'appointmentcount': appointmentcount,
        'patientdischarged': patientdischarged,
        'appointments': appointments,
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor/dashboard.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict = {
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor/patient.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients = models.Patient.objects.filter(status=True, assignedDoctorId=request.user.id)
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor/view_patient.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    query = request.GET.get('query', '')
    patients = models.Patient.objects.filter(
        status=True, assignedDoctorId=request.user.id
    ).filter(
        Q(symptoms__icontains=query) | Q(user__first_name__icontains=query)
    )
    return render(request, 'hospital/doctor/view_patient.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    doctorFullName = f"Dr. {request.user.first_name} {request.user.last_name}"
    dischargedpatients = models.PatientDischargeDetails.objects.distinct().filter(assignedDoctorName=doctorFullName)
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor/view_discharge_patient.html', {'dischargedpatients': dischargedpatients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor/appointment.html', {'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(status=True, doctorId=request.user.id)
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.filter(status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor/view_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(status=True, doctorId=request.user.id)
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.filter(status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor/delete_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(status=True, doctorId=request.user.id)
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.filter(status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor/delete_appointment.html', {'appointments': appointments, 'doctor': doctor})


# ──────────────── DOCTOR: SCHEDULE CONSULTATION ────────────────
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_schedule_consultation_view(request, pk):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointment = models.Appointment.objects.get(id=pk)
    if request.method == 'POST':
        appointment.consultationDate = request.POST.get('consultationDate')
        appointment.consultationTime = request.POST.get('consultationTime')
        appointment.consultationNotes = request.POST.get('consultationNotes', '')
        appointment.save()
        messages.success(request, f'Consultation scheduled for {appointment.patientName}.')
        return redirect('doctor-view-appointment')
    return render(request, 'hospital/doctor/schedule_consultation.html', {
        'appointment': appointment,
        'doctor': doctor,
    })


# ══════════════════════════════════════════════════════════════
# PATIENT VIEWS
# ══════════════════════════════════════════════════════════════
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    doctor = models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    appointments = models.Appointment.objects.filter(patientId=request.user.id).order_by('-id')
    appointmentcount = appointments.filter(status=True).count()
    pendingappointmentcount = appointments.filter(status=False).count()
    discharge = models.PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-id')
    mydict = {
        'patient': patient,
        'doctor': doctor,
        'doctorName': doctor.get_name,
        'doctorMobile': doctor.mobile,
        'doctorAddress': doctor.address,
        'symptoms': patient.symptoms,
        'doctorDepartment': doctor.department,
        'admitDate': patient.admitDate,
        'appointments': appointments,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
        'discharge': discharge,
    }
    return render(request, 'hospital/patient/dashboard.html', context=mydict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient/appointment.html', {'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm = forms.PatientAppointmentForm()
    patient = models.Patient.objects.get(user_id=request.user.id)
    message = None
    mydict = {'appointmentForm': appointmentForm, 'patient': patient, 'message': message}
    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.POST.get('doctorId')
            appointment.patientId = request.user.id
            appointment.doctorName = models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName = request.user.first_name
            appointment.status = False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request, 'hospital/patient/book_appointment.html', context=mydict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_doctor_view(request):
    doctors = models.Doctor.objects.filter(status=True)
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient/view_doctor.html', {'patient': patient, 'doctors': doctors})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def search_doctor_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    query = request.GET.get('query', '')
    doctors = models.Doctor.objects.filter(status=True).filter(
        Q(department__icontains=query) | Q(user__first_name__icontains=query)
    )
    return render(request, 'hospital/patient/view_doctor.html', {'patient': patient, 'doctors': doctors})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(patientId=request.user.id)
    return render(request, 'hospital/patient/view_appointment.html', {'appointments': appointments, 'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    dischargeDetails = models.PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-id')[:1]
    patientDict = None
    if dischargeDetails:
        patientDict = {
            'is_discharged': True,
            'patient': patient,
            'patientId': patient.id,
            'patientName': patient.get_name,
            'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
            'address': patient.address,
            'mobile': patient.mobile,
            'symptoms': patient.symptoms,
            'admitDate': patient.admitDate,
            'releaseDate': dischargeDetails[0].releaseDate,
            'daySpent': dischargeDetails[0].daySpent,
            'medicineCost': dischargeDetails[0].medicineCost,
            'roomCharge': dischargeDetails[0].roomCharge,
            'doctorFee': dischargeDetails[0].doctorFee,
            'OtherCharge': dischargeDetails[0].OtherCharge,
            'total': dischargeDetails[0].total,
        }
    else:
        patientDict = {
            'is_discharged': False,
            'patient': patient,
            'patientId': request.user.id,
        }
    return render(request, 'hospital/patient/discharge.html', context=patientDict)


# ──────────────── PATIENT: MEDICAL RECORDS TIMELINE ────────────────
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_medical_records_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(patientId=request.user.id).order_by('-appointmentDate')
    discharges = models.PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-releaseDate')

    # Build timeline
    timeline = []
    timeline.append({
        'type': 'admit',
        'date': patient.admitDate,
        'title': 'Admitted to Hospital',
        'detail': f'Symptoms: {patient.symptoms}',
        'icon': 'fa-hospital',
        'color': '#0f3460',
    })
    for apt in appointments:
        timeline.append({
            'type': 'appointment',
            'date': apt.appointmentDate,
            'title': f'Appointment with Dr. {apt.doctorName}',
            'detail': apt.description,
            'status': 'Approved' if apt.status else 'Pending',
            'icon': 'fa-calendar-check',
            'color': '#2a9d8f' if apt.status else '#c9a84c',
        })
        if apt.consultationDate:
            timeline.append({
                'type': 'consultation',
                'date': apt.consultationDate,
                'title': f'Consultation with Dr. {apt.doctorName}',
                'detail': f'Time: {apt.consultationTime.strftime("%I:%M %p") if apt.consultationTime else "TBD"}' + (f' | Notes: {apt.consultationNotes}' if apt.consultationNotes else ''),
                'icon': 'fa-comments-medical' if hasattr(apt, 'consultationNotes') else 'fa-comments',
                'color': '#6C5CE7',
            })
    for d in discharges:
        timeline.append({
            'type': 'discharge',
            'date': d.releaseDate,
            'title': 'Discharged from Hospital',
            'detail': f'Days spent: {d.daySpent} | Total bill: ₹{d.total}',
            'icon': 'fa-sign-out-alt',
            'color': '#FF6B6B',
            'canReapply': d.canReapply,
            'followUpNotes': d.followUpNotes,
        })

    timeline.sort(key=lambda x: x['date'], reverse=True)

    return render(request, 'hospital/patient/medical_records.html', {
        'patient': patient,
        'timeline': timeline,
        'appointments': appointments,
        'discharges': discharges,
    })


# ──────────────── PATIENT: REAPPLY AFTER DISCHARGE ────────────────
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_reapply_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    # Check if patient was discharged and can reapply
    lastDischarge = models.PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-id').first()
    if not lastDischarge:
        messages.warning(request, 'You have not been discharged yet.')
        return redirect('patient-dashboard')
    if not lastDischarge.canReapply:
        messages.error(request, 'Your doctor has not approved reapplication. Please contact the hospital.')
        return redirect('patient-discharge')

    if request.method == 'POST':
        new_symptoms = request.POST.get('symptoms', patient.symptoms)
        patient.symptoms = new_symptoms
        patient.status = False  # Needs re-approval
        patient.save()
        messages.success(request, 'Reapplication submitted successfully! Your account is pending admin approval.')
        return redirect('patient-dashboard')

    return render(request, 'hospital/patient/reapply.html', {
        'patient': patient,
        'lastDischarge': lastDischarge,
    })


# ══════════════════════════════════════════════════════════════
# ABOUT US & CONTACT US
# ══════════════════════════════════════════════════════════════
def aboutus_view(request):
    return render(request, 'hospital/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(
                f'{name} || {email}',
                message,
                settings.EMAIL_HOST_USER,
                settings.EMAIL_RECEIVING_USER,
                fail_silently=False,
            )
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form': sub})
