from rest_framework.pagination import PageNumberPagination  



class ShortURLPagination(PageNumberPagination):

    page_size = 5  # Number of items per page
    page_size_query_param = "page_size"  # Allow client to set page size
    max_page_size = 20  # Maximum items per page
    