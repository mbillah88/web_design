# accounts/views/dashboard.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import Permission, ActionType

@login_required
def home(request):
    # ✅ Optional: check access permission
    access_action = ActionType.objects.filter(key='access').first()
    has_access = Permission.objects.filter(
        role=request.user.role,
        module__url_name='dashboard',
        action=access_action,
        is_allowed=True
    ).exists()

    if not has_access:
        return render(request, '403.html')  # Optional: custom access denied page

    return render(request, 'accounts/dashboard.html', {
        'page_title': 'ড্যাশবোর্ড',
        'welcome_text': f"স্বাগতম, {request.user.get_full_name()}!",
    })
