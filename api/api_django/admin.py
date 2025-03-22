from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Category, Discount, Order, OrderProduct, Product,
                     ProductReview, PurchaseHistory, User)


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["id", "username", "email", "first_name", "last_name", "role"]
    list_filter = ["role"]
    search_fields = ["username", "email"]
    ordering = ["username"]


admin.site.register(User, CustomUserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "pub_date",
        "video",
        "image",
    )
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "pub_date", "discount")
    list_filter = ("pub_date",)
    search_fields = ("user__username",)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "customer",
        "rating",
        "comment",
        "sentiment",
        "created_at",
        "video",
        "image",
    )
    list_filter = ("rating", "created_at")
    search_fields = (
        "product__name",
        "customer__user__username",
        "comment",
        "sentiment",
    )


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    ]
    search_fields = ["code"]


@admin.register(PurchaseHistory)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order",
        "product",
        "price",
        "quantity",
        "purchase_date",
    )
    list_filter = ("user", "purchase_date")
    search_fields = ("user__username", "product__name")
