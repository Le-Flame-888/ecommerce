from django import forms

class CouponApplyForm(forms.Form):
    code = forms.CharField(label='Code Promo')
