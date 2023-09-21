from django.shortcuts import render
from .forms import CustomUserCreationForm


def index(request):
    return render(request, 'index.html')


def order(request):
    return render(request, 'order.html')


def lk(request):
    return render(request, 'lk.html')


def dish(request, dish_id=None):
    if dish_id is None:
        dish = {}
    else:
        dish = {}
    return render(request, 'dish.html', context=dish)


def register(request):
    return render(request, 'auth/register.html')


def contacts(request):
    return render(request, 'contacts.html')

def authenticate(request):
    return render(request, 'auth/auth.html')
