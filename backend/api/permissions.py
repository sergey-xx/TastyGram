from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Доступ разрешен только для суперпользователей, администраторов, авторов.
    объектов или пользователей с ролью модератора. Остальные пользователи
    могут только просматривать объекты, но не редактировать или удалять их.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
        )
