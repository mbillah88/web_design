from django import forms
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'date_of_birth', 'profile_image'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'first_name': 'প্রথম নাম',
            'last_name': 'শেষ নাম',
            'email': 'ইমেইল',
            'phone': 'ফোন নম্বর',
            'address': 'ঠিকানা',
            'date_of_birth': 'জন্ম তারিখ',
            'profile_image': 'প্রোফাইল ছবি'
        }
        help_texts = {
            'first_name': 'আপনার প্রথম নাম লিখুন',
            'last_name': 'আপনার শেষ নাম লিখুন',
            'email': 'আপনার ইমেইল ঠিকানা লিখুন',
            'phone': 'আপনার ফোন নম্বর লিখুন (ঐচ্ছিক)',
            'address': 'আপনার ঠিকানা লিখুন (ঐচ্ছিক)',
            'date_of_birth': 'আপনার জন্ম তারিখ লিখুন (ঐচ্ছিক)',
            'profile_image': 'আপনার প্রোফাইল ছবি আপলোড করুন (ঐচ্ছিক)'
        }
        error_messages = {
            'email': {
                'invalid': 'অনুগ্রহ করে একটি বৈধ ইমেইল ঠিকানা লিখুন',
            },
            'phone': {
                'max_length': 'ফোন নম্বরটি 15 অক্ষরের বেশি হতে পারবে না',
            }
        }
        help_texts = {
            'profile_image': 'আপনার প্রোফাইল ছবি আপলোড করুন (ঐচ্ছিক)',
        }
        error_messages = {
            'profile_image': {
                'invalid': 'অনুগ্রহ করে একটি বৈধ ইমেইল ঠিকানা লিখুন',
            },
        }
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'profile_image': 'প্রোফাইল ছবি',
        }
        
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='পাসওয়ার্ড', widget=forms.PasswordInput)
    password2 = forms.CharField(label='পুনরায় পাসওয়ার্ড', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'phone', 'address', 'date_of_birth', 'profile_image']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("পাসওয়ার্ড মিলছে না")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user