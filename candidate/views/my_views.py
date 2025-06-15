from django.shortcuts import render

def my_home(request):
    """
    Render the home profile page for a candidate.
    """
    return render(request, "my/home.html")