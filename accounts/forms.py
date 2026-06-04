from django import forms
from django.contrib.auth import get_user_model

from book.models import Books


class AdminBookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ('titulo', 'autor', 'editora', 'ano_publicacao', 'resumo')
        widgets = {
            'resumo': forms.Textarea(attrs={'rows': 5}),
        }


class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
    )
    is_staff = forms.BooleanField(
        label='Membro staff',
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'is_staff')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = True

        if commit:
            user.save()

        return user


class AdminUserUpdateForm(forms.ModelForm):
    is_staff = forms.BooleanField(
        label='Membro staff',
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff')
