from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ADMIN = "admin"
    USER = "user"
    SUPPLIER = "supplier"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    ROLE_CHOICES = [
        (ADMIN, "Администратор"),
        (USER, "Пользователь"),
        (SUPPLIER, "Поставщик"),
        (EMPLOYEE, "Сотрудник"),
        (CUSTOMER, "Клиент"),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Имя пользователя",
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Эл. почта",
        help_text="Введите электронную почту",
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=150,
        blank=True,
        null=True,
        default="user",
        verbose_name="Роль",
        help_text="Выберите роль",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    yandex_oauth_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="Яндекс OAuth ID"
)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    # @property: Этот декоратор позволяет методам is_admin и is_moderator работать как атрибуты.
    # То есть, вы можете получить их значение, как если бы это были обычные атрибуты, а не методы.
    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_employee(self):
        return self.role == self.EMPLOYEE

    @property
    def is_supplier(self):
        return self.role == self.SUPPLIER

    @property
    def is_customer(self):
        return self.role == self.CUSTOMER
    
    @property
    def is_user(self):
        return self.role == self.USER


class Customer(models.Model):
    """Клиент"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=128)
    company_name = models.CharField(max_length=128)
    country = models.CharField(max_length=128)

    def __str__(self):
        return f"Клиент {self.contact_name}, {self.user.username}"


class Supplier(models.Model):
    """Поставщик"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="supplier"
    )  # Связь с пользователем
    name = models.CharField(max_length=128)
    contact_name = models.CharField(max_length=128)
    contact_phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Сотрудник"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee"
    )  # Связь с пользователем
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    phone = models.CharField(max_length=15)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
