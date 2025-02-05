from django.core.management.base import BaseCommand
from django.utils import timezone
from mailapp.models import EmailMessage
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete email messages older than 1 hour'

    def handle(self, *args, **options):
        expiration_delta = timedelta(hours=1)
        expiration_time = timezone.now() - expiration_delta
        old_messages = EmailMessage.objects.filter(received_at__lt=expiration_time)
        count = old_messages.count()
        old_messages.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} expired email messages."))
