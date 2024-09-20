from django.urls import path, include
from .views import (
    index, DashboardView, CustomerCreateView, CustomerDetailView, CustomerUpdateView, CustomerDeleteView,
    ProductCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView,
    LeadCreateView, LeadDetailView, LeadUpdateView, LeadDeleteView,
    EngagementCreateView, EngagementDetailView, EngagementUpdateView, EngagementDeleteView,
    ProductsPurchasedCreateView, ProductsPurchasedUpdateView, ProductsPurchasedDeleteView,
    CreateUserView, InternalView, CustomerListView, LeadListView, ProductListView, EngagementListView,
    signout_view, CustomLoginView, InternalServicesEditView, LifetimeValueEditView, customer_autocomplete,
    ViewAccountView, EditAccountView, ProductsPurchasedDetailView
)

urlpatterns = [
    # Index page (landing page)
    path('', index, name='index'),

    # Internal
    path('internal/', InternalView.as_view(), name='internal'),
    path('internal/edit/<str:metric>/', InternalServicesEditView.as_view(), name='internal_services_edit'),
    path('internal/life-value/edit/', LifetimeValueEditView.as_view(), name='lifetime_value_edit'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Customer management
    path('customers/', CustomerListView.as_view(), name='customer_list'),  
    path('customer/add/', CustomerCreateView.as_view(), name='customer_add'),
    path('customer/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_edit'),
    path('customer/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),
    path('customer-autocomplete/', customer_autocomplete, name='customer_autocomplete'),

    # Product management
    path('products/', ProductListView.as_view(), name='product_list'),  
    path('product/add/', ProductCreateView.as_view(), name='product_add'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Lead management
    path('leads/', LeadListView.as_view(), name='lead_list'),  
    path('lead/add/', LeadCreateView.as_view(), name='lead_add'),
    path('lead/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),
    path('lead/<int:pk>/edit/', LeadUpdateView.as_view(), name='lead_edit'),
    path('lead/<int:pk>/delete/', LeadDeleteView.as_view(), name='lead_delete'),

    # Engagement management
    path('engagements/', EngagementListView.as_view(), name='engagement_list'),  
    path('engagement/add/', EngagementCreateView.as_view(), name='engagement_add'),
    path('engagement/<int:pk>/', EngagementDetailView.as_view(), name='engagement_detail'),
    path('engagement/<int:pk>/edit/', EngagementUpdateView.as_view(), name='engagement_edit'),
    path('engagement/<int:pk>/delete/', EngagementDeleteView.as_view(), name='engagement_delete'),

    # Products Purchased management
    path('products-purchased/add/', ProductsPurchasedCreateView.as_view(), name='products_purchased_add'),
    path('products-purchased/<int:pk>/edit/', ProductsPurchasedUpdateView.as_view(), name='products_purchased_edit'),
    path('products-purchased/<int:pk>/delete/', ProductsPurchasedDeleteView.as_view(), name='products_purchased_delete'),
    path('products-purchased/<int:pk>/', ProductsPurchasedDetailView.as_view(), name='products_purchased_detail'),
    
    # Accounts
    path('accounts/login/', CustomLoginView.as_view(), name='login'), 
    path('accounts/logout/', signout_view, name='logout'), 
    path('accounts/', include('django.contrib.auth.urls')),  
    path('signup/', CreateUserView.as_view(), name='signup'),  
    path('account/', ViewAccountView.as_view(), name='view_account'),
    path('account/edit/', EditAccountView.as_view(), name='edit_account'),
]
