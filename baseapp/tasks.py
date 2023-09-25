from __future__ import absolute_import, unicode_literals

import datetime
import random

from celery import shared_task
from django.db.models import Prefetch
from collections import Counter

from .models import Dish, Subscription, Allergy, DishIngredientItem, Ingredient


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
        subscription.today_dishes.set('')
        subscription.save()
        subscription_allergies = subscription.allergies.all()
        dishes = Dish.objects.filter(
            is_free=False,
            menu_category=subscription.menu_category
        ).prefetch_related(
            Prefetch(
                'dish_items',
                queryset=DishIngredientItem.objects.all().prefetch_related(
                    Prefetch(
                        'ingredient',
                        queryset=Ingredient.objects.filter(
                            allergies__in=subscription_allergies,
                        )
                    )
                )
            )
        )

        if subscription_allergies:
            allergies_ingredients = []
            for allergy in subscription_allergies:
                allergy_ingredients = []
                for ingredient in allergy.ingredients.all():
                    for ingredient_item in ingredient.ingredient_items.all():
                        ingredient = ingredient_item.ingredient
                        if ingredient not in allergy_ingredients:
                            allergy_ingredients.append(ingredient)

                allergies_ingredients += allergy_ingredients

            allergies_ingredients_counter = Counter(allergies_ingredients)

            available_ingredients = [
                ingredient for ingredient in allergies_ingredients_counter if
                allergies_ingredients_counter[ingredient] == len(subscription_allergies)
            ]

            available_dishes = []

            for dish in dishes:
                available_dish = True
                dish_items = dish.dish_items.all()
                for dish_item in dish_items:
                    ingredient = dish_item.ingredient
                    if ingredient not in available_ingredients:
                        available_dish = False
                        break

                if available_dish:
                    available_dishes.append(dish)

        else:
            available_dishes = dishes

        for meal_type in subscription.meal_types.all():
            meal_type_dishes = []
            for dish in available_dishes:
                if dish.meal_type == meal_type:
                    meal_type_dishes.append(dish)

            if meal_type_dishes:
                today_dish = random.choice(meal_type_dishes)

                subscription.today_dishes.add(today_dish)
                subscription.save()


