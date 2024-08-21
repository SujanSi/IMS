from django import forms
from.models import CompanyInfo, Category, Unit ,Product,Stock, Order, OrderItem,ReturnProduct
from django.contrib.auth.forms import UserCreationForm
from core.models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email','username','password1','password2']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['name', 'address', 'city', 'phone', 'email']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields =['code', 'category', 'name', 'unit', 'description', 'price']

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'quantity']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'price', 'quantity','unit_name']


class ReturnProductForm(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = ['order_item', 'reason', 'image', 'returned_quantity']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'returned_quantity': forms.NumberInput(attrs={'step': 1}),
        }

class UpdateReturnStatusForm(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = ['status']