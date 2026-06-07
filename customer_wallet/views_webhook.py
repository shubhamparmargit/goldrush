from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.conf import settings
from customer_wallet.models import WalletRechargeOrder
# RazorPay
import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def razorpay_webhook(request):

    payload = request.body
    signature = request.headers.get("X-Razorpay-Signature")

    try:
        razorpay_client.utility.verify_webhook_signature(
            payload,
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        return HttpResponse(status=400)

    data = json.loads(payload)

    if data.get("event") == "payment.captured":

        payment = data["payload"]["payment"]["entity"]

        order_id = payment.get("order_id")

        try:
            order = WalletRechargeOrder.objects.get(
                razorpay_order_id=order_id
            )

            if order.status == "Created":
                order.status = "Paid"
                order.save(update_fields=["status"])

        except WalletRechargeOrder.DoesNotExist:
            pass

    return HttpResponse(status=200)