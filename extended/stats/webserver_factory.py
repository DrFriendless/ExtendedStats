webserver = None

def get():
    global webserver
    if webserver is None:
        import django_webserver
        webserver = django_webserver
    return webserver

