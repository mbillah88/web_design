from django import forms

class PayForm(forms.Form):
    PAYMENT_CHOICES = [
        (1, 'Cash'),
        (2, 'Due'),
        (3, 'Others'),
        # ...existing choices...
    ]
    
    payment_type = forms.ChoiceField(choices=PAYMENT_CHOICES)
    # ...existing fields...

    def __init__(self, *args, **kwargs):
        due_payment = kwargs.pop('due_payment', False)
        super(PayForm, self).__init__(*args, **kwargs)
        if due_payment:
            self.fields['payment_type'].initial = 1
        # ...existing code...
