from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import MenuCategory, MealType, Allergy


class MultiMealTypeField(forms.MultipleChoiceField):
    def validate(self, value):
        if not any(map(int, value)):
            raise ValidationError('Выберите хотя бы один тип приема пищи!')


class CustomAuthentication(AuthenticationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите e-mail'
            }
        )
    )
    name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
                'autofocus': True,
            }
        )
    )
    password1 = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль',
            }
        )
    )
    password2 = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Повторите пароль',
            }
        )
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')


class OrderForm(forms.Form):
    promocode = forms.CharField(
        required=False,
    )
    month_count = forms.IntegerField(
        required=True,
    )
    portion_quantity = forms.IntegerField(
        required=True,
    )
    menu_category = forms.ModelChoiceField(
        queryset=MenuCategory.objects.all(),
        widget=forms.RadioSelect(
            attrs={
                'class': 'foodplan_selected d-none',
            }
        ),
    )
    meal_types_choices = MealType.objects.all().order_by('name').values_list('id', 'name')
    meal_types = MultiMealTypeField(
        choices=meal_types_choices,
    )
    allergies = forms.ModelMultipleChoiceField(
        queryset=Allergy.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
