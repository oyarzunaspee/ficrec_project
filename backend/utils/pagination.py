from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    
    def get_page_number(self, request, paginator):
        page_number = request.query_params.get("page") or 1
        self.current = int(page_number)
        if self.current < paginator.num_pages:
            self.next = self.current + 1
        else:
            self.next = None
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number
    
    def get_paginated_response(self, data):
        return Response({
            "pages": self.page.paginator.num_pages,
            "current": self.current,
            "next": self.next,
            "results": data,
        })