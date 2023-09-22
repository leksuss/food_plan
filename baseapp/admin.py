from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import CustomUser, Dish, DishIngredientItem, Ingredient, MealType, MenuCategory, Allergy, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name',)
    ordering = ('email',)


class DishIngredientItemInline(admin.TabularInline):
    model = DishIngredientItem
    extra = 0


class DishInline(admin.TabularInline):
    model = MenuCategory.dish.through
    extra = 0


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'meal_type',
        'is_free',
        'calories',
    ]

    list_filter = [
        'name',
        'meal_type',
        'is_free',
        'calories',
    ]

    inlines = [
        DishIngredientItemInline
    ]

    readonly_fields = [
        'get_image_preview',
    ]

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:baseapp_dish_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'price',
    ]

    list_filter = [
        'name',
        'price',
    ]

    inlines = [
        DishIngredientItemInline
    ]


@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'price',
    ]

    list_filter = [
        'name',
        'price',
    ]


@admin.register(DishIngredientItem)
class DishIngredientItemAdmin(admin.ModelAdmin):
    list_display = [
        'dish',
        'ingredient',
        'quantity',
    ]

    list_filter = [
        'dish',
        'ingredient',
        'quantity',
    ]


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]

    list_filter = [
        'name',
    ]

    inlines = [
        DishInline
    ]


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]

    list_filter = [
        'name',
    ]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'created_at',
        'expires_at',
    ]

    list_filter = [
        'created_at',
        'expires_at',
    ]



