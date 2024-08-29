from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomerInformation, Product, CustomerLead, Engagement, User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 
                  'email', 'password1', 'password2')

class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerInformation
        fields = ['name', 'email', 'phone', 'industry', 'company', 'education', 'income']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']


class LeadForm(forms.ModelForm):
    class Meta:
        model = CustomerLead
        fields = ['customer', 'status', 'likelihood_to_convert', 'lead_stage']


class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        fields = ['customer', 'level_of_engagement', 'type_of_engagement', 'engagement_date']
