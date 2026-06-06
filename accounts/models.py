from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    class Sexo(models.TextChoices):
        MASCULINO = 'masculino', 'Masculino'
        FEMININO = 'feminino', 'Feminino'
        OUTRO = 'outro', 'Outro'
        NAO_INFORMADO = 'nao_informado', 'Nao informado'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    sexo = models.CharField(
        max_length=20,
        choices=Sexo.choices,
        default=Sexo.NAO_INFORMADO,
    )
    matricula = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'
