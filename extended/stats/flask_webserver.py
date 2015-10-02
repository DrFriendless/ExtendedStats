def redirect(url):
    return None

def response(*args, **kwargs):
    return None

def render(template, context, request, *args, **kwargs):
    return None

def get_cookie(request, cookieName):
    return request.cookies.get(cookieName)