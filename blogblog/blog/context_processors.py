# Context processor for displaying the user's authorization status in the site's DOM (used in base.html)
def auth(request):
    return {'user_authenticated': request.user.is_authenticated}


def canonical_url(request):
    return {'canonical_path': request.build_absolute_uri(request.path)}
