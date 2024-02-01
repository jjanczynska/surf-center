from django.shortcuts import render


# Error handling view for 404, 405 and 500
def handler404(request, exception):
    """ Error Handler 404 - Page Not Found """
    return render(request, "404.html", status=404)


def handler405(request, exception):
    return render(request, "405.html", status=405)


def handler500(request):
    return render(request, "500.html", status=500)