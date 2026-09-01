from django.shortcuts import render, redirect, get_object_or_404

from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

from accounts.decorators import role_required

from cryptoutils.aes import encrypt_data, decrypt_data

from cryptoutils.ed25519 import (
    generate_keypair,
    sign_data,
    verify_signature,
)

from cryptoutils.sha3 import hash_data


# ============================================================
# PATIENT - BOOK APPOINTMENT
# ============================================================

@role_required("PATIENT")
def book_appointment(request):

    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related(
        "doctor"
    ).order_by(
        "-appointment_date",
        "-appointment_time"
    )

    if request.method == "POST":

        form = AppointmentForm(request.POST)

        if form.is_valid():

            appointment = form.save(commit=False)

            appointment.patient = request.user

            appointment.status = Appointment.Status.PENDING

            appointment.save()

            return redirect("book_appointment")

    else:

        form = AppointmentForm()

    return render(
        request,
        "clinic/book_appointment.html",
        {
            "form": form,
            "appointments": appointments,
        }
    )


# ============================================================
# PATIENT - VIEW APPOINTMENTS
# ============================================================

@role_required("PATIENT")
def patient_appointments(request):

    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related(
        "doctor"
    ).order_by(
        "-appointment_date",
        "-appointment_time"
    )

    return render(
        request,
        "clinic/patient_appointments.html",
        {
            "appointments": appointments
        }
    )


# ============================================================
# DOCTOR - VIEW APPOINTMENTS
# ============================================================

@role_required("DOCTOR")
def doctor_appointments(request):

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).select_related(
        "patient"
    ).order_by(
        "appointment_date",
        "appointment_time"
    )

    return render(
        request,
        "clinic/doctor_appointments.html",
        {
            "appointments": appointments
        }
    )


# ============================================================
# DOCTOR - ACCEPT / REJECT APPOINTMENT
# ============================================================

@role_required("DOCTOR")
def update_appointment_status(
    request,
    appointment_id
):

    if request.method != "POST":

        return redirect("doctor_appointments")

    appointment = Appointment.objects.filter(
        id=appointment_id,
        doctor=request.user
    ).first()

    if appointment is None:

        return redirect("doctor_appointments")

    action = request.POST.get("action")

    if action == "accept":

        appointment.status = Appointment.Status.ACCEPTED

        appointment.save()

    elif action == "reject":

        appointment.status = Appointment.Status.REJECTED

        appointment.save()

    return redirect("doctor_appointments")


# ============================================================
# DOCTOR - CREATE / UPDATE MEDICAL RECORD
# ============================================================

@role_required("DOCTOR")
def create_medical_record(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user,
        status=Appointment.Status.ACCEPTED
    )

    record = MedicalRecord.objects.filter(
        appointment=appointment
    ).first()

    if request.method == "POST":

        diagnosis = request.POST.get(
            "diagnosis",
            ""
        ).strip()

        clinical_notes = request.POST.get(
            "clinical_notes",
            ""
        ).strip()

        if not diagnosis:

            return render(
                request,
                "clinic/create_medical_record.html",
                {
                    "appointment": appointment,
                    "record": record,
                    "error": "Diagnosis is required."
                }
            )

        # Update existing record
        if record:

            record.clinical_notes = clinical_notes

        # Create new record
        else:

            record = MedicalRecord(
                appointment=appointment,
                patient=appointment.patient,
                doctor=request.user,
                clinical_notes=clinical_notes
            )

        # Encrypt diagnosis before saving
        record.encrypt_diagnosis(diagnosis)

        record.save()

        return redirect(
            "doctor_appointments"
        )

    return render(
        request,
        "clinic/create_medical_record.html",
        {
            "appointment": appointment,
            "record": record
        }
    )


# ============================================================
# DOCTOR - VIEW MEDICAL RECORD
# ============================================================

@role_required("DOCTOR")
def view_medical_record(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user
    )

    record = get_object_or_404(
        MedicalRecord,
        appointment=appointment
    )

    diagnosis = record.get_decrypted_diagnosis()

    prescriptions = Prescription.objects.filter(
        record=record
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "clinic/view_medical_record.html",
        {
            "appointment": appointment,
            "record": record,
            "diagnosis": diagnosis,
            "prescriptions": prescriptions,
        }
    )


# ============================================================
# DOCTOR - CREATE PRESCRIPTION
# ============================================================

@role_required("DOCTOR")
def create_prescription(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user,
        status=Appointment.Status.ACCEPTED
    )

    record = get_object_or_404(
        MedicalRecord,
        appointment=appointment,
        doctor=request.user
    )

    if request.method == "POST":

        medication = request.POST.get(
            "medication",
            ""
        ).strip()

        instructions = request.POST.get(
            "instructions",
            ""
        ).strip()

        if not medication:

            return render(
                request,
                "clinic/create_prescription.html",
                {
                    "appointment": appointment,
                    "record": record,
                    "error": "Medication is required."
                }
            )

        prescription_data = (
            medication
            + "|"
            + instructions
        )

        # ----------------------------------------------------
        # GET OR CREATE DOCTOR KEY
        # ----------------------------------------------------

        doctor_key = getattr(
            request.user,
            "doctor_key",
            None
        )

        if doctor_key is None:

            private_key, public_key = generate_keypair()

            # Encrypt private key with AES-GCM
            private_nonce, encrypted_private_key = encrypt_data(
                private_key
            )

            doctor_key = DoctorKey.objects.create(
                doctor=request.user,
                public_key=public_key,
                encrypted_private_key=encrypted_private_key,
                private_key_nonce=private_nonce
            )

        else:

            # Decrypt stored private key
            private_key = decrypt_data(
                doctor_key.private_key_nonce,
                doctor_key.encrypted_private_key
            )

        # ----------------------------------------------------
        # SIGN PRESCRIPTION
        # ----------------------------------------------------

        signature = sign_data(
            prescription_data,
            private_key
        )

        # ----------------------------------------------------
        # SAVE PRESCRIPTION
        # ----------------------------------------------------

        Prescription.objects.create(
            record=record,
            doctor=request.user,
            patient=appointment.patient,
            medication=medication,
            instructions=instructions,
            signature=signature,
            doctor_public_key_snapshot=(
                doctor_key.public_key
            )
        )

        return redirect(
            "view_medical_record",
            appointment_id=appointment.id
        )

    return render(
        request,
        "clinic/create_prescription.html",
        {
            "appointment": appointment,
            "record": record
        }
    )


# ============================================================
# VERIFY PRESCRIPTION SIGNATURE
# ============================================================

@role_required("DOCTOR")
def verify_prescription(
    request,
    prescription_id
):

    prescription = get_object_or_404(
        Prescription,
        id=prescription_id,
        doctor=request.user
    )

    prescription_data = (
        prescription.medication
        + "|"
        + prescription.instructions
    )

    is_valid = verify_signature(
        prescription_data,
        prescription.signature,
        prescription.doctor_public_key_snapshot
    )

    return render(
        request,
        "clinic/verify_prescription.html",
        {
            "prescription": prescription,
            "is_valid": is_valid
        }
    )


# ============================================================
# VERIFY MEDICAL RECORD INTEGRITY
# ============================================================

@role_required("DOCTOR")
def verify_medical_record(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user
    )

    record = get_object_or_404(
        MedicalRecord,
        appointment=appointment
    )

    is_valid = record.verify_diagnosis_integrity()

    return render(
        request,
        "clinic/verify_medical_record.html",
        {
            "appointment": appointment,
            "record": record,
            "is_valid": is_valid
        }
    )


# ============================================================
# PATIENT - VIEW MEDICAL RECORDS
# ============================================================

@role_required("PATIENT")
def patient_medical_records(request):

    records = MedicalRecord.objects.filter(
        patient=request.user
    ).order_by(
        "-created_at"
    )

    medical_records = []

    for record in records:

        medical_records.append({
            "record": record,
            "diagnosis": record.get_decrypted_diagnosis(),
            "prescriptions": record.prescriptions.all(),
        })

    return render(
        request,
        "clinic/patient_medical_records.html",
        {
            "medical_records": medical_records
        }
    )

# ============================================================
# PATIENT - VIEW PRESCRIPTIONS
# ============================================================

@role_required("PATIENT")
def patient_prescriptions(request):

    prescriptions = Prescription.objects.filter(
        patient=request.user
    ).select_related(
        "doctor",
        "record"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "clinic/patient_prescriptions.html",
        {
            "prescriptions": prescriptions
        }
    )

# ============================================================
# SECURITY DEMONSTRATION
# ============================================================

# ============================================================
# SECURITY DEMONSTRATION
# AES-256-GCM + Ed25519 + SHA-3-256
# ============================================================

def security_demo(request):

    # ========================================================
    # POST REQUEST
    # ========================================================

    if request.method == "POST":

        algorithm = request.POST.get("algorithm", "")
        data = request.POST.get("data", "")

        # ====================================================
        # RESET ED25519 DEMO
        # ====================================================

        if algorithm == "ed25519_reset":

            request.session.pop(
                "ed_original_data",
                None
            )

            request.session.pop(
                "ed_signature",
                None
            )

            request.session.pop(
                "ed_public_key",
                None
            )

            request.session.modified = True

            return JsonResponse({
                "success": True
            })


        # ====================================================
        # RESET SHA-3 DEMO
        # ====================================================

        if algorithm == "sha3_reset":

            request.session.pop(
                "sha3_original_data",
                None
            )

            request.session.pop(
                "sha3_original_hash",
                None
            )

            request.session.modified = True

            return JsonResponse({
                "success": True
            })


        # ====================================================
        # ALGORITHM 1
        # AES-256-GCM
        # ====================================================

        if algorithm == "aes":

            if not data:

                return JsonResponse({
                    "success": False,
                    "error": "Please enter medical data."
                })


            try:

                plaintext = data

                nonce, ciphertext = encrypt_data(
                    plaintext
                )

                decrypted = decrypt_data(
                    nonce,
                    ciphertext
                )

                return JsonResponse({

                    "success": True,

                    "algorithm": "AES-256-GCM",

                    "plaintext": plaintext,

                    "nonce": nonce,

                    "ciphertext": ciphertext,

                    "decrypted": decrypted,

                    "verified": (
                        decrypted == plaintext
                    )

                })


            except Exception as e:

                return JsonResponse({

                    "success": False,

                    "error": str(e)

                })


        # ====================================================
        # ALGORITHM 2
        # ED25519 DIGITAL SIGNATURE
        # ====================================================

        if algorithm == "ed25519":

            if not data:

                return JsonResponse({

                    "success": False,

                    "error":
                        "Please enter prescription data."

                })


            try:

                # --------------------------------------------
                # FIRST SCAN
                # --------------------------------------------

                if "ed_original_data" not in request.session:

                    private_key, public_key = (
                        generate_keypair()
                    )

                    signature = sign_data(
                        data,
                        private_key
                    )

                    request.session[
                        "ed_original_data"
                    ] = data

                    request.session[
                        "ed_signature"
                    ] = signature

                    request.session[
                        "ed_public_key"
                    ] = public_key

                    request.session.modified = True

                    valid = verify_signature(
                        data,
                        signature,
                        public_key
                    )

                    return JsonResponse({

                        "success": True,

                        "algorithm": "Ed25519",

                        "data": data,

                        "original_data": data,

                        "signature": signature,

                        "public_key": public_key,

                        "verified": valid,

                        "first_scan": True,

                        "modified": False

                    })


                # --------------------------------------------
                # SECOND / LATER SCAN
                # --------------------------------------------

                original_data = request.session[
                    "ed_original_data"
                ]

                original_signature = request.session[
                    "ed_signature"
                ]

                original_public_key = request.session[
                    "ed_public_key"
                ]

                valid = verify_signature(
                    data,
                    original_signature,
                    original_public_key
                )

                return JsonResponse({

                    "success": True,

                    "algorithm": "Ed25519",

                    "data": data,

                    "original_data":
                        original_data,

                    "signature":
                        original_signature,

                    "public_key":
                        original_public_key,

                    "verified":
                        valid,

                    "first_scan":
                        False,

                    "modified":
                        data != original_data

                })


            except Exception as e:

                return JsonResponse({

                    "success": False,

                    "error": str(e)

                })


        # ====================================================
        # ALGORITHM 3
        # SHA-3-256
        # ====================================================

        if algorithm == "sha3":

            if not data:

                return JsonResponse({

                    "success": False,

                    "error":
                        "Please enter medical data."

                })


            try:

                # --------------------------------------------
                # CALCULATE CURRENT HASH
                # --------------------------------------------

                current_hash = hash_data(
                    data
                )


                # --------------------------------------------
                # FIRST SCAN
                # --------------------------------------------

                if (
                    "sha3_original_data"
                    not in request.session
                ):

                    request.session[
                        "sha3_original_data"
                    ] = data

                    request.session[
                        "sha3_original_hash"
                    ] = current_hash

                    request.session.modified = True

                    return JsonResponse({

                        "success": True,

                        "algorithm":
                            "SHA-3-256",

                        "original_data":
                            data,

                        "original_hash":
                            current_hash,

                        "current_data":
                            data,

                        "current_hash":
                            current_hash,

                        "verified":
                            True,

                        "modified":
                            False,

                        "first_scan":
                            True

                    })


                # --------------------------------------------
                # SECOND / LATER SCAN
                # --------------------------------------------

                original_data = request.session[
                    "sha3_original_data"
                ]

                original_hash = request.session[
                    "sha3_original_hash"
                ]

                verified = (
                    current_hash ==
                    original_hash
                )

                return JsonResponse({

                    "success": True,

                    "algorithm":
                        "SHA-3-256",

                    "original_data":
                        original_data,

                    "original_hash":
                        original_hash,

                    "current_data":
                        data,

                    "current_hash":
                        current_hash,

                    "verified":
                        verified,

                    "modified":
                        data != original_data,

                    "first_scan":
                        False

                })


            except Exception as e:

                return JsonResponse({

                    "success": False,

                    "error": str(e)

                })


        # ====================================================
        # UNKNOWN ALGORITHM
        # ====================================================

        return JsonResponse({

            "success": False,

            "error": "Unknown algorithm."

        })


    # ========================================================
    # GET REQUEST
    # ========================================================

    return render(
        request,
        "clinic/security_demo.html"
    )
