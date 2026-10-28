from django.core.management.base import BaseCommand
from voting.models import Vote
import hashlib

class Command(BaseCommand):
    help = "Backfill missing generated_signature for existing votes"

    def handle(self, *args, **kwargs):
        updated = 0
        for vote in Vote.objects.filter(generated_signature__isnull=True):
            data = f"{vote.candidate}-{vote.timestamp.isoformat()}"
            vote.generated_signature = hashlib.sha256(data.encode()).hexdigest()
            vote.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} votes with generated_signature"))