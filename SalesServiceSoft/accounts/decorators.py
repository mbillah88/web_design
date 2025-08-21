# accounts/decorators.py
def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("আপনার এই পৃষ্ঠায় প্রবেশাধিকার নেই।")
        return wrapper
    return decorator
