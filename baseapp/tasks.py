from __future__ import absolute_import, unicode_literals

import datetime

from celery import shared_task
from django.db.models import Prefetch

from .models import Subscription, Allergy


@shared_task
def update_subscriptions_menu():
    current_datetime = datetime.datetime.now()
    subscriptions = Subscription.objects.filter(
        is_paid=True,
        expires_at__gte=current_datetime,
    ).prefetch_related(
        Prefetch(
            'allergies',
            queryset=Allergy.objects.prefetch_related(
                'ingredients'
            )
        ),
        'meal_types',
        'menu_category',
    )

    for subscription in subscriptions:
        subscription.set_today_dishes()
