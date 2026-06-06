from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth import forms
from .models import UserProfile


class CustomUserCreationForm(forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sexo', 'matricula')
    search_fields = ('user__username', 'user__email', 'matricula')
    list_filter = ('sexo',)
