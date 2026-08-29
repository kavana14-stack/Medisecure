from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from accounts.views import (
    home,
    login_view,
    register_view,
    patient_dashboard,
    doctor_dashboard,
    admin_dashboard,
    security_center,
    verify_chain,
)


urlpatterns = [

    # Django admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Public home page
    path(
        "",
        home,
        name="home"
    ),

    # Login
    path(
        "login/",
        login_view,
        name="login"
    ),

    # Registration
    path(
        "register/",
        register_view,
        name="register"
    ),

    # Logout
    path(
        "logout/",
        LogoutView.as_view(
            next_page="/"
        ),
        name="logout"
    ),

    # Patient dashboard
    path(
        "patient/dashboard/",
        patient_dashboard,
        name="patient_dashboard"
    ),

    # Doctor dashboard
    path(
        "doctor/dashboard/",
        doctor_dashboard,
        name="doctor_dashboard"
    ),

    # Admin dashboard
    path(
        "admin-dashboard/",
        admin_dashboard,
        name="admin_dashboard"
    ),

    # Security center
    path(
        "security-center/",
        security_center,
        name="security_center"
    ),

    # Hash-chain verification
    path(
        "verify-chain/",
        verify_chain,
        name="verify_chain"
    ),

    # Clinic application
    path(
        "clinic/",
        include("clinic.urls")
    ),

]