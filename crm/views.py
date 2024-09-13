from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Sum, Q
from django.utils import timezone
from .models import (
    CustomerInformation, Product, ProductsPurchased, CustomerLead, Engagement, LifetimeValue, InternalServices
)
from .forms import CustomerForm, ProductForm, LeadForm, EngagementForm, CustomUserCreationForm

def index(request):
    return render(request, 'General/index.html')

class CreateUserView(CreateView):
    template_name = 'accounts/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')

class DashboardView(ListView):
    model = CustomerInformation
    template_name = 'General/dashboard.html'
    context_object_name = 'customers'
    paginate_by = 10  # Pagination for customers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Customer Search/Filter Logic
        customer_search = self.request.GET.get('customer_search', '')
        if customer_search:
            customers = CustomerInformation.objects.filter(
                Q(name__icontains=customer_search) | Q(email__icontains=customer_search) | Q(phone__icontains=customer_search)
            )
        else:
            customers = CustomerInformation.objects.all()

        # Pagination for customers
        paginator = self.get_paginator(customers, self.paginate_by)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)
        context['customers'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['page_obj'] = page_obj

        # Lead Search/Filter Logic
        lead_search = self.request.GET.get('lead_search', '')
        if lead_search:
            leads = CustomerLead.objects.filter(
                Q(customer__name__icontains=lead_search) | Q(status__icontains=lead_search)
            )
        else:
            leads = CustomerLead.objects.all()

        # Pagination for leads
        paginator_leads = self.get_paginator(leads, self.paginate_by)
        page_leads = self.request.GET.get('lead_page')
        page_obj_leads = paginator_leads.get_page(page_leads)
        context['leads'] = page_obj_leads
        context['is_paginated_leads'] = page_obj_leads.has_other_pages()
        context['page_obj_leads'] = page_obj_leads

        # Product Search/Filter Logic
        product_search = self.request.GET.get('product_search', '')
        if product_search:
            products = Product.objects.filter(
                Q(name__icontains=product_search)
            )
        else:
            products = Product.objects.all()

        # Pagination for products
        paginator_products = self.get_paginator(products, self.paginate_by)
        page_products = self.request.GET.get('product_page')
        page_obj_products = paginator_products.get_page(page_products)
        context['products'] = page_obj_products
        context['is_paginated_products'] = page_obj_products.has_other_pages()
        context['page_obj_products'] = page_obj_products

        # Engagement Search/Filter Logic
        engagement_search = self.request.GET.get('engagement_search', '')
        if engagement_search:
            engagements = Engagement.objects.filter(
                Q(customer__name__icontains=engagement_search) | Q(type_of_engagement__icontains=engagement_search)
            )
        else:
            engagements = Engagement.objects.all()

        # Pagination for engagements
        paginator_engagements = self.get_paginator(engagements, self.paginate_by)
        page_engagements = self.request.GET.get('engagement_page')
        page_obj_engagements = paginator_engagements.get_page(page_engagements)
        context['engagements'] = page_obj_engagements
        context['is_paginated_engagements'] = page_obj_engagements.has_other_pages()
        context['page_obj_engagements'] = page_obj_engagements

        # Internal metrics for dashboard
        internal_services = InternalServices.objects.first()
        context['growth_rate'] = internal_services.current_growth_rate if internal_services and internal_services.current_growth_rate is not None else "N/A"
        context['projected_revenue'] = internal_services.projected_revenue if internal_services and internal_services.projected_revenue is not None else 0
        context['churn_rate'] = internal_services.internal_churn_rate if internal_services and internal_services.internal_churn_rate is not None else "N/A"

        return context

class CustomerCreateView(CreateView):
    model = CustomerInformation
    form_class = CustomerForm
    template_name = 'Customer/customer_add.html'
    success_url = reverse_lazy('dashboard')


class CustomerDetailView(DetailView):
    model = CustomerInformation
    template_name = 'Customer/customer_detail.html'
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
    template_name = 'Customer/customer_edit.html'
    success_url = reverse_lazy('dashboard')


class CustomerDeleteView(DeleteView):
    model = CustomerInformation
    template_name = 'Customer/customer_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'Product/product_add.html'
    success_url = reverse_lazy('dashboard')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'Product/product_detail.html'
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
    template_name = 'Product/product_edit.html'
    success_url = reverse_lazy('dashboard')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'Product/product_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class LeadCreateView(CreateView):
    model = CustomerLead
    form_class = LeadForm
    template_name = 'Lead/lead_add.html'
    success_url = reverse_lazy('dashboard')


class LeadDetailView(DetailView):
    model = CustomerLead
    template_name = 'Lead/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.object
        context['total_time_in_pipeline'] = (timezone.now().date() - lead.customer.created_at).days
        return context


class LeadUpdateView(UpdateView):
    model = CustomerLead
    form_class = LeadForm
    template_name = 'Lead/lead_edit.html'
    success_url = reverse_lazy('dashboard')


class LeadDeleteView(DeleteView):
    model = CustomerLead
    template_name = 'Lead/lead_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class EngagementCreateView(CreateView):
    model = Engagement
    form_class = EngagementForm
    template_name = 'Engagement/engagement_add.html'
    success_url = reverse_lazy('dashboard')


class EngagementDetailView(DetailView):
    model = Engagement
    template_name = 'Engagement/engagement_detail.html'
    context_object_name = 'engagement'


class EngagementUpdateView(UpdateView):
    model = Engagement
    form_class = EngagementForm
    template_name = 'Engagement/engagement_edit.html'
    success_url = reverse_lazy('dashboard')


class EngagementDeleteView(DeleteView):
    model = Engagement
    template_name = 'Engagement/engagement_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedCreateView(CreateView):
    model = ProductsPurchased
    template_name = 'Products-Purchased/products_purchased_add.html'
    fields = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedUpdateView(UpdateView):
    model = ProductsPurchased
    template_name = 'Products-Purchased/products_purchased_edit.html'
    fields = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    success_url = reverse_lazy('dashboard')


class ProductsPurchasedDeleteView(DeleteView):
    model = ProductsPurchased
    template_name = 'Products-Purchased/products_purchased_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class InternalView(TemplateView):
    template_name = 'Internal/internal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        internal_services = InternalServices.objects.first()

        context['current_revenue'] = internal_services.current_revenue if internal_services else "N/A"
        context['projected_revenue'] = internal_services.projected_revenue if internal_services else "N/A"
        context['growth_rate'] = internal_services.current_growth_rate if internal_services else "N/A"
        context['churn_rate'] = internal_services.internal_churn_rate if internal_services else "N/A"

        return context
    
    
class CustomerListView(ListView):
    model = CustomerInformation
    template_name = 'Customer/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10 

    def get_queryset(self):
        query = self.request.GET.get('customer_search', '')
        if query:
            return CustomerInformation.objects.filter(
                Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
            )
        return CustomerInformation.objects.all()


class LeadListView(ListView):
    model = CustomerLead
    template_name = 'Lead/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 10  

    def get_queryset(self):
        query = self.request.GET.get('lead_search', '')
        if query:
            return CustomerLead.objects.filter(
                Q(customer__name__icontains=query) | Q(status__icontains=query)
            )
        return CustomerLead.objects.all()


class ProductListView(ListView):
    model = Product
    template_name = 'Product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10  

    def get_queryset(self):
        query = self.request.GET.get('product_search', '')
        if query:
            return Product.objects.filter(Q(name__icontains=query))
        return Product.objects.all()


class EngagementListView(ListView):
    model = Engagement
    template_name = 'Engagement/engagement_list.html'
    context_object_name = 'engagements'
    paginate_by = 10  

    def get_queryset(self):
        query = self.request.GET.get('engagement_search', '')
        if query:
            return Engagement.objects.filter(
                Q(customer__name__icontains=query) | Q(type_of_engagement__icontains=query)
            )
        return Engagement.objects.all()
