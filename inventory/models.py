
from django.db import models


class Product(models.Model):

    product_name = models.CharField(max_length=100)

    category = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField(default=0)

    minimum_stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name


class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)

    customer = models.CharField(max_length=100)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"Order #{self.order_id}"


class StockTransaction(models.Model):

    TRANSACTION_TYPES = [
        ('Stock In', 'Stock In'),
        ('Stock Out', 'Stock Out'),
    ]

    transaction_id = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    quantity = models.PositiveIntegerField()

    previous_quantity = models.PositiveIntegerField()

    updated_quantity = models.PositiveIntegerField()

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.product_name} - {self.transaction_type}"


class Alert(models.Model):

    ALERT_TYPES = [
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    ]

    STATUS_CHOICES = [
        ('Unread', 'Unread'),
        ('Read', 'Read'),
        ('Resolved', 'Resolved'),
    ]

    alert_id = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPES
    )

    message = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Unread'
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.product_name} - {self.alert_type}"