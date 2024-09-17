from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerInformation, Product, CustomerLead, Engagement, User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerInformation
        fields = ['name', 'email', 'phone', 'industry', 'company', 'education', 'income']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

from django import forms
from .models import CustomerInformation, CustomerLead

class LeadForm(forms.ModelForm):
    # Adding a checkbox to indicate creating a new lead without an associated customer
    new_lead_without_customer = forms.BooleanField(required=False, label='Create new lead without associating with a customer')

    class Meta:
        model = CustomerLead
        fields = ['customer', 'name', 'email', 'phone', 'company', 'status', 'likelihood_to_convert', 'lead_stage']

    def __init__(self, *args, **kwargs):
        super(LeadForm, self).__init__(*args, **kwargs)
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


class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        fields = ['customer', 'level_of_engagement', 'type_of_engagement', 'engagement_date']
