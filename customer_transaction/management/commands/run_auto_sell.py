import time
from django.core.management.base import BaseCommand
from customer_transaction.services import auto_sell_runner


class Command(BaseCommand):
    help = "Run auto sell/stop-loss checker in a continuous loop (default: every 30 seconds)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Polling interval in seconds (default: 30). Lower = more precise stop-loss trigger.'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run only once and exit (useful for testing).'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']

        self.stdout.write(
            self.style.SUCCESS(
                f"Auto sell runner started — polling every {interval}s"
                + (" (single run)" if run_once else " (continuous loop)")
            )
        )

        while True:
            try:
                auto_sell_runner()
                self.stdout.write(f"[{self._now()}] Auto sell check complete.")
            except Exception as e:
                self.stderr.write(f"[{self._now()}] ERROR in auto_sell_runner: {e}")

            if run_once:
                break

            time.sleep(interval)

    @staticmethod
    def _now():
        from django.utils import timezone
        return timezone.localtime(timezone.now()).strftime("%d %b %Y %H:%M:%S")
