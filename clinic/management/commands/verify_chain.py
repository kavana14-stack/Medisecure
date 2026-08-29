from django.core.management.base import BaseCommand

from clinic.models import MedicalRecord
from cryptoutils.sha3 import hash_data


class Command(BaseCommand):

    help = "Verify the SHA-3 medical record hash chain."

    def handle(self, *args, **options):

        records = MedicalRecord.objects.all().order_by(
            "created_at",
            "id"
        )

        if not records.exists():

            self.stdout.write(
                self.style.WARNING(
                    "No medical records found."
                )
            )

            return

        previous_hash = "0" * 64

        chain_valid = True

        for record in records:

            record_data = (
                str(record.id)
                + "|"
                + record.diagnosis_nonce
                + "|"
                + record.encrypted_diagnosis
                + "|"
                + record.clinical_notes
            )

            expected_hash = hash_data(
                previous_hash + record_data
            )

            if record.prev_hash != previous_hash:

                self.stdout.write(
                    self.style.ERROR(
                        f"Record {record.id}: PREVIOUS HASH MISMATCH"
                    )
                )

                chain_valid = False

            elif record.record_hash != expected_hash:

                self.stdout.write(
                    self.style.ERROR(
                        f"Record {record.id}: RECORD HASH MISMATCH"
                    )
                )

                chain_valid = False

            else:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Record {record.id}: VALID"
                    )
                )

            previous_hash = record.record_hash

        if chain_valid:

            self.stdout.write(
                self.style.SUCCESS(
                    "\n✅ HASH CHAIN VERIFIED SUCCESSFULLY"
                )
            )

        else:

            self.stdout.write(
                self.style.ERROR(
                    "\n❌ HASH CHAIN INTEGRITY CHECK FAILED"
                )
            )
