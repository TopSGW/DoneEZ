from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    # Default page size
    page_size = 10
    # Allow client to set the page size using this query parameter
    page_size_query_param = 'page_size'
    # Maximum page size to prevent excessive data retrieval
    max_page_size = 100
    # Query parameter for the page number
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
