from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from book.models import Books
from .models import UserProfile


class RegisterUserForm(UserCreationForm):
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=UserProfile.Sexo.choices,
    )
    matricula = forms.CharField(
        label='Matricula',
        max_length=30,
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'sexo', 'matricula', 'password1', 'password2')

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if matricula and UserProfile.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Ja existe um usuario com essa matricula.')
        return matricula or None

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            UserProfile.objects.create(
                user=user,
                sexo=self.cleaned_data['sexo'],
                matricula=self.cleaned_data['matricula'],
            )

        return user


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
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=UserProfile.Sexo.choices,
    )
    matricula = forms.CharField(
        label='Matricula',
        max_length=30,
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'is_staff', 'sexo', 'matricula')

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if matricula and UserProfile.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Ja existe um usuario com essa matricula.')
        return matricula or None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = True

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                sexo=self.cleaned_data['sexo'],
                matricula=self.cleaned_data['matricula'],
            )

        return user


class AdminUserUpdateForm(forms.ModelForm):
    is_staff = forms.BooleanField(
        label='Membro staff',
        required=False,
    )
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=UserProfile.Sexo.choices,
    )
    matricula = forms.CharField(
        label='Matricula',
        max_length=30,
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'sexo', 'matricula')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, 'profile', None)
        if profile is not None:
            self.fields['sexo'].initial = profile.sexo
            self.fields['matricula'].initial = profile.matricula

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        queryset = UserProfile.objects.filter(matricula=matricula) if matricula else UserProfile.objects.none()

        if self.instance and self.instance.pk:
            queryset = queryset.exclude(user=self.instance)

        if queryset.exists():
            raise forms.ValidationError('Ja existe um usuario com essa matricula.')

        return matricula or None

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'sexo': self.cleaned_data['sexo'],
                    'matricula': self.cleaned_data['matricula'],
                },
            )

        return user
