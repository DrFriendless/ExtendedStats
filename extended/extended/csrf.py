from django.shortcuts import render_to_response

def wtf(request, reason=""):
    params = { "reason" : reason }
    return render_to_response("stats/csrf.html", params)