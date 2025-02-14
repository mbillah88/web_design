from django.shortcuts import render
from .forms import PayForm
from .models import Payment  # Assuming you have a Payment model
from django.utils import timezone

def check_due_payment():
    # Example logic to determine if payment is due
    # Replace with actual logic as needed
    due_date = timezone.now() - timezone.timedelta(days=1)  # Example: payment due if older than 30 days
    unpaid_payments = Payment.objects.filter(due_date__lte=due_date, status='unpaid')
    return unpaid_payments.exists()

def payment_view(request):
    due_payment = check_due_payment()
    form = PayForm(due_payment=due_payment)
    return render(request, 'business_apps/purchase_due_payment.html', {'pay_form': form})
