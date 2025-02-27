from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Product, Order
from django.urls import reverse

User = get_user_model()

class WarehouseTests(TestCase):

    def setUp(self):
        """Set up test users and products."""
        self.admin_user = User.objects.create_user(username="admin013", password="AdminAdmin#013", role="admin")
        self.employee_user = User.objects.create_user(username="employee01", password="HNfzAf3BzmXWIK0", role="employee")
        self.product = Product.objects.create(name="MacBook Pro", description="Apple Laptop", quantity=10, price=2000)
    
    def test_employee_cannot_create_product(self):
        """Ensure employees cannot add new products."""
        self.client.login(username="employee01", password="HNfzAf3BzmXWIK0")
        response = self.client.post(reverse("product_create"), {"name": "iPhone 16 Pro", "description": "Latest iPhone", "quantity": 5, "price": 1500})
        self.assertNotEqual(response.status_code, 200)  # Should be forbidden
    
    def test_admin_can_create_product(self):
        """Ensure admins can create a new product."""
        self.client.login(username="admin013", password="AdminAdmin#013")
        response = self.client.post(reverse("product_create"), {"name": "iPad Pro", "description": "Apple Tablet", "quantity": 10, "price": 1000})
        self.assertEqual(response.status_code, 302)  # Redirect means success
    
    def test_order_stock_update(self):
        """Ensure that placing an order reduces stock correctly."""
        self.client.login(username="employee01", password="HNfzAf3BzmXWIK0")
        order = Order.objects.create(product=self.product, quantity=2, ordered_by=self.employee_user, status="completed")
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 8)  # Stock should be reduced from 10 to 8
