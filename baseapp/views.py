from datetime import datetime, timedelta
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import Http404

from yookassa import Configuration, Payment

from .forms import CustomUserCreationForm, CustomAuthentication, OrderForm
from .models import Dish, Subscription, MealType
from foodplan.settings import BASE_PRICE, BULK_DISCOUNT, SITE_URL, YKASSA_SHOP_ID, YKASSA_SECRET_KEY


def index(request):
    return render(request, 'index.html')


@login_required(login_url='auth')
def order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            menu_category = form.cleaned_data['menu_category']
            allergies = form.cleaned_data['allergies']
            month_count = form.cleaned_data['month_count']
            portion_quantity = form.cleaned_data['portion_quantity']
            meal_type_ids = list(map(int, form.cleaned_data['meal_types']))

            subscription = Subscription.objects.create(
                user = request.user,
                expires_at=datetime.now() + timedelta(days=month_count*30),
                portion_quantity=portion_quantity,
                menu_category=menu_category,
            )
            subscription.allergies.set(allergies)
            subscription.meal_types.set(MealType.objects.filter(id__in=meal_type_ids))

            price = BASE_PRICE * month_count * subscription.meal_types.count()
            if month_count > 1:
                price = int(price * (100 - BULK_DISCOUNT) / 100)

            Configuration.account_id = YKASSA_SHOP_ID
            Configuration.secret_key = YKASSA_SECRET_KEY

            payment = Payment.create(
                {
                    'amount': {
                        'value': price,
                        'currency': 'RUB',
                    },
                    'confirmation': {
                        'type': 'redirect',
                        'return_url': f'{SITE_URL}/payment_result/?subscription_id={subscription.id}',
                    },
                    'capture': True,
                    'description': f'Оплата подписки #{subscription.id}',
                },
                uuid.uuid4()
            )
            subscription.payment_id = json.loads(payment.json())['id']
            subscription.save()

            context = {
                'subscription': subscription,
                'price': price,
                'payment': payment,
                'month_count': month_count,
            }
            return render(request, 'order_confirm.html', context=context)
    else:
        form = OrderForm()

    context = {
        'form': form,
    }
    return render(request, 'order.html', context=context)


@login_required(login_url='auth')
def payment_result(request):
    is_paid = False
    subscription_id = request.GET.get('subscription_id')
    if subscription_id and subscription_id.isnumeric():

        subscription = get_object_or_404(Subscription, pk=subscription_id)

        Configuration.account_id = YKASSA_SHOP_ID
        Configuration.secret_key = YKASSA_SECRET_KEY
        payment = json.loads((Payment.find_one(subscription.payment_id)).json())
        if payment['status'] == 'succeeded':
            is_paid = True
        subscription.is_paid = is_paid
        subscription.save()

        context = {
            'subscription': subscription,
        }
    else:
        raise Http404()

    return render(request, 'payment_result.html', context=context)


@login_required(login_url='auth')
def lk(request):
    return render(request, 'lk.html')


def dish(request, dish_id=None):
    if dish_id is None:
        dish = {}
    else:
        dish = {}
    return render(request, 'dish.html', context=dish)


def register(request, redirect_to_order='False'):

    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'GET':
        request.session['redirect_to_order'] = redirect_to_order
        print(f"0 {request.session['redirect_to_order']}")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, new_user)
            if request.session['redirect_to_order'] == 'True':
                print(f"1 {request.session['redirect_to_order']}")
                del request.session['redirect_to_order']
                return redirect('order')
            else:
                print(f"2 {request.session['redirect_to_order']}")
                del request.session['redirect_to_order']
                return redirect('index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form,
    }

    return render(request, 'auth/register.html', context=context)


def auth(request):

    context = {
        'user_not_found_error': False,
    }
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('email'), password=request.POST.get('password1'))
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            form = CustomAuthentication()
            context['user_not_found_error'] = True
    else:
        form = CustomAuthentication()

    context['form'] = form

    return render(request, 'auth/auth.html', context=context)


@login_required(login_url='auth')
def logged_out(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'auth/logged_out.html')


def contacts(request):
    return render(request, 'contacts.html')
