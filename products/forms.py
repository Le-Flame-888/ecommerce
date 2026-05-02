from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:border-black focus:ring-black'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:border-black focus:ring-black', 'placeholder': 'Votre avis sur ce produit...'}),
        }
