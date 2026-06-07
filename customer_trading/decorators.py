from functools import wraps
from django.shortcuts import redirect
from django.conf import settings
from django.core.cache import cache
from utility.views import CustomerUtil

cust_obj = CustomerUtil()


def _extract_request(args):
    """
    Supports both:
    - function view: (request, ...)
    - class method: (self, request, ...)
    """
    if len(args) == 0:
        return None

    # If first arg has 'META' → it's request
    if hasattr(args[0], "META"):
        return args[0]

    # Otherwise second arg should be request
    if len(args) > 1 and hasattr(args[1], "META"):
        return args[1]

    return None


def require_trading_auth(view_func):

    @wraps(view_func)
    def wrapper(*args, **kwargs):

        request = _extract_request(args)

        if not request:
            return redirect("digital_gateway")

        # print('force_logout',getattr(request, "force_logout", False))
        if getattr(request, "force_logout", False):
            return redirect("trading_logout_page")

        if getattr(request, "trading_error", None):
            return redirect("digital_gateway")

        customer = getattr(request, "trading_customer", None)

        if not customer:
            return redirect("digital_gateway")

        return view_func(*args, **kwargs)

    return wrapper


def require_trading_pin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):

        request = _extract_request(args)

        if not request:
            return redirect("digital_gateway")

        # 🔒 Middleware logout / auth error check
        # print('force_logout',getattr(request, "force_logout", False))
        if getattr(request, "force_logout", False):
            return redirect("trading_logout_page")

        if getattr(request, "trading_error", None):
            return redirect("digital_gateway")

        customer = getattr(request, "trading_customer", None)
        if not customer:
            return redirect("digital_gateway")

        pin_key = cust_obj.get_pin_cache_key(customer.id)

        # 🔐 PIN session check
        if not cache.get(pin_key):
            return redirect("digital_gateway")

        # 🔄 Sliding TTL refresh
        cache.set(pin_key, True, timeout=settings.PIN_TTL_SECONDS)

        return view_func(*args, **kwargs)

    return wrapper