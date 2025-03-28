from django.shortcuts import render

def index(request):
    return render(request,"lacfom/index.html", context={"user_name": "user"})