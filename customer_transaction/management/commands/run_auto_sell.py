from django.core.management.base import BaseCommand
from customer_transaction.models import CustomerTransaction
from customer_wallet.models import CustomerWallet
from django.db import transaction
from django.utils import timezone

from customer_transaction.services import (
    auto_sell_runner   # 👈 yahi tumhara existing logic
)

class Command(BaseCommand):
    help = "Run auto sell for eligible live orders"

    def handle(self, *args, **options):
        self.stdout.write("Auto sell runner started")
        auto_sell_runner()
        self.stdout.write("Auto sell runner finished")
