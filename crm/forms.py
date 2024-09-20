from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerInformation, Product, CustomerLead, Engagement, InternalServices, User

# -------------------------------------------
# User Forms
# -------------------------------------------

class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user (sign-up)."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


# -------------------------------------------
# Customer Forms
# -------------------------------------------

class CustomerForm(forms.ModelForm):
    """Form for managing customer information."""
    class Meta:
        model = CustomerInformation
        fields = ['name', 'email', 'phone', 'industry', 'company', 'education', 'income']


# -------------------------------------------
# Product Forms
# -------------------------------------------

class ProductForm(forms.ModelForm):
    """Form for managing product information."""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']


# -------------------------------------------
# Lead Forms
# -------------------------------------------

class LeadForm(forms.ModelForm):
    """Form for managing customer leads with the option to create a new lead without an associated customer."""
    new_lead_without_customer = forms.BooleanField(required=False, label='Create new lead without associating with a customer')

    class Meta:
        model = CustomerLead
        fields = ['customer', 'name', 'email', 'phone', 'company', 'status', 'likelihood_to_convert', 'lead_stage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].required = False
        self.fields['customer'].widget = forms.TextInput(attrs={'placeholder': 'Search for an existing customer'})

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        name = cleaned_data.get('name')
        new_lead_without_customer = cleaned_data.get('new_lead_without_customer')

        if not customer and not new_lead_without_customer and not name:
            raise forms.ValidationError("Either select an existing customer or provide a name for the new lead.")

        return cleaned_data


# -------------------------------------------
# Engagement Forms
# -------------------------------------------

class EngagementForm(forms.ModelForm):
    """Form for managing customer engagement."""
    class Meta:
        model = Engagement
        fields = ['customer', 'level_of_engagement', 'type_of_engagement', 'engagement_date']


# -------------------------------------------
# Internal Services Forms
# -------------------------------------------

class InternalServiceMetricForm(forms.ModelForm):
    """Form for editing a specific metric in InternalServices."""
    value = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label='Metric Value',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the value'
        })
    )

    class Meta:
        model = InternalServices
        fields = []  # Dynamically handle fields in the view logic.


# -------------------------------------------
# Organization Notes:
# 1. All forms related to specific features (User, Customer, Product, etc.) are grouped together.
# 2. Comments are added to explain the purpose of each form.
# 3. Form code is simplified and follows Django best practices.
# 4. Repeated imports are removed to avoid duplication.
