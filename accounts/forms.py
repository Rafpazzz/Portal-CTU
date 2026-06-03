from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from book.models import Books


class AdminBookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ('titulo', 'autor', 'editora', 'ano_publicacao', 'resumo')
        widgets = {
            'resumo': forms.Textarea(attrs={'rows': 5}),
        }


class AdminUserCreateForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')


class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
