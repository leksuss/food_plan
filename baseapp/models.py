from collections import Counter
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch


class MealType(models.Model):
    name = models.CharField(
        'Название',
        max_length=50,
    )

    price = models.PositiveIntegerField(
        'Цена',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Тип приема пищи'
        verbose_name_plural = 'Типы приемов пищи'

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(
        'Название блюда',
        max_length=50,
    )

    description = models.TextField(
        'Описание',
        max_length=500,
        blank=True,
    )

    recipe = models.TextField(
        'Рецепт',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='dishes_images',
    )

    is_free = models.BooleanField(
        'Бесплатное',
        default=False,
    )

    meal_type = models.ForeignKey(
        MealType,
        verbose_name='Тип приема пищи',
        on_delete=models.CASCADE,
        related_name='dishes',
    )

    calories = models.PositiveIntegerField(
        'Количество калорий',
        validators=[MinValueValidator(1)],
    )

    cooking_time = models.TimeField(
        'Время приготовления'
    )

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=50,
    )

    price = models.PositiveIntegerField(
        'Цена ингредиента',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class DishIngredientItem(models.Model):
    dish = models.ForeignKey(
        Dish,
        verbose_name='Блюдо',
        on_delete=models.CASCADE,
        related_name='dish_items',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_items',
    )

    quantity = models.PositiveIntegerField(
        'Количество ингредиента',
        validators=[MinValueValidator(1)],
    )

    measurement = models.CharField(
        'Мера ингредиента',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Ингредиент в блюде'
        verbose_name_plural = 'Ингредиенты в блюде'

    def __str__(self):
        return f'{self.ingredient.name} для {self.dish.name}'


class MenuCategory(models.Model):
    name = models.CharField(
        'Название',
        max_length=50,
    )

    dish = models.ManyToManyField(
        Dish,
        verbose_name='Блюда',
        related_name='menu_category',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='menu_category_images',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Вид диеты'
        verbose_name_plural = 'Виды диеты'

    def __str__(self):
        return self.name


class Allergy(models.Model):
    name = models.CharField(
        'Название',
        max_length=50,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Подходящие ингредиенты',
        related_name='allergies',
    )

    class Meta:
        verbose_name = 'Аллергия'
        verbose_name_plural = 'Аллергии'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )

    today_dishes = models.ManyToManyField(
        Dish,
        verbose_name='Сегодняшние блюда подписки',
        related_name='dish_subscriptions',
        blank=True,
    )

    allergies = models.ManyToManyField(
        Allergy,
        verbose_name='Аллергии',
        related_name='allergy_subscriptions',
        blank=True,
    )

    meal_types = models.ManyToManyField(
        MealType,
        verbose_name='Типы приемов пищи',
        related_name='subscriptions',
        blank=True,
    )

    menu_category = models.ForeignKey(
        MenuCategory,
        verbose_name='Категория меню',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        verbose_name='Дата истечения подписки',
    )

    portion_quantity = models.PositiveIntegerField(
        'Количество персон',
        default=1,
        validators=[MinValueValidator(1)],
    )

    is_paid = models.BooleanField(
        'Подписка оплачена?',
        default=False,
    )

    payment_id = models.CharField(
        'Идентификатор платежного агента',
        max_length=250,
        null=True,
        blank=True,
    )

    def calorie_count(self):
        return sum([dish.calories for dish in self.today_dishes.all()])


    def set_today_dishes(self):
        self.today_dishes.set('')
        self.save()
        subscription_allergies = self.allergies.all()
        dishes = Dish.objects.filter(
            is_free=False,
            menu_category=self.menu_category
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

        for meal_type in self.meal_types.all():
            meal_type_dishes = []
            for dish in available_dishes:
                if dish.meal_type == meal_type:
                    meal_type_dishes.append(dish)

            if meal_type_dishes:
                today_dish = random.choice(meal_type_dishes)

                self.today_dishes.add(today_dish)
                self.save()


    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.user.email


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('Почта должна быть введена'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.id, filename)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('E-mail', unique=True)
    name = models.CharField('Имя', max_length=250, blank=True)
    avatar = models.ImageField('Аватар', blank=True, upload_to=user_directory_path)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

