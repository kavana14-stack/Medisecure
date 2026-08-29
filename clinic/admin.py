from django.contrib import admin

from .models import Appointment
from .models import Appointment, MedicalRecord


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "patient",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "appointment_date",
    )

    search_fields = (
        "patient__username",
        "doctor__username",
    )
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):

    list_display = (
        "patient",
        "doctor",
        "appointment",
        "created_at",
    )

    search_fields = (
        "patient__username",
        "doctor__username",
    )