from django.shortcuts import render, redirect
from customer_wallet.models import CustomerWallet, CustomerDemoWallet
from customer_transaction.models import CustomerTransaction, TransactionAutoSellHistory, CustomerDemoTransaction, DemoTransactionAutoSellHistory
from utility.views import RandomIdGenerate, current_date, Utility, CustomerUtil
import json, requests, sys
from django.http.response import JsonResponse
from rest_framework import status
from django.db import transaction
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import logging
from customer_trading.decorators import require_trading_pin, require_trading_auth
from django.utils import timezone
import datetime

def is_market_open():
    now = timezone.localtime(timezone.now())
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    current_time = now.time()
    start_time = datetime.time(9, 0, 0)
    end_time = datetime.time(23, 59, 59)
    return start_time <= current_time <= end_time

util_obj = Utility()
random_obj = RandomIdGenerate()
cust_util_obj = CustomerUtil()

def get_dollar_rate():
    from portal_misc.models import CompanyBankDetails
    try:
        bank = CompanyBankDetails.objects.first()
        if bank and bank.dollar_rate:
            return Decimal(str(bank.dollar_rate))
    except Exception:
        pass
    try:
        return Decimal(str(CompanyBankDetails._meta.get_field('dollar_rate').default))
    except Exception:
        pass
    return Decimal("83.00")


gold_weights_gm = [10, 20, 50, 100, 200, 500, 1000, 2500, 5000, 10000]
silver_weights_gm = [500, 1000, 1500, 2000, 3000, 4000, 4500, 8000, 16000]

class Pages:
    def weights(self,request,metal_type):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)

        if metal_type == "gold":
            weights = gold_weights_gm
            title = "Select Gold Quantity"
        else:
            weights = silver_weights_gm
            title = "Select Silver Quantity"

        # Build weight items with booking amount
        weight_items = []
        for gm in weights:
            if metal_type == "gold":
                booking_amt = gm * 50
            else:
                booking_amt = gm
            weight_items.append({
                "gm": gm,
                "booking_amount": f"{booking_amt:,}"
            })

        try:
            metal = getMetalRate()
            current_metal_rate = metal["buy_gold_rate"] if metal_type == 'gold' else metal["buy_silver_rate"]
            currency = metal["currency"]
        except Exception:
            return JsonResponse({
                "status": False,
                "message": "Unable to fetch gold rate"
            })

        return render(request,'digital-investment/weights.html',{'wallet_balance':wallet_balance, 'weight_items': weight_items, 'metal_type': metal_type, 'title': title, 'current_metal_rate': current_metal_rate, 'currency_icon': metal["currency_icon"]})
    
    def live_orders(self,request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)

        od_obj = OrderList()
        orders = od_obj.get_live_orders(request, customer)

        wallet_model = CustomerDemoWallet if getattr(request, "is_demo_account", False) else CustomerWallet
        wallet, _ = wallet_model.objects.get_or_create(customer=customer)
        stop_loss_percentage = wallet.stop_loss_percentage

        return render(request,'digital-investment/live-orders.html',{
            'wallet_balance': wallet_balance,
            'orders': orders,
            'stop_loss_percentage': stop_loss_percentage
        })
    
    def past_orders(self,request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)

        od_obj = OrderList()
        orders = od_obj.get_past_orders(request, customer)

        return render(request,'digital-investment/past-orders.html',{'wallet_balance':wallet_balance, 'orders':orders})
    
class TransactionBuySell:
    @require_trading_pin
    def order_calculation(self, request):
        gm = int(request.GET.get("gm", 0))
        metal_type = request.GET.get("metal_type")

        if gm <= 0:
            return JsonResponse({"status": False, "message": "Invalid gold quantity"})
        
        metal_type = metal_type.upper()
        if metal_type not in ["GOLD", "SILVER"]:
            return JsonResponse({"status": False, "message": "Invalid metal type"})

        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False,"message": "Digital investment access is disabled or invalid request"})
        
        membership = cust_util_obj.get_current_membership(customer, request)
        if not membership:
            from customer_wallet.models import MembershipMaster
            membership = MembershipMaster.objects.filter(level="Normal").first()
            if not membership:
                return JsonResponse({"status": False,"message": "Membership not found"})
        
        # try:
        calculated_data = calculate_order(gm, membership, metal_type)
        # except:
            # return JsonResponse({"status": False,"message":"Something went wrong. Please try again later."})

        return JsonResponse(calculated_data)
    
    @require_trading_pin
    def buy_metal(self, request):
        if not is_market_open():
            return JsonResponse({"status": False, "message": "Market is closed. Digital Investment is allowed from Monday to Friday, 09:00 AM to 11:59 PM."})
        try:
            data = json.loads(request.body)
            gm = int(data.get("gm", 0))
            order_type = data.get("order_type", "BOOKING")  # BUY = Booking, SELL = Buyback
            metal_type = data.get("metal_type", "GOLD")
            auto_sell_enabled = data.get("auto_sell_enabled", False)
            auto_sell_amount = data.get("auto_sell_amount")
            transaction_id = random_obj.generateUID()
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid payload"})
        
        wallet_model = CustomerDemoWallet if getattr(request, "is_demo_account", False) else CustomerWallet
        trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction
        sell_model = DemoTransactionAutoSellHistory if getattr(request, "is_demo_account", False) else TransactionAutoSellHistory

        if gm <= 0:
            return JsonResponse({"status": False, "message": "Invalid gold quantity"})
        
        if order_type not in ["BOOKING", "BUYBACK"]:
            return JsonResponse({"status": False, "message": "Invalid order type"})
        
        metal_type = metal_type.upper()
        if metal_type not in ["GOLD", "SILVER"]:
            return JsonResponse({"status": False, "message": "Invalid metal type"})
        
        # 🔹 If auto sell OFF → ignore amount
        if not auto_sell_enabled:
            auto_sell_amount = None

        # 🔹 If auto sell ON → validate amount
        if auto_sell_enabled:
            if not auto_sell_amount:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid auto sell amount"
                })

            try:
                auto_sell_amount = Decimal(auto_sell_amount)
            except:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid auto sell amount"
                })

            if auto_sell_amount <= 0:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid auto sell amount"
                })

        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Digital investment access disabled"})
        
        is_allowed, message = cust_util_obj.check_daily_transaction_limit(customer, request)
        if not is_allowed:
            return JsonResponse({"status": False,"message": message})

        try:
            wallet = wallet_model.objects.get(customer=customer)
        except wallet_model.DoesNotExist:
            return JsonResponse({"status": False, "message": "Wallet not found"})

        if not wallet.current_membership:
            return JsonResponse({"status": False, "message": "No active membership"})

        membership = wallet.current_membership

        try:
            # 🔥 LIVE RATE
            metal = getMetalRate()
            if order_type == "BOOKING":
                metal_rate = metal["buy_gold_rate"] if metal_type == 'GOLD' else metal["buy_silver_rate"]
            else:
                metal_rate = metal["sell_gold_rate"] if metal_type == 'GOLD' else metal["sell_silver_rate"]
            currency = metal["currency"]
            metal_value = metal_rate

            # 💰 CALCULATION
            calculated_data = calculate_order(gm, membership, metal_type)
            order_amt = calculated_data['order_amt']
            service_fee = calculated_data['service_fee']
            gst = calculated_data['gst']
            reward = calculated_data['reward']
            actual_service_fee = calculated_data['actual_service_fee']
            market_amount = calculated_data['market_amount']
        except Exception as e:
            logger.exception("Gold rate calculation failed:")
            return JsonResponse({"status": False,"message": "Gold rate calculation failed: " + str(e)})

        # 🔐 ATOMIC TRANSACTION
        try:
            with transaction.atomic():
                wallet = wallet_model.objects.select_for_update().get(customer=customer)

                if wallet.balance < order_amt:
                    return JsonResponse({"status": False,"message": "Insufficient wallet balance"})

                wallet.balance -= order_amt
                wallet.save(update_fields=["balance"])

                txn = trans_model.objects.create(
                    transaction_id=transaction_id,
                    customer=customer,
                    wallet=wallet,
                    membership=membership,
                    transaction_type="BUY",
                    metal_type=metal_type,
                    order_type=order_type,
                    quantity_gm=gm,
                    metal_rate_per_gm=metal_rate,
                    metal_value=metal_value,
                    currency=currency,
                    order_amount=order_amt,
                    service_fee=service_fee,
                    gst=gst,
                    reward=reward,
                    actual_service_fee=actual_service_fee,
                    market_amount=market_amount,
                    created_at=current_date,
                    auto_sell_enabled=auto_sell_enabled,
                    auto_sell_amount=auto_sell_amount,
                )

                if auto_sell_enabled and auto_sell_amount:
                    sell_model.objects.create(
                        transaction=txn,
                        old_auto_sell_amount=None,
                        new_auto_sell_amount=auto_sell_amount,
                        changed_by="CUSTOMER",
                        created_at=current_date,
                    )

        except Exception as e:
            return JsonResponse({"status": False,"message": "Transaction failed, please retry "+str(e)})

        return JsonResponse({"status": True,"message": metal_type+" purchased successfully","wallet_balance": str(wallet.balance)})
        # return render(request, "digital-investment/payment-success.html", {
        #     "amount": order_amt,
        #     "membership": wallet.current_membership.level,
        #     "transaction_id": transaction_id
        # })

    @require_trading_pin
    def sell_metal(self, request):
        try:
            data = json.loads(request.body)
            transaction_id = data.get("transaction_id")
            # metal_type = data.get("metal_type", "GOLD")
            unique_id = random_obj.generateUID()
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid payload"})
        
        trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction

        if not transaction_id:
            return JsonResponse({"status": False, "message": "Invalid request"})
        
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Digital investment access disabled"})
        
        is_allowed, message = cust_util_obj.check_daily_transaction_limit(customer, request)
        if not is_allowed:
            return JsonResponse({"status": False,"message": message})

        try:
            buy_txn = trans_model.objects.get(
                transaction_id=transaction_id,
                customer=customer,
                transaction_type="BUY"
            )

            # print('metal_type :: ',buy_txn.metal_type)
        
            metal_type = buy_txn.metal_type.upper()
            if metal_type not in ["GOLD", "SILVER"]:
                return JsonResponse({"status": False, "message": "Invalid metal type"})

            # 🔥 Live rate
            metal = getMetalRate()
            if buy_txn.order_type == "BOOKING":
                current_metal_rate = metal["sell_gold_rate"] if metal_type == 'GOLD' else metal["sell_silver_rate"]
            else:
                current_metal_rate = metal["buy_gold_rate"] if metal_type == 'GOLD' else metal["buy_silver_rate"]
            # print('current_metal_rate :: ',current_metal_rate)
            # current_metal_rate = Decimal(158.04)

            result = execute_sell(request, buy_txn=buy_txn,current_metal_rate=current_metal_rate,sold_via="MANUAL")

            if not result:
                return JsonResponse({"status": False, "message": "Already sold"})
  
        except trans_model.DoesNotExist:
            return JsonResponse({"status": False, "message": "Order not found"})

        except Exception as e:
            logger.exception("Sell failed exception:")
            return JsonResponse({"status": False, "message": "Sell failed: " + str(e)})

        return JsonResponse({
            "status": True,
            "wallet_balance": str(result["wallet_balance"]),
            "pnl_amount": str(result["pnl"]["pnl_amount"]),
            "pnl_percent": str(result["pnl"]["pnl_percent"]),
            "order_type": buy_txn.order_type
        })

    @require_trading_pin
    def update_auto_sell(self, request):
        try:
            data = json.loads(request.body)
            transaction_id = data.get("transaction_id")
            auto_sell_enabled = data.get("auto_sell_enabled", False)
            auto_sell_amount = data.get("auto_sell_amount")
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid payload"})
        
        trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction
        sell_model = DemoTransactionAutoSellHistory if getattr(request, "is_demo_account", False) else TransactionAutoSellHistory

        # 🔹 If auto sell OFF → ignore amount
        if not auto_sell_enabled:
            auto_sell_amount = None

        # 🔹 If auto sell ON → validate amount
        if auto_sell_enabled:
            if not auto_sell_amount:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid auto sell amount"
                })

            try:
                auto_sell_amount = Decimal(auto_sell_amount)
            except:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid auto sell amount"
                })

            if auto_sell_amount <= 0:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid auto sell amount"
                })

        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Digital investment access disabled"})

        try:
            with transaction.atomic():

                txn = (
                    trans_model.objects
                    .select_for_update()
                    .get(
                        customer=customer,
                        transaction_id=transaction_id,
                        transaction_type="BUY"
                    )
                )

                old_value = txn.auto_sell_amount

                txn.auto_sell_enabled = auto_sell_enabled
                txn.auto_sell_amount = auto_sell_amount
                txn.save(update_fields=["auto_sell_enabled", "auto_sell_amount"])

                # 📜 HISTORY – sirf jab auto sell enabled ho
                if auto_sell_enabled:
                    sell_model.objects.create(
                        transaction=txn,
                        old_auto_sell_amount=old_value,
                        new_auto_sell_amount=auto_sell_amount,
                        changed_by="CUSTOMER",
                        created_at=current_date
                    )

        except trans_model.DoesNotExist:
            return JsonResponse({"status": False, "message": "Order not found"})

        except Exception:
            return JsonResponse({"status": False, "message": "Unable to update auto sell"})

        return JsonResponse({"status": True, "message": "Auto sell updated"})

class OrderList:
    def get_live_orders(self, request, customer):
        orders = get_active_live_orders(request, customer)

        data = []
        for o in orders:
            buy_rate = o.metal_rate_per_gm
            if getattr(o, 'currency', 'INR') == 'USD':
                usd_to_inr = get_dollar_rate()
                buy_rate = (buy_rate / Decimal("31.1034768")) * usd_to_inr
            buy_metal_value = (buy_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

            data.append({
                "transaction_id": o.transaction_id,
                "card_icon": o.metal_type.lower(),
                "metal_type": o.metal_type,
                "quantity": o.quantity_gm,
                "buy_price": str(buy_metal_value),
                "invested_price": str(o.order_amount),
                "date": timezone.localtime(o.created_at).strftime("%d %b %Y • %I:%M %p"),
                "order_type": o.order_type,
            })

        return data
    
    def live_orders_pnl(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Digital investment access disabled"})

        orders = get_active_live_orders(request, customer)

        try:
            metal = getMetalRate()
        except Exception:
            return JsonResponse({"status": False, "message": "Unable to fetch gold rate"})

        data = []
        for o in orders:
            try:
                if o.order_type == "BOOKING":
                    current_metal_rate = metal["sell_gold_rate"] if o.metal_type == 'GOLD' else metal["sell_silver_rate"]
                else:
                    current_metal_rate = metal["buy_gold_rate"] if o.metal_type == 'GOLD' else metal["buy_silver_rate"]
            except Exception:
                return JsonResponse({"status": False, "message": "Unable to fetch gold rate"})
    
            pnl = calculate_live_pnl(o, current_metal_rate)
            
            market_open = is_market_open()
            status_label = "<span style='color: green; font-weight: bold;'>Market Open</span>" if market_open else "<span style='color: red; font-weight: bold;'>Market Closed</span>"
            date_time_str = timezone.localtime(timezone.now()).strftime("%d %b %Y • %I:%M:%S %p")
            date_time_str = f"{date_time_str} • {status_label}"
 
            data.append({
                "transaction_id": o.transaction_id,
                "current_price": str(pnl["sell_metal_value"]),
                "pnl_amount": str(pnl["pnl_amount"]),
                "pnl_percent": str(pnl["pnl_percent"]),
                "is_profit": pnl["is_profit"],
                "difference": pnl["difference"],
                "date_time": date_time_str,
            })

        return JsonResponse({"status": True, "orders": data})

    def live_order_details(self, request):
        transaction_id = request.GET.get("transaction_id")

        if not transaction_id:
            return JsonResponse({
                "status": False,
                "message": "Invalid request"
            })

        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Digital investment access disabled"})

        # 🔍 Fetch order (ONLY live BUY order)
        try:
            order = (get_active_live_orders(request, customer).get(transaction_id=transaction_id))
        except:
            return JsonResponse({
                "status": False,
                "message": "Order not found or already sold"
            })

        # 📈 Current metal rate
        try:
            metal = getMetalRate()
            if order.order_type == "BOOKING":
                current_metal_rate = metal["sell_gold_rate"] if order.metal_type == 'GOLD' else metal["sell_silver_rate"]
            else:
                current_metal_rate = metal["buy_gold_rate"] if order.metal_type == 'GOLD' else metal["buy_silver_rate"]
            currency_icon = metal["currency_icon"]
        except Exception:
            return JsonResponse({
                "status": False,
                "message": "Unable to fetch gold rate"
            })

        # 🧮 PNL calculation
        pnl = calculate_live_pnl(order, current_metal_rate)

        return JsonResponse({
            "status": True,
            "transaction_id": order.transaction_id,
            "metal_type": order.metal_type,
            "quantity": order.quantity_gm,

            # BUY SIDE
            "buy_rate": str(pnl["buy_metal_value"]),
            "buy_date": timezone.localtime(order.created_at).strftime("%d %b %Y • %I:%M %p"),
            "invested_amount": str(order.order_amount),
            "market_amount": str(order.market_amount),
            "service_fee": str(order.service_fee),

            # CURRENT
            "current_metal_rate": str(pnl["sell_metal_value"]),
            "current_value": str(pnl["current_value"]),

            # PNL
            "pnl_amount": str(pnl["pnl_amount"]),
            "pnl_percent": str(pnl["pnl_percent"]),
            "is_profit": pnl["is_profit"],
            "difference": pnl["difference"],

            # META
            "membership": order.membership.level,
            "currency_icon": currency_icon,
            "order_type": order.order_type,

            "auto_sell_enabled": bool(order.auto_sell_enabled),
            "auto_sell_amount": order.auto_sell_amount,
        })

    def get_past_orders(self, request, customer):
        trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction
        sell_relation = "demo_sell_transactions" if getattr(request, "is_demo_account", False) else "sell_transactions"

        orders = (
            trans_model.objects.filter(
                customer=customer,
                transaction_type="BUY",
                # metal_type="GOLD"
            )
            # .filter(sell_relation__isnull=False)
            .filter(**{f"{sell_relation}__isnull": False})
            .exclude(auto_closed_weekly=True)
            .prefetch_related(sell_relation)
            .order_by("-created_at")
        )

        data = []

        for buy in orders:
            sell = getattr(buy, sell_relation).first()

            buy_rate = buy.metal_rate_per_gm
            if getattr(buy, 'currency', 'INR') == 'USD':
                usd_to_inr = get_dollar_rate()
                buy_rate = (buy_rate / Decimal("31.1034768")) * usd_to_inr
            buy_metal_value = (buy_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

            sell_rate = sell.metal_rate_per_gm
            if getattr(sell, 'currency', 'INR') == 'USD':
                usd_to_inr = get_dollar_rate()
                sell_rate = (sell_rate / Decimal("31.1034768")) * usd_to_inr
            sell_metal_value = (sell_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

            data.append({
                "transaction_id": buy.transaction_id,
                "card_icon": buy.metal_type.lower(),
                "metal_type": buy.metal_type,
                "quantity": buy.quantity_gm,
                "profit_loss": sell.profit_loss,
                "profit_loss_icon": sell.profit_loss.lower(),
                "buy_price": str(buy_metal_value),
                "sell_price": str(sell_metal_value),
                "pnl_amount": str(abs(sell.profit_loss_amount)),
                "invested_price": str(buy.order_amount),
                "sell_date": timezone.localtime(sell.created_at).strftime("%d %b %Y • %I:%M %p"),
                "is_profit": sell.profit_loss == "PROFIT",
                "order_type": buy.order_type,
            })

        return data

    def past_order_details(self, request):
        trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction
        transaction_id = request.GET.get("transaction_id")
        sell_relation = "demo_sell_transactions" if getattr(request, "is_demo_account", False) else "sell_transactions"

        if not transaction_id:
            return JsonResponse({
                "status": False,
                "message": "Invalid request"
            })

        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return JsonResponse({"status": False, "message": "Digital investment access disabled"})

        # 🔍 Fetch order (ONLY live BUY order)
        try:
            buy = trans_model.objects.get(customer=customer,transaction_id=transaction_id,transaction_type="BUY", auto_closed_weekly=False)
        except trans_model.DoesNotExist:
            return JsonResponse({
                "status": False,
                "message": "Transaction not found"
            })
        
        sell = getattr(buy, sell_relation).first()
        if not sell:
            return JsonResponse({
                "status": False,
                "message": "Sell transaction not found"
            })
        
        currency_icon = '$' if sell.currency == 'USD' else '₹'

        return JsonResponse({
            "status": True,

            # BASIC
            "metal_type": buy.metal_type,
            "quantity": buy.quantity_gm,

            # BUY
            "buy_rate": str(buy.metal_value),
            "invested_amount": str(buy.order_amount),
            "market_amount": str(buy.market_amount),
            "service_fee": str(buy.service_fee),
            "buy_date": timezone.localtime(buy.created_at).strftime("%d %b %Y • %I:%M %p"),

            # SELL
            "sell_rate": str(sell.metal_value),
            "sell_amount": str(sell.market_amount),
            "sell_date": timezone.localtime(sell.created_at).strftime("%d %b %Y • %I:%M %p"),

            # PNL
            "pnl_amount": str(sell.profit_loss_amount),
            "pnl_percent": str(sell.profit_loss_percent),
            "is_profit": sell.profit_loss == "PROFIT",
            "currency_icon": currency_icon,
            "order_type": buy.order_type,

            "is_auto_sold": sell.sold_via == "AUTO",
            "auto_sell_amount": buy.auto_sell_amount,
            "sold_via": sell.sold_via
        })

logger = logging.getLogger(__name__)

METAL_RATE_CACHE_KEY = "last_metal_rates_v2"

def getMetalRate():
    """
    Fetches live gold and silver mid-prices from the Tradefeeds API.
    Endpoint: GET https://data.tradefeeds.com/api/v1/commodity_prices
    Params:   key=<METAL_API_KEY>, name=gold|silver
    Response: result.output[0].price  (USD per troy ounce, mid-price)

    Market-closed behavior:
    - When market is closed, returns the last cached rates (frozen at market close).
    - When market is open, fetches fresh rates and updates the cache.
    - This prevents artificial PnL fluctuations after trading hours.

    Spread is applied symmetrically around mid-price:
        buy_rate  = mid_price - spread
        sell_rate = mid_price + spread
    """
    from django.core.cache import cache
    # --- Cooldown check: if rates were fetched less than 1 second ago, return cache ---
    # This protects the Tradefeeds API from rate-limiting when clients poll at 0-1 seconds.
    cooldown = cache.get("live_metal_rates_cooldown")
    if cooldown:
        cached_rates = cache.get(METAL_RATE_CACHE_KEY)
        if cached_rates:
            try:
                return {
                    "buy_gold_rate":    Decimal(str(cached_rates["buy_gold_rate"])),
                    "sell_gold_rate":   Decimal(str(cached_rates["sell_gold_rate"])),
                    "buy_silver_rate":  Decimal(str(cached_rates["buy_silver_rate"])),
                    "sell_silver_rate": Decimal(str(cached_rates["sell_silver_rate"])),
                    "spread":           Decimal(str(cached_rates["spread"])),
                    "currency":         cached_rates["currency"],
                    "currency_icon":    cached_rates["currency_icon"]
                }
            except Exception as e:
                logger.error(f"Error parsing cooldown cached rates: {e}")

    # --- Market closed: return frozen rates from cache ---
    if not is_market_open():
        cached_rates = cache.get(METAL_RATE_CACHE_KEY)
        if cached_rates:
            try:
                logger.info("Market closed — returning cached metal rates (frozen at last market close).")
                return {
                    "buy_gold_rate":    Decimal(str(cached_rates["buy_gold_rate"])),
                    "sell_gold_rate":   Decimal(str(cached_rates["sell_gold_rate"])),
                    "buy_silver_rate":  Decimal(str(cached_rates["buy_silver_rate"])),
                    "sell_silver_rate": Decimal(str(cached_rates["sell_silver_rate"])),
                    "spread":           Decimal(str(cached_rates["spread"])),
                    "currency":         cached_rates["currency"],
                    "currency_icon":    cached_rates["currency_icon"]
                }
            except Exception as e:
                logger.error(f"Error parsing cached rates: {e}")
        # No cache yet (e.g. first server start after a weekend) — fall through to fetch once
        logger.warning("Market closed but no cached rates found — fetching once to populate cache.")

    BASE_URL = "https://data.tradefeeds.com/api/v1/commodity_prices"
    api_key = settings.METAL_API_KEY

    try:
        # --- Fetch Gold ---
        gold_resp = requests.get(
            BASE_URL,
            params={"key": api_key, "name": "gold"},
            timeout=10
        )
        gold_resp.raise_for_status()
        gold_data = gold_resp.json()

        gold_output = gold_data.get("result", {}).get("output", [])
        if not gold_output:
            raise ValueError(f"Tradefeeds: gold output missing. API Response: {gold_data}")
        gold_price_usd = Decimal(str(gold_output[0]["price"]))

        # --- Fetch Silver ---
        silver_resp = requests.get(
            BASE_URL,
            params={"key": api_key, "name": "silver"},
            timeout=10
        )
        silver_resp.raise_for_status()
        silver_data = silver_resp.json()

        silver_output = silver_data.get("result", {}).get("output", [])
        if not silver_output:
            raise ValueError(f"Tradefeeds: silver output missing. API Response: {silver_data}")
        silver_price_usd = Decimal(str(silver_output[0]["price"]))

        # --- Currency conversion ---
        usd_to_inr = get_dollar_rate()

        # Tradefeeds returns USD per troy ounce (same unit as freegoldprice.org)
        # Convert: USD/troy_oz ÷ 31.1034768 g/troy_oz = USD/gram
        # Then:    USD/gram × INR/USD = INR/gram
        ounce_weight = Decimal("31.1034768")

        gold_mid_per_gm   = gold_price_usd / ounce_weight
        silver_mid_per_gm = silver_price_usd / ounce_weight

        # Raw INR price per gram (unscaled)
        gold_raw_inr   = gold_mid_per_gm * usd_to_inr
        silver_raw_inr = silver_mid_per_gm * usd_to_inr

        # --- Fetch all config from DB in one call ---
        from portal_misc.models import CompanyBankDetails
        bank = CompanyBankDetails.objects.first()
        if not bank:
            raise Exception("CompanyBankDetails record not found. Please configure it in admin.")

        spread_points = Decimal(str(bank.spread)) if bank.spread is not None else Decimal("200")

        # BASE_GOLD_PRICE: anchor INR/gm around which scaling is applied.
        # Auto-calibrated from live price on first call — no manual admin input needed.
        if bank.base_gold_price is None:
            bank.base_gold_price = gold_raw_inr.quantize(Decimal("0.00"))
            bank.save(update_fields=["base_gold_price"])
        BASE_GOLD_PRICE = Decimal(str(bank.base_gold_price))

        # SCALE = ounce_weight / usd_to_inr
        # Ensures exactly 1 INR/gm change per $1/oz move in gold price,
        # regardless of the current USD/INR exchange rate.
        # Proof: raw change = $1/31.1g × usd_to_inr ≈ 3.06 INR/gm
        #        × SCALE (31.1/usd_to_inr) → = 1 INR/gm ✓
        SCALE = ounce_weight / usd_to_inr

        # Scale gold around anchor: only the DEVIATION from anchor is compressed
        gold_mid_inr   = BASE_GOLD_PRICE + ((gold_raw_inr - BASE_GOLD_PRICE) * SCALE)

        # Scale silver: keeps the raw INR/gm rate (no gold compression scale)
        silver_mid_inr = silver_raw_inr

        currency = 'INR'
        currency_icon = '₹'

        # Spread: also scaled so 1 USD/oz spread ≈ 1 INR/gm impact (not 3 INR/gm)
        spread_in_inr_gold = ((spread_points / ounce_weight) * usd_to_inr) * SCALE

        # Scale silver spread proportionally to gold/silver price ratio
        ratio = gold_mid_per_gm / silver_mid_per_gm if silver_mid_per_gm > 0 else Decimal("65")
        spread_in_inr_silver = spread_in_inr_gold / ratio


        # --- Final buy/sell rates (spread applied symmetrically around mid-price) ---
        buy_gold_rate    = gold_mid_inr - spread_in_inr_gold
        sell_gold_rate   = gold_mid_inr + spread_in_inr_gold
        buy_silver_rate  = silver_mid_inr - spread_in_inr_silver
        sell_silver_rate = silver_mid_inr + spread_in_inr_silver

        # --- Logging ---
        log_msg = (
            f"\n========================================\n"
            f"METAL RATE API CONVERSION LOGS (Tradefeeds - troy ounce):\n"
            f"Raw API Gold Mid:   {gold_price_usd} USD/troy oz\n"
            f"Raw API Silver Mid: {silver_price_usd} USD/troy oz\n"
            f"Exchange Rate (usd_to_inr): {usd_to_inr}\n"
            f"Spread Points (from DB): {spread_points} USD/oz\n"
            f"----------------------------------------\n"
            f"Conversion to USD/gm (÷ {ounce_weight} g/troy oz):\n"
            f"Gold Mid:   {gold_mid_per_gm} USD/gm\n"
            f"Silver Mid: {silver_mid_per_gm} USD/gm\n"
            f"----------------------------------------\n"
            f"Conversion to INR/gm (* {usd_to_inr}):\n"
            f"Gold Mid INR:   {gold_mid_inr} INR/gm\n"
            f"Silver Mid INR: {silver_mid_inr} INR/gm\n"
            f"----------------------------------------\n"
            f"Spread in INR per gram (symmetric):\n"
            f"Gold Spread:   {spread_in_inr_gold} INR/gm\n"
            f"Silver Spread: {spread_in_inr_silver} INR/gm\n"
            f"----------------------------------------\n"
            f"Final Rates after Spread:\n"
            f"Buy Gold Rate:    {buy_gold_rate} INR/gm\n"
            f"Sell Gold Rate:   {sell_gold_rate} INR/gm\n"
            f"Buy Silver Rate:  {buy_silver_rate} INR/gm\n"
            f"Sell Silver Rate: {sell_silver_rate} INR/gm\n"
            f"========================================\n"
        )
        logger.info(log_msg)
        print(log_msg)
        sys.stdout.flush()

        rates = {
            "buy_gold_rate":    buy_gold_rate.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP),
            "sell_gold_rate":   sell_gold_rate.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP),
            "buy_silver_rate":  buy_silver_rate.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP),
            "sell_silver_rate": sell_silver_rate.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP),
            "spread": spread_points,
            "currency": currency,
            "currency_icon": currency_icon
        }

        # Save to cache as strings (ensures JSON/Redis/Memcached serializability)
        from django.core.cache import cache
        try:
            cache_rates = {
                "buy_gold_rate":    str(rates["buy_gold_rate"]),
                "sell_gold_rate":   str(rates["sell_gold_rate"]),
                "buy_silver_rate":  str(rates["buy_silver_rate"]),
                "sell_silver_rate": str(rates["sell_silver_rate"]),
                "spread":           str(rates["spread"]),
                "currency":         rates["currency"],
                "currency_icon":    rates["currency_icon"]
            }
            cache.set(METAL_RATE_CACHE_KEY, cache_rates, timeout=None)
            cache.set("live_metal_rates_cooldown", True, timeout=1)
        except Exception as e:
            logger.error(f"Error caching metal rates: {e}")

        return rates

    except Exception as e:
        logger.error(f"Metal rate fetch failed: {e}")
        # Try returning last cached rates as fallback (better than crashing)
        from django.core.cache import cache
        try:
            cached_rates = cache.get(METAL_RATE_CACHE_KEY)
            if cached_rates:
                logger.warning("API failed — returning last cached metal rates as fallback.")
                return {
                    "buy_gold_rate":    Decimal(str(cached_rates["buy_gold_rate"])),
                    "sell_gold_rate":   Decimal(str(cached_rates["sell_gold_rate"])),
                    "buy_silver_rate":  Decimal(str(cached_rates["buy_silver_rate"])),
                    "sell_silver_rate": Decimal(str(cached_rates["sell_silver_rate"])),
                    "spread":           Decimal(str(cached_rates["spread"])),
                    "currency":         cached_rates["currency"],
                    "currency_icon":    cached_rates["currency_icon"]
                }
        except Exception as cache_err:
            logger.error(f"Error retrieving cached rates in fallback: {cache_err}")
        raise Exception(f"Unable to fetch metal rates: {e}")


    
def getMetalData(request):
    try:
        metal = getMetalRate()
        current_gold_rate = metal["buy_gold_rate"]
        current_silver_rate = metal["buy_silver_rate"]
        currency_icon = metal["currency_icon"]
    except Exception:
        return JsonResponse({
            "status": False,
            "message": "Unable to fetch gold rate"
        })   
    
    market_open = is_market_open()
    status_label = "<span style='color: green; font-weight: bold;'>Market Open</span>" if market_open else "<span style='color: red; font-weight: bold;'>Market Closed</span>"
    date_time_str = timezone.localtime(timezone.now()).strftime("%d %b %Y • %I:%M:%S %p")
    
    return JsonResponse({
        "current_gold_rate": current_gold_rate,
        "current_silver_rate": current_silver_rate,
        "currency_icon": currency_icon,
        "date_time": f"{date_time_str} • {status_label}",
    })

# rates = getMetalRate()
# buy_rate  = rates["buy_gold_rate"]   # BUY time use
# sell_rate = rates["sell_gold_rate"]  # SELL time use
# print(buy_rate)
# print(sell_rate)

def calculate_order(gm, membership, metal_type):
    order_amt = Decimal(gm) * 50 if metal_type == 'GOLD' else Decimal(gm)
    
    # Base fee is 10% of order amount
    base_fee = (order_amt * Decimal('0.10')).quantize(Decimal("0"), rounding=ROUND_HALF_UP)
    
    # Discount based on membership level (membership.service_fee per 10gm)
    discount = Decimal('50') - Decimal(membership.service_fee)
    service_fee = base_fee - discount
    
    # Rewards calculation
    if membership.level == 'Normal':
        reward = (service_fee * Decimal('0.10')).quantize(Decimal("0"), rounding=ROUND_HALF_UP)
    else:
        reward = (order_amt * Decimal('0.01')).quantize(Decimal("0"), rounding=ROUND_HALF_UP)
        
    # GST calculation (18% on service fee)
    gst = (service_fee * Decimal("0.18")).quantize(Decimal("0"), rounding=ROUND_HALF_UP)
    
    # Actual service fee calculation
    actual_service_fee = (service_fee - (gst + reward)).quantize(Decimal("0"), rounding=ROUND_HALF_UP)
    
    # Market amount
    market_amount = (order_amt - service_fee).quantize(Decimal("0"), rounding=ROUND_HALF_UP)

    spread_val = 200
    try:
        from portal_misc.models import CompanyBankDetails
        bank = CompanyBankDetails.objects.first()
        if bank and bank.spread is not None:
            spread_val = bank.spread
    except Exception:
        pass

    return {
        "status": True,
        "order_amt": order_amt,
        "service_fee": service_fee,
        "market_amount": market_amount,
        "gst": gst,
        "reward": reward,
        "actual_service_fee": actual_service_fee,
        "spread": str(spread_val),
    }

def get_active_live_orders(request, customer, metal_type="GOLD"):
    trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction
    sell_relation = "demo_sell_transactions" if getattr(request, "is_demo_account", False) else "sell_transactions"
    
    return (
        trans_model.objects
        .filter(
            customer=customer,
            transaction_type="BUY",
            # metal_type=metal_type
        )
        # .exclude(sell_transactions__isnull=False)
        .exclude(**{f"{sell_relation}__isnull": False})
        .exclude(auto_closed_weekly=True)
        .order_by("-created_at")
    )

# def calculate_live_pnl(order, current_metal_rate):
#     buy_metal_value = (Decimal(order.quantity_gm) * order.metal_rate_per_gm).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
#     sell_metal_value = (Decimal(order.quantity_gm) * current_metal_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

#     # 🔁 Direction depends on order type
#     if order.order_type == "BOOKING":          # BOOKING
#         diff = sell_metal_value - buy_metal_value
#     else:                                      # BUYBACK
#         diff = buy_metal_value - sell_metal_value

#     pnl_percent = Decimal("0.0")
#     if buy_metal_value > 0:
#         # pnl_percent = ((sell_metal_value - buy_metal_value) / buy_metal_value * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

#         pnl_percent = (diff / buy_metal_value * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

#     pnl_amount = (order.market_amount * pnl_percent / Decimal("100")).quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)

#     current_value = (order.market_amount + pnl_amount).quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)

#     return {
#         "current_value": current_value,
#         "pnl_amount": pnl_amount,
#         "pnl_percent": pnl_percent,
#         "is_profit": pnl_amount >= 0,
#         'buy_metal_value':buy_metal_value,
#         'sell_metal_value':sell_metal_value
#     }

def calculate_live_pnl(order, current_metal_rate):
    buy_rate = order.metal_rate_per_gm
    if getattr(order, 'currency', 'INR') == 'USD':
        usd_to_inr = get_dollar_rate()
        buy_rate = (buy_rate / Decimal("31.1034768")) * usd_to_inr

    buy_metal_value = (buy_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
    sell_metal_value = (current_metal_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    # 🔁 Direction depends on order type
    if order.order_type == "BOOKING":          # BOOKING
        diff = sell_metal_value - buy_metal_value
    else:                                      # BUYBACK
        diff = buy_metal_value - sell_metal_value

    pnl_amount = (order.quantity_gm * diff).quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)

    pnl_percent = Decimal("0.0")
    if buy_metal_value > 0 and order.market_amount > 0:
        pnl_percent = (pnl_amount / order.market_amount * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if pnl_percent > Decimal("9999.99"):
            pnl_percent = Decimal("9999.99")
        elif pnl_percent < Decimal("-9999.99"):
            pnl_percent = Decimal("-9999.99")

    # print("diff::",diff)
    # print("pnl_amount::",pnl_amount)
    # print("pnl_percent::",pnl_percent)

    current_value = (order.market_amount + pnl_amount).quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)
    if current_value < Decimal("0.0"):
        current_value = Decimal("0.0")
        pnl_amount = -order.market_amount
        pnl_percent = Decimal("-100.00")

    return {
        "current_value": current_value,
        "pnl_amount": pnl_amount,
        "pnl_percent": pnl_percent,
        "is_profit": pnl_amount >= 0,
        'buy_metal_value':buy_metal_value,
        'sell_metal_value':sell_metal_value,
        'difference': diff
    }

def execute_sell(request,buy_txn,current_metal_rate,sold_via="MANUAL"):
    is_demo = getattr(request, "is_demo_account", False) if request else False
    trans_model = CustomerDemoTransaction if is_demo else CustomerTransaction
    wallet_model = CustomerDemoWallet if is_demo else CustomerWallet
    sell_relation = "demo_sell_transactions" if is_demo else "sell_transactions"

    with transaction.atomic():
        buy_txn = (trans_model.objects.select_for_update().get(id=buy_txn.id))

        if getattr(buy_txn, sell_relation).exists():
            return None  # already sold

        pnl = calculate_live_pnl(buy_txn, current_metal_rate)

        wallet = (wallet_model.objects.select_for_update().get(customer=buy_txn.customer))

        wallet.balance += pnl["current_value"]
        wallet.save(update_fields=["balance"])

        # metal_value = (Decimal(buy_txn.quantity_gm) * current_metal_rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
        metal_value = current_metal_rate

        sell_txn = trans_model.objects.create(
            transaction_id=random_obj.generateUID(),
            customer=buy_txn.customer,
            wallet=wallet,
            membership=buy_txn.membership,

            transaction_type="SELL",
            order_type=buy_txn.order_type,
            metal_type=buy_txn.metal_type,

            quantity_gm=buy_txn.quantity_gm,
            metal_rate_per_gm=current_metal_rate,
            metal_value=metal_value,
            currency=buy_txn.currency,

            order_amount=pnl["current_value"],
            market_amount=pnl["current_value"],

            service_fee=Decimal("0"),
            gst=Decimal("0"),
            reward=Decimal("0"),
            actual_service_fee=Decimal("0"),

            parent_buy=buy_txn,

            profit_loss="PROFIT" if pnl["pnl_amount"] >= 0 else "LOSS",
            profit_loss_amount=pnl["pnl_amount"],
            profit_loss_percent=pnl["pnl_percent"],

            sold_via=sold_via,
            created_at=current_date,
            auto_closed_weekly=(sold_via == "WEEKLY_AUTO_CLOSE"),
        )

        # 🔥 auto sell ke case me disable
        if sold_via == "AUTO":
            buy_txn.auto_sell_enabled = False
            buy_txn.save(update_fields=["auto_sell_enabled"])
        elif sold_via == "WEEKLY_AUTO_CLOSE":
            buy_txn.auto_sell_enabled = False
            buy_txn.auto_closed_weekly = True
            buy_txn.save(update_fields=["auto_sell_enabled", "auto_closed_weekly"])

        return {
            "sell_txn": sell_txn,
            "wallet_balance": wallet.balance,
            "pnl": pnl
        }