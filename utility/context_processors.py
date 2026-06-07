from utility.menu_config import MENU_CONFIG
from utility.middleware.check_access_middleware import PAGE_ACCESS

def sidebar_context(request):
    role = request.session.get('role')

    if not role:
        return {"SIDEBAR": []}

    sidebar = []

    for section in MENU_CONFIG:   # ✅ list loop
        allowed_items = []

        for item in section["menu"]:
            allowed_roles = PAGE_ACCESS.get(item["view"])
            if not allowed_roles or role in allowed_roles:
                allowed_items.append(item)

        if allowed_items:
            sidebar.append({
                "icon": section.get("icon", ""),
                "name": section.get("name"),
                "menu": allowed_items
            })

    # print("sidebar", sidebar)
    return {"SIDEBAR": sidebar}