from django.urls import path

from .views import (
    book_appointment,
    patient_appointments,
    doctor_appointments,
    update_appointment_status,
    create_medical_record,
     view_medical_record,
       create_prescription,
        verify_prescription,
        verify_medical_record,
        patient_medical_records,
        patient_prescriptions,
)


urlpatterns = [

    path(
        "book/",
        book_appointment,
        name="book_appointment"
    ),

    path(
        "my-appointments/",
        patient_appointments,
        name="patient_appointments"
    ),

    path(
        "doctor/appointments/",
        doctor_appointments,
        name="doctor_appointments"
    ),

    path(
        "doctor/appointments/<int:appointment_id>/status/",
        update_appointment_status,
        name="update_appointment_status"
    ),

    path(
        "doctor/appointments/<int:appointment_id>/medical-record/create/",
        create_medical_record,
        name="create_medical_record"
    ),
    path(
    "doctor/appointments/<int:appointment_id>/medical-record/",
    view_medical_record,
    name="view_medical_record"
    ),
    path(
    "doctor/appointments/<int:appointment_id>/prescription/create/",
    create_prescription,
    name="create_prescription"
    ),
    path(
    "doctor/prescription/<int:prescription_id>/verify/",
    verify_prescription,
    name="verify_prescription"
    ),
    path(
    "doctor/appointments/<int:appointment_id>/medical-record/verify/",
    verify_medical_record,
    name="verify_medical_record"
    ),
    path(
    "my-medical-records/",
    patient_medical_records,
    name="patient_medical_records"
    ),
    path(
    "my-prescriptions/",
    patient_prescriptions,
    name="patient_prescriptions"
),
]
