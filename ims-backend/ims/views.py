from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import CompanyInfo,Category,Unit,Product,Stock,Order,OrderItem,ReturnProduct
from .forms import LoginForm, SignupForm, CompanyInfoForm, CategoryForm, UnitForm, ProductForm, StockForm, OrderForm, OrderItemForm, ReturnProductForm, UpdateReturnStatusForm,ReturnProductForm
from decimal import Decimal
from django.core.paginator import Paginator
from core.pagination import paginate_queryset
from decimal import Decimal, ROUND_DOWN
from django.db.models import Sum, Count
from core.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

# Create your views here.


class IndexView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products_with_stock = []

        total_products = Product.objects.count()
        total_companies = CompanyInfo.objects.count()
        total_order_items = OrderItem.objects.filter(order__customer=request.user.username).count()

        print(f"User: {request.user.username}")
        print(f"Total Products: {total_products}")
        print(f"Total Companies: {total_companies}")
        print(f"Total Order Items: {total_order_items}")

        for category in categories:
            for product in category.product_set.all():
                stock = Stock.objects.filter(product=product).first()
                available_stock = stock.quantity if stock else 0
                products_with_stock.append({
                    'category': category,
                    'product': product,
                    'available_stock': available_stock
                })

        chart_labels = ['Categories', 'Products', 'Companies', 'Order Items']
        chart_values = [categories.count(), total_products, total_companies, total_order_items]

        context = {
            'categories': categories,
            'products_with_stock': products_with_stock,
            'total_products': total_products,
            'total_order_items': total_order_items,
            'total_companies': total_companies,
            'chart_labels': chart_labels,
            'chart_values': chart_values,
        }

        return render(request, 'index.html', context)



class SignupView(View):
    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
        return render(request, 'signup.html', {'form': form})
    



class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if CompanyInfo.objects.filter(user=user).exists():
                    return redirect('home')
                else:
                    return redirect('company_create')
            else:
                messages.error(request, "Invalid username or password.") 
        return render(request, 'login.html', {"form": form})
    


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login_view')
    
#end of user authentication


class CompanyListView(LoginRequiredMixin, ListView):
    model = CompanyInfo
    template_name = 'company.html'
    context_object_name = 'companies'
    paginate_by = 10

class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = CompanyInfo
    form_class = CompanyInfoForm
    template_name = 'add_company.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = CompanyInfo
    form_class = CompanyInfoForm
    template_name = 'company_update.html'
    success_url = reverse_lazy('company')

class CompanyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        company = get_object_or_404(CompanyInfo, pk=pk)
        company.delete()
        return redirect('company')
#end of company CRUD


class CategoryListView(LoginRequiredMixin,ListView):
    permission_required = 'ims.view_category'
    model = Category
    template_name = 'category.html'
    context_object_name = 'categories'

    def get_paginate_by(self, queryset=None):
        # Return the number of items per page from the query parameters or default to 2
        return self.request.GET.get('items_per_page', 2)

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Stock.objects.filter(product__name__icontains=query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items_per_page'] = self.get_paginate_by()
        return context

@method_decorator(permission_required('ims.add_category'), name='dispatch')
class CategoryCreateView(LoginRequiredMixin, CreateView):
    permission_required = 'ims.add_category'
    model = Category
    form_class = CategoryForm
    template_name = 'add_category.html'
    success_url = reverse_lazy('category')

@method_decorator(permission_required('ims.change_category'), name='dispatch')
class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'ims.change_category'
    model = Category
    form_class = CategoryForm
    template_name = 'category_update.html'
    success_url = reverse_lazy('category')

@login_required
@permission_required('ims.delete_category')
def category_delete(request, pk):
    categories = Category.objects.get(id = pk)
    categories.delete()
    return redirect('category')

#end of category-CRUD




#start of product-CRUD
class ProductListView(LoginRequiredMixin, ListView):
    permission_required = 'ims.view_product'
    model = Product
    template_name = 'product.html'
    context_object_name = 'products'

    def get_paginate_by(self, queryset=None):
        # Return the number of items per page from the query parameters or default to 2
        return self.request.GET.get('items_per_page', 2)

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Stock.objects.filter(product__name__icontains=query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items_per_page'] = self.get_paginate_by()
        return context
    

@method_decorator(permission_required('ims.add_product'), name='dispatch')
class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'ims.add_product'
    model = Product
    form_class = ProductForm
    template_name = 'product_create.html'
    success_url = reverse_lazy('product')

@method_decorator(permission_required('ims.change_product'), name='dispatch')
class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'ims.change_product'
    model = Product
    form_class = ProductForm
    template_name = 'product_update.html'
    success_url = reverse_lazy('product')


@login_required
@permission_required('ims.delete_product')
def product_delete(request,pk):
    product  = Product.objects.get(pk=pk)
    product.delete()
    return redirect('product')

#end of product-CRUD


#start of Unit-CRUD
class UnitListView(LoginRequiredMixin,ListView):
    permission_required = 'ims.view_unit'
    model = Unit
    template_name = 'unit.html'
    context_object_name = 'units'

    def get_paginate_by(self, queryset=None):
        # Return the number of items per page from the query parameters or default to 2
        return self.request.GET.get('items_per_page', 2)

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Stock.objects.filter(product__name__icontains=query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items_per_page'] = self.get_paginate_by()
        return context
    

@method_decorator(permission_required('ims.add_unit'), name='dispatch')
class UnitCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'ims.add_unit'
    model = Unit
    form_class = UnitForm
    template_name = 'unit_create.html'
    success_url = reverse_lazy('unit')

@method_decorator(permission_required('ims.change_unit'), name='dispatch')
class UnitUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'ims.change_unit'
    model = Unit
    form_class = UnitForm
    template_name = 'unit_update.html'
    success_url = reverse_lazy('unit')


@login_required
@permission_required('ims.delete_unit')
def unit_delete(request,pk):
    unit  = Unit.objects.get(pk=pk)
    unit.delete()
    return redirect('unit')

#end of Unit-CRUD




#start of Stock-Crud
class StockListView(LoginRequiredMixin, ListView):
    permission_required = 'ims.view_stock'
    model = Stock
    template_name = 'stock.html'
    context_object_name = 'stocks'

    def get_paginate_by(self, queryset=None):
        # Return the number of items per page from the query parameters or default to 2
        return self.request.GET.get('items_per_page', 2)

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Stock.objects.filter(product__name__icontains=query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items_per_page'] = self.get_paginate_by()
        return context

@method_decorator(permission_required('ims.add_stock'), name='dispatch')
class StockCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'ims.add_stock'
    model = Stock
    form_class = StockForm
    template_name = 'stock_create.html'
    success_url = reverse_lazy('stock')

@method_decorator(permission_required('ims.change_stock'), name='dispatch')
class StockUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'ims.change_stock'
    model = Stock
    form_class = StockForm
    template_name = 'stock_update.html'
    success_url = reverse_lazy('stock')


@login_required
@permission_required('ims.delete_stock')
def stock_delete(request,pk):
    stock  = Stock.objects.get(pk=pk)
    stock.delete()
    return redirect('stock')

#end of Stock-Crud


def convert_to_grams(quantity, unit_name):
    unit_name = unit_name.lower()
    if unit_name == 'gram':
        return quantity
    elif unit_name == 'kg':
        return quantity * Decimal('1000')
    elif unit_name == 'pound':
        return quantity * Decimal('453.592')
    elif unit_name == 'ounce':
        return quantity * Decimal('28.3495')
    elif unit_name == 'mg':
        return quantity * Decimal('0.001')
    elif unit_name == 'liter':
        return quantity * Decimal('1000')
    elif unit_name == 'cc' or unit_name == 'cubic centimeter':
        return quantity
    elif unit_name == 'gallon':
        return quantity * Decimal('3785.41')
    elif unit_name == 'packet':
        return quantity  # Treat packet as a standard unit, no conversion needed
    else:
        raise ValueError(f"Unit {unit_name} not recognized for conversion to grams")

def convert_from_grams(quantity_in_grams, unit_name):
    unit_name = unit_name.lower()
    if unit_name == 'gram':
        return quantity_in_grams
    elif unit_name == 'kg':
        return quantity_in_grams / Decimal('1000')
    elif unit_name == 'pound':
        return quantity_in_grams / Decimal('453.592')
    elif unit_name == 'ounce':
        return quantity_in_grams / Decimal('28.3495')
    elif unit_name == 'mg':
        return quantity_in_grams / Decimal('0.001')
    elif unit_name == 'liter':
        return quantity_in_grams / Decimal('1000')
    elif unit_name == 'cc' or unit_name == 'cubic centimeter':
        return quantity_in_grams
    elif unit_name == 'gallon':
        return quantity_in_grams / Decimal('3785.41')
    elif unit_name == 'packet':
        return quantity_in_grams  # Treat packet as a standard unit, no conversion needed
    else:
        raise ValueError(f"Unit {unit_name} not recognized for conversion from grams")
    

from django.db import transaction

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            product_id = request.POST.get('product_id')
            quantity = Decimal(request.POST.get('quantity'))
            unit_name = request.POST.get('unit_name').lower()

            print(unit_name)

            # Retrieve product, order, and related stock
            product = get_object_or_404(Product, pk=product_id)
            order, created = Order.objects.get_or_create(customer=request.user.username)
            order_item = OrderItem.objects.filter(order=order, product=product).first()
            stock = get_object_or_404(Stock, product=product)

            if unit_name != stock.product.unit.name and unit_name != 'packet':
                converted_quantity = convert_to_grams(quantity, unit_name)
            else:
                # No conversion needed for packets or same unit as stock
                converted_quantity = quantity  

            if product.unit.name.lower() == 'packet':
                if unit_name != 'packet':
                    raise ValueError(f"This product must be ordered in units of 'packet'.")
                converted_quantity = quantity  # No conversion needed for 'packet'
            else:
                if unit_name == 'packet':
                    raise ValueError(f"This product cannot be ordered in units of 'packet'.")
                
            # Check if the converted quantity exceeds the available stock in grams
            if stock.to_gram < converted_quantity:
                messages.error(request, f"Not enough stock available for {product.name}")
                return redirect('category_list')

            if unit_name == 'packet':
                total_price = Decimal(product.price)
            elif unit_name == stock.product.unit.name.lower():
                total_price = Decimal(product.price) * Decimal(quantity)
            else:
                # Calculate unit price in grams
                unit_price_in_grams = Decimal(product.price) / convert_to_grams(Decimal('1'), product.unit.name)
                total_price = unit_price_in_grams * converted_quantity


            # Perform the operations within a transaction to ensure consistency
            with transaction.atomic():
                existing_order_item = OrderItem.objects.filter(order=order, product=product, unit_name=unit_name).first()
                if existing_order_item:
                    # If the order item exists, update the quantity and to_gram
                    existing_order_item.quantity = Decimal(str(existing_order_item.quantity)) + Decimal(quantity)
                    existing_order_item.price = Decimal(existing_order_item.price) + total_price  # Convert existing_order_item.price to Decimal
                    existing_order_item.to_gram = Decimal(str(existing_order_item.to_gram)) + Decimal(converted_quantity)
                    existing_order_item.save()
                    messages.success(request, f"Quantity of {product.name} updated in your cart.")
                else:
                    # If the order item doesn't exist, create a new one
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=total_price,
                        unit_name=unit_name,
                        to_gram=converted_quantity
                    )
                    messages.success(request, f"{product.name} added to your cart.")
                # Deduct from stock quantity in base unit (kg) and grams
                if unit_name != stock.product.unit.name:
                    # Convert back the consumed stock quantity to the base unit (kg)
                    converted_stock_quantity = convert_from_grams(converted_quantity, product.unit.name)
                else:
                    converted_stock_quantity = quantity

                # Deduct from stock quantity in base unit (kg)
                stock.quantity -= converted_stock_quantity
                

                # Deduct from stock quantity in grams exactly as ordered
                stock.to_gram -= converted_quantity

                # Save the updated stock
                stock.save()

            return redirect('final_cart')

        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('category_list')
        except Stock.DoesNotExist:
            messages.error(request, f"No stock available for {product.name}.")
            return redirect('category_list')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('category_list')
    else:
        return redirect('category_list')
    
     

@login_required  
def final_cart(request):
    order = Order.objects.filter(customer=request.user.username).first()
    order_items = OrderItem.objects.filter(order=order) if order else []
    company_info = CompanyInfo.objects.get(user=request.user)

    subtotal = Decimal('0.00')
    for order_item in order_items:
        # Convert price and quantity to Decimal and format to two decimal places
        price = Decimal(order_item.price).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        quantity = Decimal(order_item.quantity).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        total = (price * quantity).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

        order_item.price = price
        order_item.quantity = quantity
        order_item.total = total
        subtotal += total

    vat_rate = Decimal('0.20')  # Assuming 20% VAT rate
    vat_due = (subtotal * vat_rate).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    total_due = (subtotal + vat_due).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

    context = {
        'order_items': order_items,
        'subtotal': subtotal,
        'vat_rate': vat_rate,
        'vat_due': vat_due,
        'total_due': total_due,
        'user': request.user,
        'company_info': company_info
    }

    return render(request, 'final_cart.html', context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    products_with_stock = []
    units = Unit.objects.all()

    for category in categories:
        for product in category.product_set.all():
            stock = Stock.objects.filter(product=product).first()
            available_stock = stock.quantity if stock else 0
            products_with_stock.append({
                'category': category,
                'product': product,
                'available_stock': available_stock,
                'price': product.price
            })

    context = {
        'categories': categories,
        'products_with_stock': products_with_stock,
         'units': units
    }
    return render(request, 'product_list.html', context)



def return_product(request):
    if request.method == "POST":
        form = ReturnProductForm(request.POST, request.FILES)
        if form.is_valid():
            return_product = form.save(commit=False)
            return_product.returned_by = request.user
            return_product.save()
            messages.success(request, 'Return request submitted successfully.')
            return redirect('home')  # Adjust to your order detail view
    else:
        form = ReturnProductForm()

    return render(request, 'return_product.html', {'form': form})


@login_required
def return_status(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page')
    items_per_page = request.GET.get('items_per_page', 3)
    
    return_products = ReturnProduct.objects.filter(returned_by=request.user)
    
    if query:
        return_products = return_products.filter(order_item__product__name__icontains=query)
    
    paginator = Paginator(return_products, items_per_page)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'return_status.html', {
        'return_products': page_obj.object_list,
        'page_obj': page_obj,
        'items_per_page': items_per_page,
        'query': query
    })





def admin_return_status(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page')
    items_per_page = request.GET.get('items_per_page', 5)

    return_products = ReturnProduct.objects.all()

    if query:
        return_products = return_products.filter(order_item__product__name__icontains=query)

    paginator = Paginator(return_products, items_per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_check_return.html', {
        'return_products': page_obj.object_list,
        'page_obj': page_obj,
        'items_per_page': items_per_page,
        'query': query
    })

@login_required
def update_return_status(request, pk):
    return_product = get_object_or_404(ReturnProduct, pk=pk)
    
    if request.method == "POST":
        form = UpdateReturnStatusForm(request.POST, instance=return_product)
        if form.is_valid():
            return_product = form.save()
            
            # Get the related order item and stock
            order_item = return_product.order_item
            product = order_item.product
            stock = get_object_or_404(Stock, product=product)
            
            # Calculate the returned quantity in grams
            returned_quantity = return_product.returned_quantity
            returned_unit_name = order_item.unit_name
            
            if returned_unit_name != 'packet':
                converted_returned_quantity = convert_to_grams(returned_quantity, returned_unit_name)
            else:
                converted_returned_quantity = returned_quantity  # No conversion needed for packet

            # Convert the quantity back to the original unit of the product
            if product.unit.name.lower() != 'packet':
                converted_returned_stock_quantity = convert_from_grams(converted_returned_quantity, product.unit.name)
            else:
                converted_returned_stock_quantity = returned_quantity  # No conversion needed for packet
            
            # Perform the operations within a transaction to ensure consistency
            with transaction.atomic():
                # Update the stock
                stock.quantity += converted_returned_stock_quantity
                stock.to_gram += converted_returned_quantity
                stock.save()
            
            messages.success(request, 'Return status updated successfully and stock adjusted.')
            return redirect('admin_return_status')
    else:
        form = UpdateReturnStatusForm(instance=return_product)
    
    return render(request, 'update_return_status.html', {'form': form})