from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator


class MealType(models.Model):
    name = models.CharField(
        'Название',
        max_length=50,
    )

    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        default=100,
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
        max_length=200,
        blank=True,
    )

    recipe = models.TextField(
        'Рецепт',
        max_length=200,
        blank=True,
    )

    image = models.ImageField(
        'Картинка',
        upload_to='dishes_images',
    )

    is_free = models.BinaryField(
        'Бесплатное',
        default=False,
    )

    meal_type = models.ForeignKey(
        MealType,
        verbose_name='Тип приема пищи',
        on_delete=models.CASCADE,
        related_name='dishes',
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

    calories = models.DecimalField(
        'Количество калорий',
        decimal_places=2,
        max_digits=7,
    )

    price = models.DecimalField(
        'Цена ингредиента',
        max_digits=8,
        decimal_places=2,
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
        return f'{self.ingredient.name} для {self.dish.name}.'


class MenuCategory(models.Model):
    name = models.CharField(
        'Название',
        max_length=50,
    )

    dish = models.ManyToManyField(
        Dish,
        verbose_name='Блюдо',
        related_name='type_of_menu',
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


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )

    today_dishes = models.ManyToManyField(
        Dish,
        verbose_name='Сегодняшние блюда подписки',
        related_name='dish_subscriptions',
        null=True,
        blank=True,
    )

    allergies = models.ManyToManyField(
        MealType,
        verbose_name='Аллергии',
        related_name='allergy_subscriptions',
        null=True,
        blank=True,
    )

    meal_types = models.ManyToManyField(
        MealType,
        verbose_name='Типы приемов пищи',
        related_name='subscriptions',
        null=True,
        blank=True,
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
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.user.name

