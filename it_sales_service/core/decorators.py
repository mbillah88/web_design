from django.shortcuts import redirect
from functools import wraps

def role_required(role_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role.name != role_name:
                return redirect('unauthorized')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
