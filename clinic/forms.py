from django import forms

from .models import Appointment
from accounts.models import User


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment

        fields = [
            "doctor",
            "appointment_date",
            "appointment_time",
            "reason",
        ]

        widgets = {

            "appointment_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "appointment_time": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Briefly describe the reason for your appointment"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = User.objects.filter(
            role=User.Role.DOCTOR
        )