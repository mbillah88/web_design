SUPERADMIN_MODULES = [
    'user_list', 'user_add', 'user_edit', 'profile_view', 'profile_update', 'add_department',
    'role_list', 'role_add', 'role_edit', 'role_delete', 'permission_role', 'permission_update',
    'module_list', 'module_add', 'module_edit', 'module_delete', 'module_sync',
    'module_group_list', 'module_group_save', 'module_group_delete'
]

MODULE_LAYOUT = {
    "Dashboard": {
        "accounts:dashboard": {
            "icon": "bi-house",
            "is_header": True,
            "label": "Dashboard"  # ✅ Custom display name
        }
    },
    "Accounts": {
        "accounts:user_list": {
            "label": "User Management",  # ✅ Custom display name
            "icon": "bi-people",
            "children": [
                "accounts:user_create",
                "accounts:user_edit",
                "accounts:user_delete",
                "accounts:profile_view",
                "accounts:add_department",
                "accounts:edit_department",
                "accounts:delete_department"
            ]
        },
        "accounts:role_list": {
            "icon": "bi-person-badge",
            "children": ["accounts:role_add", "accounts:role_edit", "accounts:role_delete", "accounts:permission_role", "accounts:permission_update"]
        },
        "accounts:module_list": {
            "icon": "bi-box",
            "children": ["accounts:module_add", "accounts:module_edit", "accounts:module_delete", "accounts:module_sync", "accounts:module_group_list", "accounts:module_group_save", "accounts:module_group_delete"]
        }
    },
    "Products": {
        "products:product_list": {
            "icon": "bi-box",
            "children": [
                "products:create", "products:edit", "products:delete", "products:json"
            ]
        }, 
        "products:category_list": {
            "icon": "bi-box",
            "children": [
                "products:category_create", "products:category_edit", "products:category_delete"
            ]
        }, 
        "products:brand_list": {
            "icon": "bi-box",
            "children": [
                "products:create_brand", "products:edit_brand", "products:delete_brand", "products:brand_list_json"
            ]
        }, 
        "products:unit_list": {
            "icon": "bi-box",
            "children": [
                "products:brand_create", "products:brand_edit", "products:brand_delete"
            ]
        }, 
        "products:warranty_list": {
            "icon": "bi-box",
            "children": [
                "products:create_warranty", "products:edit_warranty", "products:delete_warranty"
            ]
        }
    },
    "Purchase": {
        "products:purchase_list": {
            "icon": "bi-box",
            "children": [
                "products:purchase_create", "products:purchase_payment", "products:supplier_create"
            ]
        }, 
        "products:payment_list": {
            "icon": "bi-box"
        }, 
        "products:refund_list": {
            "icon": "bi-box",
            "children": [
                "products:process_refund"
            ]
        }
    }
    #"⚙️ Settings": {
    #    "permission_matrix": {
    #        "icon": "bi-grid",
    #        "is_header": True
    #    }
    #}
}
