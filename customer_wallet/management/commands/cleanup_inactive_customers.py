from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from customer.models import Customer
from customer_wallet.models import WalletRechargeHistory, CustomerWallet


class Command(BaseCommand):
    help = 'Delete/block customers inactive for 30+ days (no recharge in 30 days)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview only, no changes')

    def handle(self, *args, **options):
        dry_run    = options['dry_run']
        cutoff     = timezone.now() - timedelta(days=30)

        # --- Case 1: Never recharged + registered > 30 days ago → DELETE ---
        never_recharged = Customer.objects.filter(
            date__lt=cutoff
        ).exclude(
            id__in=WalletRechargeHistory.objects.values_list('customer_id', flat=True)
        )

        delete_count = never_recharged.count()

        # --- Case 2: Had recharges but last one > 30 days ago → BLOCK ---
        recharge_cutoff_ids = WalletRechargeHistory.objects.filter(
            status='Success',
            created_at__gte=cutoff
        ).values_list('customer_id', flat=True)

        had_recharge_inactive = Customer.objects.filter(
            id__in=WalletRechargeHistory.objects.values_list('customer_id', flat=True)
        ).exclude(
            id__in=recharge_cutoff_ids
        ).filter(
            access='Granted'
        )

        block_count = had_recharge_inactive.count()

        self.stdout.write(f'[Inactive Cleanup] Cutoff date: {cutoff.strftime("%d-%m-%Y")}')
        self.stdout.write(f'  → Never recharged (will DELETE): {delete_count}')
        self.stdout.write(f'  → Recharged but inactive (will BLOCK): {block_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes made.'))
            return

        with transaction.atomic():
            # DELETE never-recharged
            deleted, _ = never_recharged.delete()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted {deleted} inactive registrations'))

            # BLOCK inactive recharged customers
            blocked = had_recharge_inactive.update(access='Blocked')
            self.stdout.write(self.style.SUCCESS(f'  ✓ Blocked {blocked} inactive customers'))

        self.stdout.write(self.style.SUCCESS('Cleanup complete.'))
