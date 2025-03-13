from django.contrib import admin

from .models import Customer, Employee, Supplier


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "contact_name",
        "phone_number",
        "address",
        "company_name",
        "country",
    )
    search_fields = ("user__username", "contact_name", "company_name")
    list_filter = ("country",)


class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "contact_phone", "created_at")
    search_fields = ("name", "contact_name", "contact_email")
    list_filter = ("created_at",)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "salary")
    search_fields = ("first_name", "last_name")
    list_filter = ("salary",)


# Регистрируем модели в админке
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Employee, EmployeeAdmin)
