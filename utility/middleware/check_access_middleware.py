from django.shortcuts import redirect
from utility.views import Utility

# print("hello 1  → middleware file loaded")

util_obj = Utility()

# page access url name => name='image_slider'
PAGE_ACCESS = {
    'image_slider': [1, 5],
    'metal_purity_price': [1, 5],
    'unit': [1, 5],
    'category': [1, 5],
    'add_product': [1, 5],
    'update_product':[1, 5],
    'product_list': [1, 5],
    'product_stock': [1, 5],
    'stock_movement':[1, 5],
    'customer_list': [1, 4, 5],
    'customer_cart_list': [1, 5],
    'customer_order_list': [1, 5],
    'franchise_module': [1, 2, 3, 5],
    "franchise_list":[1, 2, 3, 5],
    "contact_messages":[1],
    "portal_users":[1],
    "registration_report":[1],
    "transaction_report":[1],
    "wallet_recharge_report":[1],
    "first_recharge_report":[1],
    "franchise_report":[1],
    "customer_report":[1],
    "customer_transfer_report":[1],
    "order_report":[1],
    "no_recharge_report":[1],
    "inactive_customer_report":[1],
    "withdrawal_report":[1],
}

# print("hello 2  → PAGE_ACCESS defined")

class CheckAccessMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # print("hello init → middleware initialized")

    def __call__(self, request):
        # ⚠️ yahan view info available nahi hota
        # print("hello 3  → __call__ hit")
        response = self.get_response(request)
        # print("hello 3.1 → response returned from view")
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # print("hello 4  → process_view hit")

        # 🚫 Skip trading module completely
        if request.path.startswith("/digital-investment"):
            return None

        resolver = request.resolver_match
        if not resolver:
            return None

        view_name = resolver.url_name
        # print("hello 5  → view_name =", view_name)

        # 🔹 LOGIN PAGE SKIP
        # if view_name == 'auth_login':
        if view_name not in PAGE_ACCESS:
            # print("hello 6  → login page, skipping checks")
            return None

        # 🔹 SESSION CHECK
        if util_obj.checkSession(request) == True:
            # print("hello 7  → session failed, redirecting to login")
            return util_obj.goToLogin(request)

        # print("hello 8  → session OK")

        # 🔹 ROLE CHECK
        allowed_roles = PAGE_ACCESS[view_name]
        user_role = request.session.get('role')

        # print("hello 9  → User Role:", user_role)
        # print("hello 10 → Allowed Roles:", allowed_roles)

        # if allowed_roles and user_role not in allowed_roles:
        if user_role not in allowed_roles:
            # print("hello 11 → role not allowed, redirect unauthorized")
            return redirect('unauthorized')

        # print("hello 12 → access granted")
        return None   # continue normal flow