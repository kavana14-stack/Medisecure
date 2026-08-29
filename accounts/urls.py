from django.urls import path

from .views import (
    home,
    login_view,
    register_view,
    patient_dashboard,
    doctor_dashboard,
    admin_dashboard,
    security_center,
)


urlpatterns = [

   path(
    "",
    home,
    name="home"
),

    path(
        "register/",
        register_view,
        name="register"
    ),

    path(
        "patient/dashboard/",
        patient_dashboard,
        name="patient_dashboard"
    ),

    path(
        "doctor/dashboard/",
        doctor_dashboard,
        name="doctor_dashboard"
    ),

    path(
        "admin/dashboard/",
        admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "security-center/",
        security_center,
        name="security_center"
    ),

]
