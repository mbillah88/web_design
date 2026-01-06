from models import Warranty
class WarrantyForm(forms.ModelForm):
    class Meta:
        model = Warranty
        fields = ['name', 'type', 'duration_months', 'terms', 'is_active']
        widgets = {
            'terms': forms.Textarea(attrs={'rows': 3}),
        }
class WarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = Warranty
        fields = '__all__'
