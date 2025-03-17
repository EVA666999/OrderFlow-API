from django.contrib.auth.password_validation import validate_password
from django.forms import ValidationError
from rest_framework import serializers

from .models import Customer, Employee, Supplier, User


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    # Обновление данных, которые могут быть изменены
    phone_number = serializers.CharField(required=False)  # Customers
    address = serializers.CharField(required=False)
    contact_name = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    country = serializers.CharField(required=False)

    name = serializers.CharField(required=False)  # Для Supplier
    contact_phone = serializers.CharField(required=False)  # Для Supplier

    first_name = serializers.CharField(required=False)  # Для Employee
    last_name = serializers.CharField(required=False)  # Для Employee
    phone = serializers.CharField(required=False)  # Для Employee
    salary = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )  # Для Employee

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "role",
            "password",
            "phone_number",
            "address",
            "contact_name",
            "company_name",
            "country",
            "name",
            "contact_phone",
            "first_name",
            "last_name",
            "phone",
            "salary",
        )

    def validate_password(self, value):
        """Валидация пароля (если передан)."""
        if value:
            validate_password(value)
        return value

    def validate_role(self, value):
        """Запрещаем обычным пользователям выбирать административные роли, но разрешаем это админам."""
        user = self.context["request"].user  # Получаем текущего пользователя

        if (
            user.is_staff and value == User.ADMIN
        ):  # Если это админ, роль может быть изменена на ADMIN
            return value

        if value == User.ADMIN:  # Если пользователь не админ, запретим роль ADMIN
            raise serializers.ValidationError(
                "Нельзя выбрать роль ADMIN для обычных пользователей."
            )

        return value

    def update(self, instance, validated_data):
        """Обновляем данные пользователя и обрабатываем пароль отдельно."""
        password = validated_data.get("password")
        if password:
            instance.set_password(password)  # Обновляем пароль, если передан

        # Обновление полей пользователя
        for field, value in validated_data.items():
            if field != "password":  # Не обновляем пароль
                setattr(instance, field, value)

        # Теперь нужно обработать обновление данных для связанных моделей, например, для Employee, Supplier, Customer
        if instance.role == User.EMPLOYEE:
            # Обновление данных Employee
            employee_data = {
                "first_name": validated_data.get("first_name"),
                "last_name": validated_data.get("last_name"),
                "phone": validated_data.get("phone"),
                "salary": validated_data.get("salary"),
            }
            employee = instance.employee  # Получаем связанную модель Employee
            for key, value in employee_data.items():
                if value:
                    setattr(employee, key, value)
            employee.save()

        elif instance.role == User.SUPPLIER:
            # Обновление данных Supplier
            supplier_data = {
                "name": validated_data.get("name"),
                "contact_name": validated_data.get("contact_name"),
                "contact_phone": validated_data.get("contact_phone"),
                "address": validated_data.get("address"),
            }
            supplier = instance.supplier  # Получаем связанную модель Supplier
            for key, value in supplier_data.items():
                if value:
                    setattr(supplier, key, value)
            supplier.save()

        elif instance.role == User.CUSTOMER:
            # Обновление данных Customer
            customer_data = {
                "phone_number": validated_data.get("phone_number"),
                "address": validated_data.get("address"),
                "contact_name": validated_data.get("contact_name"),
                "company_name": validated_data.get("company_name"),
                "country": validated_data.get("country"),
            }
            print(customer_data)
            customer = instance.customer  # Получаем связанную модель Customer
            for key, value in customer_data.items():
                if value:
                    setattr(customer, key, value)
            customer.save()

        instance.save()  # Сохраняем пользователя после изменений
        return instance


class CustomUserCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    password = serializers.CharField(write_only=True, required=True)

    # Обязательные поля для разных ролей
    phone_number = serializers.CharField(required=False)  # customers
    address = serializers.CharField(required=False)
    contact_name = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    country = serializers.CharField(required=False)

    name = serializers.CharField(required=False)  # Обязательно для Supplier
    contact_phone = serializers.CharField(required=False)  # Обязательно для Supplier

    first_name = serializers.CharField(required=False)  # Обязательно для Employee
    last_name = serializers.CharField(required=False)  # Обязательно для Employee
    phone = serializers.CharField(required=False)  # Обязательно для Employee
    salary = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )  # Обязательно для Employee

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "role",
            "password",
            "phone_number",
            "address",
            "contact_name",
            "company_name",
            "country",
            "name",
            "contact_phone",
            "first_name",
            "last_name",
            "phone",
            "salary",
        )

    def to_representation(self, instance):
        """Добавляем дополнительные поля в вывод."""
        data = super().to_representation(instance)

        if (
            instance.role == User.SUPPLIER
            or instance.role == User.EMPLOYEE
            or instance.role == User.CUSTOMER
        ):
            supplier = getattr(
                instance, "supplier", None
            )  # Проверяем, есть ли у User связанный Supplier
            employee = getattr(
                instance, "employee", None
            )  # Проверяем, есть ли у User связанный Employee
            customer = getattr(
                instance, "customer", None
            )  # Проверяем, есть ли у User связанный Customer
            if supplier:
                data.update(
                    {
                        "name": supplier.name,
                        "contact_name": supplier.contact_name,
                        "contact_phone": supplier.contact_phone,
                        "address": supplier.address,
                    }
                )
            elif customer:
                data.update(
                    {
                        "phone_number": customer.phone_number,
                        "address": customer.address,
                        "contact_name": customer.contact_name,
                        "company_name": customer.company_name,
                        "country": customer.country,
                    }
                )
            elif employee:
                data.update(
                    {
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "phone": employee.phone,
                        "salary": employee.salary,
                    }
                )

        return data

    def validate_role(self, value):
        """Запрещаем обычным пользователям выбирать административные роли."""
        if value in [User.ADMIN]:  # Запрещаем эти роли
            raise serializers.ValidationError("Нельзя выбрать эту роль.")
        return value

    def validate(self, data):
        """Проверяем, что для выбранной роли заполнены обязательные поля."""
        role = data.get("role")

        # Проверка обязательных полей для роли 'Customer'
        if role == User.CUSTOMER:
            required_fields = [
                "phone_number",
                "address",
                "contact_name",
                "company_name",
                "country",
            ]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValidationError(
                    f"Вы выбрали роль 'Customer'. Пожалуйста, заполните следующие поля: {', '.join(missing_fields)}."
                )

        # Проверка обязательных полей для роли 'Supplier'
        elif role == User.SUPPLIER:
            required_fields = ["name", "contact_name", "contact_phone", "address"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValidationError(
                    f"Вы выбрали роль 'Supplier'. Пожалуйста, заполните следующие поля: {', '.join(missing_fields)}."
                )

        elif role == User.EMPLOYEE:
            required_fields = ["first_name", "last_name", "phone", "salary"]

            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValidationError(
                    f"Вы выбрали роль 'employee'. Пожалуйста, заполните следующие поля: {', '.join(missing_fields)}."
                )

        # Проверка для других ролей, если нужно

        return data

    def validate_password(self, value):
        """Валидация пароля (если передан)."""
        if value:
            validate_password(value)
        return value

    def validate_email(self, value):
        """Валидация пароля (если передан)."""
        if value:
            validate_password(value)
        return value

    def update(self, instance, validated_data):
        """Обновляем данные пользователя и обрабатываем пароль отдельно."""
        password = validated_data.get("password")
        if password:
            instance.set_password(password)  # Если пароль передан, обновляем его

        # Обновляем остальные поля
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    def create(self, validated_data):
        """Создаем пользователя и его дополнительные данные в зависимости от роли."""

        # Извлекаем пароль
        password = validated_data.pop("password")

        # Шаг 1: Создаем пользователя
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=password,
            role=validated_data["role"],
        )

        # Шаг 2: Проверяем роль пользователя и создаем или обновляем информацию о нем

        if user.role == User.CUSTOMER:
            # Для роли 'Customer' нужно создать или обновить информацию о клиенте
            customer_data = {
                "phone_number": validated_data.get("phone_number"),
                "address": validated_data.get("address"),
                "contact_name": validated_data.get("contact_name"),
                "company_name": validated_data.get("company_name"),
                "country": validated_data.get("country"),
            }
            # Если клиент уже есть, обновим его данные. Если нет — создадим.
            customer, created = Customer.objects.get_or_create(
                user=user, defaults=customer_data
            )
            if not created:
                # Если клиент уже существует, обновляем его данные
                for key, value in customer_data.items():
                    setattr(customer, key, value)
                customer.save()

        elif user.role == User.SUPPLIER:
            # Для роли 'Supplier' (Поставщик) создаем или обновляем информацию о поставщике
            supplier_data = {
                "name": validated_data.get("name"),
                "contact_name": validated_data.get("contact_name"),
                "contact_phone": validated_data.get("contact_phone"),
                "address": validated_data.get("address"),
            }
            supplier, created = Supplier.objects.get_or_create(
                user=user, defaults=supplier_data
            )
            if not created:
                # Если поставщик уже существует, обновляем его данные
                for key, value in supplier_data.items():
                    setattr(supplier, key, value)
                supplier.save()

        elif user.role == User.EMPLOYEE:
            # Для роли 'Employee' (Сотрудник) создаем или обновляем информацию о сотруднике
            employee_data = {
                "first_name": validated_data.get("first_name"),
                "last_name": validated_data.get("last_name"),
                "phone": validated_data.get("phone"),
                "salary": validated_data.get("salary"),
            }
            employee, created = Employee.objects.get_or_create(
                user=user, defaults=employee_data
            )
            if not created:
                # Если сотрудник уже существует, обновляем его данные
                for key, value in employee_data.items():
                    setattr(employee, key, value)
                employee.save()

        # Возвращаем пользователя
        return user


class Usersermeializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
