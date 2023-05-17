def auth(request):
    """
    Context processor that provides information about the user's authentication status.

    This context processor adds a variable `user_authenticated` to the template context,
    indicating whether the user is authenticated or not.

    Args:
        request (HttpRequest): The current HTTP request.

    Returns:
        dict: A dictionary containing the `user_authenticated` variable.
    """
    return {'user_authenticated': request.user.is_authenticated}


def canonical_url(request):
    """
    Context processor that provides the canonical URL of the current page.

    This context processor adds a variable `canonical_path` to the template context,
    containing the canonical URL of the current page. The canonical URL is built using
    the `build_absolute_uri()` method of the request object.

    Args:
        request (HttpRequest): The current HTTP request.

    Returns:
        dict: A dictionary containing the `canonical_path` variable.
    """
    return {'canonical_path': request.build_absolute_uri(request.path)}
