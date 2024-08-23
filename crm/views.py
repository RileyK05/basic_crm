from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Sum
from django.utils import timezone
from .models import (
    CustomerInformation, Product, ProductsPurchased, CustomerLead, Engagement, LifetimeValue, InternalServices
)
from .forms import CustomerForm, ProductForm, LeadForm, EngagementForm


class DashboardView(ListView):
    model = CustomerInformation
    template_name = 'dashboard.html'
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_customers'] = CustomerInformation.objects.annotate(
            total_revenue=Sum('productspurchased__amount_spent')
        ).order_by('-total_revenue')[:5]
        context['top_leads'] = CustomerLead.objects.order_by('-likelihood_to_convert')[:5]
        context['engagement_summary'] = Engagement.objects.values('type_of_engagement').annotate(
            count=Sum('id')
        )
        context['sales_funnel'] = CustomerLead.objects.values('lead_stage').annotate(
            count=Sum('id')
        )
        internal_services = InternalServices.objects.first()
        context['growth_rate'] = internal_services.current_growth_rate
        context['projected_revenue'] = internal_services.projected_revenue
        context['churn_rate'] = internal_services.internal_churn_rate
        return context


class CustomerCreateView(CreateView):
    model = CustomerInformation
    form_class = CustomerForm
    template_name = 'customer_add.html'
    success_url = reverse_lazy('dashboard')


class CustomerDetailView(DetailView):
    model = CustomerInformation
    template_name = 'customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        context['total_revenue'] = ProductsPurchased.objects.filter(customer=customer).aggregate(
            total=Sum('amount_spent')
        )['total'] or 0
        context['likelihood_to_churn'] = customer.likelihood_to_churn()
        lifetime_value = LifetimeValue.objects.filter(customer=customer).first()
        if lifetime_value:
            context['lifetime_value'] = lifetime_value.calculate_lifetime_value()
        else:
            context['lifetime_value'] = 0
        return context


class CustomerUpdateView(UpdateView):
    model = CustomerInformation
    form_class = CustomerForm
    template_name = 'customer_edit.html'
    success_url = reverse_lazy('dashboard')


class CustomerDeleteView(DeleteView):
    model = CustomerInformation
    template_name = 'customer_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_add.html'
    success_url = reverse_lazy('dashboard')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['total_revenue'] = ProductsPurchased.objects.filter(product=product).aggregate(
            total=Sum('amount_spent')
        )['total'] or 0
        return context


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_edit.html'
    success_url = reverse_lazy('dashboard')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class LeadCreateView(CreateView):
    model = CustomerLead
    form_class = LeadForm
    template_name = 'lead_add.html'
    success_url = reverse_lazy('dashboard')


class LeadDetailView(DetailView):
    model = CustomerLead
    template_name = 'lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.object
        context['total_time_in_pipeline'] = (timezone.now().date() - lead.customer.created_at).days
        return context


class LeadUpdateView(UpdateView):
    model = CustomerLead
    form_class = LeadForm
    template_name = 'lead_edit.html'
    success_url = reverse_lazy('dashboard')


class LeadDeleteView(DeleteView):
    model = CustomerLead
    template_name = 'lead_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class EngagementCreateView(CreateView):
    model = Engagement
    form_class = EngagementForm
    template_name = 'engagement_add.html'
    success_url = reverse_lazy('dashboard')


class EngagementDetailView(DetailView):
    model = Engagement
    template_name = 'engagement_detail.html'
    context_object_name = 'engagement'


class EngagementUpdateView(UpdateView):
    model = Engagement
    form_class = EngagementForm
    template_name = 'engagement_edit.html'
    success_url = reverse_lazy('dashboard')


class EngagementDeleteView(DeleteView):
    model = Engagement
    template_name = 'engagement_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedCreateView(CreateView):
    model = ProductsPurchased
    template_name = 'products_purchased_add.html'
    fields = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedUpdateView(UpdateView):
    model = ProductsPurchased
    template_name = 'products_purchased_edit.html'
    fields = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedDeleteView(DeleteView):
    model = ProductsPurchased
    template_name = 'products_purchased_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
