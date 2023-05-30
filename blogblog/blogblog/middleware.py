from django.http import HttpResponseRedirect


class RemoveSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/' and request.path.endswith('/'):
            return HttpResponseRedirect(request.path[:-1])
        response = self.get_response(request)
        return response
