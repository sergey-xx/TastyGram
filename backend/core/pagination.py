from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class CustomPagination(PageNumberPagination):
    """Кастомный Пагинатор."""

    page_size_query_param = 'limit'
    page_size = settings.PAGE_SIZE
