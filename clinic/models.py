from django.conf import settings
from django.db import models
from cryptoutils.aes import encrypt_data, decrypt_data
from cryptoutils.sha3 import hash_data, build_hash_chain

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        limit_choices_to={"role": "PATIENT"}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
        limit_choices_to={"role": "DOCTOR"}
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} -> {self.doctor.username} ({self.appointment_date})"

class MedicalRecord(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="medical_record"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_records"
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_medical_records"
    )
    # AES-256-GCM ciphertext & nonce
    encrypted_diagnosis = models.TextField(blank=True)
    diagnosis_nonce = models.CharField(max_length=32, blank=True)
    diagnosis_hash = models.CharField(max_length=64, blank=True)

    # SHA-3-256 Hash Chain
    prev_hash = models.CharField(max_length=64, default="0" * 64)
    record_hash = models.CharField(max_length=64, blank=True)

    clinical_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def encrypt_diagnosis(self, plaintext):
        if not plaintext:
            return
        nonce, ciphertext = encrypt_data(plaintext)
        self.diagnosis_nonce = nonce
        self.encrypted_diagnosis = ciphertext
        self.diagnosis_hash = hash_data(self.diagnosis_nonce + self.encrypted_diagnosis)

    def get_decrypted_diagnosis(self):
        if not self.encrypted_diagnosis or not self.diagnosis_nonce:
            return ""
        try:
            return decrypt_data(self.diagnosis_nonce, self.encrypted_diagnosis)
        except Exception:
            return "[DECRYPTION FAILED: DATA TAMPERED OR INVALID KEY]"

    def verify_diagnosis_integrity(self):
        if not self.diagnosis_hash:
            return False
        current_hash = hash_data(self.diagnosis_nonce + self.encrypted_diagnosis)
        return current_hash == self.diagnosis_hash

    def generate_record_hash(self):
        record_data = (
            f"{self.id}|"
            f"{self.diagnosis_nonce}|"
            f"{self.encrypted_diagnosis}|"
            f"{self.clinical_notes}"
        )
        self.record_hash = hash_data(self.prev_hash + record_data)

    def save(self, *args, **kwargs):
        # Prevent recursion when updating chain hashes
        if kwargs.get("update_fields") == ["prev_hash", "record_hash"]:
            super().save(*args, **kwargs)
            return

        super().save(*args, **kwargs)
        records = MedicalRecord.objects.all().order_by("created_at", "id")
        build_hash_chain(records)

    def __str__(self):
        return f"Medical Record - {self.patient.username} - {self.created_at}"

class DoctorKey(models.Model):
    doctor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_key"
    )
    public_key = models.TextField()
    encrypted_private_key = models.TextField()
    private_key_nonce = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DoctorKey - {self.doctor.username}"

class Prescription(models.Model):
    record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_prescriptions"
    )
    medication = models.TextField()
    instructions = models.TextField(blank=True)
    signature = models.TextField()
    doctor_public_key_snapshot = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription - {self.patient.username} - {self.medication}"