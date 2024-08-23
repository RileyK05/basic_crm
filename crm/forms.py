from django import forms
from .models import CustomerInformation, Product, CustomerLead, Engagement

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
