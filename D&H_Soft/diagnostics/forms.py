from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import (
    TestCategory, TestGroup, TestItem,
    Patient, PatientVisit, IPDAdmission, Consultant
)

# -------------------------------
# 🔬 Test Management Forms
# -------------------------------

class TestCategoryForm(forms.ModelForm):
    class Meta:
        model = TestCategory
        fields = ['name', 'description']

class TestGroupForm(forms.ModelForm):
    class Meta:
        model = TestGroup
        fields = ['code', 'name', 'sub_category', 'price', 'discounted_price', 'percent_discount']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'percent_discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class TestItemForm(forms.ModelForm):
    class Meta:
        model = TestItem
        fields = ['name', 'group', 'unit', 'reference_range']

# -------------------------------
# 🧍 Patient Form
# -------------------------------
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'mobile', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('age', css_class='col-md-3'),
                Column('gender', css_class='col-md-3'),
            ),
            Row(
                Column('mobile', css_class='col-md-6'),
                Column('address', css_class='col-md-6'),
            )
        )

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# -------------------------------
# 🩺 Patient Visit Form
# -------------------------------
class PatientVisitForm(forms.ModelForm):
    consultant = forms.ModelChoiceField(
        queryset=Consultant.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        required=True
    )
    referred_by = forms.ModelChoiceField(
        queryset=Consultant.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        required=False
    )

    class Meta:
        model = PatientVisit
        fields = ['consultant', 'referred_by', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('consultant', css_class='col-md-6'),
                Column('referred_by', css_class='col-md-6'),
            ),
            Row(
                Column('notes', css_class='col-12'),
            )
        )

        self.fields['notes'].widget.attrs.update({'class': 'form-control'})

# -------------------------------
# 🏥 IPD Admission Form
# -------------------------------
class IPDAdmissionForm(forms.ModelForm):
    current_consultant = forms.ModelChoiceField(
        queryset=Consultant.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        required=True
    )

    class Meta:
        model = IPDAdmission
        fields = ['current_bed', 'current_consultant', 'admission_reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('current_bed', css_class='col-md-6'),
                Column('current_consultant', css_class='col-md-6'),
            ),
            Row(
                Column('admission_reason', css_class='col-12'),
            )
        )

        self.fields['current_bed'].widget.attrs.update({'class': 'form-select'})
        self.fields['admission_reason'].widget.attrs.update({'class': 'form-control'})
