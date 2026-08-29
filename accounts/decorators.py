from functools import wraps

from django.contrib.auth import logout
from django.shortcuts import redirect


def role_required(required_role):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # User is not logged in
            if not request.user.is_authenticated:
                return redirect("login")

            # User is logged in but does not have permission
            if request.user.role != required_role:

                # IMPORTANT:
                # Do NOT logout the user here.
                # A wrong link must never destroy the login session.

                if request.user.role == "DOCTOR":
                    return redirect("doctor_dashboard")

                if request.user.role == "PATIENT":
                    return redirect("patient_dashboard")

                if request.user.role == "ADMIN":
                    return redirect("admin_dashboard")

                return redirect("login")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator