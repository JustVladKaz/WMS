from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
import bleach

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('employee', 'Employee'),]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        self.description = bleach.clean(self.description, tags=["b", "i", "u", "p", "br"], strip=True)
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),]
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    def save(self, *args, **kwargs):
        if self.pk:
            previous_order = Order.objects.get(pk=self.pk)
        else:
            previous_order = None
        if previous_order is None:
            product = self.product
            if product.quantity >= self.quantity:
                product.quantity -= self.quantity
                product.save()
            else:
                raise ValueError("Not enough stock available!")
        elif previous_order.status != "canceled" and self.status == "canceled":
            product = self.product
            product.quantity += self.quantity
            product.save()
        elif previous_order.status == "canceled" and self.status != "canceled":
            product = self.product
            if product.quantity >= self.quantity:
                product.quantity -= self.quantity
                product.save()
            else:
                raise ValueError("Not enough stock available!")
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"Order {self.id} - {self.product.name} - {self.status.capitalize()}"

class Report(models.Model):
    REPORT_TYPES = [
        ('sales', 'Sales Report'),
        ('low_stock', 'Low Stock Report'),]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(default="")
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"
