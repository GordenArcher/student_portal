from django.shortcuts import render
from django.http.response import HttpResponse

# Create your views here.

def home_page(request):

    return render(request, "Index.html")