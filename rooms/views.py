from django.shortcuts import render

# Create your views here.
def add_room(request):
    return render(request, "seller_functions/add_room.html")