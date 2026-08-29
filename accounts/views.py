from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .decorators import role_required
from clinic.models import Appointment, MedicalRecord
from cryptoutils.sha3 import hash_data

def home(request):
    return render(request, "accounts/home.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == "PATIENT":
                return redirect("patient_dashboard")
            elif user.role == "DOCTOR":
                return redirect("doctor_dashboard")
            elif user.role == "ADMIN":
                return redirect("admin_dashboard")

        return render(request, "accounts/login.html", {"error": "Invalid username or password."})
    return render(request, "accounts/login.html")

@role_required("PATIENT")
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by("-appointment_date", "-appointment_time")
    records_count = MedicalRecord.objects.filter(patient=request.user).count()
    next_appointment = appointments.filter(status=Appointment.Status.ACCEPTED).first() or appointments.first()

    return render(request, "accounts/patient_dashboard.html", {
        "appointments": appointments,
        "appointments_count": appointments.count(),
        "records_count": records_count,
        "next_appointment": next_appointment,
    })

@role_required("DOCTOR")
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(doctor=request.user)
    pending_count = appointments.filter(status=Appointment.Status.PENDING).count()
    records_count = MedicalRecord.objects.filter(doctor=request.user).count()

    return render(request, "accounts/doctor_dashboard.html", {
        "pending_count": pending_count,
        "records_count": records_count,
    })

@role_required("ADMIN")
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")

@role_required("ADMIN")
def security_center(request):
    return render(request, "accounts/security_center.html")

@role_required("ADMIN")
def verify_chain(request):
    records = MedicalRecord.objects.all().order_by("created_at", "id")
    previous_hash = "0" * 64
    results = []
    chain_valid = True

    for record in records:
        record_data = (
            f"{record.id}|"
            f"{record.diagnosis_nonce}|"
            f"{record.encrypted_diagnosis}|"
            f"{record.clinical_notes}"
        )
        expected_hash = hash_data(previous_hash + record_data)
        valid = (record.prev_hash == previous_hash and record.record_hash == expected_hash)
        if not valid:
            chain_valid = False

        results.append({
            "id": record.id,
            "patient": record.patient.username,
            "doctor": record.doctor.username,
            "prev_hash": record.prev_hash,
            "record_hash": record.record_hash,
            "valid": valid
        })
        previous_hash = record.record_hash

    return render(request, "accounts/verify_chain.html", {
        "results": results,
        "chain_valid": chain_valid
    })

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})