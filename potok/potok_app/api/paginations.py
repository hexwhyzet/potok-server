from rest_framework.pagination import PageNumberPagination


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10


class MediumResultsSetPagination(PageNumberPagination):
    page_size = 25


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
