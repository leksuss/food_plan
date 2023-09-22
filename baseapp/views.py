from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm


def index(request):
    return render(request, 'index.html')


def order(request):
    return render(request, 'order.html')


@login_required(login_url='auth')
def lk(request):
    return render(request, 'lk.html')


def dish(request, dish_id=None):
    if dish_id is None:
        dish = {}
    else:
        dish = {}
    return render(request, 'dish.html', context=dish)


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Вы успешно зарегистрированы!')
            new_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form,
    }

    return render(request, 'auth/register.html', context=context)


def contacts(request):
    return render(request, 'contacts.html')


def auth(request):
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'auth/auth.html')
