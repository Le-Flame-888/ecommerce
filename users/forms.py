from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('street', 'city', 'postal_code', 'country')
        widgets = {
            'street': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900'}),
            'city': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900'}),
            'country': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900'}),
        }
