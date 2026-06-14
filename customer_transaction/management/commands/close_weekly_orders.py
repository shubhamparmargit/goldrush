from django.core.management.base import BaseCommand
from customer_transaction.services import weekly_auto_close_runner

class Command(BaseCommand):
    help = "Close all running active digital investment orders at weekly boundary"

    def handle(self, *args, **options):
        self.stdout.write("Weekly auto-close job started...")
        weekly_auto_close_runner()
        self.stdout.write("Weekly auto-close job completed successfully.")
