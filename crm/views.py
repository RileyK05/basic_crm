from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Sum, Q
from django.utils import timezone
from .models import (
    CustomerInformation, Product, ProductsPurchased, CustomerLead, Engagement, LifetimeValue, InternalServices
)
from .forms import CustomerForm, ProductForm, LeadForm, EngagementForm, CustomUserCreationForm



# General Views
# -------------------------------------------------------

def index(request):
    """ Landing page view. """
    return render(request, 'General/index.html')


class DashboardView(ListView):
    """ Main dashboard view, displays a summary of customers, leads, products, and engagements. """
    model = CustomerInformation
    template_name = 'General/dashboard.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Customer search
        customer_search = self.request.GET.get('customer_search', '')
        customers = CustomerInformation.objects.filter(
            Q(name__icontains=customer_search) |
            Q(email__icontains=customer_search) |
            Q(phone__icontains=customer_search)
        ) if customer_search else CustomerInformation.objects.all()
        context.update(self._get_paginated_context(customers, 'customers'))

        # Lead search
        lead_search = self.request.GET.get('lead_search', '')
        leads = CustomerLead.objects.filter(
            Q(customer__name__icontains=lead_search) |
            Q(status__icontains=lead_search)
        ) if lead_search else CustomerLead.objects.all()
        context.update(self._get_paginated_context(leads, 'leads'))

        # Product search
        product_search = self.request.GET.get('product_search', '')
        products = Product.objects.filter(Q(name__icontains=product_search)) if product_search else Product.objects.all()
        context.update(self._get_paginated_context(products, 'products'))

        # Engagement search
        engagement_search = self.request.GET.get('engagement_search', '')
        engagements = Engagement.objects.filter(
            Q(customer__name__icontains=engagement_search) |
            Q(type_of_engagement__icontains=engagement_search)
        ) if engagement_search else Engagement.objects.all()
        context.update(self._get_paginated_context(engagements, 'engagements'))

        # Internal Services context
        internal_services = InternalServices.objects.first()
        if internal_services:
            context['growth_rate'] = internal_services.current_growth_rate or "N/A"
            context['projected_revenue'] = internal_services.projected_revenue or 0
            context['churn_rate'] = internal_services.internal_churn_rate or "N/A"
        else:
            context.update({'growth_rate': "N/A", 'projected_revenue': 0, 'churn_rate': "N/A"})

        return context

    def _get_paginated_context(self, queryset, context_name):
        paginator = self.get_paginator(queryset, self.paginate_by)
        page = self.request.GET.get(f'{context_name}_page')
        page_obj = paginator.get_page(page)
        return {
            context_name: page_obj,
            f'is_paginated_{context_name}': page_obj.has_other_pages(),
            f'page_obj_{context_name}': page_obj,
        }


# Authentication and User Management Views
# -------------------------------------------------------

class CreateUserView(CreateView):
    """ View for creating a new user (sign-up). """
    template_name = 'accounts/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    """ Custom login view. """
    template_name = 'accounts/login.html'
    authentication_form = AuthenticationForm


def signout_view(request):
    """ Log out the current user. """
    logout(request)
    return redirect('index')


# Customer Views
# -------------------------------------------------------

def customer_autocomplete(request):
    """View to handle customer autocomplete search."""
    if 'term' in request.GET:
        qs = CustomerInformation.objects.filter(name__icontains=request.GET.get('term'))[:10]
        customers = list(qs.values('id', 'name', 'email'))
        return JsonResponse(customers, safe=False)
    return JsonResponse([], safe=False)


class CustomerListView(ListView):
    """ View to list all customers with search functionality. """
    model = CustomerInformation
    template_name = 'Customer/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('customer_search', '')
        if query:
            return CustomerInformation.objects.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
        return CustomerInformation.objects.all()


class CustomerCreateView(CreateView):
    """ View for adding a new customer. """
    model = CustomerInformation
    form_class = CustomerForm
    template_name = 'Customer/customer_add.html'
    success_url = reverse_lazy('dashboard')


class CustomerDetailView(DetailView):
    """ View to display customer details. """
    model = CustomerInformation
    template_name = 'Customer/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        context['total_revenue'] = ProductsPurchased.objects.filter(customer=customer).aggregate(total=Sum('amount_spent'))['total'] or 0
        context['likelihood_to_churn'] = customer.likelihood_to_churn()
        lifetime_value = LifetimeValue.objects.filter(customer=customer).first()
        context['lifetime_value'] = lifetime_value.calculate_lifetime_value() if lifetime_value else 0
        return context


class CustomerUpdateView(UpdateView):
    """ View to update customer details. """
    model = CustomerInformation
    form_class = CustomerForm
    template_name = 'Customer/customer_edit.html'
    success_url = reverse_lazy('dashboard')


class CustomerDeleteView(DeleteView):
    """ View to delete a customer. """
    model = CustomerInformation
    template_name = 'Customer/customer_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


# Lead Views
# -------------------------------------------------------

class LeadListView(ListView):
    """ View to list all leads with search functionality. """
    model = CustomerLead
    template_name = 'Lead/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('lead_search', '')
        if query:
            return CustomerLead.objects.filter(
                Q(customer__name__icontains=query) |
                Q(name__icontains=query) |
                Q(status__icontains=query)
            )
        return CustomerLead.objects.all()


class LeadCreateView(CreateView):
    """ View for adding a new lead. """
    model = CustomerLead
    form_class = LeadForm
    template_name = 'Lead/lead_add.html'
    success_url = reverse_lazy('dashboard')

class LeadDetailView(DetailView):
    """View to display lead details."""
    model = CustomerLead
    template_name = 'Lead/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.object
        context['total_time_in_pipeline'] = (now().date() - lead.created_at.date()).days

        return context



class LeadUpdateView(UpdateView):
    """ View to update lead details. """
    model = CustomerLead
    form_class = LeadForm
    template_name = 'Lead/lead_edit.html'
    success_url = reverse_lazy('dashboard')


class LeadDeleteView(DeleteView):
    """ View to delete a lead. """
    model = CustomerLead
    template_name = 'Lead/lead_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


# Product Views
# -------------------------------------------------------

class ProductListView(ListView):
    """ View to list all products with search functionality. """
    model = Product
    template_name = 'Product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('product_search', '')
        if query:
            return Product.objects.filter(Q(name__icontains=query))
        return Product.objects.all()


class ProductCreateView(CreateView):
    """ View for adding a new product. """
    model = Product
    form_class = ProductForm
    template_name = 'Product/product_add.html'
    success_url = reverse_lazy('dashboard')


class ProductDetailView(DetailView):
    """ View to display product details. """
    model = Product
    template_name = 'Product/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['total_revenue'] = ProductsPurchased.objects.filter(product=product).aggregate(total=Sum('amount_spent'))['total'] or 0
        return context


class ProductUpdateView(UpdateView):
    """ View to update product details. """
    model = Product
    form_class = ProductForm
    template_name = 'Product/product_edit.html'
    success_url = reverse_lazy('dashboard')


class ProductDeleteView(DeleteView):
    """ View to delete a product. """
    model = Product
    template_name = 'Product/product_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


# Engagement Views
# -------------------------------------------------------

class EngagementListView(ListView):
    """ View to list all engagements with search functionality. """
    model = Engagement
    template_name = 'Engagement/engagement_list.html'
    context_object_name = 'engagements'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('engagement_search', '')
        if query:
            return Engagement.objects.filter(
                Q(customer__name__icontains=query) |
                Q(type_of_engagement__icontains=query)
            )
        return Engagement.objects.all()


class EngagementCreateView(CreateView):
    """ View for adding a new engagement. """
    model = Engagement
    form_class = EngagementForm
    template_name = 'Engagement/engagement_add.html'
    success_url = reverse_lazy('dashboard')


class EngagementDetailView(DetailView):
    """ View to display engagement details. """
    model = Engagement
    template_name = 'Engagement/engagement_detail.html'
    context_object_name = 'engagement'


class EngagementUpdateView(UpdateView):
    """ View to update engagement details. """
    model = Engagement
    form_class = EngagementForm
    template_name = 'Engagement/engagement_edit.html'
    success_url = reverse_lazy('dashboard')


class EngagementDeleteView(DeleteView):
    """ View to delete an engagement. """
    model = Engagement
    template_name = 'Engagement/engagement_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


# Internal Services Views
# -------------------------------------------------------

class InternalView(TemplateView):
    """ View to display internal metrics. """
    template_name = 'Internal/internal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        internal_services = InternalServices.objects.first()

        # Set context variables for all the internal service metrics
        if internal_services:
            context.update({
                'current_revenue': internal_services.current_revenue,
                'projected_revenue': internal_services.projected_revenue,
                'past_growth_rate': internal_services.past_growth_rate,
                'current_growth_rate': internal_services.current_growth_rate,
                'projected_growth': internal_services.projected_growth,
                'total_customers': internal_services.total_customers,
                'average_length_of_customer': internal_services.average_length_of_customer,
                'internal_churn_rate': internal_services.internal_churn_rate,
                'average_cost_to_acquire': internal_services.average_cost_to_acquire,
                'average_revenue_per_customer': internal_services.average_revenue_per_customer,
                'industry_growth_rate': internal_services.industry_growth_rate,
                'average_lifetime_value': internal_services.average_lifetime_value,
                'average_lifetime_value_id': internal_services.id
            })
        else:
            # Default values if no InternalServices object exists
            context.update({
                'current_revenue': "N/A",
                'projected_revenue': "N/A",
                'past_growth_rate': "N/A",
                'current_growth_rate': "N/A",
                'projected_growth': "N/A",
                'total_customers': "N/A",
                'average_length_of_customer': "N/A",
                'internal_churn_rate': "N/A",
                'average_cost_to_acquire': "N/A",
                'average_revenue_per_customer': "N/A",
                'industry_growth_rate': "N/A",
                'average_lifetime_value': "N/A",
                'average_lifetime_value_id': None
            })
        return context


class InternalServicesEditView(UpdateView):
    """ View to edit internal services data. """
    model = InternalServices
    template_name = 'Internal/internal_services_edit.html'
    fields = [
        'current_revenue', 'projected_revenue', 'past_growth_rate', 'current_growth_rate',
        'projected_growth', 'total_customers', 'average_length_of_customer', 'internal_churn_rate',
        'average_cost_to_acquire', 'average_revenue_per_customer', 'industry_growth_rate'
    ]
    success_url = reverse_lazy('internal')

    def get_object(self, queryset=None):
        internal_services, created = InternalServices.objects.get_or_create()
        return internal_services


class LifetimeValueEditView(UpdateView):
    """ View to edit average lifetime value. """
    model = InternalServices
    template_name = 'Internal/lifetime_value_edit.html'
    fields = ['average_lifetime_value'] 
    success_url = reverse_lazy('internal') 

    def get_object(self, queryset=None):
        internal_services = InternalServices.objects.first()
        if not internal_services:
            internal_services = InternalServices.objects.create()
        return internal_services


# Products Purchased Views
# -------------------------------------------------------

class ProductsPurchasedCreateView(CreateView):
    """ View for adding a product purchase. """
    model = ProductsPurchased
    template_name = 'Products-Purchased/products_purchased_add.html'
    fields = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedUpdateView(UpdateView):
    """ View to update product purchase details. """
    model = ProductsPurchased
    template_name = 'Products-Purchased/products_purchased_edit.html'
    fields = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedDeleteView(DeleteView):
    """ View to delete a product purchase record. """
    model = ProductsPurchased
    template_name = 'Products-Purchased/products_purchased_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
