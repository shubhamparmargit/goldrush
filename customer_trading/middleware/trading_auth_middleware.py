from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from utility.views import CustomerUtil
from django.core.cache import cache
from django.db.models import Sum
from django.conf import settings

cust_util_obj = CustomerUtil()

class TradingAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):

        request.trading_customer = None
        request.validated_token = None
        request.trading_error = None
        request.new_access_token = None
        request.force_logout = False
        request.is_demo_account = False
        request.reward_points = 0

        # Apply only to trading URLs
        # Skip authentication for bridge route
        if "bridge" in request.path:
            return None

        # Apply only to protected trading pages
        if "digital-investment" not in request.path:
            return None

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        # If both missing → no session
        if not access_token and not refresh_token:
            request.trading_error = "Authentication required."
            request.force_logout = True
            return None

        jwt_auth = JWTAuthentication()

        # 🔹 1️⃣ Try Access Token
        if access_token:
            try:
                validated_token = jwt_auth.get_validated_token(access_token)

                if not validated_token.get("trading_access"):
                    request.trading_error = "Trading access denied."
                    request.force_logout = True
                    return None
                
                if cache.get(f"JWT_LOGOUT:{validated_token.get('jti')}"):
                    request.trading_error = "Session expired"
                    request.force_logout = True
                    return None

                customer_uid = validated_token.get("customer_uid")
                trading_account = cust_util_obj.get_valid_trading_customer(customer_uid)
                customer = trading_account.customer

                if not customer:
                    request.trading_error = "Access revoked."
                    request.force_logout = True
                    return None
                
                if validated_token.get("device_id") != customer.unique_application_id:
                    request.trading_error = "Device mismatch."
                    request.force_logout = True
                    return None

                request.trading_customer = customer
                request.validated_token = validated_token
                request.is_demo_account = (trading_account.account_type == "DEMO")
                request.reward_points = self._get_reward_points(customer)
                return None

            except AuthenticationFailed:
                pass  # Try refresh


        # 🔹 2️⃣ Try Refresh Token
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)

                if not refresh.get("trading_access"):
                    request.trading_error = "Trading access denied."
                    request.force_logout = True
                    return None

                customer_uid = refresh.get("customer_uid")
                trading_account = cust_util_obj.get_valid_trading_customer(customer_uid)
                customer = trading_account.customer

                if not customer:
                    request.trading_error = "Access revoked."
                    request.force_logout = True
                    return None

                new_access_token = str(refresh.access_token)
                validated_token = jwt_auth.get_validated_token(new_access_token)

                request.trading_customer = customer
                request.validated_token = validated_token
                request.new_access_token = new_access_token
                request.is_demo_account = (trading_account.account_type == "DEMO")
                request.reward_points = self._get_reward_points(customer)
                return None

            except Exception:
                request.trading_error = "Session expired. Please login again."
                request.force_logout = True
                return None

        request.trading_error = "Authentication failed."
        request.force_logout = True
        return None


    def _get_reward_points(self, customer):
        cache_key = f"REWARD_PTS:{customer.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            from customer_transaction.models import CustomerTransaction
            total = CustomerTransaction.objects.filter(
                customer=customer
            ).aggregate(total=Sum('reward'))['total'] or 0
            points = int(total)
            cache.set(cache_key, points, timeout=120)
            return points
        except Exception:
            return 0

    def process_response(self, request, response):

        new_access_token = getattr(request, "new_access_token", None)

        if new_access_token:
            response.set_cookie(
                "access_token",
                new_access_token,
                httponly=True,
                secure=not settings.DEBUG,  # Enable in HTTPS production
                samesite='Strict',
                max_age=900
            )

        # 🔥 FORCE LOGOUT
        if getattr(request, "force_logout", False):
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

        if "digital-investment" in request.path:
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        return response