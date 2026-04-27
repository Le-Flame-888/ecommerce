from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'street', 'city', 'postal_code', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Téléphone'}),
            'street': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Adresse'}),
            'city': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Ville'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Code postal'}),
            'country': forms.TextInput(attrs={'class': 'w-full border border-gray-300 px-4 py-2 text-sm rounded-none focus:outline-none focus:ring-1 focus:ring-brand-900 focus:border-brand-900', 'placeholder': 'Pays', 'value': 'Maroc'}),
        }
