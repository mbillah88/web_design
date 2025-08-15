# notice/views.py
from django.shortcuts import render
from .models import Notice

def notice_list(request):
    notices = Notice.objects.order_by('-created_at')
    return render(request, 'notice/notice_list.html', {'notices': notices})
