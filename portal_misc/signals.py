"""
portal_misc/signals.py

Listens for admin changes to CompanyBankDetails and immediately logs
a MetalRateLog row tagged as ADMIN_OVERRIDE whenever a rate-affecting
field is saved. This ensures admin panel manipulations appear instantly
in the candle chart history without waiting for the 60s API cooldown.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Fields on CompanyBankDetails that affect the live gold/silver rate
RATE_AFFECTING_FIELDS = {
    'bulk_override_gold_rate',
    'bulk_override_silver_rate',
    'spread',
    'dollar_rate',
    'base_gold_price',
    'stop_api_hits',
}


def _log_admin_rate(source="ADMIN_OVERRIDE"):
    """Fetch current computed rates and write a MetalRateLog row for both metals."""
    try:
        from customer_transaction.views import getMetalRate
        from customer_transaction.models import MetalRateLog

        rates = getMetalRate()

        gold_rate = rates.get("buy_gold_rate")
        silver_rate = rates.get("buy_silver_rate")

        if gold_rate:
            MetalRateLog.objects.create(
                metal_type="GOLD",
                rate=gold_rate,
                source=source,
            )
        if silver_rate:
            MetalRateLog.objects.create(
                metal_type="SILVER",
                rate=silver_rate,
                source=source,
            )
        logger.info(f"[AdminSignal] MetalRateLog written via {source}: Gold={gold_rate}, Silver={silver_rate}")
    except Exception as e:
        logger.error(f"[AdminSignal] Failed to log metal rate on admin save: {e}")


@receiver(post_save, sender='portal_misc.CompanyBankDetails')
def on_company_bank_details_save(sender, instance, created, update_fields, **kwargs):
    """
    Fires after CompanyBankDetails is saved from admin panel.
    Checks if any rate-affecting field changed and logs immediately.
    """
    # If update_fields is specified (e.g. auto-save), only log if relevant fields changed
    if update_fields is not None:
        changed = set(update_fields) & RATE_AFFECTING_FIELDS
        if not changed:
            return  # unrelated fields saved — skip

    # Determine source label based on which override is active
    if instance.bulk_override_gold_rate or instance.bulk_override_silver_rate:
        source = "ADMIN_OVERRIDE"
    else:
        source = "SPREAD_CHANGE"

    _log_admin_rate(source=source)
