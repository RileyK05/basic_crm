from django.contrib import admin
from .models import (
    CustomerInformation, CustomDescriptionField, Product, ProductsPurchased, CustomerLead, Engagement, LifetimeValue, InternalServices
)

@admin.register(CustomerInformation)
class CustomerInformationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'company', 'industry', 'income', 'created_at']
    search_fields = ['name', 'email', 'company', 'industry']
    list_filter = ['industry', 'company']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'industry', 'company', 'education', 'income')
        }),
        ('Important Dates', {
            'fields': ('created_at',)
        }),
    )

@admin.register(CustomDescriptionField)
class CustomDescriptionFieldAdmin(admin.ModelAdmin):
    list_display = ['customer', 'description']
    search_fields = ['customer__name', 'description']
    list_filter = ['customer']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description']
    search_fields = ['name', 'description']
    list_filter = ['price']

@admin.register(ProductsPurchased)
class ProductsPurchasedAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'number_of_products_purchased', 'date_of_sale', 'amount_spent']
    search_fields = ['customer__name', 'product__name']
    list_filter = ['date_of_sale', 'product']

@admin.register(CustomerLead)
class CustomerLeadAdmin(admin.ModelAdmin):
    list_display = ['customer', 'status', 'likelihood_to_convert', 'lead_stage']
    search_fields = ['customer__name', 'status']
    list_filter = ['lead_stage', 'status']

@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ['customer', 'level_of_engagement', 'type_of_engagement', 'engagement_date']
    search_fields = ['customer__name', 'type_of_engagement']
    list_filter = ['level_of_engagement', 'type_of_engagement', 'engagement_date']

@admin.register(LifetimeValue)
class LifetimeValueAdmin(admin.ModelAdmin):
    list_display = ['customer', 'lifetime_value', 'cost_to_acquire', 'worth_acquisition_cost']
    search_fields = ['customer__name']
    list_filter = ['lifetime_value', 'cost_to_acquire']

@admin.register(InternalServices)
class InternalServicesAdmin(admin.ModelAdmin):
    list_display = ['current_revenue', 'projected_revenue', 'current_growth_rate', 'internal_churn_rate']
    list_filter = ['current_growth_rate', 'internal_churn_rate']
    search_fields = ['current_revenue', 'projected_revenue']
