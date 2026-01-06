MODULE_STRUCTURE = {
    "👤 Accounts": {
        "user_list": ["user_add", "user_delete"],
        "role_permission_edit": ["role_create","role_delete", "clone_role"]
    },
    "📦 Products": {
        "product_list": ["product_add", "product_edit"]
    },
    "🧾 Purchase": {
        "purchase_order_list": ["purchase_invoice_list"]
    },
    "💰 Sales": {
        "sales_order_list": ["sales_invoice_list"]
    },
    "📊 Reports": {
        "sales_report": [],
        "purchase_report": []
    },
    "⚙️ Settings": {
        "sync_modules_ajax": []
    }
}

MODULE_LAYOUT = {
    "📊 Dashboard": {
        "dashboard_view": None  # ✅ সরাসরি লিংক, sidebar-এ show হবে
    },
    "👤 Accounts": {
        "user_list": {
            "children": ["user_add", "user_edit", "user_delete"],
            "icon": "bi-people"
        },
        "role_list": {
            "children": ["role_create", "role_edit", "role_delete", "clone_role", "role_permission_edit"],
            "icon": "bi-person-badge"
        },
        "module_list": {
            "children": ["module_add", "module_edit", "module_delete", "sync_modules_ajax"],
            "icon": "bi-box"
        }
    }
}



URL_ARG_MAPPING = {
    "user_edit": "user_id",
    "user_delete": "user_id",
    "profile_view": "user_id",
    "role_permission_edit": "role_id",
    "role_edit": "role_id",
    "role_delete": "role_id",
    "clone_role": "role_id",
    "module_edit": "module_id",
    "module_delete": "module_id"
}
