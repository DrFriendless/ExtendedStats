def redirect(url):
    return None

def response(*args, **kwargs):
    return None

def render(template, context, request, *args, **kwargs):
    from flask import make_response, render_template
    if template.startswith("stats/"):
        template = "angular/" + template[6:]
    resp = make_response(render_template(template, **context))
    return resp

def get_cookie(request, cookieName):
    return request.cookies.get(cookieName)