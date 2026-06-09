from django.shortcuts import render, redirect
from customer.models import Customer
from customer_wallet.models import MembershipMaster, CustomerWallet, WalletRechargeHistory, WalletRechargeOrder, WithdrawalRequest, ManualRechargeRequest, WalletManualCredit
from utility.views import RandomIdGenerate, current_date, Utility, CustomerUtil
import re, os, json
from django.http.response import JsonResponse
from rest_framework import status
from django.db import transaction
from django.conf import settings
from customer_order.views import CustomerOrderData, razorpay_client
import razorpay
from decimal import Decimal
from customer_trading.decorators import require_trading_pin, require_trading_auth
from customer_trading.models import CustomerTradingBankDetails
from portal_misc.models import BankHoliday, CompanyBankDetails

def is_withdrawal_window_open():
    now = timezone.localtime(timezone.now())
    weekday = now.weekday()  # Monday=0, Sunday=6

    if weekday >= 5:
        return False, "Withdrawals are not available on weekends (Saturday & Sunday)"

    if now.hour < 10 or now.hour >= 17:
        return False, "Withdrawals are available Monday to Friday, 10:00 AM to 5:00 PM only"

    holiday = BankHoliday.objects.filter(date=now.date(), is_active=True).first()
    if holiday:
        return False, f"Withdrawals are not available today due to bank holiday: {holiday.description}"

    return True, None
from django.utils import timezone

util_obj = Utility()
random_obj = RandomIdGenerate()
od_obj = CustomerOrderData()
cust_util_obj = CustomerUtil()

class Pages:
    def my_wallet(self,request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')

        if request.is_demo_account:
            return redirect('digital_gateway')
        
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)

        history = WalletRechargeHistory.objects.filter(
            customer=customer
        ).select_related("order").order_by("-created_at")

        return render(request,'digital-investment/my-wallet.html', {'wallet_balance':wallet_balance,'history':history})
    
    def recharge_wallet(self,request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        if request.is_demo_account:
            return redirect('digital_gateway')
        
        memberships = cust_util_obj.get_all_memberships()
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)
        company_bank = CompanyBankDetails.objects.filter(is_active=True).first()

        return render(request,'digital-investment/recharge-wallet.html', {
            'memberships': memberships,
            'wallet_balance': wallet_balance,
            'company_bank': company_bank,
        })
    
    # def payment_success(self,request):
    #     return render(request,'digital-investment/payment-success.html')
    
    # def payment_failed(self,request):
    #     return render(request,'digital-investment/payment-failed.html')

    def withdraw_amount(self,request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')

        if request.is_demo_account:
            return redirect('digital_gateway')
        
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)

        withdrawals = WithdrawalRequest.objects.filter(
            customer=customer
        ).order_by('-request_date')

        has_bank_details = CustomerTradingBankDetails.objects.filter(customer=customer).exists()

        return render(request,'digital-investment/withdraw-amount.html', {
            'wallet_balance': wallet_balance,
            'withdrawals': withdrawals,
            'has_bank_details': has_bank_details,
        })
    
class WalletOperations:
    @require_trading_pin
    def create_wallet_order(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({
                "status": False,
                "message": "Digital investment access is disabled or invalid request"
            })
        
        try:
            data = json.loads(request.body)
            amount = int(data.get("amount", 0))
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid payload"})

        # if amount < 5000:
        #     return JsonResponse({"status": False, "message": "Minimum recharge ₹5000"})

        first_recharge_done = WalletRechargeHistory.objects.filter(customer=customer,status="Success").exists()

        # 🔒 First recharge rule
        if not first_recharge_done and amount < 5000:
            return JsonResponse({
                "status": False,
                "message": "First recharge minimum ₹5000 required"
            })

        # 🔒 After first recharge
        if first_recharge_done and amount < 1:
            return JsonResponse({
                "status": False,
                "message": "Minimum recharge ₹1"
            })

        membership = (
            MembershipMaster.objects
            .filter(min_amount__lte=amount)
            .order_by("-min_amount")
            .first()
        )

        # 👉 If no membership (small recharge), keep previous
        if not membership and first_recharge_done:
            wallet = CustomerWallet.objects.filter(customer=customer).first()
            membership = wallet.current_membership if wallet else None

        # 🔐 Everything inside atomic
        try:
            with transaction.atomic():
                order = od_obj.create_razorpay_order(amount)

                # 🔐 Razorpay response validation
                if not order or "id" not in order:
                    raise Exception("Invalid Razorpay order response")

                WalletRechargeOrder.objects.create(
                    customer=customer,
                    razorpay_order_id=order["id"],
                    amount=amount,
                    membership=membership,
                    status="Created"
                )

        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": "Unable to create wallet order"
            })

        return JsonResponse({
            "status": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "key": settings.RAZORPAY_KEY_ID,
            "prefill": {
                "name": customer.name,
                "contact": customer.mobile,
                "email": customer.email or ""
            }
        })

    def wallet_payment_failed(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        order_id = request.GET.get("order_id")
        reason = request.GET.get("reason", "Payment cancelled")

        order = None
        if order_id:
            try:
                order = WalletRechargeOrder.objects.get(
                    razorpay_order_id=order_id
                )
                if order.status == "Created":
                    order.status = "Failed"
                    order.save(update_fields=["status"])
            except WalletRechargeOrder.DoesNotExist:
                pass

        return render(request, "digital-investment/payment-failed.html", {
            "reason": reason,
            "amount": order.amount if order else None,
            "order_id": order_id
        })

    def wallet_payment_success(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return render(request, 'digital-investment/error.html', {
                'msg': 'Digital investment access is disabled or invalid request'
            })

        payment_id = request.POST.get("razorpay_payment_id")
        order_id   = request.POST.get("razorpay_order_id")
        signature  = request.POST.get("razorpay_signature")

        if not all([payment_id, order_id, signature]):
            return redirect("wallet_payment_failed")

        # 🔐 Razorpay verify
        # print(payment_id, order_id, signature)
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id,
                "razorpay_signature": signature
            })
        except razorpay.errors.SignatureVerificationError:
            return redirect("wallet_payment_failed")
        
        # print("STEP 1 signature ok")
        
        try:
            payment = razorpay_client.payment.fetch(payment_id)

            if payment.get("status") not in ["captured", "authorized"]:
                return redirect("wallet_payment_failed")

        except Exception:
            return redirect("wallet_payment_failed")
        
        # print("STEP 2 payment fetched", payment)

        # 🔒 DB atomic starts
        try:
            with transaction.atomic():

                order = (
                    WalletRechargeOrder.objects
                    .select_for_update()
                    .get(
                        razorpay_order_id=order_id,
                        customer=customer
                    )
                )

                # 🛑 Order replay protection
                if order.status != "Created":
                    return redirect("wallet_history")
                
                # print("STEP 3 order verified")

                # 🛑 Idempotent protection
                if order.status == "Paid":
                    return redirect("wallet_history")
                
                # 🔒 Amount verification
                # print("Razorpay amount:", payment.get("amount"))
                # print("Order amount:", order.amount * 100)
                if int(payment.get("amount", 0)) != int(order.amount * 100):
                    return redirect("wallet_payment_failed")
                
                # print("STEP 4 amount verified")

                # 💰 Wallet update
                wallet, _ = CustomerWallet.objects.select_for_update().get_or_create(
                    customer=customer
                )

                # wallet.balance = wallet.balance + Decimal(order.amount)
                wallet.balance += Decimal(order.amount)

                new_membership = order.membership

                if wallet.current_membership is None:
                    wallet.current_membership = new_membership
                else:
                    if new_membership.min_amount > wallet.current_membership.min_amount:
                        wallet.current_membership = new_membership

                wallet.save()

                # 📜 History entry
                # WalletRechargeHistory.objects.create(
                #     customer=customer,
                #     order=order,
                #     amount=order.amount,
                #     membership_allocated=order.membership,
                #     razorpay_payment_id=payment_id,
                #     razorpay_signature=signature,
                #     status="Success"
                # )

                WalletRechargeHistory.objects.create(
                    customer=customer,
                    order=order,
                    amount=order.amount,
                    membership_allocated=wallet.current_membership,
                    razorpay_payment_id=payment_id,
                    razorpay_signature=signature,
                    status="Success"
                )

                # ✅ Order final update
                order.status = "Paid"
                order.save(update_fields=["status"])

        except WalletRechargeOrder.DoesNotExist:
            return redirect("wallet_payment_failed")

        except Exception:
            # any DB / logic failure → rollback
            return redirect("wallet_payment_failed")

        return render(request, "digital-investment/payment-success.html", {
            "amount": order.amount,
            "membership": wallet.current_membership.level,
            "transaction_id": payment_id
        })
    
    def wallet_history_detail(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        order_id = request.GET.get("order_id")

        try:
            history = WalletRechargeHistory.objects.select_related(
                "order", "membership_allocated"
            ).get(
                customer=customer,
                order__razorpay_order_id=order_id
            )
        except WalletRechargeHistory.DoesNotExist:
            return JsonResponse({"status": False})

        return JsonResponse({
            "status": True,
            "txn_id": order_id,
            "type": "Credit" if history.amount > 0 else "Debit",
            "amount": history.amount,
            "status": history.status,
            "gateway": "Razorpay",
            "membership": history.membership_allocated.level if history.membership_allocated else "-",
            "balance": history.customer.customerwallet.balance,
            "date": timezone.localtime(history.created_at).strftime('%d %b %Y, %I:%M %p')
        })
    
    def submitManualRecharge(self, request):
        if request.trading_error:
            return JsonResponse({'status': False, 'message': 'Access denied'})

        customer = request.trading_customer
        if not customer:
            return JsonResponse({'status': False, 'message': 'Invalid customer'})

        if request.method != 'POST':
            return JsonResponse({'status': False, 'message': 'Invalid request'})

        try:
            amount       = int(request.POST.get('amount', 0))
            utr_number   = request.POST.get('utr_number', '').strip()
            payment_mode = request.POST.get('payment_mode', 'UPI').strip()

            if amount < 1:
                return JsonResponse({'status': False, 'message': 'Enter a valid amount'})
            if not utr_number:
                return JsonResponse({'status': False, 'message': 'UTR / Transaction Reference is required'})
            if payment_mode not in ('UPI', 'NEFT', 'IMPS', 'RTGS'):
                return JsonResponse({'status': False, 'message': 'Invalid payment mode'})

            # duplicate UTR check
            if ManualRechargeRequest.objects.filter(utr_number=utr_number).exists():
                return JsonResponse({'status': False, 'message': 'This UTR number has already been submitted'})

            first_recharge_done = WalletRechargeHistory.objects.filter(customer=customer, status='Success').exists()
            if not first_recharge_done and amount < 5000:
                return JsonResponse({'status': False, 'message': 'First recharge minimum ₹5000 required'})

            membership = (
                MembershipMaster.objects
                .filter(min_amount__lte=amount)
                .order_by('-min_amount')
                .first()
            )
            if not membership and first_recharge_done:
                wallet = CustomerWallet.objects.filter(customer=customer).first()
                membership = wallet.current_membership if wallet else None

            # save screenshot if uploaded
            screenshot_path = None
            if request.FILES.get('screenshot'):
                file_obj = request.FILES['screenshot']
                base_dir = os.path.join(settings.MEDIA_ROOT, f'manual-recharge/{customer.unique_id}/')
                os.makedirs(base_dir, exist_ok=True)
                ext = os.path.splitext(file_obj.name)[1]
                filename = f'utr_{utr_number}{ext}'
                with open(os.path.join(base_dir, filename), 'wb+') as dest:
                    for chunk in file_obj.chunks():
                        dest.write(chunk)
                screenshot_path = f'manual-recharge/{customer.unique_id}/{filename}'

            ManualRechargeRequest.objects.create(
                unique_id    = random_obj.generateUID(),
                customer     = customer,
                amount       = amount,
                utr_number   = utr_number,
                payment_mode = payment_mode,
                screenshot   = screenshot_path,
                membership   = membership,
                status       = 'PENDING',
            )

            return JsonResponse({'status': True, 'message': 'Payment submitted. Your wallet will be credited after admin verification.'})

        except Exception as e:
            return JsonResponse({'status': False, 'message': 'Something went wrong'})


class WithdrawalOperations:
    def requestWithdrawal(self, request):

        # ✅ METHOD CHECK
        if request.method != 'POST':
            return JsonResponse({'status': False, 'message': 'Invalid request method'})

        # ✅ TRADING ACCESS CHECK
        if getattr(request, 'trading_error', False):
            return JsonResponse({
                "status": False,
                "message": "Digital investment access is disabled"
            })

        customer = getattr(request, 'trading_customer', None)

        if not customer:
            return JsonResponse({
                "status": False,
                "message": "Invalid customer"
            })

        try:
            allowed, reason = is_withdrawal_window_open()
            if not allowed:
                return JsonResponse({'status': False, 'message': reason})

            if not CustomerTradingBankDetails.objects.filter(customer=customer).exists():
                return JsonResponse({'status': False, 'need_bank_details': True, 'message': 'Please submit your bank details first'})

            data = json.loads(request.body)
            amount = Decimal(str(data.get('amount', 0)))

            # ✅ BASIC VALIDATION
            if amount <= 0:
                return JsonResponse({'status': False, 'message': 'Invalid withdrawal amount'})

            if amount < Decimal('100'):
                return JsonResponse({'status': False, 'message': 'Minimum withdrawal is ₹100'})

            with transaction.atomic():

                # 🔒 LOCK WALLET
                wallet = CustomerWallet.objects.select_for_update().get(customer=customer)

                if WithdrawalRequest.objects.filter(customer=customer, status='PENDING').exists():
                    return JsonResponse({
                        'status': False,
                        'message': 'You already have a pending withdrawal request'
                    })

                # ✅ BALANCE CHECK
                if amount > wallet.balance:
                    return JsonResponse({'status': False, 'message': 'Insufficient balance'})

                # ✅ CALCULATION
                service_charge = amount * Decimal('0.01')
                gst = service_charge * Decimal('0.18')
                total_deduction = service_charge + gst
                final_amount = amount - total_deduction

                # ✅ CREATE REQUEST
                WithdrawalRequest.objects.create(
                    unique_id=random_obj.generateUID(),
                    customer=customer,
                    request_amount=amount,
                    service_charge=service_charge,
                    gst_amount=gst,
                    total_deduction=total_deduction,
                    final_amount=final_amount,
                    status='PENDING',
                    request_date=current_date
                )

                # 🔥 DEDUCT BALANCE
                wallet.balance -= amount
                wallet.save(update_fields=['balance'])

                return JsonResponse({
                    'status': True,
                    'message': 'Withdrawal request submitted successfully',
                    'wallet_balance': float(wallet.balance)
                })

        except CustomerWallet.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Wallet not found'})

        except Exception as e:
            print("Withdrawal Error:", str(e))
            return JsonResponse({'status': False, 'message': 'Something went wrong'})
        
    def getWithdrawalList(self, request):
        if request.trading_error:
            return JsonResponse({"status": False, "message": "Access denied"})

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Invalid user"})

        data = []

        try:
            withdrawals = WithdrawalRequest.objects.filter(
                customer=customer
            ).order_by('-request_date')
        except Exception:
            return JsonResponse({"status": False})

        for w in withdrawals:
            data.append({
                "amount": float(w.request_amount),
                "status": w.status,
                "status_class": w.status.lower(),
                "service_charge": float(w.service_charge),
                "gst": float(w.gst_amount),
                "final_amount": float(w.final_amount),

                "request_date_full": w.request_date.strftime("%d %b %Y, %I:%M %p"),
                "request_date": w.request_date.strftime("%d %b %Y"),

                "action_date": w.action_date.strftime("%d %b %Y") if w.action_date else None,
                "txn": w.transaction_number or "",
                "remark": w.remark or ""
            })

        return JsonResponse({"status": True, "data": data})

    def updateWithdrawalStatus(self, request):
        if request.method != 'POST':
            return JsonResponse({'success': 0, 'message': 'Invalid request method'})

        unique_id = request.POST.get('unique_id')
        status = request.POST.get('status')
        txn = request.POST.get('transaction_number')
        remark = request.POST.get('remark')

        # ✅ BASIC VALIDATION
        if not unique_id:
            return JsonResponse({'success': 0, 'message': 'Invalid withdrawal ID'})

        if status not in ["Approved", "Rejected"]:
            return JsonResponse({'success': 0, 'message': 'Invalid status'})

        try:
            with transaction.atomic():

                # 🔒 LOCK RECORD
                obj = WithdrawalRequest.objects.select_for_update().get(unique_id=unique_id)

                # ✅ STATUS CHECK
                if obj.status != 'PENDING':
                    return JsonResponse({'success': 0, 'message': 'Already processed'})

                # ✅ APPROVE FLOW
                if status == "Approved":

                    # 🔥 txn mandatory
                    if not txn or not txn.strip():
                        return JsonResponse({'success': 0, 'message': 'Transaction number required'})

                    # 🔥 length validation
                    if len(txn) < 5:
                        return JsonResponse({'success': 0, 'message': 'Invalid transaction number'})

                    # 🔥 duplicate txn prevention (important)
                    if WithdrawalRequest.objects.filter(transaction_number=txn).exclude(unique_id=unique_id).exists():
                        return JsonResponse({'success': 0, 'message': 'Transaction number already used'})

                    obj.status = 'APPROVED'
                    obj.transaction_number = txn.strip()
                    obj.remark = remark.strip() if remark else None

                # ❌ REJECT FLOW
                elif status == "Rejected":

                    # 🔥 OPTIONAL: remark mandatory (recommended)
                    if not remark or not remark.strip():
                        return JsonResponse({'success': 0, 'message': 'Remark is required for rejection'})

                    wallet = CustomerWallet.objects.select_for_update().get(customer=obj.customer)

                    # 🔥 REFUND CHECK (safety)
                    if obj.request_amount <= 0:
                        return JsonResponse({'success': 0, 'message': 'Invalid request amount'})

                    # 🔥 REFUND
                    wallet.balance += obj.request_amount
                    wallet.save(update_fields=['balance'])

                    obj.status = 'REJECTED'
                    obj.remark = remark.strip()

                # ✅ COMMON UPDATE
                obj.action_by = request.session.get('logged') or 'admin'
                obj.action_date = timezone.now()
                obj.save()

                return JsonResponse({'success': 1, 'message': f'Withdrawal {status} successfully'})

        except WithdrawalRequest.DoesNotExist:
            return JsonResponse({'success': 0, 'message': 'Withdrawal not found'})

        except CustomerWallet.DoesNotExist:
            return JsonResponse({'success': 0, 'message': 'Wallet not found'})

        except Exception as e:
            print("Withdrawal Update Error:", str(e))
            return JsonResponse({'success': 0, 'message': 'Something went wrong'})


class ManualRechargePortal:

    def manual_recharge_list_page(self, request):
        if util_obj.checkSession(request) == False:
            return render(request, 'portal/manual-recharge-requests.html')
        return util_obj.goToLogin(request)

    def get_manual_recharge_list(self, request):
        if util_obj.checkSession(request) == False:
            try:
                requests_qs = ManualRechargeRequest.objects.select_related('customer', 'membership').all()
                data = []
                for r in requests_qs:
                    data.append({
                        'id': r.id,
                        'unique_id': r.unique_id,
                        'customer_name': r.customer.name,
                        'mobile': r.customer.mobile,
                        'amount': r.amount,
                        'utr_number': r.utr_number,
                        'payment_mode': r.payment_mode,
                        'membership': r.membership.level if r.membership else '-',
                        'status': r.status,
                        'screenshot': settings.DOMAIN_NAME + 'media/' + r.screenshot if r.screenshot else '',
                        'request_date': timezone.localtime(r.request_date).strftime('%d-%m-%Y %I:%M %p'),
                        'action_date': timezone.localtime(r.action_date).strftime('%d-%m-%Y %I:%M %p') if r.action_date else '',
                        'action_by': r.action_by or '',
                        'remark': r.remark or '',
                    })
                return JsonResponse({'success': '1', 'data': data})
            except Exception:
                return JsonResponse({'success': '0', 'message': 'Something went wrong'})
        return util_obj.goToLogin(request)

    def approve_manual_recharge(self, request):
        if util_obj.checkSession(request) == False:
            if request.method != 'POST':
                return JsonResponse({'success': '0', 'message': 'Invalid request'})
            try:
                unique_id = request.POST.get('unique_id', '').strip()
                remark    = request.POST.get('remark', '').strip()
                username  = request.session.get('logged', 'admin')
                login_id  = request.session.get('login_id')

                obj = ManualRechargeRequest.objects.select_for_update().get(unique_id=unique_id)

                if obj.status != 'PENDING':
                    return JsonResponse({'success': '0', 'message': 'Already processed'})

                with transaction.atomic():
                    wallet = CustomerWallet.objects.select_for_update().get(customer=obj.customer)
                    wallet.balance += obj.amount
                    if obj.membership:
                        wallet.current_membership = obj.membership
                    wallet.save(update_fields=['balance', 'current_membership'])

                    obj.status      = 'APPROVED'
                    obj.action_by   = username
                    obj.action_date = timezone.now()
                    obj.remark      = remark
                    obj.save()

                    util_obj.activity_log(login_id, username, "Manual Recharge", f"Approved ₹{obj.amount} for {obj.customer.mobile} | UTR: {obj.utr_number}")

                return JsonResponse({'success': '1', 'message': f'₹{obj.amount} credited to wallet successfully'})

            except ManualRechargeRequest.DoesNotExist:
                return JsonResponse({'success': '0', 'message': 'Request not found'})
            except Exception as e:
                return JsonResponse({'success': '0', 'message': 'Something went wrong', 'error': str(e)})
        return util_obj.goToLogin(request)

    def reject_manual_recharge(self, request):
        if util_obj.checkSession(request) == False:
            if request.method != 'POST':
                return JsonResponse({'success': '0', 'message': 'Invalid request'})
            try:
                unique_id = request.POST.get('unique_id', '').strip()
                remark    = request.POST.get('remark', '').strip()
                username  = request.session.get('logged', 'admin')
                login_id  = request.session.get('login_id')

                if not remark:
                    return JsonResponse({'success': '0', 'message': 'Remark is required for rejection'})

                obj = ManualRechargeRequest.objects.get(unique_id=unique_id)

                if obj.status != 'PENDING':
                    return JsonResponse({'success': '0', 'message': 'Already processed'})

                obj.status      = 'REJECTED'
                obj.action_by   = username
                obj.action_date = timezone.now()
                obj.remark      = remark
                obj.save()

                util_obj.activity_log(login_id, username, "Manual Recharge", f"Rejected for {obj.customer.mobile} | UTR: {obj.utr_number} | Reason: {remark}")

                return JsonResponse({'success': '1', 'message': 'Request rejected'})

            except ManualRechargeRequest.DoesNotExist:
                return JsonResponse({'success': '0', 'message': 'Request not found'})
            except Exception:
                return JsonResponse({'success': '0', 'message': 'Something went wrong'})
        return util_obj.goToLogin(request)


class CompanyBankPortal:

    def company_bank_page(self, request):
        if util_obj.checkSession(request) == False:
            bank = CompanyBankDetails.objects.first()
            return render(request, 'portal/company-bank-details.html', {'bank': bank})
        return util_obj.goToLogin(request)

    def save_company_bank(self, request):
        if util_obj.checkSession(request) == False:
            if request.method != 'POST':
                return JsonResponse({'success': '0', 'message': 'Invalid request'})
            try:
                account_name   = request.POST.get('account_name', '').strip()
                bank_name      = request.POST.get('bank_name', '').strip()
                account_number = request.POST.get('account_number', '').strip()
                ifsc_code      = request.POST.get('ifsc_code', '').strip()
                branch_name    = request.POST.get('branch_name', '').strip()
                upi_id         = request.POST.get('upi_id', '').strip()

                if not all([account_name, bank_name, account_number, ifsc_code]):
                    return JsonResponse({'success': '0', 'message': 'Account name, bank name, account number and IFSC are required'})

                bank, created = CompanyBankDetails.objects.get_or_create(id=1)
                bank.account_name   = account_name
                bank.bank_name      = bank_name
                bank.account_number = account_number
                bank.ifsc_code      = ifsc_code
                bank.branch_name    = branch_name
                bank.upi_id         = upi_id
                bank.is_active      = True

                if request.FILES.get('qr_code_image'):
                    file_obj = request.FILES['qr_code_image']
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'company/')
                    os.makedirs(upload_dir, exist_ok=True)
                    ext = os.path.splitext(file_obj.name)[1]
                    filename = f'company_upi_qr{ext}'
                    with open(os.path.join(upload_dir, filename), 'wb+') as dest:
                        for chunk in file_obj.chunks():
                            dest.write(chunk)
                    bank.qr_code_image = f'company/{filename}'

                bank.save()

                username = request.session.get('logged', 'admin')
                login_id = request.session.get('login_id')
                util_obj.activity_log(login_id, username, "Company Bank", "Company bank details updated")

                return JsonResponse({'success': '1', 'message': 'Company bank details saved successfully'})

            except Exception as e:
                return JsonResponse({'success': '0', 'message': 'Something went wrong', 'error': str(e)})
        return util_obj.goToLogin(request)


class AddWalletBalance:

    def add_wallet_page(self, request):
        if util_obj.checkSession(request) == False:
            return render(request, 'portal/add-wallet-balance.html')
        return util_obj.goToLogin(request)

    def search_customer(self, request):
        if util_obj.checkSession(request) == False:
            mobile = request.GET.get('mobile', '').strip()
            if not mobile:
                return JsonResponse({'success': '0', 'message': 'Enter mobile number'})
            try:
                customer = Customer.objects.get(mobile=mobile, access='Granted')
                wallet   = CustomerWallet.objects.filter(customer=customer).first()
                return JsonResponse({
                    'success': '1',
                    'unique_id': customer.unique_id,
                    'name': customer.name,
                    'mobile': customer.mobile,
                    'balance': float(wallet.balance) if wallet else 0,
                })
            except Customer.DoesNotExist:
                return JsonResponse({'success': '0', 'message': 'Customer not found or blocked'})
            except Exception:
                return JsonResponse({'success': '0', 'message': 'Something went wrong'})
        return util_obj.goToLogin(request)

    def credit_wallet(self, request):
        if util_obj.checkSession(request) == False:
            if request.method != 'POST':
                return JsonResponse({'success': '0', 'message': 'Invalid request'})
            try:
                unique_id  = request.POST.get('unique_id', '').strip()
                amount     = int(request.POST.get('amount', 0))
                remark     = request.POST.get('remark', '').strip()
                utr_number = request.POST.get('utr_number', '').strip()
                username   = request.session.get('logged', 'admin')
                login_id   = request.session.get('login_id')

                if not unique_id:
                    return JsonResponse({'success': '0', 'message': 'Invalid customer'})
                if amount < 1:
                    return JsonResponse({'success': '0', 'message': 'Enter a valid amount'})
                if not remark:
                    return JsonResponse({'success': '0', 'message': 'Remark is required'})

                customer = Customer.objects.get(unique_id=unique_id, access='Granted')

                with transaction.atomic():
                    wallet = CustomerWallet.objects.select_for_update().get(customer=customer)
                    balance_before = wallet.balance
                    wallet.balance += amount
                    wallet.save(update_fields=['balance'])

                    WalletManualCredit.objects.create(
                        unique_id      = random_obj.generateUID(),
                        customer       = customer,
                        amount         = amount,
                        remark         = remark,
                        utr_number     = utr_number,
                        balance_before = balance_before,
                        balance_after  = wallet.balance,
                        credited_by    = username,
                    )

                    util_obj.activity_log(login_id, username, "Manual Wallet Credit",
                        f"Rs.{amount} credited to {customer.mobile} | UTR: {utr_number or 'N/A'} | Remark: {remark}")

                return JsonResponse({
                    'success': '1',
                    'message': f'Rs.{amount} credited successfully to {customer.name}',
                    'new_balance': float(wallet.balance),
                })

            except Customer.DoesNotExist:
                return JsonResponse({'success': '0', 'message': 'Customer not found'})
            except CustomerWallet.DoesNotExist:
                return JsonResponse({'success': '0', 'message': 'Wallet not found for this customer'})
            except Exception as e:
                return JsonResponse({'success': '0', 'message': 'Something went wrong', 'error': str(e)})
        return util_obj.goToLogin(request)

    def credit_history(self, request):
        if util_obj.checkSession(request) == False:
            try:
                mobile = request.GET.get('mobile', '').strip()
                qs = WalletManualCredit.objects.select_related('customer').all()
                if mobile:
                    qs = qs.filter(customer__mobile=mobile)
                data = []
                for c in qs[:200]:
                    data.append({
                        'date'          : timezone.localtime(c.credited_on).strftime('%d-%m-%Y %I:%M %p'),
                        'customer_name' : c.customer.name,
                        'mobile'        : c.customer.mobile,
                        'amount'        : c.amount,
                        'balance_before': float(c.balance_before),
                        'balance_after' : float(c.balance_after),
                        'utr_number'    : c.utr_number or '-',
                        'remark'        : c.remark,
                        'credited_by'   : c.credited_by,
                    })
                return JsonResponse({'success': '1', 'data': data})
            except Exception:
                return JsonResponse({'success': '0', 'message': 'Something went wrong'})
        return util_obj.goToLogin(request)