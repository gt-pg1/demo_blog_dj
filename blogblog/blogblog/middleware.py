from django.http import HttpResponseRedirect
from django.urls import resolve


class RemoveSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url_name = resolve(request.path_info).namespace
        if url_name != 'admin' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if request.path != '/' and request.path.endswith('/'):
                return HttpResponseRedirect(request.path[:-1])
        response = self.get_response(request)
        return response
