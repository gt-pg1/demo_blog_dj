def auth(request):
    return {'user_authenticated': request.user.is_authenticated}