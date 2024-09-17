from django.db import models
from django.utils import timezone
from django.db.models import Sum, Avg
from django.contrib.auth.models import AbstractUser

# --- Custom User Model ---
class User(AbstractUser):
    ROLES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('SalesRep', 'Sales Representative'),
        ('CustomerServ', 'Customer Service'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='SalesRep')

    def __str__(self):
        return self.username

    # Role check methods for convenience
    def is_admin(self):
        return self.role == 'Admin'

    def is_manager(self):
        return self.role == 'Manager'

    def is_sales_rep(self):
        return self.role == 'SalesRep'

    def is_customer_serv(self):
        return self.role == 'CustomerServ'


# --- Customer Models ---
class CustomerInformation(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def likelihood_to_churn(self):
        """Calculates likelihood to churn based on engagement and internal churn rate."""
        engagements = self.engagement_set.all()
        churn_rate = InternalServices.get_internal_churn_rate()
        if engagements.exists():
            avg_engagement = engagements.aggregate(
                avg_engagement=Avg('level_of_engagement')
            )['avg_engagement']
            return churn_rate * (1 - avg_engagement)
        return "No engagement for customer"


class CustomDescriptionField(models.Model):
    customer = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"Custom Description for {self.customer.name}"


# --- Product Models ---
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    def total_revenue(self):
        """Calculates total revenue from product sales."""
        return self.productspurchased_set.aggregate(total=Sum('amount_spent'))['total']


class ProductsPurchased(models.Model):
    customer = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number_of_products_purchased = models.PositiveIntegerField()
    date_of_sale = models.DateField(default=timezone.now)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer.name} purchased {self.product.name}"


# --- Lead Models ---
class CustomerLead(models.Model):
    LEAD_STAGES = [
        ('Initial Contact', 'Initial Contact'),
        ('Qualified', 'Qualified'),
        ('Negotiation', 'Negotiation'),
        ('Won', 'Won'),
        ('Lost', 'Lost'),
    ]

    customer = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20)
    likelihood_to_convert = models.DecimalField(max_digits=5, decimal_places=2, help_text='Likelihood in percentage')
    lead_stage = models.CharField(max_length=50, choices=LEAD_STAGES)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.customer:
            return f"Lead for {self.customer.name} - {self.lead_stage}"
        return f"Lead: {self.name or 'Unnamed'} - {self.lead_stage}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


# --- Engagement Models ---
class Engagement(models.Model):
    ENGAGEMENT_TYPE = [
        ('Call', 'Call'),
        ('Email', 'Email'),
        ('Meeting', 'Meeting'),
        ('Website Visit', 'Website Visit'),
    ]

    customer = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    level_of_engagement = models.CharField(max_length=10, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    type_of_engagement = models.CharField(max_length=20, choices=ENGAGEMENT_TYPE)
    engagement_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Engagement with {self.customer.name} - {self.type_of_engagement}"


# --- Lifetime Value Models ---
class LifetimeValue(models.Model):
    customer = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    cost_to_acquire = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    worth_acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Lifetime Value for {self.customer.name}"

    def calculate_lifetime_value(self):
        """Calculates lifetime value based on revenue, purchase frequency, and length of customer."""
        purchases = ProductsPurchased.objects.filter(customer=self.customer)
        if purchases.exists():
            avg_purchase_value = purchases.aggregate(avg_value=Avg('amount_spent'))['avg_value']
            purchase_frequency = purchases.count()
            customer_length = InternalServices.get_average_customer_length(self.customer)
            self.lifetime_value = avg_purchase_value * purchase_frequency * customer_length
            return self.lifetime_value
        return 0

    def calculate_worth_acquisition(self):
        """Calculates worth acquisition cost as lifetime value - cost to acquire."""
        if self.lifetime_value and self.cost_to_acquire:
            self.worth_acquisition_cost = self.lifetime_value - self.cost_to_acquire
        return self.worth_acquisition_cost


# --- Internal Services Model ---
class InternalServices(models.Model):
    current_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    projected_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    past_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    current_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    projected_growth = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_customers = models.PositiveIntegerField(blank=True, null=True)
    average_length_of_customer = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    internal_churn_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    average_cost_to_acquire = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    average_revenue_per_customer = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    industry_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    average_lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return "Internal Services Data"

    @staticmethod
    def get_internal_churn_rate():
        """Calculates internal churn rate: (lost customers / total customers)."""
        return InternalServices.objects.aggregate(churn_rate=Avg('internal_churn_rate'))['churn_rate'] or 0

    @staticmethod
    def calculate_average_lifetime_value():
        """Calculates the average lifetime value for all customers."""
        lifetime_values = LifetimeValue.objects.aggregate(avg_lifetime_value=Avg('lifetime_value'))
        return lifetime_values['avg_lifetime_value'] or 0
