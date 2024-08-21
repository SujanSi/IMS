from django.contrib import admin
from .models import CompanyInfo,Category,Unit,Product,Stock,Order,OrderItem,ReturnProduct
# Register your models here.


admin.site.register(CompanyInfo)
admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ReturnProduct)