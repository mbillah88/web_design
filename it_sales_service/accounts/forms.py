from django import forms
from accounts.models import CustomUser, Profile, Role, Department, Permission, Module

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'রোলের নাম লিখুন'
            })
        }

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password', 'confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user 
# accounts/forms.py
class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="পাসওয়ার্ড"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="পাসওয়ার্ড নিশ্চিত করুন"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'password', 'confirm_password']
        #readonly_fields = ('is_protected',)  # Optional: prevent accidental change
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            #'is_protected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }  


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("পাসওয়ার্ড মিলছে না।")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)  # ✅ Only if password provided

        if commit:
            user.save()
        return user
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'নামের প্রথম অংশ',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'নামের শেষ অংশ',
                'autocomplete': 'family-name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'date',
                'placeholder': 'জন্ম তারিখ'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'ফোন নম্বর',
                'inputmode': 'tel'
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'মোবাইল নম্বর',
                'inputmode': 'tel'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 2,
                'placeholder': 'বর্তমান ঠিকানা'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'জরুরি যোগাযোগের নাম'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'জরুরি ফোন নম্বর',
                'inputmode': 'tel'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'পদবি'
            }),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-sm',
                'accept': 'image/*'
            }),
        }
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'বিভাগের নাম',
                'autocomplete': 'off'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'বিভাগ কোড',
                'autocomplete': 'off'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'বর্ণনা লিখুন',
                'rows': 2
            }),
        }
        labels = {
            'name': 'বিভাগের নাম',
            'code': 'বিভাগ কোড',
            'description': 'বর্ণনা'
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = [
            'name',
            'url_name',
            'icon',
            'is_visible',
            'order',
            'parent',
            'group',
            'is_accordion',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'মডিউল নাম'
            }),
            'url_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL নাম'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'আইকন ক্লাস (bi bi-...)'
            }),
            'is_visible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'group': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_accordion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'নাম',
            'url_name': 'URL নাম',
            'icon': 'আইকন',
            'is_visible': 'দৃশ্যমান?',
            'order': 'ক্রম',
            'parent': 'Parent মডিউল',
            'group': 'গ্রুপ',
            'is_accordion': 'Accordion?',
        }
class DashboardForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")
        return cleaned_data