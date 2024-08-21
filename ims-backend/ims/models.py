from django.db import models
from django.utils import timezone
from core.models import User
from django.core.validators import FileExtensionValidator

# Create your models here.


class BaseModel(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CompanyInfo(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = phone = models.CharField(max_length=20, null=True, blank=True) 
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, default = 1)

    def __str__(self):
        return self.name

class Category(BaseModel):
    name = models.CharField(max_length=250)
    description = models.TextField()

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

     

class Product(BaseModel):
    code = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=0)
    name=models.CharField(max_length=250,blank=True, null=True)
    unit=models.ForeignKey(Unit,on_delete=models.CASCADE)
    description = models.TextField()
    price = models.FloatField(default=0)
    status = models.CharField(max_length=10, default="active")

    def __str__(self):
        return self.name if self.name else "Unnamed Product"


class Stock(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places= 2)
    to_gram = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}" if self.product and self.product.name else "Unnamed Stock"
    

class Order(BaseModel):
    customer = models.CharField(max_length = 250)

    def __str__(self):
        return self.customer
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank= True, null= True)
    price = models.FloatField(default=0)
    quantity = models.DecimalField(max_digits=20, decimal_places= 2)
    unit_name = models.CharField(max_length=20, default=0)
    to_gram = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"OrderItem #{self.pk} - Product: {self.product.name} - Quantity: {self.quantity}"


class ReturnProduct(BaseModel):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    reason = models.TextField(verbose_name="Reason for Return")
    status = models.CharField(max_length=50, choices=[
        ("PENDING", "Pending Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ], default="PENDING")
    returned_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date_returned = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='return_images/', blank=True, null=True)
    returned_quantity = models.DecimalField(max_digits=20,decimal_places=2)

    
    def __str__(self):
        return f"Return #{self.pk} - Order Item: {self.order_item}"