from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "role",
        ]

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")

        if password and confirm_password:

            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        if role == User.Role.ADMIN:
            raise forms.ValidationError(
                "Admin accounts cannot be created through public registration."
            )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        password = self.cleaned_data["password"]

        user.set_password(password)

        if commit:
            user.save()

        return user