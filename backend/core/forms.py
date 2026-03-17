from django import forms
from .models import Tender, User, Bid

class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        fields = ['title', 'category', 'budget', 'location', 'deadline', 'description', 'document']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'company_name']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
             
        return cleaned_data

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount', 'proposal_text', 'proposal_document']
        widgets = {
             'proposal_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your proposal...'}),
             'bid_amount': forms.NumberInput(attrs={'placeholder': 'Your Bid Amount (INR)'}),
        }
