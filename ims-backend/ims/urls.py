from django.urls import path
from . import views
from .views import (
    IndexView, LoginView, SignupView, LogoutView,CompanyListView, CompanyCreateView, 
    CompanyUpdateView, CompanyDeleteView,CategoryListView, CategoryCreateView, 
    CategoryUpdateView,ProductListView, ProductCreateView, 
    ProductUpdateView,UnitListView,UnitCreateView, UnitUpdateView, StockListView, StockCreateView, StockUpdateView,)

urlpatterns = [

    path("", IndexView.as_view(), name="home"),
    path('login/', LoginView.as_view(), name='login_view'),
    path('signup/', SignupView.as_view(), name='signup_view'),
    path('logout/', LogoutView.as_view(), name="logout_view"),

    path('company/', CompanyListView.as_view(), name='company'),
    path('company_create/', CompanyCreateView.as_view(), name='company_create'),
    path('company_update/<int:pk>/', CompanyUpdateView.as_view(), name="company_update"),
    path('company_delete/<int:pk>/', CompanyDeleteView.as_view(), name="company_delete"),

    path('category/', CategoryListView.as_view(), name='category'),
    path('category_create/', CategoryCreateView.as_view(), name='category_create'),
    path('category_update/<int:pk>/', CategoryUpdateView.as_view(), name="category_update"),
    path('category_delete/<int:pk>/', views.category_delete, name="category_delete"),

    path('product/', ProductListView.as_view(), name='product'),
    path('product_create/', ProductCreateView.as_view(), name='product_create'),
    path('product_update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('product_delete/<int:pk>/', views.product_delete, name="product_delete"),

    path('unit/', UnitListView.as_view(), name='unit'),
    path('unit_create/', UnitCreateView.as_view(), name='unit_create'),
    path('unit_update/<int:pk>/', UnitUpdateView.as_view(), name='unit_update'),
    path('unit_delete/<int:pk>/', views.unit_delete, name="unit_delete"),

    path('stock/', StockListView.as_view(), name='stock'),
    path('stock_create/', StockCreateView.as_view(), name='stock_create'),
    path('stock_update/<int:pk>/', StockUpdateView.as_view(), name='stock_update'),
    path('stock_delete/<int:pk>/', views.stock_delete, name="stock_delete"),



    path('final_cart/', views.final_cart, name='final_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('category_list/', views.category_list, name='category_list'),
    

    path('return_product/', views.return_product, name='return_product'),
    path('return_status/', views.return_status, name='return_status'),
    
    path('admin-return-status/', views.admin_return_status, name='admin_return_status'),
    path('return-status/update/<int:pk>/', views.update_return_status, name='update_return_status'),

]
