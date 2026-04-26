from django import forms
from django.utils import timezone
from .models import Pickup, WasteType


class PickupForm(forms.ModelForm):
    """Form for creating pickups"""

    waste_types = forms.ModelMultipleChoiceField(
        queryset=WasteType.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the types of waste for pickup"
    )

    class Meta:
        model = Pickup
        fields = ['date', 'time', 'priority', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions or notes...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to tomorrow
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        self.fields['date'].initial = tomorrow


class PickupUpdateForm(forms.ModelForm):
    """Form for updating pickups"""

    class Meta:
        model = Pickup
        fields = ['date', 'time', 'priority', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('instance')
        if user and user.status != 'pending':
            # Disable certain fields if pickup is not pending
            self.fields['date'].disabled = True
            self.fields['time'].disabled = True


class WasteTypeForm(forms.ModelForm):
    """Form for waste types"""

    class Meta:
        model = WasteType
        fields = ['name', 'description', 'recyclable', 'hazardous', 'base_fee', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recyclable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hazardous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'base_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }