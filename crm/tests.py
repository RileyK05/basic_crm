from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import (
    CustomerInformation, Product, ProductsPurchased, CustomerLead, Engagement, LifetimeValue, InternalServices
)

class CustomerInformationTestCase(TestCase):

    def setUp(self):
        self.customer = CustomerInformation.objects.create(
            name="Test Customer",
            email="test@example.com",
            phone="1234567890",
            industry="Technology",
            company="Tech Co.",
            education="Bachelor's",
            income=100000.00,
        )

    def test_create_customer(self):
        customer = CustomerInformation.objects.get(email="test@example.com")
        self.assertEqual(customer.name, "Test Customer")

    def test_update_customer(self):
        self.customer.email = "new_email@example.com"
        self.customer.save()
        updated_customer = CustomerInformation.objects.get(email="new_email@example.com")
        self.assertEqual(updated_customer.email, "new_email@example.com")

    def test_delete_customer(self):
        self.customer.delete()
        self.assertEqual(CustomerInformation.objects.count(), 0)

    def test_customer_likelihood_to_churn_no_engagement(self):
        self.assertEqual(self.customer.likelihood_to_churn(), 0)


class ProductTestCase(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name="Product 1",
            description="This is a product.",
            price=49.99,
        )

    def test_create_product(self):
        product = Product.objects.get(name="Product 1")
        self.assertEqual(product.price, 49.99)

    def test_update_product(self):
        self.product.price = 59.99
        self.product.save()
        updated_product = Product.objects.get(name="Product 1")
        self.assertEqual(updated_product.price, 59.99)

    def test_delete_product(self):
        self.product.delete()
        self.assertEqual(Product.objects.count(), 0)


class CustomerLeadTestCase(TestCase):

    def setUp(self):
        self.customer = CustomerInformation.objects.create(
            name="Lead Customer",
            email="lead@example.com",
            phone="9876543210",
        )
        self.lead = CustomerLead.objects.create(
            customer=self.customer,
            status="Qualified",
            likelihood_to_convert=75.00,
            lead_stage="Negotiation",
        )

    def test_create_lead(self):
        lead = CustomerLead.objects.get(customer=self.customer)
        self.assertEqual(lead.status, "Qualified")

    def test_update_lead(self):
        self.lead.status = "Won"
        self.lead.save()
        updated_lead = CustomerLead.objects.get(customer=self.customer)
        self.assertEqual(updated_lead.status, "Won")

    def test_delete_lead(self):
        self.lead.delete()
        self.assertEqual(CustomerLead.objects.count(), 0)


class EngagementTestCase(TestCase):

    def setUp(self):
        self.customer = CustomerInformation.objects.create(
            name="Engaged Customer",
            email="engage@example.com",
            phone="1234509876",
        )
        self.engagement = Engagement.objects.create(
            customer=self.customer,
            level_of_engagement="Medium",
            type_of_engagement="Call",
            engagement_date=timezone.now(),
        )

    def test_create_engagement(self):
        engagement = Engagement.objects.get(customer=self.customer)
        self.assertEqual(engagement.level_of_engagement, "Medium")

    def test_update_engagement(self):
        self.engagement.level_of_engagement = "High"
        self.engagement.save()
        updated_engagement = Engagement.objects.get(customer=self.customer)
        self.assertEqual(updated_engagement.level_of_engagement, "High")

    def test_delete_engagement(self):
        self.engagement.delete()
        self.assertEqual(Engagement.objects.count(), 0)


class ProductsPurchasedTestCase(TestCase):

    def setUp(self):
        self.customer = CustomerInformation.objects.create(
            name="Purchasing Customer",
            email="purchase@example.com",
            phone="5550001112",
        )
        self.product = Product.objects.create(
            name="Purchase Product",
            price=19.99,
        )
        self.purchase = ProductsPurchased.objects.create(
            customer=self.customer,
            product=self.product,
            number_of_products_purchased=2,
            date_of_sale=timezone.now(),
            amount_spent=39.98,
        )

    def test_create_purchase(self):
        purchase = ProductsPurchased.objects.get(customer=self.customer)
        self.assertEqual(purchase.amount_spent, 39.98)

    def test_update_purchase(self):
        self.purchase.number_of_products_purchased = 3
        self.purchase.save()
        updated_purchase = ProductsPurchased.objects.get(customer=self.customer)
        self.assertEqual(updated_purchase.number_of_products_purchased, 3)

    def test_delete_purchase(self):
        self.purchase.delete()
        self.assertEqual(ProductsPurchased.objects.count(), 0)


class LifetimeValueTestCase(TestCase):

    def setUp(self):
        self.customer = CustomerInformation.objects.create(
            name="Lifetime Customer",
            email="lifetime@example.com",
            phone="5559998887",
        )
        self.lifetime_value = LifetimeValue.objects.create(
            customer=self.customer,
            lifetime_value=1000.00,
            cost_to_acquire=500.00,
            worth_acquisition_cost=500.00,
        )

    def test_calculate_lifetime_value(self):
        self.assertEqual(self.lifetime_value.calculate_lifetime_value(), 1000.00)

    def test_calculate_worth_acquisition_cost(self):
        self.assertEqual(self.lifetime_value.calculate_worth_acquisition(), 500.00)


class InternalServicesTestCase(TestCase):

    def setUp(self):
        self.internal_services = InternalServices.objects.create(
            current_revenue=500000.00,
            projected_revenue=600000.00,
            current_growth_rate=5.00,
            internal_churn_rate=2.00,
        )

    def test_internal_services_revenue(self):
        self.assertEqual(self.internal_services.current_revenue, 500000.00)

    def test_projected_revenue(self):
        self.assertEqual(self.internal_services.projected_revenue, 600000.00)
