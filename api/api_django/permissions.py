from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthor(permissions.BasePermission):
    """
    Разрешение, которое дает доступ только автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ только если пользователь является автором объекта
        return (
            obj.user == request.user
        )  # Проверка, что объект принадлежит текущему пользователю


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение, которое позволяет только администраторам изменять данные,
    а для всех остальных доступ только для чтения (например, GET).
    """

    def has_permission(self, request, view):
        # Если метод безопасный (например, GET, HEAD, OPTIONS), разрешаем доступ
        if request.method in SAFE_METHODS:
            return True
        # Если метод не безопасный, проверяем, является ли пользователь администратором
        return request.user and request.user.is_staff


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_supplier


class IsSupplier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_supplier


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_customer


class IsAdminOrEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_employee  # Админ или сотрудник


class IsAdminOrSupplier(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_supplier  # Админ или сотрудник


class IsAdminOrCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_customer
        )


class IsAdminOrAuthenticated(BasePermission):
    """
    Разрешение, которое проверяет, что пользователь является администратором
    или аутентифицированным пользователем.
    """

    def has_permission(self, request, view):
        # Проверяем, что пользователь либо администратор, либо аутентифицирован
        return request.user.is_staff or request.user.is_authenticated
