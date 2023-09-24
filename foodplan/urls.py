"""
URL configuration for foodplan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

import baseapp.views
from . import settings


urlpatterns = [
    path('', baseapp.views.index, name='index'),
    path('order/', baseapp.views.order, name='order'),
    path('payment_result/', baseapp.views.payment_result, name='payment_result'),
    path('dish/', baseapp.views.dish, name='free_dish'),
    path('dish/<int:dish_id>/', baseapp.views.dish, name='dish'),
    path('lk/', baseapp.views.lk, name='lk'),
    path('contacts/', baseapp.views.contacts, name='contacts'),
    path('register/', baseapp.views.register, name='register'),
    path('register/<str:redirect_to_order>', baseapp.views.register, name='register'),
    path('admin/', admin.site.urls),
    path('auth/', baseapp.views.auth, name='auth'),
    path('logged_out/', baseapp.views.logged_out, name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
